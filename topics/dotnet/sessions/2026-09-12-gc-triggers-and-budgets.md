---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-12
mode: interview
excursion: false
questions: 8
avg_target: 2.8
avg_awarded: 1.6
concepts: [gc-triggers-and-budgets, large-object-heap, finalization-and-freachable-queue, stack-vs-heap-layout]
self_flagged: []
disputes: 0
---

# 2026-09-12 — GC triggers and budgets

**Proposed by rule:** 1 — overdue queue item (next 2026-09-09, overdue 3 days)
**Override:** none

Planned mix: 7 depth on [[gc-triggers-and-budgets]], 2 adjacent
([[gc-generations]], large-object-heap), 1 cold recall from the queue
([[stack-vs-heap-layout]]). Taught 2026-09-08, four days before this session,
so a level may rise.

## Q1 — [[gc-triggers-and-budgets]] — target L2 — depth

**Question:** A plain console app, nothing else running:
`for (int i = 0; i < 1000; i++) { var buf = new byte[10_000]; }`.
At what point, if ever, does a garbage collection start, and what exactly
causes it to start at that point?

**Answer:** "Garbage collection can start whenever the gen 0 allocation budget
is exceeded. After that the main thread in which the program run will start the
GC." Named the budget as the trigger unprompted. Terse; did not initially say
which allocation is the one that starts it.

**Probes:**
1. *Does a collection definitely happen in this loop, and what number decides?*
   → "The GC starts on a `new` allocation which exceeds the limit. In our case
   we can't tell for sure whether it will start or not, because the budget is
   dynamic and it depends on the initial memory and can change after a few
   iterations." Named the exact trigger point and the dynamic budget.

**Awarded:** L2 — met target. The budget is named as the trigger, the crossing
`new` as the moment, and the budget correctly described as dynamic rather than
a constant. The 2026-09-08 miss (trigger model was "end of request") is closed.
Capped at target L2.

## Q2 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** An ASP.NET service holds each request's state in an object that
stays alive across a slow `await` on a database call. Under load you see the
gen 1 and gen 2 collection counts climbing, not just gen 0. What decides that a
given collection is a gen 1 or a gen 2 rather than a gen 0, and when the GC
picks gen 2, what does it actually collect?

**Answer:** Promotion mechanics correct and unprompted: a surviving object moves
gen 0 → gen 1 → gen 2, "it checks if the object still has alive/active
references". Explained the scenario plausibly: many concurrent requests, state
alive across the DB call, so survivors accumulate. On the second half: "when GC
picks gen two it collects objects which are marked as gen two, and it also
collects large object heap objects" — LOH correct, but the scope of a gen 2
collection was given as gen 2 only. Did not name per-generation budgets
unaided.

**Probes:**
1. *What is the runtime measuring when it decides, before marking, that this
   collection is a gen 1 rather than a gen 0?* → "Each generation has its own
   budget for garbage collection and all of these budgets are dynamic. So we
   try to run garbage collection on a specific generation which exceeds the
   budget." Correct.
2. *A gen 2 collection starts; an object allocated 1 ms ago in gen 0 has just
   become unreachable — reclaimed now or next gen 0 GC?* → "It will reclaim it,
   because when the collection runs on older generations it also collects all
   child generations. Gen two collects gen one and gen zero, gen one collects
   gen zero." Correct.

**Awarded:** L2 — the deciding mechanism (per-generation budgets) and the
condemned-younger-generations semantics were both correct but only under
probing; the unaided answer scoped a gen 2 collection to gen 2 objects plus the
LOH, which is incomplete. L3 requires unaided use. Between L2 and L3 → L2.

## Q3 — [[gc-triggers-and-budgets]] — target L4 — depth

**Question:** Two services allocate the same total bytes per second. Service A
discards each request's state immediately. Service B holds its request state
alive across a slow `await`, as in Q2, then discards it. B's total allocation
is no higher than A's. Why is B's pattern specifically more expensive for the
GC, and what is happening underneath to make it so?

**Answer:** "The objects get promoted to gen one and gen two. And gen one and
gen two have higher budgets, so garbage collector allows these collections to
grow more than gen 0. So service A runs a lot of gen zero collections, and
service B runs all types of garbage collections." Promotion and the differing
collection profile are correct. Nothing on why an individual collection costs
more.

**Probes:**
1. *Is A's single gen 0 collection the same cost as B's? Why or why not?* → "In
   service B a lot of objects survive gen zero collection because they are
   waiting for the DB call, so they still have an active reference, and a lot
   more objects get promoted to gen 1 comparing to service A. After a few
   iterations the budgets for gen zero will differ in both services and they
   will run with different intervals." Survivor count and interval, still not
   cost.
2. *Break down the work the collector does in one gen 0 collection; which parts
   get more expensive and why?* → "It checks for object references. If object
   has no active references it can be collected. I can't tell which parts get
   more expensive because you haven't explained it properly for me."

