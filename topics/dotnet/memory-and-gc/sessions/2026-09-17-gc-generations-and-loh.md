---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-17
mode: interview
coached: true
excursion: false
questions: 10
avg_target: 3.4
avg_awarded: 2.3
concepts: [gc-generations, large-object-heap, stack-vs-heap-layout, gc-triggers-and-budgets, boxing]
self_flagged: [1, 5, 7, 10]
disputes: 0
---

# 2026-09-17 — GC generations and the large object heap

**Proposed by rule:** 1 — overdue queue items, both due 2026-09-14
**Override:** none

**Mode:** coached (`coached: true`). This session was the trial that introduced
the mode; it was run before the mode existed in the files, and `interview`
gained the `exam` / `coached` parameter immediately afterwards on the same day.

At the user's request, the correction and
a model answer were given in chat after each question and its probes, instead
of only at the end. Grades stayed hidden until after self-assessment, and no
later question re-tested a point corrected earlier. Two consequences for
anyone reading this file later: the self-assessment below was made *after*
seeing the corrections, so it is weaker calibration data than a normal
session's, and questions 5–10 were constrained away from corrected ground. If
the format is kept, `BOOTSTRAP.md` decides first, then `CLAUDE.md` and
`interview/SKILL.md`.

## Q1 — [[gc-generations]] — target L3 — depth

**Question:** An ASP.NET Core service used to build each response object and
throw it away at the end of the request. A new feature caches every response
object for 30 seconds, then evicts it. Traffic and sizes unchanged. GC time
rises and gen 2 collections become much more frequent. Using the generational
model, explain why a 30-second lifetime costs the GC more than both a 50 ms
lifetime and a permanent one. What would you change, and what does each option
cost?

**Answer:** "Because of GC budgets these responses tend to survive garbage
collections because they still have alive reference. So they get promoted to
Gen 2 ... for garbage collector 30 seconds is a lot and multiple collections
can run during this period." Named gen 2 collections as expensive ("we collect
the whole heap and all generations") and promotion as costly. Options offered:
revert, extend the lifetime to near-permanent, or move the cache to Redis.

**Probes:**
1. *Why is permanent cheaper than 30 seconds, if both reach gen 2?* → "the
   budgets for Gen 2 will grow for some time and after that will stay flat.
   And since the objects will be reachable forever, we won't have to collect
   it." Correct.
2. *Price the Redis option against shortening the TTL.* → "network latency and
   serialization allocations per request ... redis cluster will cost us
   additional budgets." Correct as far as it goes; no mention that a
   serialized payload over 85,000 bytes lands on the LOH.

**Awarded:** L2 — the promotion mechanism is right and unprompted, but the two
halves the question explicitly asked for (why permanent is cheaper, what each
option costs) both required a probe. Never stated that evicted entries become
garbage *inside gen 2*, reclaimable only by a full collection, which is the
actual engine of the rising gen 2 count; never mentioned repeated copying of
the survivors during their 30 seconds, nor the old→young card marking on cache
insert. Cap: trade-offs only on prompting.

## Q2 — [[large-object-heap]] — target L4 — depth

**Question:** A background service allocates a `byte[]` sized from each
uploaded file (200 KB – 2 MB), reads into it, and caches a small result object
for hours. After days it throws `OutOfMemoryException`; the dump shows 6 GB
held with ~4 GB free on the managed heap. How can it be out of memory with
4 GB free? What in the numbers confirms it, and which detail in the code makes
it worse than plain buffer churn?

**Answer:** "It happens due to large object heap fragmentation. LOH is never
compacted unlike the small heap ... we get free and used chunks of memory one
after another ... we have four gigabytes free, but the biggest chunk available
can be less than 2 megabytes." Named free-list reuse, correctly identified the
variable buffer size as the aggravating detail, and that everything ≥ 85,000
bytes lands on the LOH at birth. For confirmation: "look at which generations
we have the most free memory ... generation 2 and large object heap".

**Probes:**
1. *What would you watch over days to tell fragmentation from a leak?* → "in
   both cases heap size grows, but with a leak the used space grows as well.
   With fragmentation used memory stays flat and we have plenty of free space."
   Correct direction, but never named the largest contiguous free block.

**Awarded:** L3 — mechanism is complete and unprompted, including the detail
the question was built around. The confirming numbers stayed at the level of
"lots of free space", which is the symptom already given in the question; the
discriminating measure (total free rising while the largest contiguous block
stays flat) never appeared, and gen 2 and the LOH were treated as one thing.
Cap: L4 needs the measurement, not only the mechanism.

## Q3 — [[gc-generations]] — target L4 — depth

