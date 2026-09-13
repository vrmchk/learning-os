---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-13
mode: interview
excursion: false
questions: 10
avg_target: 3.4
avg_awarded: 2.4
concepts: [gc-triggers-and-budgets, boxing, gc-generations]
self_flagged: []
disputes: 0
---

# 2026-09-13 — GC triggers and budgets

**Proposed by rule:** 1 — overdue queue item (next 2026-09-13, due today)
**Override:** none

Planned mix: 7 depth on [[gc-triggers-and-budgets]], 2 cold recall from the
queue ([[boxing]], due today, taught 2026-09-12 so a rise is allowed), 1
prerequisite ([[gc-generations]]).

Coverage notes, per §2. The `gc-triggers-and-budgets` note covers budgets and
escalation, the mark-and-copy cost model, server versus workstation heaps, the
75% container hard limit, mid-life crisis and the leak-versus-headroom
diagnosis — all askable at depth. Its one open drill miss (what capping
`GCHeapCount` does to per-heap budgets, and the 75% default) is `teach`'s job
and may only appear as `discovery`. Same for `boxing`'s two open drill misses
(the struct-keyed dictionary box count, and what the generic constraint costs).

[[gc-generations]] and [[large-object-heap]] were taught today, so per §4.2 no
level of theirs can rise in this session; a grade is still recorded.

## Q1 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** Same code, same traffic, nothing deployed. But this week your
gen 0 collections are running roughly twice as often as last week. What could
cause that, and what would you look at to confirm it?

*Clarification asked by the user before answering, and given:* gen 0 has
roughly doubled; gen 1 and gen 2 are essentially unchanged.

**Answer:** "The first reason that comes into my mind is that it's possible
that GC just decided to shrink the gen 0 budget, because the GC determines the
optimal limits for itself. Maybe somehow the allocation or survival rate
increased, but I'm not sure how that can be possible if the same code is
deployed. Also I'm not sure what to look at." Budget correctly described as
dynamic and self-tuned; allocation and survival correctly named as the drivers;
but stuck on how either could change without a deploy, and the measurement half
declined outright.

**Probes:**
1. *Besides the code, what does a program's allocation rate depend on?* → "The
   traffic and the requests which our system receives. It can be possible that
   if the traffic is the same maybe the requests themselves have gotten bigger
   or we have some long running db queries or we're waiting some answers from
   external API for a long time." Recovered the key point: same code does not
   mean same workload. (The slow-dependency case is a *survival* driver rather
   than an allocation one.)
2. *Gen 1 is flat while gen 0 doubled — what does that say about survivors, and
   which explanation does it favour?* → "Allocation rate is up, not the
   survivors, because in that case gen 1 would significantly increase."
   Correct, and the right use of the evidence in the question.

**Awarded:** L2 — the budget is correctly understood as dynamic and self-tuned,
and the discrimination from the gen 1 evidence under probe 2 is exactly the
right move. Against that, the unaided answer could not get from "same code" to
"different workload", and the second half of the question — what to measure to
confirm it — was never answered at all. L3 requires unaided use. Between L2 and
L3 → L2.

## Q2 — [[gc-triggers-and-budgets]] — target L4 — depth

**Question:** You switch a service from Workstation GC to Server GC on a
16-core box and change nothing else. What happens to the number of heaps, to
the budgets, and to the process's memory footprint — and why?

**Answer:** Mechanism delivered unaided and essentially complete: "we will have
16 heaps because we have 16 cores, unless it is limited by GC heap count
setting"; "the budget will significantly increase and each core has it's own
budgets per each gen"; "each core gets a separate GC thread and they run in
parallel"; "the memory will increase significantly because instead of 1 heap we
now have 16 of them". Closed with a wrong causal claim: that Workstation GC
means being "limited to small workstation container" and switching lets you use
the whole machine.

