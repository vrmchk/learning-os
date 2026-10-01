---
concept: parallelism-vs-concurrency
topic: dotnet
cluster: async-and-threading
created: 2026-09-19
taught: 2026-10-01
---

# Parallelism vs concurrency

## What it is

Two words often used as if they meant the same thing. They don't, and the
difference decides which tool you pick.

- **Concurrency** — several tasks *in progress* during the same period. They
  need not be running at the same instant; one can be paused while another runs.
  It is about how the program is *structured*: it does not wait for one thing
  to finish before starting the next.
- **Parallelism** — several tasks *executing at the same instant*, on
  different cores. It is about how the program *runs*, and it needs more than
  one core.

```
ONE core — concurrent, NOT parallel:
  A▓▓▓▓░░░░░░A▓▓▓░░░░░░A▓▓ done        ▓ running
     B░░░▓▓▓▓▓B░░░▓▓▓▓▓B▓▓▓ done       ░ started, not running right now
  ──────────────────────────────▶ time

TWO cores — parallel:
  core 0  A▓▓▓▓▓▓▓▓▓▓
  core 1  B▓▓▓▓▓▓▓▓▓▓
```

In both, A and B are in progress the whole time; only in the second are they
*running* at the same moment. Interview phrasing: *concurrency is dealing with
many things at once; parallelism is doing many things at once.* Matrix
multiplication across cores is parallelism; calling an API and doing other work
while it answers is concurrency.

## Using it

*So concurrency is about not waiting, and parallelism about using several
cores. How do you decide which one a job needs, and what do you write?*

Two questions about the work:

