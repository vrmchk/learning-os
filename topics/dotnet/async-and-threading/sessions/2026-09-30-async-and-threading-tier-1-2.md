---
topic: dotnet
cluster: async-and-threading
date: 2026-09-30
mode: interview
coached: true
excursion: false
questions: 4
avg_target: 3.8
avg_awarded: 1.5
concepts: [thread-pool-internals, threads-and-scheduling, parallelism-vs-concurrency, cancellation-tokens]
self_flagged: [1, 2, 3, 4]
disputes: 0
---

# 2026-09-30 — Async and threading, tier 1 (ladder format)

**Proposed by rule:** 1 — overdue queue items (thread-pool-internals 9 days); user asked for the async-and-threading cluster
**Override:** user narrowed to the taught async-and-threading concepts

Coached format, and the first session in the ladder format (`BOOTSTRAP.md`
§6, "Question ladders"). After each ladder the user rated it in one word
before any correction was given; those ratings are the self-assessment. No
point corrected within this session was re-asked. Points corrected earlier
today in [[2026-09-30-async-and-threading-tier-1]] were not asked either: a
thread's stack as reserved address space, what binds for blocked I/O threads,
the lost-update mechanism on one core, deadlocks on one core, and
memory-visibility races. That is why Q2 never reached rung 4 material on
thread cost, and why Q3's rung 3 was aimed at async's costs rather than at why
it scales.

## Q1 — [[thread-pool-internals]] — target L5 — depth

**Rung 1 — Explain (L1):** *What is the thread pool in .NET, and why does it exist?* → a mechanism to "reuse already created threads instead of deleting them"; creating a thread is costly — "one megabyte ... per each thread" reserved and ~100 µs to create, "which can be more than the work which will be done on this thread"; finished threads go back to the pool and the next task takes a free one. — **cleared**

**Rung 2 — Use (L2):** *In everyday .NET code, what actually puts work onto the thread pool? Name as many sources as you can.* → "calling an async method, `Task.Run`, `Task.Factory`".

**Probes:**
1. *Which part of an async method runs on the pool — the call itself?* → "the task from async method can be run on some thread from pool"; declined the mechanics as the state machine is untaught. Did not say that the call runs synchronously on the caller's thread and only the continuation after an `await` is queued to the pool.
2. *ASP.NET Core API with no `Task.Run` anywhere — is the pool used, and what feeds it?* → "each request ... can run on threads from thread pool"; multiple concurrent requests, multiple threads.

— **not cleared**; climb stops. Three of the note's six sources named (`Task.Run`, `Task.Factory.StartNew`, requests); continuations after `await`, timer callbacks and I/O completions missing; "calling an async method" given as a source, which it is not.

**Rating:** shaky ("between solid and shaky, closer to shaky")

**Awarded:** L1 — rung 1 cleared; rung 2 half-answered (half the sources, and the async source stated wrongly), so not cleared.

## Q2 — [[threads-and-scheduling]] — target L5 — depth

Hooked to Q1: the user said creating a thread is costly because a .NET thread wraps an OS thread.

**Rung 1 — Explain (L1):** *You said a .NET thread is expensive to create. What is a thread in .NET — what is actually behind `System.Threading.Thread`, and who decides when it runs?* → "a wrapper over a system OS thread"; "a kernel object and one megabyte of reserved address space" behind it — but "I don't really understand what the kernel object is ... I just remember about it". Did not answer who schedules it.

**Probes:**
1. *Who decides which core it runs on, when it starts, when it is taken off?* → "on the high level ... thread pool decides"; "on lower level ... some kind of OS scheduler".
2. *A `new Thread(...)` outside the pool on a busy 8-core box — which of the two gives it a core and takes it off; what does the pool decide instead?* → the OS scheduler decides; the pool only decides which work item runs on which pool thread; the threads themselves are managed by the OS scheduler.

— **cleared** (after two probes). Miss recorded: "kernel object" used without being able to unpack it.

**Rung 2 — Use (L2):** *How do you run code on a dedicated thread yourself, and what is the difference between a foreground and a background thread?* → create a `new Thread` and pass it the method; "also we can run parallel LINQ". Foreground: the process waits for it at termination; background: terminated without waiting. Trade-off stated unprompted: foreground can delay shutdown, background can be killed mid-work "while we are not at a safe point".