**Probes:**
1. *Is that what Workstation GC actually is?* → "No, it's a GC mode, but
   Workstation GC is optimized to be used inside of the small container with a
   limited resources. If you run GC in a workstation mode on a VM with 16 cores
   it won't be optimized for that performance, because you aren't using the
   cores and aren't able to divide the memory and run GCs in parallel."
   Corrected cleanly and explained why Workstation underuses a large host.
2. *What are you buying with the extra memory, and when is it a bad trade?* →
   "We buy throughput with parallel collection, bad trade on shared hosts."
   Correct.

**Awarded:** L3 — the internals came out cold and correct: heap count, per-heap
per-generation budgets, a dedicated GC thread per heap, parallel collection,
and the memory consequence following from the budget multiplication. That is
well above L2. Not L4: the answer asserted a wrong reason before correcting it
under probe, and the purpose of the mode — throughput — arrived only on probe 2,
so it was not the cold whiteboard L4 asks for. Between L3 and L4 → L3.

Worth recording: this is the same material that graded **L1** on 2026-09-12
(Q4) and was taught that day.

## Q3 — [[gc-triggers-and-budgets]] — target L4 — depth

**Question:** A service does only short-lived per-request work. No caches, no
statics of any size. Over a week in production its gen 2 collection count
climbs steadily, while its allocation rate stays flat. What is happening, and
what in the code would you go looking for?

**Answer:** Two hypotheses, neither the intended one. First, "we probably have
some memory leak… unmanaged resource hanging like files open or db connections,
invoked without Dispose or using". Second, large requests over the threshold
going "straight to LOH", collectable only with gen 2. Did not engage the
flat-allocation clue, and the premise (no caches, no statics) gives a classic
leak little to root itself on.

**Probes:**
1. *Allocation rate is flat — does the large-request hypothesis fit?* → "Allocation
   rate is how much we allocate, not how big are objects which we're
   allocating, so it fits my hypothesis." A fair reading of an ambiguous term;
   the ambiguity was the examiner's. Term then pinned to bytes per second, as
   the runtime counter reports it, and re-asked → "In this case it doesn't fit
   and we probably have a leak as I've described in case 1." Correct
   elimination once the term was fixed.
2. *Suppose nothing leaks, nothing is rooted, allocation stays flat — can gen 2
   still climb?* → "It can be possible if our objects are in mid life crisis,
   which means that they live just enough to survive gen 0 collection and get
   promoted to gen 1 or gen 2 if they survive even longer and then die."
   Correct, and correctly described.

**Awarded:** L2 — the LOH reasoning was sound and the elimination on the
byte-rate clue was a good move. But the actual mechanism arrived only after a
probe that had narrowed the conditions to it, the unaided diagnosis went to a
leak the premise argues against, and the second half of the question — what in
the code to look for — was answered only for the leak, never for the mid-life
crisis (state held alive across a slow `await`, short-TTL caches). L4 wants the
mechanism cold. Between L2 and L3 → L2.

## Q4 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** A colleague adds `GC.Collect()` at the end of a nightly batch job
to "clean up before the service goes back to serving traffic". What actually
happens when that line runs, and what does it cost beyond the pause itself?

**Answer:** Both halves answered unaided and correctly. "When the generation is
not specified… it basically tries to collect the memory in whole small and large
heap and runs the collection for all of the generations." And beyond the
blocking pause: "it resets all the GC configs and modifications for the budgets
and how often should the GC run."

**Probes:**
1. *What specifically does the collector lose, and what is the consequence?* →
   "It loses the existing budgets and optimization and it will require some
   time and number of collections to gather the data for optimal budgets based
   on the survival rates." Correct unpack: the budgets were learned from
   observed survival and re-learning costs collections.

**Awarded:** L3 — met target. What the call does and its non-obvious cost both
came out unaided, and "resets tuning" survived being unpacked rather than
sitting there as a memorised phrase. Not capped: the question was about cost
and the cost was given. Not named, and not required at this target: that a full
collection also promotes every survivor into gen 2, the most expensive place to
collect them from later.

## Q5 — [[gc-triggers-and-budgets]] — target L4 — depth

