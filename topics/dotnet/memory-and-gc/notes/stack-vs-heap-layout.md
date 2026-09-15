---
concept: stack-vs-heap-layout
topic: dotnet
cluster: memory-and-gc
created: 2026-09-08
taught: 2026-09-15
---

# Stack vs heap layout

## Mechanism

### The stack

- **One stack per thread**, never shared. The main thread, every thread-pool
  worker, the finalizer thread — each has its own. Fixed size, reserved at
  thread creation (1 MB default on Windows, 1.5 MB for secondary threads on
  Linux).
- That is why a plain local is thread-safe by construction, and why a local
  that must survive an `await` is moved to the heap: the continuation may run
  on a different thread, with a different stack.
- Each call pushes a **frame**: return address, saved registers, locals,
  spill temporaries.

Example method used below — any method holding the 2026-09-08 question's code:

```csharp
void Handle()
{
    int x = 5;
    var p = new Point(1, 2);      // struct Point { int X; int Y; }
    var list = new List<int>();
}
```

```
call Handle():    rsp -= frameSize     <- the entire "allocation"
Handle() returns: rsp += frameSize     <- the entire "free"
```

- Nothing is zeroed or freed item by item; the next call overwrites the bytes.
  No GC involvement in frames.
- The optimising JIT **enregisters** many locals — they live in CPU registers
  and never get a stack slot.

### The GC heap

- Every object: 16-byte header (sync block index + method table pointer), then
  fields. Allocation is a pointer bump in the thread's allocation context.
- An object exists until the GC finds it **unreachable** and a later
  collection reclaims its space.

### The rule: a value lives where its container lives

Not "value types live on the stack".

| What | Where the bits are |
|---|---|
| value-type local | stack slot or register |
| reference-type local | the **reference** (8 bytes) in a slot/register; the **object** on the heap |
| value-type field of a class | inline **inside the object, on the heap** |
| array element (`int[]`) | inline inside the array object, on the heap |
| local captured by a lambda | hoisted into a compiler-generated closure class, on the heap |
| local surviving an `await` | hoisted into a state-machine field; on the heap once an await does not complete synchronously |
| static field | runtime-owned heap storage; a root for its load context's lifetime |
| a `ref struct` value itself (`Span<T>`) | stack or register only, compiler-enforced — but **not** the memory a span points at |

Recent JITs (.NET 9/10) can stack-allocate a small object that provably never
escapes. An optimisation, never a language guarantee — not something to rely on
or semantically observe.

### Sizes — how many bytes a `new` asks for

Computed **once per type** by the class loader and stored in the method table.
`new` does no arithmetic at runtime.

- **Field sizes:** `byte`/`bool` 1 · `short`/`char` 2 · `int`/`float` 4 ·
  `long`/`double`/`DateTime` 8 · **any reference field 8** (a pointer, however
  big the object behind it) · a **struct field = the struct's full size**,
  inline.
- **Struct:** sum of fields plus padding. Each field aligns to its own size (up
  to 8); the total rounds up to the largest alignment. No header. Order
  matters, because C# lays structs out sequentially — unless the struct holds
  a reference field, in which case the runtime is free to reorder it:
  - `{ byte; int; byte }` → 1 + 3 pad + 4 + 1 + 3 pad = **12**
  - `{ int; byte; byte }` → 4 + 1 + 1 + 2 pad = **8**
- **Class instance:** 16-byte header + fields (base-class fields first),
  rounded up to 8. The runtime **reorders** class fields to minimise padding.
  Minimum 24 bytes, even for a class with no fields.
- **Array:** 16 header + 8 length slot + count × element size.
  `int[1000]` = 16 + 8 + 4,000 = **4,024**. `object[1000]` = 8,024, plus the
  objects themselves.
- **Shallow, not retained.** An object's size never includes what its
  references point at.

| Type | Size (x64) |
|---|---|
| `struct Point { int X; int Y; }` | 8 |
| `class PointC { int X; int Y; }` | 16 + 8 = 24 |
| `class Order { DateTime Created; List<int> Lines; }` | 16 + 8 + 8 = 32 |
| the `List<int>` it points at (`_items` ref, `_size`, `_version`) | 16 + 8 + 4 + 4 = 32 |
| its `int[]` backing store, capacity 4 | 16 + 8 + 16 = 40 |

Checked with `Unsafe.SizeOf<T>()` for structs (it returns 8 for a class — the
reference), and with `GC.GetAllocatedBytesForCurrentThread()` before and after
a `new` for heap objects.