**Probes:**
1. *What threads does PLINQ run its work on?* → "not sure ... I can guess that it runs on thread pool threads ... just a guess".
2. *`new Thread(Work)` — foreground or background by default? `Task.Run`?* → foreground by default; `Task.Run` background; stopping properly needs a `CancellationToken` checked inside the method.

— **cleared**. Miss recorded: offered PLINQ as a way to get a dedicated thread; it partitions work across pool threads.

**Rung 3 — Trade-offs (L3):** *Most code should never create a `Thread` itself. When does a dedicated thread genuinely beat the thread pool or async — and what do you pay for it?* → long-running CPU-bound work, "analytic data calculations ... data processing"; "I can't answer confidently what we pay for it".

**Probes:**
1. *Why is long-running work a problem on the pool specifically — ten-minute job via `Task.Run`?* → "we have a limit of how many thread pool threads can run at the same time"; if all are occupied, others wait — "not 100% sure".
2. *What do you take on or give up by owning the thread?* → "we handle the thread allocation on our own"; after the work it is destroyed and cannot be reused.

— **not cleared**; climb stops. Only the textbook case (long-running work); none of the cases the note gives — thread affinity for a native library, STA apartment state, a custom stack size, a process-lifetime loop, a blocking SDK with no async API, thread priority. Frames the pool problem as a hard thread limit rather than the pool mistaking a long-running item for a blocked one and injecting threads to compensate. Costs partial: owning the lifetime; no mention of shutdown handling, ~1 MB reserved and ~100 µs creation, or `TaskCreationOptions.LongRunning` as the middle path.

**Rating:** shaky ("weak shaky")

**Awarded:** L2 — rungs 1–2 cleared, rung 3 missed the cases and the costs (trade-off cap).

## Q3 — [[parallelism-vs-concurrency]] — target L4 — depth

Hooked to Q2: the user reached for "CPU-bound work" as the case for a thread. Target capped at L4: rung 5 would be a quantified design, and an open drill miss records that design answers are not quantified.

**Rung 1 — Explain (L1):** *You keep separating CPU-bound work from the rest. In those terms — what is concurrency, what is parallelism, and how are they different?* → concurrency is "structuring the program in a way which allows us to deal with multiple tasks at once, without waiting for each of them to complete"; parallelism is "actually running them at the same time". Examples: matrix multiplication across threads (parallelism); calling an external API and doing other work while waiting (concurrency). — **cleared**

**Rung 2 — Use (L2):** *You have two jobs: resize 10,000 images in memory, and call an external API 10,000 times. Which .NET tool do you reach for in each, and why that one?* → images are "pure CPU bound work" → threads; the API calls are I/O-bound → async tasks, and "to do it truly concurrently ... `Task.WhenAll`".

**Probes:**
1. *"Use threads" — what would you actually write, and how many resizes at once?* → a method for the unit of work passed to `new Thread`; "a number of threads which is close to core count" — eight on eight cores, a few fewer on a big box to leave room for the system.
2. *Teammate writes `Task.WhenAll(images.Select(img => Task.Run(() => Resize(img))))` — does it work, what is worse or better than your version?* → "I can't answer confidently".

— **cleared**: the tool choice matches the note's own table (CPU-bound → threads / pool / `Parallel`, I/O-bound → async) and the CPU side is bounded at core count unaided. Miss recorded: hand-rolls threads and partitioning rather than `Parallel.ForEach` / PLINQ, and cannot compare it with `Task.Run` per item (one `Task` per item, pool-scheduled, no chunking).

**Rung 3 — Trade-offs (L3):** *A colleague says "I made the endpoint async, so now it's faster." What does async actually buy you, and what does it cost?* → "async doesn't make our endpoints faster, it allows them to scale better"; making an endpoint async "actually makes it slower because we generate a lot of code at compile time for a state machine".

**Probes:**
1. *Generated code costs nothing per request — at runtime, what does one async call that actually waits cost that the sync one does not?* → "I don't know".
2. *Leave performance aside — what does async cost the codebase and debugging?* → "a little bit more complicated than sync ... looks almost as simple"; "when we debug async code it runs the same way as sync so during debug we lose the concurrency".

— **not cleared**; climb stops. Scalability-not-speed stated unaided and correctly. Costs wrong or missing: attributes the slowdown to compile-time code rather than a runtime state-machine allocation per suspension plus completion dispatch; does not name async as viral through the call stack, nor worse stack traces; the debugging claim is incorrect.

