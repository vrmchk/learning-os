---
concept: gc-triggers-and-budgets
topic: dotnet
cluster: memory-and-gc
created: 2026-09-08
taught: 2026-09-12
---

# GC triggers and budgets

## Mechanism

### What starts a collection

- Allocation is a pointer bump inside a per-thread **allocation context** (a
  small window of gen 0). `new` makes no garbage decision. When the window is
  exhausted the thread asks the GC for another.
- Gen 0 has an **allocation budget**: bytes that may be allocated before a
  collection is due. The allocation that crosses the budget **triggers the
  GC**. Collections start on a `new`, never on scope exit, method return, or
  end of request.
- **Every generation has its own budget.** Promotions into gen 1 count against
  gen 1's budget; exceeding it makes the next GC a gen 1 GC. Likewise gen 2.
  LOH allocations count against the LOH budget → gen 2. The GC condemns the
  **highest** generation whose budget is spent, **plus everything younger** —
  so a gen 2 GC collects gen 1 and gen 0 too.
- The budget is **dynamic**: initial size from cache size, retuned after each
  GC by **survival rate** — high survival → budget grows, low survival →
  shrinks or holds.
- Other triggers: `GC.Collect()`; OS **high memory load** (~90% of physical or
  of the container limit); approaching `GCHeapHardLimit`. Process exit does not
  collect.

### What a collection costs — the collector never looks at garbage

Two phases. **Mark** walks the object graph from the roots (JIT-reported live
stack slots, statics, GC handles, card-table entries for old→young refs) and
marks everything reachable. **Relocate** slides survivors down to close holes
and rewrites every reference to them.

Dead objects are never visited, never counted, never freed individually. They
are the space *between* survivors, reclaimed by resetting the allocation
pointer.

```
gen 0 before:   [A][b][c][D][e][f][g][h][i][J]    lowercase = unreachable
mark visits:     A           D              J     <- 3 objects of work
gen 0 after:    [A][D][J]........................ <- 7 dead cost nothing
                          ^ allocation pointer
```

**Cost of one collection ≈ survivors marked + survivor bytes copied.** Not the
heap size. Not how many references point at an object. Not how many objects
died.

- Gen 0 at 1% survival is nearly free, and stays nearly free however large the
  budget is. A bigger budget makes pauses **rarer**, not longer.
- A gen 2 collection is expensive because the condemned set is the whole heap,
  so mark work scales with the **entire live set** of the process. Gen 2 count
  is the number to watch.
- The **generational hypothesis** — most objects die young — is a bet about
  survival rate. When it holds, condemning only gen 0 keeps the live set tiny.
  That is the whole reason generational collection is cheaper.

### Server vs Workstation — a decision about how many heaps exist

- **Workstation:** one heap for the process, one set of generation budgets.
  Collections run on the thread whose allocation crossed the budget, apart from
  concurrent gen 2 work on a background thread.
- **Server:** one heap **per core** (or per `GCHeapCount`), each with its own
  gen 0/1/2 budgets, plus one dedicated GC thread per heap. 32 cores → 32
  heaps → 32 gen 0 budgets. Collections run in parallel across those threads,
  which is the throughput win; total memory held before collecting is ~32×
  larger. The memory cost is the mechanism, not a side effect.

## Failure modes

- **Mid-life crisis.** Objects survive just long enough to be promoted, then
  die in gen 1/gen 2 where collection is expensive — state held across a slow
  `await`, short-TTL caches. The service pays three times: many survivors to
  mark and copy in each gen 0 GC, promotions filling gen 1 so gen 1 GCs start,
  and gen 2 growing. Symptom: climbing gen 2 count on a "per-request only"
  service.
- **Reaching for the budget knob.** On seeing heavy GC time the instinct is to
  collect more often or shrink the budget. Cost per collection is *survivors*,
  so collecting the same survivors more often multiplies the work. The lever is
  survival rate, not frequency. `GC.Collect()` forces a full blocking GC and
  resets tuning — worse.