**Question:** Two gen 0 collections in the same process. The first finds 10,000
objects in gen 0, of which 100 survive. The second finds 1,000 objects, of
which 900 survive. Which collection takes longer, and walk me through where the
time actually goes.

**Answer:** "The 2nd one because the collection cost is determined by the
survivors. After we determine which objects are alive we have to compact them
to the end of the generation inside of the heap and move the gen boundary
pointer forward, so after the collection the survivors become gen 1. So the
more objects survive the more objects we have to move inside of the memory."
Right conclusion, right cost principle, and the compaction and boundary move
integrated from yesterday's teaching. Glossed the mark phase as "after we
determine which objects are alive", and omitted reference rewriting.

**Probes:**
1. *Is the moving all the work? What happens before compaction, and does it
   scale too?* → "It's not the only work, we also have to walk object graph to
   find all alive references and after moving we have to rewrite all alive
   references." Both missing pieces produced immediately and precisely.

**Awarded:** L3 — the cost principle and the promotion mechanism came out
unaided, which is a complete reversal of 2026-09-12 Q3 where the cost model was
absent entirely. Not L4: the question asked for the walk-through and the
unaided walk-through skipped the mark phase and the reference rewriting, both
of which appeared the moment they were asked for. Knowledge present, not
volunteered. Between L3 and L4 → L3.

## Q6 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** A collection runs and it turns out to be a gen 2. Name every way
the runtime could have arrived at that decision.

**Answer:** Four of five, unaided and precise: "Gen 2 budget exceeded, LOH
budget exceeded, `GC.Collect()`, high memory load (more than 90% limit)."
The 90% figure correct.

**Probes:**
1. *That is four. Is the list complete?* — deliberately neutral, carrying no
   information → "There is also a setting like GC heap hard limit." The fifth.

**Awarded:** L3 — met target. Four of five produced cold with the right
threshold figure, and the fifth recovered from a probe that gave nothing away.
No cap: the question asked for enumeration, not a trade-off.

## Q7 — [[boxing]] — target L2 — cold recall

**Question:** You write `object o = 42;`. Where does the boxed value
physically live, what does that object consist of, and how big is it on x64?

**Answer:** All three parts, unaided and correct: "The box value lives on the
heap. The object consists of sync block, method table reference and the value
itself. It will be 24 bytes on x64."

**Probes:**
1. *Where does 24 come from, given the value is 4 bytes?* → "The sync block +
   method table reference + the value itself sums up to this number." Asserted
   the sum without doing it; 8 + 8 + 4 is 20.
2. *Eight plus eight plus four is twenty. Where is the other four?* → "The min
   size of the value of an object is 8 bytes. So 8 bytes are allocated anyways
   for the value even when our value size is 4." Reaches the padding, with the
   cause misattributed: the rounding is **8-byte alignment of the whole
   object** (and 24 is the minimum object size on x64), not a minimum width for
   the value field.

**Awarded:** L2 — met target. Every part of the question asked was answered
cold and correctly, and the 2026-09-12 miss (asserting a boxed copy lives on
the stack, held under two probes) is decisively closed. The derivation wobbled:
the arithmetic was claimed rather than performed, and the padding was explained
by the wrong cause.

## Q8 — [[boxing]] — target L3 — cold recall

**Question:** You have a million ints. Compare holding them in `List<int>`
against `List<object>`. What is the memory difference, and what is the
difference when you read all million?

**Answer:** Memory comparison substantially right: "4 bytes times million" against
"24 bytes times million which is 6 times more memory". Mechanism right: each
value in the object list must be boxed, while `List<int>` needs no per-item sync
block or method table and puts 4 bytes into a contiguous block. Read cost: "we
have to unbox each value and on the scale of million performing a type check
for each item is expensive as well." Omits the 8 bytes per pointer in the
`object[]` itself (the real comparison is ~4 MB against ~32 MB, 8×, not 6×).
Says "at
compile time the new type is generated" — third occurrence of this imprecision;
specialisation happens at runtime.