**Awarded:** L2 — applies the budget and promotion model correctly to predict
the two collection profiles, which is use with reference. The question was why
it costs more, and the cost model is absent: work is still described as
checking references, with nothing about marking the live set or copying
survivors. Missed trade-off → cap L2. This is the same cost-model gap recorded
against [[gc-generations]] on 2026-09-08, now showing up here.

## Q4 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** A service runs happily on a 32-core VM with 64 GB of RAM under
Server GC. It is moved unchanged into a container limited to 512 MB. What
changes about how the GC behaves, and what would you change in configuration?

**Answer:** "We should change the configuration from server GC to workstation
GC." The correct remedy, named unprompted and without hesitation. Nothing on
what changes in GC behaviour.

**Probes:**
1. *Why does Server GC specifically hurt in a 512 MB container — what is it
   doing that costs the memory?* → "You haven't explained it extensively enough
   for me to explain." Treated as a pass.

**Awarded:** L1 — named the right knob but could not unpack either term. Per
the anti-inflation rule, a term used but not unpackable is L1 for that term,
however good the surrounding answer. Per-core heaps, per-heap budgets, and the
75% heap hard limit all absent. This was also the drill miss on 2026-09-08.

## Q5 — [[gc-triggers-and-budgets]] — target L4 — depth

**Question:** A service has been up six hours. RSS sits at 1.4 GB and is flat.
Gen 0 collections number in the thousands, gen 1 in the hundreds, gen 2 exactly
three. Ops says there is a memory leak. What do you tell them, and what would
those same three numbers look like if there genuinely were a leak?

**Answer:** "It doesn't look like a leak, because the memory stays flat and we
don't have much gen 2 collections, which indicates that probably the budgets
for gen 2 just increased because we have enough resources. And we have a good
proportion between counts in different generations — thousands gen 0 and
hundreds gen 1 is a good indicator." Correct conclusion with the right
mechanism, unprompted. Did not address the second half.

**Probes:**
1. *If it genuinely were a leak, what would those three numbers look like?* →
   "Gen 1 and 2 significantly higher and closer to gen 0 counts." Directionally
   right.
2. *Gen 2 counts high and climbing — what one measurement separates a leak from
   heavy promotion?* → "Used memory increasing instead of staying flat."
   Correct in substance: growth across full collections is the leak signal.

**Awarded:** L3 — fluent unaided diagnosis naming budget growth under headroom,
the rarity of gen 2, and the generation-count proportions, then the correct
discriminating measurement under probe. Not L4: the second half needed a probe,
and the signal was given as "used memory" rather than the live set after a full
collection, with nothing on why RSS alone misleads. The 2026-09-08 drill hit on
this has held four days.

## Q6 — large-object-heap — target L2 — adjacent

**Question:** You allocate `new byte[100_000]`. Which heap does it land on, what
decides that, and how does its collection differ from a small array's?

**Answer:** "Probably large object heap, but I don't remember the exact size
after which the objects are allocated there. And all LOH objects are moved to
gen 2 straight away." Correct heap and correct that the LOH is collected with
gen 2. Threshold not recalled (85,000 bytes).

**Probes:**
1. *When a large array dies, how does the collector deal with the space it
   leaves, compared with a dead small object?* → "Dead small object will
   probably be gen 0 object and such a large array will be gen 2 straight
   away." Restated placement, not the question.
2. *Plenty of free space inside the LOH, yet a new large allocation still grows
   the heap — what is going on?* → "Maybe the space which was released isn't
   reused for some reason and we allocate more new space on the heap." Restated
   the symptom; did not reach non-compaction or fragmentation.

**Awarded:** L1 — first contact. Can define it and correctly pairs it with gen
2, cannot use it: no threshold, and across two probes nothing on the LOH being
swept rather than compacted, which is the whole difference the question asked
about. Between L1 and L2 → L1.

## Q7 — finalization-and-freachable-queue — target L2 — adjacent

**Question:** You open a `FileStream`, never call `Dispose`, and never use a
`using`. The local variable goes out of scope. When does the OS file handle get
released, and what decides that?

**Answer:** "When the next GC happens it will trigger the Dispose of this
resource, until that time it can be hanging." The practical consequence is
right: the handle lingers, release is tied to a future GC, not to scope exit.
Mechanism conflated with `Dispose`.

**Probes:**
1. *Which thread performs the cleanup, and is it finished when the GC
   completes?* → "The GC is triggered by the thread in which the budget was
   exceeded" (correct, carried over from Q1) "but I suggest that the cleanup is
   performed by the thread which was holding that resource open." Incorrect.
2. *The opening thread finished seconds ago and has other work; what mechanism
   gets the cleanup done?* → "Thread pool." Incorrect.

**Awarded:** L1 — knows the symptom and that release waits for a GC, which is
the failure mode that matters in production. The mechanism is absent across two
probes: no finalizer, no finalizer queue, no dedicated finalizer thread, and no
sense that the object survives the first GC in order to be finalized. Can
define, cannot use → L1.

