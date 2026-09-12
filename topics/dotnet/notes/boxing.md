---
concept: boxing
topic: dotnet
cluster: memory-and-gc
created: 2026-09-12
taught: 2026-09-12
---

# Boxing

## Mechanism

- A value type **is** its bits, stored inline wherever it lives: a local in a
  stack slot, a field inside its containing object, an element inside an
  array. At runtime those bits carry no header and no type information.
- A slot typed `object` — or an interface — needs a pointer to a real heap
  object, and every heap object starts with a **sync block index** and a
  **method table pointer**.
- **Boxing** bridges the two: allocate a new object on the GC heap holding
  that header plus a **copy** of the value, and yield a reference to it.

```
int x = 42;              stack: [42]          <- 4 bytes of bits, no header

object o = x;            stack: [o] ──────┐
                                          v
                         heap:  [ sync block | method table -> Int32 | 42 ]
                                  24 bytes on x64, for a 4-byte int
```

- **The box is on the heap, always.** That is the definition, not a detail. A
  box on the stack would be pointless: the whole purpose is to produce
  something a reference can point at, and a reference to a stack slot cannot
  outlive the frame. The value starts inline; boxing moves a *copy* to the
  heap.
- Boxing **copies**, so the box is a snapshot — later changes to `x` do not
  touch it.

### The object header — what those 16 bytes are

```
             -8                0                8
              [ sync block ] [ method table ] [ fields... ]
                                ^
                        the reference points HERE
```

The reference points at the **method table pointer**; the **sync block index**
sits at a negative offset behind it (-8 on x64, -4 on x86).

- **Method table pointer** → the runtime's description of the type: size, base
  type, interface map, and the slot table used for virtual dispatch. It is what
  makes `GetType()`, `is`, casts and virtual calls work. On a box it says
  `Int32`, which is exactly what an unboxing cast inspects.
- **Sync block index** → one word of bit-packed state, not normally a pointer.
  Holds the `Monitor`/`lock` state (most locks live entirely here as a **thin
  lock**: owning thread id + recursion count, no allocation), the cached hash
  code once `GetHashCode()` is called, and GC/pinning bits. When one word
  cannot hold everything (real contention, or a hash code *and* a lock), the
  runtime **inflates** it: allocates a real sync block in a global table and
  stores an index to it here. Hence the name.

So a field-less object still costs 16 bytes of header, and `lock` on a plain
object is nearly free until contended.

**The 24 bytes:** 8 sync block + 8 method table + 4 payload + 4 padding to
8-byte alignment. 24 bytes to carry 4 — and 24 is the minimum object size on
x64 regardless.

### Unboxing is the cheap direction

**Unboxing** (`(int)o`, `unbox.any` in IL) does two things: load the
referenced object's method table pointer and compare it to the target type
(`InvalidCastException` on mismatch), then copy the value bits out.

- **No allocation, no GC pressure.** Cost is a load/compare/branch plus a copy.
- The part that actually hurts is the **dereference**: reaching into the box to
  read it, paying a possible cache miss to retrieve 4 bytes of payload.
- So in a read-heavy loop over an already-boxed collection, the *unboxing* is
  what you feel, even though the *boxing* caused it. This asymmetry is why the
  advice is always "avoid the box", never "avoid the unbox".

### Generics do not box — why `List<int>` is not `ArrayList`

- Generics are **specialized per value type**. `List<int>` is its own runtime
  type with its own JIT-compiled code, and its backing store is a real
  `int[]`: elements inline, 4 bytes each, contiguous. `Add` writes bits into
  the array; the indexer reads them back. No object is created, so there is
  nothing to box and nothing to unbox.
- `ArrayList` is the thing that boxes: its backing store is `object[]`, so
  adding an `int` boxes and reading requires an unbox. Removing that cost is a
  large part of why generics were added in .NET 2.0.
- `List<object>` and `object[]` still box, because the slot really is a
  reference.
- Reference types share **one** compiled instantiation over `object` (a
  pointer is a pointer); value types each get **their own**, because the
  layout differs.

### Where boxing still happens

`object o = 42` · assigning a struct to an interface · `List<object>`,
`Dictionary<string, object>`, `object[]` · `params object[]` in formatting and
logging · calling a struct's interface method through the interface (but a
generic constraint `where T : IFoo` compiles to a **constrained call** and does
not box) · `foreach` over `IEnumerable<int>` when the concrete type has a
struct enumerator (the enumerator is boxed once per loop).

## Failure modes