**Question:** Three gen 0 collections: A — 50,000 objects, 200 survive; B —
500 objects, 200 survive; C — 50,000 objects, 40,000 survive. Rank the pauses
and explain what the collector does that produces that ranking. Which leaves
the process in the worst state minutes later, and why?

**Answer:** "A and B have the same cost and C is the heaviest ... the
collection costs us only by survivors, not by allocations." Work per survivor
given as copy, move, and update every reference to the live object. C worst
later: "it enters into midlife crisis ... Gen 1 and Gen 2 collections are way
more costly."

**Probes:**
1. *What does the collector do with the gen 0 budget after C?* → "it will
   shrink the budget so gen 0 collections happen more often." Correct, but no
   reason given (bounding how much is promoted per collection).

**Awarded:** L3 — the governing rule and the ranking are right and unprompted.
Compaction direction stated backwards ("moved to the end of gen 0"); survivors
are compacted *down* against gen 1 and the boundary slides up above them. The
aftermath was named ("mid-life crisis") but not traced: gen 1 budget exhausted
by 40,000 promotions → gen 1 collections → survivors into gen 2 → gen 2 budget
filled by promotion.

## Q4 — [[large-object-heap]] — target L3 — depth

**Question:** A reporting endpoint appends 60,000 formatted rows (~80 chars
each) to a `StringBuilder` and returns `sb.ToString()`. A colleague says only
two objects matter, the builder and the ~10 MB final string, so the LOH cost is
one large object per request. What is wrong with that account? Walk through
what the code does to the heaps and say what you would change.

**Answer:** Named the 60,000 temporary strings from `Format` as the biggest
issue and that they exceed the gen 0 budget several times; the final string
lands straight on the LOH; `StringBuilder` "uses several char arrays linked
together, which will also survive until gen 2". Fixes offered: have `Format`
return a `Span`/`ReadOnlySpan` "so that data will live on stack", and stream
rows directly to the HTTP response instead of calling `ToString()`.

**Probes:**
1. *Where would a returned span point, and does it compile?* → "we cannot
   return a span from the method, we can only pass it as a parameter." The safe
   rule, but not the actual one: a `Span<T>` over heap memory can be returned;
   one over the method's own frame cannot.

**Awarded:** L3 — rejected the colleague's framing for the right reasons and
reached the correct fix (stream, never materialise) unprompted, with the chunked
builder and the 2-bytes-per-char consequence both present. Held below L4 by the
wrong `Span` proposal, and by not pricing `ToString()` itself: it allocates the
~9.6 MB string *and* copies all ~600 chunks, so both are live at once.

## Q5 — [[gc-generations]] — target L4 — depth

**Question:** On .NET Framework and early .NET Core, where do gen 0, gen 1 and
gen 2 physically live, and what happens in a long-running process as the memory
holding gen 0 and gen 1 runs out of room? What did .NET 7 change, what problem
was it solving, and what stayed the same?

**Answer:** "They lived one after another ... the survivors in gen 0 were moved
to the end of gen 0 memory and then we move the pointer boundary of gen 1 up."
Problem solved by regions given as "some generation memory fills up and we
can't allocate into it anymore but there are plenty of free space in other
generations", and the regions model as "we split the memory between different
regions and each region is split between those three generations."

**Probes:**
1. *What does the runtime do with the ephemeral segment when it can give no
   more space?* → "Will begin a fresh new one." Half.
2. *What generation are the objects in the old segment then?* → "gen 2."
   Correct, on the second probe.

**Awarded:** L2 — segment retirement into gen 2, the core of the question,
needed two probes; gen 2's own segments were never mentioned; compaction
direction wrong for the second time this session; and the regions model came
out inverted — a region belongs to one generation, not one region split across
three. Cap: mechanism supplied by probing, not by the answer.

## Q6 — [[large-object-heap]] — target L4 — depth

**Question:** Documentation sometimes calls the LOH "generation 3". Is that a
figure of speech or is something real behind it? Say precisely what is true and
what is false in the name, and what the runtime actually tracks.

**Answer:** True part given as: it has its own budget, and objects ≥ 85,000
bytes go there straight away. The stated "false" part was "when gen 2
collection is triggered we collect large object heap as well and perform a full
collection" — which is true.

**Probes:**
1. *Is that statement true or false?* → "true."
2. *Then what is false about calling it generation 3?* → "if it truly was
   generation 3, if gen 2 collection budget was exceeded we wouldn't collect
   it and would collect it only when LOH's own budget is exceeded." Not the
   falsehood; separate accounting with shared escalation is exactly how it
   works.