### `ref struct` and `Span<T>` — what stays on the stack

- `ref struct` is a **struct** with a rule: the value itself may never reach the
  heap. The compiler rejects boxing it, a field of it in a class or normal
  struct, arrays of it, capturing it in a lambda, and holding it across an
  `await`. That guarantee is total — enforced at compile time.
- There is no `ref class`. It does not apply to reference types.
- `Span<T>` is a ref struct of two fields: a `ref T` to the first element and an
  `int` length. **It does not move data.** It points wherever the data already
  is:
  - `new int[100].AsSpan()` → the array is on the heap; only the 16-byte span
    is on the stack
  - `Span<int> s = stackalloc int[64];` → the 256 bytes are in the frame
  - native memory, or a slice of a string
- Only **`stackalloc`** puts the data itself on the stack, and only for
  unmanaged element types — no references, so no reference-type objects.
- Why the rule exists: a `ref T` is an **interior pointer**, which the GC tracks
  in stack frames but not inside heap objects. And a span over `stackalloc`
  memory must not outlive the frame; ref-safety rules stop a method returning
  it.

```
Handle()'s frame (stack)              GC heap
┌──────────────────────────┐
│ x    : 5                 │
│ p    : [X=1][Y=2]        │  <- struct bits inline
│ list : 0x…a0 ────────────┼──────►  [sync|MT List<int>|_items ─┐|_size|_version]
└──────────────────────────┘                                     v
                                      [sync|MT int[]|length| int int int int ]
```

### What happens on return

1. The frame goes. `x`, `p` and the `list` **reference** cease to exist.
2. **The `List<int>` object is not touched.** One root disappeared.
3. If nothing else refers to it, it is *unreachable* — still occupying heap
   bytes.
4. Its space returns when a collection of its generation runs, triggered by an
   **allocation budget** being exceeded ([[gc-triggers-and-budgets]]) —
   milliseconds or minutes later. The GC never frees a dead object
   individually: it marks live objects and compacts or sweeps around the dead,
   so dead space costs nothing to reclaim.

### How the GC reads the stack

- The JIT emits **GC info** per compiled method: which stack slots and
  registers hold live references at each safe point.
- At a collection the runtime suspends threads and **walks each stack** frame
  by frame, reading those locations as **roots**. Statics, GC handles and the
  finalization queue are roots too.
- Liveness is **by code position**: optimised code treats a reference as dead
  after its last use, **before the method returns**. An object can be
  collected while the method that created it is still running.
- **Unoptimised code** — Debug builds, and Tier-0 code in Release before
  tier-up — keeps local references reported live to the end of the method.

## Failure modes

- **"Out of scope, so freed."** An object reachable from a static, cache,
  singleton or event subscription lives forever. Scope ends; reachability does
  not. Symptom: gen 2 size climbing across full collections.
- **Debug vs Release lifetimes differ.** A memory test that passes in Debug can
  show earlier collection in Release, or vice versa. `x = null` at method end
  is almost always useless in Release — the JIT already knows `x` is dead.
- **Collected too early.** Optimised code drops the last reference to an object
  whose finalizer closes a native handle while a native call still uses the
  handle; the finalizer runs mid-call. Hence `GC.KeepAlive(obj)` and
  `SafeHandle`. See [[finalization-and-freachable-queue]].
- **Heap allocation with no `new`.** Captured lambda locals, locals across an
  `await`, [[boxing]], a struct stored in a class field. Symptom: profiler
  allocations in code that looks allocation-free.
- **`StackOverflowException`.** Unbounded recursion or oversized `stackalloc`
  kills the **process**; it cannot be caught. Distinct from
  `OutOfMemoryException`, a heap failure and usually catchable.
- **Large struct copies.** Every assign, pass and return by value copies all
  bytes. A mutable struct modified through a copy — including a defensive copy
  on a `readonly` field — silently loses the change.

## Trade-offs

- **Stack:** allocation and free are pointer moves, excellent locality, zero GC.
  Costs: small fixed size, cannot outlive the frame, cannot be shared across
  threads, size known at JIT time (except `stackalloc`).
- **Heap:** arbitrary lifetime and sharing. Allocation is **also cheap**; the
  cost is downstream — every allocation spends gen 0 budget (collection
  frequency), every survivor is mark/copy work, every reference followed is a
  potential cache miss.