**Probes:**
1. *Where are the million boxes sitting relative to one another, and what does
   that mean for reading them in order?* → "Both lists sit in the heap and in
   our case in LOH. And the boxes inside of `List<object>` sit one after another
   as a continuous block of memory as well." **Both wrong.** The backing arrays
   are on the LOH; the boxes are 24-byte objects on the small object heap,
   scattered wherever gen 0 had room.
2. *How many separate heap objects exist, and how big is each?* → "Million heap
   objects each one with it's own sync block and method table pointer and each
   one with the size of 24 bytes." States the facts that refute the contiguity
   claim without noticing the contradiction, and does not revise.

**Awarded:** L2 — the comparison, the per-item size and the reason generics
avoid boxing all came out unaided, which is real use of the model. But the
dominant read cost was not merely omitted: locality was actively contradicted,
the boxes were placed on the wrong heap, and neither survived being handed the
refuting facts. Lost locality is exactly what the note calls "usually the
biggest cost, and the one people omit". Between L2 and L3 → L2.

## Q9 — [[gc-generations]] — target L3 — prerequisite

**Question:** Every reference assignment your program performs pays a small
cost, always, whether or not a collection is anywhere near. What is that cost
for, and what would break without it?

**Answer:** "There is a write barrier which checks whether the object is
referenced from older GC generations." Names the mechanism unaided, but
describes it as a *check* rather than a *record*: the barrier marks the card
covering the written location as dirty, which is why it is cheap enough to run
on every store. Second half not attempted.

**Probes:**
1. *What would break without it?* — simply re-asking the unanswered half →
   "If the collector couldn't find old-to-young references it would free alive
   objects." Correct.

**Awarded:** L2 — the barrier was named cold and the failure mode is right, but
half the question had to be re-asked, and the barrier's action was described
backwards. Between L2 and L3 → L2. Note: [[gc-generations]] was taught today,
so per §4.2 this grade cannot raise its level; it is recorded as evidence only.

## Q10 — [[gc-triggers-and-budgets]] — target L5 — depth

**Checklist — written before the question was asked, not revised after:**

- [ ] picks a GC mode and justifies it from cores **and** memory together, not
      from one alone
- [ ] names allocation discipline / survival rate as the primary lever, above
      any GC setting
- [ ] identifies gen 2 collections as the specific latency risk, and says why
      (the whole live set is marked)
- [ ] names at least one concrete allocation change (pooling, streaming under
      the LOH threshold, not holding state across an `await`)
- [ ] says what it would measure to validate the design
- [ ] states a trade-off it is knowingly accepting

**Question:** You own a service that must keep p99 latency under 50 ms. It runs
in a 2 GB container on 8 cores, and traffic is bursty. Design the GC
configuration and the allocation discipline for it, and defend your choices.

**Answer:** "We should use server GC, because we have multiple cores, but we
should limit heap count to 4, because we have only 2GB of memory. We should
avoid keeping the objects alive for the whole scope of the request until we
send a response, because if under high load we have some delays with processing
db calls or some other external services the objects can face mid life crisis.
We can try to use Span and ReadOnlySpan for string parsings and byte
manipulation to keep the data on the stack and decrease allocations on the
heap."

**Checklist, graded item by item:**

- [x] picks a GC mode and justifies it from cores **and** memory together —
      Server for the cores, heap count capped for the 2 GB. Both axes, and the
      capping is the exact point sitting in an open drill miss, volunteered
      correctly.
- [x] names allocation discipline / survival rate as the primary lever — two of
      the three points are discipline, not settings.
- [ ] identifies gen 2 collections as the specific latency risk, and says why —
      **absent.** Mid-life crisis is named, but never connected to p99, and the
      reason a gen 2 collection is the thing that breaks a latency budget (the
      whole live set is marked) is never stated. For a question whose entire
      constraint is p99, this is the centre of the answer.
- [x] names at least one concrete allocation change — two: no request state held
      across the `await`, and `Span`/`ReadOnlySpan` to cut allocations.