- **Server GC in a small container.** Heap hard limit defaults to **75% of the
  container limit**, so 512 MB → 384 MB. Server GC tries to fit one budget per
  core inside that: either every budget shrinks until collections run
  constantly, or the process OOMs well below the host's free memory. The
  per-heap GC threads also contend for a CPU allowance that may be a fraction
  of a core.
- **"Memory grows, must be a leak."** RSS tells you what the process has not
  given back. A leak is **reachable** memory growing across gen 2 collections.
  Survival rate, gen 2 count and `% Time in GC` separate the two; RSS alone
  does not.
- **Relying on scope exit for cleanup.** A `FileStream` without `using` holds
  its handle until a future GC runs the finalizer. `IDisposable` is how *you*
  choose when unmanaged resources return.

## Trade-offs

- **Budget size** trades memory for collection frequency and nothing else,
  while survival stays low: bigger → fewer pauses of the same length, larger
  footprint. This is why the dynamic tuner usually beats a hand-set value.
  Reach for `GCgen0size` only with a measured symptom.
- **Survival rate is the part you control by design.** Objects should either die
  before the first collection sees them, or live for the life of the process.
  The middle is the expensive case. Shortening the window an object stays
  reachable is worth more than any GC setting.
- **Server vs Workstation** is throughput against footprint. Server for a
  dedicated box with many cores and memory to spare; Workstation for
  containers, shared hosts, anything under ~1 GB. Setting `GCHeapCount`
  explicitly is the middle path: parallel collection without one heap per core.
  `GCConserveMemory` for tight hosts.
- **The GC will not tell you when memory comes back.** Collection timing is a
  budget, not a scope. Anything whose lifetime matters outside the process is
  disposed explicitly.

## Drill — 2026-09-12

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | 10,000 objects in gen 0, 2 survive in A and 9,000 in B — which collection takes longer and what is the extra work? | "B takes longer because the mark has to visit more objects, copy and move them to the top inside of the memory, and with more objects survived you have to visit and move more of them." Cost model correct: mark work plus copy work, both scaling with survivors. | hit |
| 2 | 8% time in GC — double the gen 0 budget, or stop holding request state across the `await`? | Picked the code change: fewer survivors lowers gen 0 cost *and* cuts promotion so higher-generation GCs run less often. Added that dynamic budget tuning almost always wins and "the survival rate is the bottleneck here, not the budget or frequency of a GC". | hit |
| 3 | 512 MB container, Server GC, mode not changeable — name another setting, what it does to the heaps, and what the runtime believes its heap limit is | Named the heap-count setting, correctly. Did not say what limiting it does (fewer heaps → fewer independent budgets → less total headroom before a collection), and did not give the 75%-of-container default, i.e. 384 MB. | miss |

Drill results do not change a level.

## Drill — 2026-09-08

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | 50 calls × 100 KB discarded — has a GC necessarily happened, what decides? | "Most likely the allocation budget is higher than 5 MB and collection did not happen." Named the budget as the decider. | hit |
| 2 | Busy API from a big VM with Server GC into a 512 MB container — what changes, what do you do? | Budget shrinks, GCs more frequent; reduce allocations, split the service. Did not name switching to Workstation GC / `GCHeapCount` / `GCConserveMemory`, or the 75% hard limit. | miss |
| 3 | RSS 1.4 GB flat, gen 0 thousands, gen 1 hundreds, gen 2 = 3 — leak? Mechanism? | "GC decided to increase the budget… gen 2 RSS is not growing but kept stable… GC optimization, not memory leak." Right conclusion and core mechanism; driver is survival rate, and low gen 2 count ⇒ almost no promotion. | hit |

Drill results do not change a level.

## Resources

## Related

[[gc-generations]] · [[stack-vs-heap-layout]]
