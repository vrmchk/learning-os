---
topic: dotnet
cluster: async-and-threading
date: 2026-09-30
mode: interview
coached: true
excursion: false
questions: 2
avg_target: 4.0
avg_awarded: 1.5
concepts: [threads-and-scheduling, parallelism-vs-concurrency]
self_flagged: [2]
disputes: 0
---

# 2026-09-30 — Async and threading, tier 1 (taught so far)

**Proposed by rule:** 1 — overdue queue items (threads-and-scheduling 10 days, parallelism-vs-concurrency and thread-pool-internals 9 days)
**Override:** user narrowed to the async-and-threading concepts taught so far

Coached format: after each question and its probes, the shortfalls and a model
answer were given before moving on. The self-assessment followed those
corrections. No later question was constrained by the no-re-test rule — the
session was stopped by the user during Q2's probes, after two questions.
[[thread-pool-internals]] was planned but not reached and is not graded.

## Q1 — [[threads-and-scheduling]] — target L4 — depth

**Question:** A colleague says "we can't go thread-per-request, 1,000 threads is 1 GB of RAM." What is right and wrong in that sentence, and what does a thread actually cost?

**Answer:** "one .NET thread costs us 1 MB of memory because this is memory allocated for this thread on creation." Main problem is creation cost — "creating a new thread is very costly in memory and time", a .NET thread wraps an OS thread; ASP.NET uses the thread pool to reuse threads. Also: "we most likely don't have a thousand cores ... threads which exceed that number will just be waiting."

**Probes:**
1. *1,000 idle threads — ~1 GB more working set? Why?* → "1 MB is memory we reserve for the thread, not allocate straight away ... not all of that memory is used." Did not say address space, pages, or touched-on-demand.
2. *Each request 200 ms waiting on DB, 1 ms CPU — waiting for what; does core count bind?* → "I wasn't wrong about core counts ... but this is not the main problem ... use async for I/O bound and threads for CPU bound." Did not say blocked threads are not competing for cores, nor name what binds.

**Awarded:** L2 — corrected "allocated" to "reserved" only under a probe and could not unpack it (no address space vs physical pages); applied the core-count argument to blocked I/O threads; never named what actually binds for I/O-bound thread-per-request. Correct on creation cost, pool reuse, and async-for-I/O.

## Q2 — [[parallelism-vs-concurrency]] — target L4 — depth

**Question:** A teammate says "our service runs on a single-core container, so we don't need to worry about race conditions on shared counters." Right or wrong, and why? Then: what class of bug does moving to 8 cores *add* that cannot happen on one core?

**Answer:** Wrong — "race condition is not a problem of parallelism but a problem of concurrency." Example given at the database level: two concurrent requests changing a value can give different results depending on scheduling. Second half: "if we move to 8 cores there can be deadlocks."

**Probes:**
1. *Single process, `static int count`, two threads doing `count++` on one core — how is an update lost? Walk the mechanism.* → "I'm not sure that you've taught me about it." Told it is covered in the note's Failure modes ("Assuming races need parallelism"); the user then stopped the session. Mechanism not given.
2. Not asked — session stopped.

**Awarded:** L1 — states the principle (concurrency suffices for a race) but cannot give the mechanism (load/add/store, preemption between steps); the second half is wrong — deadlocks do not need multiple cores — and memory-visibility races were not named.

## Self-assessment

User flagged as weak: Q2

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[threads-and-scheduling]] | L4 | L2 | — | — |
| 2 | [[parallelism-vs-concurrency]] | L4 | L1 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[threads-and-scheduling]] | L0 | L2 | Q1 L2; taught 2026-09-19, more than a day ago |
| [[parallelism-vs-concurrency]] | L0 | L1 | Q2 L1; can state the principle, cannot unpack the mechanism |

## Misses

- [[threads-and-scheduling]] — says a thread's 1 MB is "allocated"; corrected to "reserved" only under a probe and cannot unpack it as address space with physical pages touched on demand (~8–32 KB real per thread)
- [[threads-and-scheduling]] — applies the core-count limit to blocked I/O threads; cannot name what binds for I/O-bound thread-per-request (per-thread overhead, kernel objects, scheduler, pool injection rate)
- [[parallelism-vs-concurrency]] — cannot give the mechanism of a lost `count++` update on one core: load/add/store with preemption between steps
- [[parallelism-vs-concurrency]] — believes moving to many cores adds deadlocks (which need no second core); does not know the class multicore actually adds, memory-visibility races (store buffers, reordering)

## Queue

| Concept | Next |
|---|---|
| [[parallelism-vs-concurrency]] | 2026-10-01 |
| [[threads-and-scheduling]] | 2026-10-03 |
