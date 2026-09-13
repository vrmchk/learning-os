---
concept: gc-generations
topic: dotnet
cluster: memory-and-gc
created: 2026-09-08
taught: 2026-09-13
---

# GC generations

## Mechanism

### A generation is not a place — it is a range of addresses

Gen 0 and gen 1 live together in one region, the **ephemeral segment**. Gen 2
is everything older. Within the segment the generations are separated by
nothing more than **boundary pointers** the collector maintains.

```
ephemeral segment, addresses increasing to the right ->

   [ ......... gen 2 ......... | .. gen 1 .. | ... gen 0 ... | free ]
                               ^             ^               ^
                          gen2/gen1      gen1/gen0      allocation
                           boundary       boundary        pointer
```

Allocation is a pointer bump at the right-hand end, and objects never move
except during a collection, so **address order correlates with age**. The whole
design rests on that property.

**Promotion is a boundary move, not a copy between heaps.** When a gen 0
collection finishes, the survivors have been compacted to the bottom of the
gen 0 range and the collector slides the gen1/gen0 boundary above them. They
are now gen 1. Nothing was transferred anywhere; the line moved.

The model to discard is objects *migrating upward through separate areas*.
There is one heap; generations are bookkeeping over address ranges in it.
(.NET 7+ replaces segments with many small **regions**, each belonging to a
generation. The layout changes, the model does not — see
`gc-regions-and-configuration`.)

### Does gen 0 shrink, then? — no, it empties

The trap is treating gen 0 as a fixed container that the moving boundary eats
into. It is not a container at all: **gen 0 is whatever lies between the
gen1/gen0 boundary and the allocation pointer.** After a collection those two
are in the same place, so gen 0 is empty and has length zero.

```
before a gen 0 collection:          S = survivor
   [ .. gen 2 .. | . gen 1 . | S . . S . . . S . | free ]
                             ^                   ^
                        gen1/gen0           alloc pointer

after it:
   [ .. gen 2 .. | . gen 1 . S S S | free.............. ]
                                   ^
                     gen1/gen0 boundary AND alloc pointer
                     gen 0 is empty and regrows upward from here
```

Survivors are compacted down against gen 1, the boundary moves above them, and
the allocation pointer resets to that same spot. Gen 0 then regrows as you
allocate. **Its size at any instant is just how much has been allocated since
the last collection; its ceiling is the allocation budget**, which is dynamic
and retunes from observed survival. Geometry never caps it.

**What genuinely grows is gen 1**, which absorbs survivors on every gen 0
collection. It is drained by **gen 1 collections**, which have their own small
budget, collect gen 0 and gen 1 together, and promote gen 1's survivors into
gen 2 by the same boundary move. Gen 1 is deliberately kept small: it is a
waiting room asking whether an object that survived one collection is about to
die anyway.

**The ephemeral segment does eventually fill.** When it cannot give more space,
the runtime retires it into gen 2 and begins a fresh ephemeral segment. That is
how gen 2 comes to span several segments in a long-running process.

This is the exact awkwardness .NET 7 removed. With **regions**, a generation is
a *set of small regions* rather than a span between two pointers: a region that
held gen 0 is reassigned to gen 1, emptied regions return to a free pool, and
nothing slides. The model above is unchanged; the bookkeeping is cleaner.

### The generational hypothesis

An empirical claim, not a design preference: object lifetimes in real programs
are **bimodal**. The overwhelming majority die almost immediately (temporaries,
LINQ intermediates, request-scoped state). A small minority live essentially
forever (caches, singletons, configuration, whatever the container holds).
Very little sits in between.

Combine that with the cost model — **collection cost is proportional to
survivors** — and the payoff follows. Collect only the newest range, where
almost everything is already garbage, and survivors are few, so the collection
is cheap. You reclaim most of the garbage for a fraction of the work.

Collecting the whole heap instead means marking the **entire live set**, which
is dominated by long-lived objects virtually certain to still be alive.
Re-proving that the DI container is reachable, thousands of times a second, is
pure waste. **That is why generations exist.**

### The problem generations create

To collect gen 0 alone the collector must find every reference *into* gen 0.
Stacks, statics and handles are easy. But a gen 2 object can hold a reference
to a gen 0 object the moment you add an item to a long-lived cache. Ignore
those and you free a live object; scan all of gen 2 to find them and the entire
saving is gone.

The fix is the **write barrier**: a few instructions the compiler emits on
every reference-typed field store, marking the small range containing that
field as dirty. At collection time the collector scans only the dirty ranges
and treats the old→young references it finds as additional roots. So a gen 0
collection costs **survivors + dirty ranges**, not survivors + all of gen 2.

