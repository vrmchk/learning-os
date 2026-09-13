---
concept: large-object-heap
topic: dotnet
cluster: memory-and-gc
created: 2026-09-12
taught: 2026-09-13
---

# Large object heap

## Mechanism

### The threshold is 85,000 bytes

Any object whose **total size** reaches 85,000 bytes is allocated straight onto
the LOH instead of gen 0. `byte[100_000]` lands there; `byte[80_000]` does not.
Configurable since .NET Core 3.0 via `GCLOHThreshold`; almost nobody changes it.

The threshold exists because of **compaction cost**. Compacting means copying
objects and rewriting every reference to them. For a multi-megabyte array that
copy dominates everything else the collector does, so the runtime made a
deliberate exception: above a certain size, do not move the object at all.

Large objects are allocated **directly** on the LOH. They never pass through
gen 0 and are never promoted. They are collected **only as part of a gen 2
collection**, and their allocations bill against a separate LOH budget whose
exhaustion triggers exactly that. Churning large buffers is therefore a way of
forcing full collections without ever calling `GC.Collect` — see
[[gc-triggers-and-budgets]].

### Two independent axes: size picks the heap, age picks the generation

Gen 2 **is** the regular heap. The LOH is separate memory; the only thing they
share is a collection schedule.

- The **small object heap (SOH)** holds gen 0, gen 1 and gen 2. It is compacted.
- The **LOH** holds objects ≥ 85,000 bytes. It is swept.
- A full collection condemns gen 0, gen 1, gen 2 **and** the LOH together —
  which is why docs sometimes call the LOH "generation 3". That is a scheduling
  convenience, not a location. (.NET 5+ adds a third heap, the **POH** for
  pinned objects, likewise collected with gen 2.)

| Decided by | Determines | When |
|---|---|---|
| **Size** at allocation | Which heap: SOH or LOH | Once, permanently |
| **Collections survived** | Which generation, within the SOH | Repeatedly |

So an object under the threshold that survives two collections is **gen 2 on
the regular heap**, and never migrates to the LOH. Nothing ever does. Likewise
a large object is on the LOH from birth and is collected with gen 2 without
ever having been gen 0 or gen 1. Size is decided once at birth and never
revisited; age moves an object between generations only within the heap it was
born on.

### Four budgets, one escalation

There are **four separate allocation budgets**, not one shared counter. All are
dynamic and retuned from observed survival after each collection.

| Budget | Spent by | Exhaustion triggers |
|---|---|---|
| gen 0 | allocation in gen 0 | gen 0 collection |
| gen 1 | promotions out of gen 0 | gen 1 collection (also takes gen 0) |
| gen 2 | promotions out of gen 1 | gen 2 collection (everything, incl. LOH) |
| **LOH** | large allocations directly | **gen 2 collection** |

The LOH budget and the gen 2 budget are **separate counters with the same
consequence**: whichever is exhausted, the collection that runs is a gen 2,
because the LOH can only ever be collected as part of one. Separate
accounting, shared escalation.

Internally the runtime really does track the LOH as **generation 3**
(`max_generation + 1`), with its own bookkeeping slot and budget alongside the
three real generations — so the name is more than documentation shorthand, even
though the memory is a separate heap and objects there never age through
generations. The POH (.NET 5+) works the same way.

**The practical consequence**, and the signature to recognise: you can drive
full collections purely by LOH churn while gen 2's own budget is nowhere near
exhausted. A per-request 200 KB buffer promotes nothing, so gen 2's budget is
never spent and gen 0 and gen 1 never see the allocation at all — but the LOH
budget is spent once per request, and each exhaustion forces a full collection.
**Gen 2 collections at request rate with flat gen 0 and gen 1 counts is the
signature of LOH churn**, and nothing else produces that shape. Observable via
`GC.GetGCMemoryInfo()`, whose per-generation info includes the LOH.

### Swept, not compacted — and what that costs

When a large object dies its space goes on a **free list**. Survivors stay
exactly where they are. Nothing slides, nothing is copied, no gaps are closed.

That changes allocation itself. Gen 0 allocation is a **pointer bump**; LOH
allocation is a **free-list search** for a block big enough to fit. It is
slower, and it can fail even when there is ample free space in total.

```
LOH after some churn:

  [ LIVE 20MB ][ free 40MB ][ LIVE 10MB ][ free 30MB ][ LIVE 5MB ][ free 50MB ]

  request: new byte[100MB]
  total free    = 120MB
  largest block =  50MB     <- nothing fits, so the heap grows anyway
```

The released space *is* reused — but only by an allocation small enough to fit
one of the holes. A request larger than every individual hole grows the heap
regardless of the total. That is **fragmentation**, and it is the whole
difference from a compacted generation.

**Why it cannot happen on the SOH.** In a compacted heap the problem does not
arise: after a collection the survivors are packed together and all free space
is one contiguous block at the end, so an allocation fails only when you are
genuinely out of memory. The LOH does not compact, so the holes persist.

```
allocate A(50MB) B(50MB) C(50MB)   ->  [A][B][C]
B dies, collection runs            ->  [A][free 50][C]
allocate D(60MB)                   ->  60 does not fit in 50, heap grows
                                       [A][free 50][C][D]
```