1. **CPU-bound or I/O-bound?** Busy computing, or waiting on the network, a
   disk, a database? ([[glossary#CPU-bound]], [[glossary#I/O-bound]])
2. **Does it hold a thread while in progress?** CPU work does, the whole time.
   I/O work need not — the network card or disk is doing the work, not the CPU.

| Work | Needs | What you write |
|---|---|---|
| **CPU-bound**, many items | Parallelism | `Parallel.ForEach` / PLINQ |
| **I/O-bound**, many calls | Concurrency | `async`/`await` + `Task.WhenAll` |
| CPU work that must not freeze a UI | Off the UI thread | `Task.Run` |

```csharp
// CPU-bound: 10,000 images. .NET splits the list into chunks and runs them on
// pool threads, about one per core. No threads to manage yourself.
Parallel.ForEach(images, img => Resize(img));

// I/O-bound: 10,000 API calls. Start them all, wait for all to finish.
var results = await Task.WhenAll(ids.Select(id => api.GetAsync(id)));
```

Hand-rolled threads for a batch work, but `Parallel.ForEach` already does the
chunking, the about-one-per-core sizing and the waiting — they are almost never
the answer.

`Task.WhenAll` creates no threads and makes nothing parallel by itself; it means
"finish when all of these finish". What the tasks *are* decides the outcome:
over async I/O calls it is **concurrency**, no extra threads; over
`Task.Run(...)` CPU work it is **parallelism**, each `Task.Run` occupying a pool
thread.

## Trade-offs

*So CPU-bound gets parallelism and I/O-bound gets concurrency. What does each
buy, and what does it cost?*

> **Async buys scalability** — more operations in flight on one box.
> **Parallelism buys latency** — one big job finished sooner.

- **Scalability** — how much load one machine can hold. Async lets a server keep
  thousands of requests in progress because a waiting request holds no thread.
  It does **not** make any single request faster. "I made it async so it's
  faster" is the classic wrong answer.
- Parallelism makes *one* job faster by spreading it across cores — never past
  the core count.

**Async costs:**

- **A little time on every call that actually waits.** The method must pause
  and resume: .NET allocates a small heap object remembering where it was (the
  **async state machine** — `async-state-machine`, tier 2), and when the I/O
  finishes it schedules the rest of the method back onto a pool thread. Runtime
  work per call, not generated code — so one async call is a hair *slower* than
  its blocking twin.
- **Viral.** One async method forces its callers to be async, all the way up;
  stopping halfway means `.Result` — [[glossary#Sync-over-async]].
- **Harder stack traces** — the call chain is split across continuations.

**Parallelism costs:**

- **Splitting and coordinating** — items handed out, results collected; for tiny
  items the overhead can exceed the work.
- **Bounded by core count** — 8 cores is at most ~8×, in practice less.
- **No guaranteed order**, and shared state touched from several threads needs
  protecting.

**Three ways to run a CPU batch:**

| | `Parallel.ForEach` | `Task.Run` per item + `WhenAll` | Your own `Thread`s |
|---|---|---|---|
| Threads | Pool, ≈ cores | Pool | You create and size them |
| Overhead | Splits into **chunks** — few hand-offs | **One `Task` per item** — 10,000 allocations and hand-offs | Thread creation; you write the splitting |
| Verdict | **Default for CPU batches** | Fine for a few big items, wasteful for thousands of small ones | Only when you need what a pool cannot give |

## How it works

*So async lets a box hold many waiting operations without a thread each. What
happens during an `await` that makes "no thread" possible?*

`await httpClient.GetAsync(url)`, on a pool thread:

```
1. The request is handed to the OS: "send this, tell me when the reply is in".
   The call returns immediately. Nothing waits.

2. The method has nothing to do until the reply, so it returns.
   The pool thread goes straight back to the pool and handles other work.

3. … ~200 ms of network time …
   Between 2 and 4 there is NO THREAD for this request. Not blocked,
   not sleeping — none. The network card and the OS are doing the work.

4. The reply arrives. The OS signals .NET: "that operation finished".
   .NET hands the rest of the method (the continuation) to the pool.
   Some pool thread — usually a different one — runs it.
```

The OS mechanism in step 4 is an **I/O completion port** on Windows, `epoll` on
Linux — the OS's way of telling a program "this I/O you started is done" instead
of the program sitting and waiting. .NET uses it; you never call it.

**Why 500 concurrent HTTP calls need only ~8 threads.** A thread is needed only
for the *short* bursts of real work — issuing the request (step 1) and running
the continuation (step 4), microseconds each. During the 200 ms between, nobody
holds a thread. That is why the count stays low — not because the pool is
"capped at core count" (it isn't), but because **no thread is held while
waiting**.

**What the numbers mean.** By [[glossary#Little's Law]] — in flight = arrival
rate × time each takes — 500 requests/s at 200 ms means **100 in flight**,
always. Traffic fixes that number; async changes what one costs:

| | Blocking | Async |
|---|---|---|
| A waiting request is | an OS thread | a small heap object |
| Memory | ~8–32 KB stack + kernel object | ~100–300 bytes |
| Threads for 100 in flight | 100 | ≈ 8, for the CPU bursts |

Async made no request faster and removed no CPU work. It made *waiting* almost
free — the whole scalability argument.

## Where it breaks

*So async makes waiting nearly free, and parallelism puts several cores to work.
What goes wrong with each, and which bugs need which?*

**1. "Races need several cores" — false.** A **race condition** is a bug where
the result depends on the exact timing of two operations touching the same data.
It needs only **concurrency**. `count++` is three steps — load, add, store — and
on **one core** the OS can take the core away between any two:

```
Thread A: load count (5)
          ── A's time slice ends, B gets the core ──
Thread B: load count (5) → add → store 6
          ── A gets the core back ──
Thread A: add → store 6        ← B's update lost. Two increments, +1.
```

Nothing ran in parallel; they *interleaved*. Async code has the same bug when an
`await` sits between reading shared state and writing it back.

**2. "Deadlocks need several cores" — false.** Two threads on one core deadlock
fine: A holds lock 1 wanting lock 2, B holds lock 2 wanting lock 1.
Sync-over-async can deadlock with **one** thread — blocked on `.Result` while the
code that would complete it can only run on that same blocked thread
(`async-deadlocks`, tier 2).

**3. What several cores *add* — memory visibility.** With several cores, each can
hold a write in its own small pending-writes buffer for a moment, and the CPU may
reorder reads and writes for speed. So core 1 can read a value core 0 *already
wrote* and still see the old one — a **memory visibility** bug. Impossible on
one core; it is what `volatile`, `Interlocked` and memory barriers exist for
(`interlocked-and-cas`, tier 1; the Concurrency cluster).

Concurrency brings races and deadlocks; parallelism **adds** visibility bugs.

**4. Unbounded concurrency.** `await Task.WhenAll(urls.Select(GetAsync))` over
**10,000 URLs** won't explode the thread count — it opens 10,000 requests to the
downstream *at once* and can take it down. Blocking code was limited by accident
(you ran out of threads); async removes that brake, so **limiting concurrency is
your explicit job**:

```csharp
await Parallel.ForEachAsync(urls,
    new ParallelOptions { MaxDegreeOfParallelism = 50 },   // at most 50 at once
    async (url, ct) => await http.GetAsync(url, ct));
```

`SemaphoreSlim` does the same by hand (tier 1); bounded concurrency is its own
concept, `task-whenall-and-bounded-concurrency` (tier 2).

**5. The wrong tool each way.**
`Parallel.ForEach(urls, u => Download(u).Result)` — parallelism on I/O: a pool
thread per item *and* blocked; chunking overhead plus starvation.
`async Task<int> Compute() => Heavy();` — no `await`, runs synchronously, blocks
the caller as before; `async` moves nothing off the thread.

**6. Expecting 8× from 8 cores.** The unsplittable parts, coordination and
memory bandwidth eat into it fast. "How much faster?" is a number you measured.

## In practice

*So concurrency needs an explicit limit and parallelism is capped by cores. A
batch job that needs both — with the numbers.*

**Situation.** Nightly job: **10,000 records**; each needs a **50 ms DB read**
(I/O) then a **20 ms transform** (CPU). **8 cores.** Plain `foreach` today:
12 minutes.

1. **Check the current number.** 10,000 × 70 ms = 700 s ≈ **11.7 min** — matches
   the 12 minutes, so the model is right.
2. **Find the floors.**
   - **CPU floor:** 10,000 × 20 ms = 200 core-seconds; on 8 cores **25 s
     minimum**. Nothing on this box beats that.
   - **I/O:** 500 s of *waiting*, but waits overlap — with `k` reads in flight,
     500 / k s; k = 20 also gives 25 s.
   - Target **≈ 25 s**, set by the CPU.
3. **One tool, sized with arithmetic.**

   ```csharp
   await Parallel.ForEachAsync(records,
       new ParallelOptions { MaxDegreeOfParallelism = 28 },
       async (r, ct) =>
       {
           var row = await db.GetAsync(r.Id, ct);   // waits without a thread
           Transform(row);                          // 20 ms of CPU
       });
   ```

   Each item ≈ 70 ms, so N in flight complete **N / 0.07 per second**, using
   (N / 0.07) × 0.02 ≈ **0.29 × N cores**. That reaches 8 cores at **N ≈ 28**:
   below, CPU sits partly idle; above, the CPU part just queues. At N = 28:
   400 records/s → **25 s. 12 minutes → ~25–30 s, about 25×.**
4. **Price it.**

| Cost | Detail |
|---|---|
| Database load | ~28 queries at once instead of 1 — check the DB, and the connection pool (SqlClient defaults to 100) |
| Memory | ~28 rows in flight; unbounded `WhenAll` would load all 10,000 |
| Order | No fixed completion order — fine for a batch, wrong if downstream expects order |
| Failures | `Parallel.ForEachAsync` stops starting new items after the first exception and rethrows — decide: stop the run, or log and skip |

Not worth it here: a separate I/O stage and CPU stage (a pipeline) — same 25 s
floor, more moving parts.

**What the interviewer listens for:** the current number checked by arithmetic,
the floor and which resource sets it, the limit sized from the numbers rather
than guessed, and the speed-up priced in database load.

## Drill — 2026-09-20

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | 500 URLs via `Task.WhenAll(urls.Select(u => http.GetAsync(u)))` on an 8-core box, ~200 ms each, no CPU. Concurrency, parallelism, or both? How many threads, and why that number? | Said concurrency, and ~8 threads — both right. Both *reasons* wrong: gave "we do not create threads on our own explicitly" as the criterion (`Task.Run` does not either), and "up to 8 because 8 cores" as a cap. The pool grows well past core count; the count stays low because no thread is held during the wait, only for issuing and resuming. | miss |
| 2 | 10,000 records, each one ~50 ms DB call plus ~20 ms CPU transform, 8 cores, currently a serial `foreach` taking 12 minutes. Restructure it, and say what each part buys. | Design correct and unaided: separate I/O from CPU, batch rather than one-at-a-time, async for the DB calls, cap CPU parallelism at core count. `SemaphoreSlim` named — the right tool for the I/O bound specifically; `Parallel.ForEachAsync` with `MaxDegreeOfParallelism` fits the CPU side better. Second clause unanswered: no payoff quantified. 10,000 x 20 ms = 200 core-seconds / 8 = ~25 s floor; I/O 500 s serial to ~5 s at 100 concurrent; 12 min to ~30 s with CPU binding. | hit |
| 3 | Mid-request `await httpClient.GetAsync(url)`, ~200 ms. What happens to the calling thread, what executes the operation, what causes resumption? | Declined, on the grounds that the async state machine had not been taught. The walk itself *was* taught in this session's "There is no thread" section; the compiler's construction of the state machine was not, and was not asked for — that is `async-state-machine`, tier 2 row 7. | miss |

Drill results do not change a level.

## Drill — 2026-10-01

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `await Task.WhenAll` over 500 HTTP calls, 8 cores, ~200 ms of pure waiting each. Concurrency or parallelism? Roughly how many threads, and why? | Concurrency. Each request's thread returns to the pool while waiting and the continuation finishes on another pool thread — the right reason. Led with the pool's growth rules (instant up to 8, then 1–2/sec), which are not why the count stays low. | hit |
| 2 | 10,000 small CPU items (~2 ms) on 8 cores: `Parallel.ForEach`, `Task.Run` per item + `WhenAll`, or your own threads — which, and what do the other two cost? | Picked `Parallel.ForEach` at about core count. Said `Task.Run` per item would be blocking code that keeps the pool injecting threads into oversubscription — it does not block; its cost is one `Task` per item (10,000 allocations and hand-offs, no chunking). Said all three use the pool — own threads do not; their cost (creation, splitting and joining by hand) not given. | miss |
| 3 | Single-core container, two concurrent requests do `counter++` on a shared static. Can an update be lost — how exactly? What new bug class appears on 8 cores? | Yes, lost — described only as one request reading the value before the other finished writing; no load/add/store and no preemption between the steps. For 8 cores: parallel threads accessing the same heap data, so use locks and beware deadlocks — the same race class again; memory visibility not named. | miss |

Drill results do not change a level.

## Model answers — 2026-10-01

### Q2 (2026-09-30) — target L4, awarded L1

*"Our service runs on a single-core container, so we don't need to worry about race conditions on shared counters." Right or wrong — and what class of bug does 8 cores add?* — [[2026-09-30-async-and-threading-tier-1]]

> Wrong — a race needs concurrency, not parallelism. `count++` is load, add,
> store; on one core the scheduler can preempt a thread between any two of
> those, another thread runs the whole increment, and when the first resumes it
> stores a stale value — one update lost, nothing ran in parallel. Async has the
> same bug when an `await` sits between reading and writing. What 8 cores adds
> is memory visibility: a write can sit in one core's store buffer or be
> reordered, so another core reads the old value after it was written — a class
> that cannot happen on one core, and what `volatile`, `Interlocked` and
> barriers are for. Deadlocks, by contrast, need no second core at all.

Missing from the graded answer: load/add/store with preemption between steps;
memory visibility as the multicore-only class; that deadlocks need no second
core.

### Q3 (2026-09-30) — target L4, awarded L2

*Rung 3: "I made the endpoint async, so now it's faster." What does async actually buy, and what does it cost?* — [[2026-09-30-async-and-threading-tier-1-2]]

> Not faster — usually a hair slower. Each async call that actually waits
> allocates a state machine and a `Task`, and its continuation has to be
> scheduled back onto a pool thread when the I/O completes. What it buys is
> scalability: while the request waits it holds no thread, so one box can have
> far more requests in flight. The other costs are structural — it's viral, one
> async call forces async all the way up, and stack traces get harder to read.
> Worth it for I/O-bound endpoints under load; pointless for CPU-bound work.

Missing from the graded answer: the runtime cost (allocation plus continuation
scheduling) rather than "generated code"; viral async; stack traces.

## Resources

## Related

[[threads-and-scheduling]] · [[thread-pool-internals]]
