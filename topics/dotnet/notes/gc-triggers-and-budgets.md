---
concept: gc-triggers-and-budgets
topic: dotnet
cluster: memory-and-gc
created: 2026-09-08
taught: 2026-09-08
---

# GC triggers and budgets

## Mechanism

- Allocation is a pointer bump inside a per-thread **allocation context**
  (a small window of gen 0). `new` makes no garbage decision. When the
  window is exhausted the thread asks the GC for another.
- Gen 0 has an **allocation budget**: bytes that may be allocated before a
  collection is due. The allocation that crosses the budget **triggers the
  GC**. Collections start on a `new`, never on scope exit, method return,
  or end of request.
- Sequence: budget crossed → all managed threads suspended at safe points →
  mark from roots (JIT-reported live stack slots, statics, GC handles) →
  unreached gen 0 objects are garbage → survivors compacted and promoted to
  gen 1 → resume. JIT liveness can mark a local dead *before* its scope
  ends; an object can be collected while its method is still running.
- The budget is **dynamic**: initial size from cache size (workstation ≈ L3,
  low MB; server GC much larger per heap), retuned after each GC by
  **survival rate** — high survival → budget grows, low survival → shrinks
  or holds.
- **Every generation has its own budget.** Promotions into gen 1 count
  against gen 1's budget; exceeding it makes the next GC a gen 1 GC (which
  collects gen 0 too). Likewise gen 2. LOH allocations count against the
  LOH budget → gen 2. The GC condemns the *highest* generation whose budget
  is spent, plus everything younger.
- Other triggers: `GC.Collect()`; OS **high memory load** (~90% of physical
  or of the container limit — a system signal, not "my process feels
  tight"); approaching `GCHeapHardLimit`. Process exit does not collect.

## Failure modes

- **"Memory grows, must be a leak."** With headroom, budgets grow and gen 2
  rarely runs; RSS stays high because nothing asked for it back. Diagnose
  with gen 2 count and `% Time in GC`, not RSS. A leak is *reachable* memory
  growing across gen 2 collections.
- **Relying on scope exit for cleanup.** A `FileStream` without `using`
  holds its handle until a future GC runs the finalizer — seconds, minutes,
  or the next deploy. Symptoms: "file in use", handle exhaustion, pool
  starvation. `IDisposable` is how *you* choose when unmanaged resources
  return.
- **High allocation rate** → budget crossed more often → more gen 0 GCs →
  `% Time in GC` up, p99 spikes. Fix by allocating less; `GC.Collect()`
  forces a full blocking GC and resets tuning — worse.
- **Mid-life crisis.** Objects that survive just long enough to be promoted
  then die (state held across a slow `await`, short-TTL caches) die in
  gen 1/2 where collection is expensive. Symptom: gen 2 count climbing on a
  "per-request only" service.
- **Container limits.** Heap hard limit defaults to 75% of the container
  limit; budgets derive from it. Too-low limits → aggressive GC or OOM well
  below the host's free memory.

## Trade-offs

- Bigger gen 0 budget → fewer GCs, more memory, worse nursery locality.
  Smaller → more GCs, lower footprint. Gen 0 pause cost ∝ survivors, not
  budget size, so a big budget buys fewer pauses, not longer ones, while
  survival stays low.
- Server vs workstation GC is mostly a budget decision: per-core heaps with
  much larger budgets → far fewer collections, much more memory. Server for
  throughput on a dedicated box; workstation / `GCConserveMemory` for shared
  hosts and tight containers.
- Knobs (`GCgen0size`, `GCConserveMemory`, `GCHeapHardLimit`) exist; dynamic
  tuning usually wins. Reach for a knob only with a measured symptom.
- GC trades *timing* for *simplicity*: never free memory, never know when it
  returns. Anything whose lifetime matters outside the process is disposed
  explicitly, because GC timing is a budget, not a scope.

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