That 50MB hole is now usable only by something that fits inside it. If nothing
that small ever comes along, it is wasted for the life of the process.

Two refinements:

- **Adjacent free blocks are coalesced.** Had `A` and `B` both died, their space
  would merge into one 100MB block. Fragmentation is not pure one-way decay.
- **A survivor between two holes pins the split permanently**, until it dies or
  compaction is forced. The pathological pattern is therefore *alternating*
  long-lived and short-lived large allocations, where each survivor becomes a
  permanent divider.

**The measurable signature** is total free space climbing over days while the
largest contiguous block does not. That is the shape that ends in an
`OutOfMemoryException` with gigabytes reported free.

## Failure modes

- **Buffers just over the threshold, per request.** Reading a response or file
  into an array sized by content length is the classic. Every request allocates
  on the LOH, bills the LOH budget, and drives gen 2 collections at request
  rate. Symptom: a gen 2 count that tracks traffic.
- **OutOfMemoryException with memory to spare.** Fragmentation means an
  allocation fails while the process shows gigabytes free. The most confusing
  production failure the LOH produces; the free-list picture above is the whole
  explanation.
- **Growth by doubling.** `List<T>` and `StringBuilder` grow by allocating a
  larger array and abandoning the old one. Past the threshold, every doubling
  leaves a dead large array behind and punches another hole.
- **Large strings.** A `char` is 2 bytes, so any string beyond roughly 42,500
  characters is a large object. People rarely expect text to land there.
- **Assuming it is compacted like everything else.** It is not, by default.

## Trade-offs

- **Not compacting trades fragmentation for copy cost**, and for most workloads
  that is the right side of the trade: copying multi-megabyte arrays on every
  gen 2 would cost far more than the fragmentation does. 85,000 bytes is simply
  where the runtime judges copying to stop being worth it.
- **You can force compaction** — `GCSettings.LargeObjectHeapCompactionMode =
  GCLargeObjectHeapCompactionMode.CompactOnce`, then `GC.Collect()`. It
  genuinely fixes fragmentation and costs a **full blocking compacting gen 2
  collection**, which can run to seconds on a large heap. Defensible after a
  batch job or at a quiet moment; never in a request path.
- **The real fix is not allocating.** `ArrayPool<T>.Shared` rents a large buffer
  and takes it back, so one allocation serves every request and the heap never
  fragments. The price is complexity and a genuine hazard: a buffer used after
  being returned, or never returned, is a worse bug than the one being fixed.
- **The other real fix is staying under the threshold deliberately.** Stream in
  fixed chunks well below 85,000 bytes instead of buffering a whole payload,
  keeping everything in gen 0 where death is nearly free — see
  [[gc-generations]].

## Drill — 2026-09-13

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `byte[80_000]`, `byte[90_000]`, `new string('x', 50_000)` — which heap each, and why? | "a in small object heap, b and c in LOH, because b is more than 85k bytes and c because char is 2 bytes which makes this string 100k." Correct on all three, including the 2-bytes-per-char trap the question was built around. | hit |
| 2 | Fragmented LOH, OOM after a week, 200 KB per-request buffers — force compaction on a timer, or move to `ArrayPool`? What does each cost? | "ArrayPool, compaction only fixes the symptom and blocks the process." Right choice, and the rejected option correctly priced. Did not price the **chosen** option: complexity, plus use-after-return or never-returned buffers, a hazard worse than the bug being fixed. | miss |
| 3 | Gen 2 count jumps from a few per hour to several per minute after adding 100–300 KB per-request buffers; gen 0 and gen 1 unchanged. Why gen 2 specifically? | Correct conclusion and correct routing (over the threshold → straight to LOH → more gen 2 GCs), but no mechanism: never named the **separate LOH budget** whose exhaustion is what triggers a gen 2, and did not address why gen 0/gen 1 are unchanged (the buffers never pass through gen 0). A restatement rather than a walk-through. | miss |

Drill results do not change a level.

## Model answers — 2026-09-13

### Q6 (2026-09-12) — target L2, awarded L1

*You allocate `new byte[100_000]`. Which heap does it land on, what decides
that, and how does its collection differ from a small array's?*

It lands on the **large object heap**, and **size alone** decides it: any object
of 85,000 bytes or more is allocated there directly, and 100,000 plus the
header clears that. The decision is made once, at allocation, and never
revisited.

Collection differs in three ways:

1. **Timing.** A large object is collected only as part of a **gen 2**
   collection, and its allocation bills a **separate LOH budget** whose
   exhaustion triggers exactly that. Churning large arrays forces full
   collections.
2. **Swept, not compacted** — the real difference. When the array dies its space
   joins a **free list** and the surviving objects around it do not move. A dead
   *small* array is simply space the next compaction closes up.
3. **Allocation.** Because nothing moves, allocating there is a **free-list
   search** for a block that fits, not a pointer bump. Slower, and it can fail
   while plenty of free space exists in total — **fragmentation**, which is why
   a process can throw `OutOfMemoryException` with gigabytes free.

Graded answer lacked: the 85,000-byte threshold, that the LOH is swept rather
than compacted, and any account of what that costs.

## Resources

## Related

[[gc-generations]] · [[gc-triggers-and-budgets]] · [[boxing]]