- **A struct key without `IEquatable<T>`.** `Dictionary<MyStruct, V>` looks
  allocation-free. Without `IEquatable<MyStruct>`, `EqualityComparer<T>.Default`
  falls back to `Object.Equals`, which boxes **both operands on every
  comparison**. Symptom: gen 0 churn scaling with lookup count in code that
  appears to allocate nothing. Same for `IComparable<T>` in sorted collections.
- **A struct behind an interface parameter.** `void Process(IShape s)` boxes
  once per call when handed a struct. `void Process<T>(T s) where T : IShape`
  boxes nothing. The highest-yield fix in a hot path.
- **Mutation thrown away.** Box a struct, mutate it through the interface, and
  the change lands in the box while the original is untouched. Nothing looks
  wrong and the compiler does not object.
- **`params object[]`.** String formatting and most logging APIs box every
  value-type argument on every call, including calls whose level is disabled.
  `LoggerMessage.Define` and interpolated-string handlers exist for this.
- **Invisible in source.** There is no `new` to spot. Boxing appears only as a
  `box` IL instruction, so it is found with an allocation profiler or by
  reading IL — never by reading C#.
- **Lost locality — usually the biggest cost, and the one people omit.** 1,000
  ints in an `int[]` are 4,000 contiguous bytes the hardware prefetcher walks
  happily. 1,000 boxed ints in an `object[]` are 8,000 bytes of pointers plus
  1,000 separate 24-byte objects sitting wherever gen 0 happened to be.
  Reading them all becomes pointer chasing with a cache miss per element. The
  allocation is a one-off; the bad layout is paid on **every subsequent read**.
- **Gen 0 pressure and mark work.** Every box spends gen 0 budget, so boxing
  raises collection *frequency*; and every reachable box is one more object the
  collector must mark, which is survivor work. See
  [[gc-triggers-and-budgets]].

## Trade-offs

- Boxing is the **price of uniformity**: one `object` slot that holds anything
  requires everything to look like an object. Generics buy back exact layout
  and zero boxing, paid for in **code size** — each value-type instantiation
  gets its own JIT-compiled copy, costing JIT time and instruction cache.
- **Cost scales with frequency, not presence.** One box at a startup boundary
  is free in every sense that matters. The same box per item, per request or
  per message *is* the allocation profile.
- Usual escapes: generic constraints instead of interface parameters;
  `IEquatable<T>`/`IComparable<T>` on structs used in collections; generic
  logging overloads; `Span<T>` where a collection was not really needed.
- **Do not over-rotate.** Chasing every box costs readability for nothing if
  the call site runs ten times a second. Measure, then fix the hot ones.
- Boxing is also what makes `Nullable<T>` subtle: boxing an `int?` yields a
  boxed `int` when it has a value, and a plain `null` when it does not.

## Drill — 2026-09-12

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | Adding `5` to `List<int>` / `ArrayList` / `List<object>` — which box, and what is each backing store? | `a` does not box, `b` and `c` do. Reasoned that a specialised type is created for `List<int>` so the header exists once for the array and each element is just 4 bytes in a contiguous block, while `object` slots upcast each element so every one gets its own sync block and method table pointer. Correct throughout. Wrinkle: said specialisation happens at compile time; it happens at **runtime** (JIT creates the instantiation on first use). | hit |
| 2 | `Total(IShape)` vs `Total<T>(T) where T : IShape`, one million circles — which, why, and what do you give up? | Picked B and explained the absence of boxing and the per-type specialisation correctly. Did not answer the third part: what B costs. Missing — one compiled instantiation per value type (instruction cache, JIT time, AOT binary size), and the loss of a single heterogeneous call site that A provides. | miss |
| 3 | `Dictionary<OrderId, Order>` with a bare struct key — what allocates in one `TryGetValue`, how many times, why? | Identified the boxing and its cause correctly and unprompted: no `IEquatable`, no overridden `GetHashCode`. Count was wrong — said "it will box someId", i.e. once. Actual is ~7: one box to dispatch to `ValueType.GetHashCode`, then **both operands** boxed per comparison via `Object.Equals(object)`, so six across three comparisons. Did not reach the both-operands point, nor that `ValueType.Equals`/`GetHashCode` walk fields generically. | miss |

Drill results do not change a level.

No `## Model answers` section: no interview question has ever been graded on
this concept. The miss that created it surfaced inside Q8 of
[[2026-09-12-gc-triggers-and-budgets]], whose graded concept was
[[stack-vs-heap-layout]].

## Resources

## Related

[[stack-vs-heap-layout]] · [[gc-triggers-and-budgets]]