**Awarded:** L2 — the true half is partly there (own budget, size decides at
birth), but the question's core — that **nothing ever ages into or out of the
LOH**, so it is not a generation in the only sense that matters — was never
reached across two probes, and the runtime's `max_generation + 1` bookkeeping
was not named. Cap: could not separate true from false in the term it was using.

## Q7 — [[stack-vs-heap-layout]] — target L2 — adjacent

**Question:** 64-bit process. `class Order` with `int _id`, `DateTime _placed`,
`byte _status`, `int[] _lineIds` pointing at an `int[1000]`. How many bytes
does `new Order()` ask for, how many does the array ask for, show the
arithmetic, and which number would a profiler attribute to `Order`?

**Answer:** "Order object: 16 (object header, sync block and method table) + 4
+ 8 + 1 + 8 (reference to an array). Array: 16 + 4 (length) + 4 * 1000."

**Probes:**
1. *Objects are 8-byte aligned — what are the final sizes?* → "37 and 4020."
   Alignment not applied even when named.
2. *Which number does a profiler show next to `Order`, and what is the term for
   the difference?* → "I don't know", plus the view that the question is too
   niche to be asked.

**Awarded:** L1 — the header-plus-fields rule was applied correctly, but the
arithmetic could not be completed when the missing rule was handed over:
37 rounds to 40, and the array's length slot is 8 bytes on x64, not 4
(16 + 8 + 4,000 = 4,024). Shallow versus retained size absent. Between L1 and
L2 → L1.

## Q8 — [[gc-triggers-and-budgets]] — target L3 — adjacent

**Question:** A service runs a gen 0 collection about every 2 seconds. You cut
total allocation by 40%, with traffic, lifetimes and survival rates unchanged.
What happens to the gen 0 collection count per minute, and to the pause time of
each collection? Explain the mechanism behind each.

**Answer:** "The count will drop but pause time stays the same because the
pause is affected by survivors, not allocations."

**Probes:**
1. *What happens to promotion per minute and to gen 2 frequency?* → "less
   promotion per minute, so gen 2 collections less frequent." Correct.

**Awarded:** L2 — both answers correct and the governing rule stated
unprompted, but the question asked for the mechanism behind each and only one
was given: the count falls because the budget is a **byte count** that now
takes ~40% longer to fill, while each collection still triggers at the same
number of allocated bytes and therefore sees the same survivors. Cap: half the
mechanism requested was not supplied.

## Q9 — [[boxing]] — target L3 — cold recall

**Question:** `_logger.LogInformation("Order {OrderId} took {Ms} ms", orderId,
elapsedMs)` with a `long` and an `int`, at a log level where the message is
never written. What does the line allocate per call, why does the log level not
save you, and what would you change?

**Answer:** "Boxing of both arguments into params object[], level check happens
after. We can check whether this log level is enabled before calling
LogInformation."

**Probes:**
1. *Better fix if the pattern is everywhere, and what does it do differently?*
   → "LoggerMessage source generator which generates this check at compile
   time." Right tool, incomplete reason.

**Awarded:** L3 — identified the boxing, the `params object[]`, and the
ordering (arguments evaluated at the call site before the level is checked)
unprompted, and named the guard. Held at L3: the array was not counted as an
allocation distinct from the two boxes (three per call), and the source
generator was described as a compile-time level check rather than a
strongly-typed delegate that removes the boxing and the array entirely.

## Q10 — [[large-object-heap]] — target L4 — depth

**Question:** An HTTP API accepts uploads up to 50 MB, hashes them with
SHA-256, writes them to blob storage and returns a small JSON summary. 200
req/s peak, p99 target 200 ms, 4 GB container limit. The first implementation
reads the whole body into a `byte[]` sized from `Content-Length`, hashes it,
and uploads it. Design the memory strategy: what you would change and why, what
it costs, what fails if you do not, and how you would bound memory at peak.

**Checklist — written before the question was asked, not revised after:**
- [x] never materialise the payload: stream it, and keep per-chunk buffers well
      under the 85,000-byte threshold so nothing reaches the LOH
- [ ] pool the buffers (`ArrayPool<T>` / recyclable streams) and price the
      hazard: use-after-return, never-returned buffers
- [x] what fails otherwise: per-request LOH allocation drives full collections
      at request rate, and variable sizes fragment the free list until an OOM
      with memory still free
- [ ] hash incrementally over the stream rather than over a materialised array
- [ ] bound memory at peak explicitly: ceiling ≈ concurrent requests × buffer
      size, enforced by limiting concurrency and pool size, checked against the
      container limit

**Answer:** "We should not allocate such byte arrays ... it will land straight
on large object heap and with such API load we will constantly be garbage
collecting the whole heap ... we can also expect to face fragmentation issues
in the future. The solution will be to switch to streaming approach and never
allocate the whole file into the memory."