**Rating:** shaky ("weak shaky")

**Awarded:** L2 — rungs 1–2 cleared, rung 3 missed the costs (trade-off cap).

## Q4 — [[cancellation-tokens]] — target L1 — discovery

Hooked to Q2 rung 2: the user said stopping work properly needs a `CancellationToken` checked inside the method. Untaught (stub note created at write-back), so a one-rung discovery ladder: excluded from grades and from the stop rule.

**Rung 1 — Explain (L1):** *What is a `CancellationToken`, and why does .NET need one — why can't you just stop the thread or task from outside?* → "a mechanism which allows us to stop async tasks properly"; async tasks run on pool threads, which are background threads, so when the process stops "all threads are terminated straight away"; cancellation tokens allow "safe termination ... only at the safe point". — **not cleared**: defines it, but frames it only as safe process shutdown. Does not say it is a cooperative *request* signalled through a `CancellationTokenSource` that the called code must observe; does not answer why you cannot stop work from outside — a thread cannot be killed on .NET Core (`Thread.Abort` throws `PlatformNotSupportedException`); names none of the everyday sources (an aborted HTTP request, a timeout, host shutdown).

**Rating:** shaky

**Awarded:** L1 — defined, not why it exists. Discovery: excluded from the concept grade.

## Self-assessment

User rated: Q1 shaky, Q2 shaky, Q3 shaky, Q4 shaky

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[thread-pool-internals]] | L5 | L1 | weak | — |
| 2 | [[threads-and-scheduling]] | L5 | L2 | weak | — |
| 3 | [[parallelism-vs-concurrency]] | L4 | L2 | weak | — |
| 4 | [[cancellation-tokens]] | L1 | L1 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[thread-pool-internals]] | L0 | L1 | Q1: rung 1 cleared, rung 2 not; taught 2026-09-20 |
| [[threads-and-scheduling]] | L2 | L2 | held; Q2 cleared rungs 1–2 again, evidence refreshed |
| [[parallelism-vs-concurrency]] | L1 | L2 | Q3 cleared rungs 1–2 on points not corrected earlier today |
| [[cancellation-tokens]] | L0 | L0 | Q4 is `discovery` — excluded; level does not move |

## Misses

- [[thread-pool-internals]] — gives "calling an async method" as a pool source; does not know the call runs synchronously on the caller's thread and only the continuation after a suspending `await` is queued to the pool
- [[thread-pool-internals]] — cannot name timer callbacks, I/O completions or `ThreadPool.QueueUserWorkItem` as pool sources
- [[threads-and-scheduling]] — uses "kernel object" without being able to say what it is
- [[threads-and-scheduling]] — offers PLINQ as a way to get a dedicated thread; it partitions work across pool threads
- [[threads-and-scheduling]] — gives only long-running CPU work as the case for a dedicated thread (no thread affinity, STA, custom stack size, process-lifetime loop, blocking SDK, priority) and frames the pool problem as a thread limit rather than the pool mistaking a long item for a blocked one
- [[threads-and-scheduling]] — cannot state what owning a thread costs: shutdown handling, ~1 MB reserved and ~100 µs creation, and `TaskCreationOptions.LongRunning` as the middle path
- [[parallelism-vs-concurrency]] — hand-rolls threads for a CPU batch rather than `Parallel.ForEach` / PLINQ, and cannot compare it with `Task.Run` per item
- [[parallelism-vs-concurrency]] — attributes async's per-call cost to compile-time code rather than the runtime state-machine allocation and continuation dispatch
- [[parallelism-vs-concurrency]] — does not name async as viral or as costing stack-trace readability; claims async code runs synchronously under the debugger
- [[cancellation-tokens]] — frames cancellation only as safe process shutdown; does not know it is a cooperative request through a `CancellationTokenSource`, nor that a thread cannot be killed on .NET Core

## Queue

| Concept | Next |
|---|---|
| [[thread-pool-internals]] | 2026-10-01 |
| [[threads-and-scheduling]] | 2026-10-03 |
| [[parallelism-vs-concurrency]] | 2026-10-03 |

[[cancellation-tokens]] is not queued: it is untaught, and its open gap sends it
to `teach` first.