That mechanism is its own concept in the tree, `card-table-and-write-barrier`,
still at L0 and awaiting its own session. Outline only here.

## Failure modes

- **Treating gen 2 as permanent.** Gen 2 is collected, just rarely, and when it
  is, it is a full collection over the entire live set. A gen 2 that grows
  quietly is a gen 2 collection that gets slower every time it runs.
- **Mutating a large gen 2.** Every store of a young reference into an old
  object dirties a range. A big long-lived cache under constant insertion makes
  gen 0 collections progressively more expensive through card scanning alone,
  even though gen 0 itself is small. Symptom: gen 0 *pause time* rising while
  gen 0 *survival* stays flat.
- **Reading the counts without the survival rate.** A high gen 2 count is not a
  leak; it means something is surviving gen 1. The diagnostic question is
  always *what is getting promoted*, never *how many collections ran*.
- **Forcing collections.** `GC.Collect(0)` exists; calling it discards the
  tuning the collector built from observed survival rates, and a full
  `GC.Collect()` is worse. The budget is self-correcting — see
  [[gc-triggers-and-budgets]].

## Trade-offs

- **The core trade: a tax on writes to avoid a tax on collection.** The write
  barrier runs on every reference store the program ever performs, forever,
  whether or not a collection is near. That permanent small cost on the mutator
  buys collections that examine a fraction of the heap. For typical workloads
  it is overwhelmingly worth it, which is why essentially every modern managed
  runtime does it.
- **Three generations is a tuned choice, not a law.** More would mean more
  boundaries, more card bookkeeping and more promotion steps for diminishing
  returns, given a bimodal lifetime distribution. Two would collapse the useful
  distinction between "survived once, might still die" and "clearly
  long-lived".
- **When the hypothesis fails, generational collection is strictly worse.**
  Load a large object graph at startup and nearly everything survives: you pay
  compaction, promotion and card scanning to reclaim almost nothing, where a
  plain full collection would have been cheaper. This is the mid-life crisis
  scaled up.
- **The constraint you actually control is survival rate.** Generations reward
  objects that die young and objects that live forever, and punish everything
  in between.

## Drill — 2026-09-13

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | Three gen 0 objects survive a collection and become gen 1 — what physically happened, and what did the collector do? | "The three objects were compacted to the end of gen 0 and the gen 1 boundary moved above them." Exactly right, and exactly the model that replaces "objects migrate between heaps". | hit |
| 2 | A 2 GB object graph loaded at startup and held for the process lifetime — is the generational design helping or hurting, and what are you paying for? | "Hurting — everything survives so we pay compaction and promotion and scanning and get no benefits back." Complete: names the hypothesis failing and all three costs, unprompted. | hit |
| 3 | Large gen 2 cache under constant insertion; gen 0 pause time climbs for weeks while gen 0 survival and collection count stay flat. What is getting more expensive, and why? | Named the mechanism unprompted: an old→young reference from the cache dirties a range, and "it costs us more scanning on each gen 0". Wrinkle: the card marks **the field written in gen 2**, not the new gen 0 object; and the climb is because the gen 2 area being scanned keeps growing as the cache grows. | hit |

Drill results do not change a level.

## Model answers — 2026-09-13

### Q1 (2026-09-08) — target L3, awarded L1

*Explain what a generation is, what determines which generation an object is
in, and why the runtime uses generations instead of collecting the whole heap
every time.*

A generation is a **range of addresses**, not a separate heap. Gen 0 and gen 1
sit together in the ephemeral segment separated by boundary pointers, with
gen 2 below. Allocation is a pointer bump at the top of gen 0, and objects move
only during a collection, so address order tracks age.

What determines an object's generation is how many collections it has
survived — but the mechanism is a **boundary move**, not a transfer. When a
gen 0 collection ends, the survivors have been compacted down and the collector
slides the boundary above them. They are gen 1 because the line moved, not
because they went anywhere.

The runtime uses generations because **collection cost is proportional to
survivors, never to garbage**: the collector marks what is reachable and never
touches what is dead. Object lifetimes are **bimodal** — most objects die
almost immediately, a few live for the whole process, little is in between. So
condemning only the newest range means nearly everything in it is already
garbage, survivors are few, and most of the garbage is reclaimed for a fraction
of the work. Collecting the whole heap would mean marking the **entire live
set**, dominated by long-lived objects almost certain to still be alive. The
cost of the design is that an old object can reference a young one, which is
why the write barrier and card table exist.

Graded answer lacked: collection cost attributed to reference count rather than
live-set size; no generational hypothesis; and a trigger model of scope exit
and low memory rather than the allocation budget.

## Resources

## Related

[[gc-triggers-and-budgets]] · [[stack-vs-heap-layout]] · [[large-object-heap]]