- [ ] says what it would measure to validate — **absent.** Nothing at all. Same
      gap as Q1, where the measurement half was also declined.
- [ ] states a trade-off it is knowingly accepting — **absent.** Capping heap
      count trades throughput for footprint; it is implied and never named.

Score: 3 of 6.

Minor wobble: `Span` does not as such "keep the data on the stack" — a
`ReadOnlySpan<char>` over a string points at heap memory. What it avoids is
copies and intermediate allocations. Intent right, mechanism loosely stated.

**Awarded:** L2 — the mode decision is genuine design work, reasoning from two
constraints at once rather than one, and the allocation disciplines are
concrete and correct. But three of six checklist items are missing, including
the one the question was built around: why a p99 target makes gen 2 the enemy.
No trade-off was stated → **cap L2** applies regardless.

## Self-assessment

**Declined.** Asked "which answers did you think were weak?" before any grade
was shown; the user chose to skip it. `self_flagged` is empty by refusal, not
because nothing was flagged. This is the **second consecutive session** with no
self-assessment data, and it is the only input the calibration checkpoint
reads — after this session, 2 of 3 interviews carry none.

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-triggers-and-budgets]] | L3 | L2 | — | — |
| 2 | [[gc-triggers-and-budgets]] | L4 | L3 | — | — |
| 3 | [[gc-triggers-and-budgets]] | L4 | L2 | — | — |
| 4 | [[gc-triggers-and-budgets]] | L3 | L3 | — | — |
| 5 | [[gc-triggers-and-budgets]] | L4 | L3 | — | — |
| 6 | [[gc-triggers-and-budgets]] | L3 | L3 | — | — |
| 7 | [[boxing]] | L2 | L2 | — | — |
| 8 | [[boxing]] | L3 | L2 | — | — |
| 9 | [[gc-generations]] | L3 | L2 | — | — |
| 10 | [[gc-triggers-and-budgets]] | L5 | L2 | — | — |

No `discovery` questions were asked, so every question counts toward its
concept grade.

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-triggers-and-budgets]] | L1 | **L2** | min of Q1 L2, Q2 L3, Q3 L2, Q4 L3, Q5 L3, Q6 L3, Q10 L2 → L2. Taught 2026-09-12, one day clear, so a rise is permitted |
| [[boxing]] | L0 | **L2** | min of Q7 L2, Q8 L2 → L2. Taught 2026-09-12, one day clear |
| [[gc-generations]] | L1 | L1 | Q9 graded L2, which would raise it — **blocked**: the note has `taught: 2026-09-13`, and a level rises only in an interview at least one day after teaching. Grade recorded as evidence; re-testable 2026-09-14 |

Both rises are the first movement above L1 anywhere in this topic.

## Misses

- [[gc-triggers-and-budgets]] — cannot say what to measure to confirm a change
  in allocation or budget; declined the measurement half of Q1 outright and
  omitted it again in the Q10 design
- [[gc-triggers-and-budgets]] — Q10 design: gen 2 never identified as the p99
  latency risk, and no trade-off stated for the configuration chosen
- [[boxing]] — believes the boxes behind a `List<object>` sit contiguously, and
  that they live on the LOH; they are 24-byte objects scattered on the small
  object heap. Held under two probes
- [[boxing]] — states generic specialisation happens at compile time; it happens
  at runtime, when the JIT creates the instantiation. Third occurrence
- [[boxing]] — derives the 24-byte box size by assertion rather than arithmetic,
  and attributes the padding to a minimum width for the value field rather than
  8-byte alignment of the whole object
- [[gc-generations]] — describes the write barrier as *checking* for old-to-young
  references rather than *recording* that an old location was written, which is
  why it is cheap enough to run on every store

## Queue

| Concept | Next |
|---|---|
| [[gc-triggers-and-budgets]] | 2026-09-16 |
| [[boxing]] | 2026-09-16 |
| [[gc-generations]] | 2026-09-14 |