**Probes:**
1. *What buffer, what size, where from, and how do you hash without holding the
   file?* → "I'm not familiar with these classes, but I'm pretty sure it's
   possible to do it through streams without loading the whole file into
   memory."
2. *At 200 req/s in a 4 GB container, what is the ceiling and which knob sets
   it?* → "we should also probably configure workstation GC. Since the memory
   is using this 75% of 4GB which is 3 GB. If our files is 50 megabytes we will
   get out of memory exceptions very quickly especially during high load." The
   75% container heap hard limit is correct and recalled unprompted, but it is
   not the knob: the ceiling is concurrency × buffer size.

**Awarded:** L2 — 2 of 5 checklist items. The diagnosis and the direction of
the fix are right, but a design answer has to be costed and bounded: no
pooling and no pricing of it, no incremental hashing, and no memory ceiling
even when asked for directly. Cap: missed the trade-off and the bound.

## Self-assessment

User flagged as weak: Q1, Q5, Q7, Q10

Made after the per-question corrections were shown (see the format trial note
above), so it is not comparable with the self-assessments in earlier sessions.

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-generations]] | L3 | L2 | weak | — |
| 2 | [[large-object-heap]] | L4 | L3 | — | — |
| 3 | [[gc-generations]] | L4 | L3 | — | — |
| 4 | [[large-object-heap]] | L3 | L3 | — | — |
| 5 | [[gc-generations]] | L4 | L2 | weak | — |
| 6 | [[large-object-heap]] | L4 | L2 | — | — |
| 7 | [[stack-vs-heap-layout]] | L2 | L1 | weak | — |
| 8 | [[gc-triggers-and-budgets]] | L3 | L2 | — | — |
| 9 | [[boxing]] | L3 | L3 | — | — |
| 10 | [[large-object-heap]] | L4 | L2 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-generations]] | L1 | L2 | min of Q1 L2, Q3 L3, Q5 L2 |
| [[large-object-heap]] | L1 | L2 | min of Q2 L3, Q4 L3, Q6 L2, Q10 L2 |
| [[boxing]] | L2 | L3 | Q9 L3 |
| [[stack-vs-heap-layout]] | L1 | L1 | Q7 L1 — held, evidence refreshed |
| [[gc-triggers-and-budgets]] | L2 | L2 | Q8 L2 — held, evidence refreshed |

No discovery questions were asked; all ten counted toward the grades.

## Misses

- [[gc-generations]] — does not say that evicted cache entries become garbage
  *inside gen 2*, reclaimable only by a full collection; priced the options
  only when prompted
- [[gc-generations]] — states twice that survivors are compacted "to the end"
  of the generation; they are compacted down against gen 1 and the boundary
  slides up above them
- [[gc-generations]] — does not know that a full ephemeral segment is retired
  into gen 2 and a fresh one started (two probes needed), and does not place
  gen 2 in its own segments
- [[gc-generations]] — inverts the .NET 7 regions model: says each region is
  split across the three generations, rather than each region belonging to one
  generation
- [[large-object-heap]] — cannot name what is false in calling the LOH
  "generation 3": nothing ever ages into or out of it; argued instead that the
  shared escalation to a gen 2 collection is the falsehood
- [[large-object-heap]] — no discriminating measure for fragmentation: total
  free space rising while the largest contiguous free block stays flat; treats
  gen 2 and the LOH as one pool, and does not mention that adjacent free blocks
  coalesce
- [[large-object-heap]] — design answer is neither costed nor bounded: no
  pooling and no pricing of its hazards, no incremental hashing, and no memory
  ceiling (concurrency × buffer size) when asked for it directly
- [[large-object-heap]] — does not price `StringBuilder.ToString()`: it
  allocates the large string *and* copies every chunk, so both are live at once
- [[stack-vs-heap-layout]] — does not apply 8-byte object alignment even when
  told to, and gives the array length slot as 4 bytes rather than 8; shallow
  versus retained size unknown
- [[gc-triggers-and-budgets]] — does not state that the budget is a byte count,
  so cannot explain why fewer allocations mean fewer collections of unchanged
  cost
- [[boxing]] — does not count the `params object[]` as an allocation separate
  from the boxes (three per call), and describes the `[LoggerMessage]` source
  generator as a compile-time level check rather than a strongly-typed delegate
  that removes the boxing entirely

## Queue

| Concept | Next |
|---|---|
| [[stack-vs-heap-layout]] | 2026-09-18 |
| [[gc-generations]] | 2026-09-20 |
| [[large-object-heap]] | 2026-09-20 |
| [[gc-triggers-and-budgets]] | 2026-09-20 |
| [[boxing]] | 2026-09-24 |
