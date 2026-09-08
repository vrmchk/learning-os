---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-08
mode: interview
excursion: false
questions: 3
avg_target: 2.7
avg_awarded: 0.3
concepts: [gc-generations, stack-vs-heap-layout, gc-triggers-and-budgets]
self_flagged: [1, 2, 3]
disputes: 0
---

# 2026-09-08 — GC generations

**Proposed by rule:** 4 — lowest-level concepts in focus topic, row order
**Override:** none
**Stopped early:** three consecutive answers at L1 or lower → switched to `teach`.

## Q1 — [[gc-generations]] — target L3 — depth

**Question:** Explain what a generation is, what determines which generation an
object is in, and why the runtime uses generations instead of collecting the
whole heap every time.

**Answer:** "Each generation basically means how much garbage collections the
object has survived" — gen 0 none, gen 1 one, gen 2 two or more. Generations
"determine which object should be garbage collected first". "When the system
runs low on memory we first of all check for generation zero objects", which
are short-lived like local variables; gen 2 holds long-lived things like
singletons and config.

**Probes:**
1. *Why is collecting gen 0 quicker than gen 2 — what does the cost depend
   on?* → "the scope is narrower and we don't have a lot of references to this
   object all over the project, and gen 2 has a lot of references". Cost
   attributed to reference count, not live-set size.
2. *Plenty of free RAM, heavy allocation — does gen 0 ever collect, and what
   triggers it?* → "if we create an object inside of a method and it's not
   referenced outside, it is garbage collected as soon as we get out of scope
   of this method. Same with loops." GC believed to run on scope exit and on
   low memory.

**Awarded:** L1 — can define generations; the mechanism (allocation budget)
and the cost model (live set, generational hypothesis) are both wrong. Missed
trade-off → cap L2 would apply, but the wrong trigger model puts it at L1.

## Q2 — [[stack-vs-heap-layout]] — target L2 — prerequisite

**Question:** `int x = 5; var p = new Point(1,2)` (struct);
`var list = new List<int>()`. Where does each live, and what happens to each
when the method returns?

**Answer:** "x and p in the stack. list in the heap. When the method returns
we free up the memory both in stack and in heap." Did not separate the `list`
reference variable (stack) from the `List<int>` object (heap).

**Probes:**
1. *Who frees the List object, and at what moment?* → "GC frees it, at the
   moment when the method finishes and we get out of its scope."
2. *Before returning, `SomeClass.Cache = list;` — same answer?* → "Now we
   won't GC this list from the heap because there's an alive reference to
   it." Reachability via a static root understood.

**Awarded:** L1 — placement correct, reachability correct, but heap memory
is said to be freed by the GC at method exit. Between L1 and L2 → L1.

## Q3 — [[gc-triggers-and-budgets]] — target L3 — depth

**Question:** Web service, a few hundred KB of short-lived allocations per
request, nothing low on memory. Describe the sequence of events that starts a
gen 0 collection, and what makes the runtime pick gen 1 or gen 2 instead.

**Answer:** "Not sure about this one."

**Probes:**
1. *Best model — what is the runtime measuring?* → "The GC can be triggered
   for example when we finish handling this request and respond with some
   status code."

**Awarded:** L0 — cannot define the trigger. First contact, cannot define →
L0.

## Self-assessment

User flagged as weak: Q3 ("definitely"), Q1 and Q2 ("not sure if I was right
on GC getting triggered when we're out of scope").

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-generations]] | L3 | L1 | weak | — |
| 2 | [[stack-vs-heap-layout]] | L2 | L1 | weak | — |
| 3 | [[gc-triggers-and-budgets]] | L3 | L0 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-generations]] | L0 | L1 | Q1: can define, cannot use |
| [[stack-vs-heap-layout]] | L0 | L1 | Q2: placement right, lifetime wrong |
| [[gc-triggers-and-budgets]] | L0 | L0 | Q3: cannot define; evidence recorded |

## Misses

- [[gc-generations]] — believes the GC runs on scope exit and when memory is
  low; cannot say what actually triggers a collection
- [[gc-generations]] — attributes collection cost to "number of references"
  rather than the size of the live set; cannot say why generational
  collection is cheaper
- [[stack-vs-heap-layout]] — states the heap object is freed by the GC at the
  moment the method returns; does not separate the reference variable from
  the object
- [[gc-triggers-and-budgets]] — cannot name the gen 0 allocation budget as the
  trigger; model is "end of request"

## Queue

| Concept | Next |
|---|---|
| [[gc-generations]] | 2026-09-09 |
| [[stack-vs-heap-layout]] | 2026-09-09 |
| [[gc-triggers-and-budgets]] | 2026-09-09 |