- **The real decision is struct vs class, not stack vs heap.** Placement follows
  the container, so "make it a struct so it is on the stack" is the wrong
  reason.
  - **Struct:** no header, inline, not a GC object. Paid for with a copy on
    every assignment, boxing risk through interfaces, no identity. Guideline:
    small (~16 bytes or less) and immutable.
  - **Class:** identity, sharing, polymorphism. Paid for with a 16-byte header,
    an 8-byte reference and a pointer hop.
- **Where it pays:** a struct in a million-element array is a real win — one
  contiguous block, one GC object. A 64-byte struct passed by value through
  five layers is a loss.

## Drill — 2026-09-15

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `Handle()` with `int count`, `var order = new Order()` (`DateTime Created`, `List<int> Lines`), and `Func<int> next = () => count + 1` — where does each piece live, and what happens on return? | `order` variable on the stack and object on the heap, `Created` inline in the object, and the frame reused on return — correct. Placed `count` on the stack: it is **captured by the lambda**, so it is hoisted into a compiler-generated closure object on the heap, and the delegate is a second heap object. Nested the ints "inside Lines inside the Order object": `Order` holds a *reference* to a separate `List<int>`, which holds a reference to a separate `int[]` where the ints sit. Said the `order` variable becomes unreachable — the variable ceases to exist; the *object* becomes unreachable. | miss |
| 2 | Convert 64-byte `OrderLine` from class to struct "so it lives on the stack" — stored in `List<OrderLine>`, passed through layers, cast to `IPriced`. What's wrong, what does it cost, what does it gain, when would you approve? | Correctly rejected the premise (still on the heap) and named both costs: 64-byte copies per pass, a box per interface cast. Placed the lines "inside the Order object" — they would sit inline in the list's `OrderLine[]`, a separate heap object. Did not answer the gain half: no 16-byte header and 8-byte reference per line, one array object instead of N objects, contiguous layout, less mark work. Did not state conditions: `readonly struct`, `in` parameters, generic constraints instead of `IPriced` casts, a measured hot path. | miss |
| 3 | Release build: 50 MB array, last used before a ten-minute `DoOtherWork()`. Collectable before `Run()` returns? How does the GC know? Debug or first calls in Release? | Yes, and liveness ends at the last use — correct. Did not name the mechanism: JIT-emitted GC info recording which slots and registers hold live references at each safe point, read during a stack walk. Debug "keeps objects alive longer" with no reason (unoptimised code reports locals live to method end), and the Tier-0 half of the question — the first calls of a Release build — was not addressed. | miss |

Drill results do not change a level.

## Model answers — 2026-09-15

For each interview question on this concept graded below target.

### Q2 (2026-09-08) — target L2, awarded L1

*`int x = 5; var p = new Point(1,2)` (struct); `var list = new List<int>()`.
Where does each live, and what happens to each when the method returns?*

`x` and `p` are value-type locals, so their bits are in the method's frame, or
in a register. `p` is 8 bytes — two ints inline, no header. `list` is two
things: the variable is an 8-byte reference in the frame, and the `List<int>`
it points at is an object on the GC heap, which in turn points at a backing
`int[]`, another heap object. When the method returns the frame is popped:
`x`, `p` and the reference simply stop existing, and nothing is freed. The
`List<int>` object is not touched. If nothing else refers to it, it is now
unreachable, and its space comes back at the next gen 0 collection — whenever
the allocation budget runs out, not at the return. Had I stored it in a static,
it would stay reachable and survive.

Graded answer lacked: the separation of the reference from the object, and that
returning frees nothing on the heap — reclamation waits for a budget-triggered
collection.

### Q8 (2026-09-12) — target L2, awarded L1

*`Order` has a `DateTime` field; where does it live after `new Order()`? A
`List<int>` holds a thousand items; where do the ints live?*

The `DateTime` is 8 bytes inline inside the `Order` object on the heap — a
value lives where its container lives. Only the reference to the `Order` is in
the frame. The `List<int>` is a heap object holding a reference to an `int[]`,
also on the heap, with capacity at least a thousand; the ints are stored inline
in that array, 4 bytes each, contiguous. Nothing boxes: `List<int>` is a
generic instantiation the JIT specialises for `int`, so `Add` writes 4 bytes
into the array and the indexer reads them back. A box appears only with a slot
typed `object` — `ArrayList`, `List<object>` — and a box is by definition a
heap object, never on the stack.

Graded answer lacked: that `List<int>` does not box, and that a box always lives
on the heap. Both asked placements were right.

## Resources

## Related

[[gc-generations]] · [[gc-triggers-and-budgets]] · [[boxing]] · [[finalization-and-freachable-queue]]
