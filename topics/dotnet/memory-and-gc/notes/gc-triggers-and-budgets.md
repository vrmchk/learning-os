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

## Model answers — 2026-09-12

For each interview question on this concept graded below target. The
2026-09-08 Q3 is omitted: its content is today's Q1, which met target.

### Q2 (2026-09-12) — target L3, awarded L2

*What decides that a collection is a gen 1 or gen 2 rather than a gen 0, and
when the GC picks gen 2, what does it actually collect?*

Every generation has its own allocation budget, and all of them are dynamic.
Gen 0's budget is spent by `new`. Gen 1's is spent by **promotions** out of
gen 0, gen 2's by promotions out of gen 1, and the LOH has its own which bills
to gen 2. When a collection comes due the GC condemns the **highest generation
whose budget is spent, plus everything younger**. So a gen 2 collection is a
full collection: gen 2, gen 1, gen 0 and the LOH, marked together. In this
service the request state is still reachable across the `await`, so it survives
gen 0 and promotes, which spends gen 1's budget, so gen 1 collections start;
their survivors promote again and eventually spend gen 2's. That is why all
three counts climb.

Graded answer lacked: per-generation budgets (only produced under probing), and
the condemned-younger-generations rule — a gen 2 GC was scoped to gen 2 plus
the LOH.

### Q3 (2026-09-12) — target L4, awarded L2

*Two services allocate the same bytes; B holds request state across a slow
`await`. Why is B more expensive?*

Because a collection's cost is its **survivors**, not its garbage. Mark walks
the graph from the roots and visits only reachable objects — dead objects are
never touched, never counted, never individually freed. Then survivors are
copied to compact the heap and every reference to them is rewritten. So the
work is roughly survivors marked plus survivor bytes copied. A's gen 0
collections have almost no survivors, so each is nearly free. B's have
thousands, so B pays more *per collection* to mark and copy them. On top of
that B's survivors promote, spending gen 1's budget and eventually gen 2's, and
a gen 2 collection must mark the whole live set of the process. B pays three
times: dearer gen 0 collections, then gen 1 collections, then gen 2. The irony
is that the objects die anyway — just after being promoted to where dying is
expensive. That is the mid-life crisis.

Graded answer lacked: the cost model entirely. Collection work was described as
"checking references", with nothing on marking the live set or copying
survivors, so the question of why it costs more went unanswered.

### Q4 (2026-09-12) — target L3, awarded L1

*Server GC on a 32-core, 64 GB VM, moved into a 512 MB container. What changes,
and what would you change?*

Server GC gives the process **one heap per core**, each with its own gen 0/1/2
budgets, and one dedicated GC thread per heap. On 32 cores that is 32 heaps and
32 sets of budgets, so the process holds roughly 32× as much memory before it
collects anything. That is the bargain: parallel collection on dedicated
threads for throughput, paid for in footprint. In a 512 MB container the
runtime reads the cgroup limit and sets the heap hard limit to **75% of it**,
about 384 MB. Server GC then tries to fit 32 heaps' worth of budget inside
384 MB, so either every budget shrinks until collections run almost
continuously, or the process hits the hard limit and OOMs well below the host's
free memory. The 32 GC threads also contend for a CPU quota that may be a
fraction of one core. I would switch to Workstation GC: one heap, one small
budget, collection on the allocating thread. If the mode is owned elsewhere, I
would cap `GCHeapCount` to one or two and consider `GCConserveMemory`, and
verify the container limits are actually visible to the runtime.

Graded answer lacked: any mechanism. The right knob was named immediately, but
per-core heaps, per-heap budgets, the 75% hard limit and the
throughput-for-footprint trade-off were all absent.

### Q5 (2026-09-12) — target L4, awarded L3

*RSS 1.4 GB and flat; gen 0 in the thousands, gen 1 in the hundreds, gen 2
exactly three. Leak? And what would a leak look like?*

Not a leak. Three gen 2 collections against thousands of gen 0 means almost
nothing survives to gen 2, so the live set is small. RSS sits at 1.4 GB because
nothing has asked the process to give it back: with headroom the tuner grows
the budgets and gen 2 almost never runs. **Flat** is the operative word — the
process is holding memory, not accumulating it. A real leak is *reachable*
memory growing, so I would expect the gen 2 count to climb as its budget kept
being spent, and, decisively, the **heap size measured immediately after each
gen 2 collection to trend upward**, because a full collection cannot reclaim
what is still rooted. RSS alone cannot separate the two; live heap size across
consecutive full collections can. I would read it from GC counters or two
dumps, and if it is growing, diff the largest root sets between them.

Graded answer lacked: the second half needed a probe; the discriminator was
given as "used memory" rather than live heap size after a full collection; and
nothing on why RSS on its own misleads.

## Resources

## Related

[[gc-generations]] · [[stack-vs-heap-layout]]