## Q8 — [[stack-vs-heap-layout]] — target L2 — cold recall

**Question:** A class `Order` has a field of type `DateTime`, which is a
struct. You write `new Order()`. Where does that `DateTime` live? And for a
`List<int>` holding a thousand items, where do the thousand ints live?

**Answer:** Both asked placements correct, and the reference/object distinction
made explicitly and unprompted: "That DateTime will live in the heap because it
is a field of a class Order which lives in heap. In this case only reference to
this Order object will be in the stack." Same for the list. Then volunteered,
unasked: "whenever we want to get or add value to this list there will be
boxing/unboxing which is copying value from stack to heap or the other way
around. And during that process we also upcast to an object or downcast" —
incorrect, `List<int>` is generic and stores `int` inline in an `int[]`.

**Probes:**
1. *What is the backing storage inside `List<int>`, and does adding an int
   allocate on the heap?* → Detailed and correct on array layout: contiguous
   block, sized by element size and length, values stored one after another,
   list resizes (initial capacity 4, growth ~2×, exact logic not recalled),
   contrasted with a linked list. Did not answer the boxing half.
2. *Given that layout, where would the boxed copy live and how many heap
   objects exist for one int?* → "The boxed copy of a value from the list lives
   inside of the stack. And the list itself lives inside of the heap. And I
   don't understand the question."

**Awarded:** L1 — held, not raised. The two asked placements are right and the
reference-versus-object separation that was the 2026-09-08 miss is now made
correctly and unprompted, which is real movement. Against that, the answer
asserts a boxed copy lives on the stack and holds to it under two probes.
Where a boxed value lives is the graded concept itself, not a tangent, so this
cannot be graded above L1. Between L1 and L2 → L1.

## Session stopped early

Q6, Q7 and Q8 all landed at L1 or lower — three consecutive. Per `CLAUDE.md`
the session ends here at eight questions and switches to teaching.

## Self-assessment

Declined. Asked "which answers did you think were weak?" and the user chose to
skip their own evaluation, so `self_flagged` is empty by refusal, not because
nothing was flagged. The calibration checkpoint has no data from this session;
four of the five sessions it needs must come from elsewhere.

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-triggers-and-budgets]] | L2 | L2 | — | — |
| 2 | [[gc-triggers-and-budgets]] | L3 | L2 | — | — |
| 3 | [[gc-triggers-and-budgets]] | L4 | L2 | — | — |
| 4 | [[gc-triggers-and-budgets]] | L3 | L1 | — | — |
| 5 | [[gc-triggers-and-budgets]] | L4 | L3 | — | — |
| 6 | [[large-object-heap]] | L2 | L1 | — | — |
| 7 | [[finalization-and-freachable-queue]] | L2 | L1 | — | — |
| 8 | [[stack-vs-heap-layout]] | L2 | L1 | — | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-triggers-and-budgets]] | L0 | L1 | minimum awarded across Q1–Q5 is Q4's L1; taught 2026-09-08, four days clear, so a rise is permitted |
| [[large-object-heap]] | L0 | L1 | first contact, could define it, could not use it |
| [[finalization-and-freachable-queue]] | L0 | L1 | first contact, could define it, could not use it |
| [[stack-vs-heap-layout]] | L1 | L1 | held; evidence refreshed |

The minimum rule costs this session a lot. Q1 at L2, Q2 at L2, Q3 at L2 and
Q5 at L3 all sit above the recorded level, but Q4 at L1 sets the concept grade,
so `gc-triggers-and-budgets` lands at L1 rather than L2. The trigger model
taught on 2026-09-08 is genuinely in place; the surrounding mechanism is not.

## Misses

- [[gc-triggers-and-budgets]] — cannot say what work in a collection scales
  with survivors; collection cost described as "checking references"
- [[gc-triggers-and-budgets]] — cannot unpack Server versus Workstation GC: no
  per-core heaps, no per-heap budgets, no 75% heap hard limit
- [[large-object-heap]] — does not know the 85,000-byte threshold, and cannot
  say the LOH is swept rather than compacted or what that costs
- [[finalization-and-freachable-queue]] — attributes finalizer work to the
  originating thread, then to the thread pool; no finalizer queue, no finalizer
  thread; conflates the finalizer with `Dispose`
- [[boxing]] — believes `List<int>` boxes on add and read, and that a boxed
  copy lives on the stack

Partial progress not enough to clear a gap: the 2026-09-08 miss on
[[stack-vs-heap-layout]] was separating the reference variable from the object,
and Q8 did that correctly and unprompted. The gap stays `open` because
verification needs L2 or above and Q8 graded L1.

## Queue

| Concept | Next |
|---|---|
| [[gc-triggers-and-budgets]] | 2026-09-13 |
| [[large-object-heap]] | 2026-09-13 |
| [[finalization-and-freachable-queue]] | 2026-09-13 |
| [[stack-vs-heap-layout]] | 2026-09-13 |
