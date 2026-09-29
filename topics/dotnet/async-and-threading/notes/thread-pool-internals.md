---
concept: thread-pool-internals
topic: dotnet
cluster: async-and-threading
created: 2026-09-20
taught: 2026-09-20
---

# Thread pool internals

## Mechanism

**Why it exists.** A thread costs ~100 µs to create and ~1 MB of reserved
address space. Most work items run for microseconds to milliseconds. A thread
per work item would spend more on setup than on work, so the pool keeps threads
alive and reuses them.

**Two levels of queue, not one:**

```
ThreadPool
│
├── GLOBAL QUEUE  (ConcurrentQueue)
│     ← Task.Run, QueueUserWorkItem, timer callbacks,
│       I/O completions, ASP.NET Core requests
│
└── LOCAL QUEUES  (one per worker thread, a double-ended queue)
      ← work queued *from inside* a pool thread lands here
```

**A worker's dispatch loop**, in order:

```
1. pop from MY local queue          ← LIFO, newest first
2. empty? dequeue from GLOBAL       ← FIFO, fairness
3. empty? STEAL from another worker ← FIFO, from the far end
4. nothing anywhere? spin, park, eventually retire
```

Both orderings are deliberate:

- **LIFO locally** — an item this thread just queued probably touches data still
  in its L1 cache. Newest-first maximises cache hits.
- **FIFO when stealing** — take from the *opposite* end of the victim's deque:
  the oldest item, the one they are least likely to run next, and the end with
  the least contention.

### Thread counts — where the misconceptions live

```
MinThreads   = processor count (default, for workers)
               Below this, a thread is created IMMEDIATELY on demand.

above Min    → INJECTION, slow and deliberate:

  • a "gate thread" wakes roughly every 500 ms, sees queued work making
    no progress, and adds a thread
      → this is exactly where "1–2 threads per second" comes from

  • hill climbing: a feedback controller measuring completions/sec
    against thread count, hunting the throughput maximum. It adds AND
    removes threads. It is not a formula.

MaxThreads   = very large. Thousands. Not a practical ceiling.
```

**The pool is not capped at core count.** `MinThreads` *defaults* to core count,
which is the floor for instant creation, not a limit. The pool will happily run
200 threads. A healthy async server sits near core count because **nothing
blocks**, so it never needs more — an outcome, not a constraint.

**What feeds the pool:** `Task.Run`, `QueueUserWorkItem`, async continuations
after an `await` (when there is no `SynchronizationContext`), timer callbacks,
I/O completions, every ASP.NET Core request.

Historically there are **two** pools — worker threads and I/O completion
threads; `ThreadPool.GetMinThreads(out workers, out io)` returns both. Since
.NET 6 the worker pool is the managed "portable thread pool", and its
heuristics were changed to inject much faster when it detects blocking `Task`
APIs specifically.

All pool threads are **background** threads; idle ones retire after a period of
inactivity.

## Failure modes

- **Starvation, with its mechanism.** `MinThreads` = 8 means the first 8
  blocking items get threads instantly. Item 9 waits for the gate thread's next
  ~500 ms tick. Queue grows, latency spikes, thread count climbs 1–2/sec, **CPU
  stays low**. The pool is behaving correctly — it was designed for short
  non-blocking items and was given blocking ones.
- **`ThreadPool.SetMinThreads` as "the fix".** It raises the instant-creation
  floor so a burst gets threads immediately instead of at 1–2/sec. It genuinely
  helps a *burst*. It does not fix sync-over-async — it buys more threads to
  block. Costs memory, and set high enough it trades starvation for
  oversubscription.
- **Long-running work on a pool thread.** A ten-minute `Task.Run` holds a pool
  thread for ten minutes. The pool cannot distinguish "long-running" from
  "blocked" and injects threads to compensate. Use
  `TaskCreationOptions.LongRunning` or a dedicated thread — see
  [[threads-and-scheduling]].
- **Deadlock by pool exhaustion.** A pool work item waiting on another pool work
  item:

  ```
  MinThreads = 8
  8 parent items, each calling .Wait() on a child Task
  → all 8 threads blocked, 8 children queued, no thread free to run them
  → the gate thread eventually injects... at 1–2/sec, if at all
  ```

  Worse: `Task.Wait` can sometimes **inline** the child if it is still in that
  thread's local queue, so it passes in testing and deadlocks in production.
  Intermittent by construction.
- **Invisible in CPU metrics.** Starvation will not show up as CPU. Look at
  `dotnet.thread_pool.thread.count` and `dotnet.thread_pool.queue.length`.
- **Assuming thread affinity.** Work stealing and continuations mean any item
  can run on any thread. `[ThreadStatic]` and thread-local state do not survive
  across an `await`.

## Trade-offs

**Pool vs dedicated thread** — the pool amortises creation and keeps cores busy;
you give up control of lifetime, priority, stack size and apartment state, and
you share the resource with everything else in the process.

**LIFO local vs FIFO global** — cache locality against fairness. LIFO means an
item at the bottom of a busy local queue can wait a long time. That unfairness
is the price of the cache hit, and work stealing is what stops it becoming
starvation.

**Hill climbing vs a fixed size** — adapts to real workloads with no tuning and
finds a genuine throughput maximum, but reacts over *seconds*, so it is bad at
bursts, which is exactly when it is noticed.

**Why not make the pool huge?** Threads cost memory and scheduler time, and
oversubscription lowers throughput. The slow growth is not a conservative
default — the pool is hunting for maximum throughput, not trying to satisfy
every queued item immediately. Different goals; it optimises for the first.

**The framing to carry into an interview:**

> The pool is tuned for **short, non-blocking** work items. Every one of its
> failure modes is a violation of that assumption — and no amount of pool
> configuration fixes a workload that blocks.

`SetMinThreads` is the right answer to "we get a burst of 200 requests at 9am
and the first 30 seconds are terrible". It is the wrong answer to "we call
`.Result` everywhere", where the only fix is to stop blocking.

## Drill — not run

Skipped at the user's request on 2026-09-29, nine days after the explanation was
given. `teach/SKILL.md` §7 says never write a note without drilling; this note is
the exception and is recorded as such rather than left looking drilled.

Consequences, so they are not discovered later: there is no evidence the
explanation landed, and no drill-miss gap rows were created — so the first real
test of this concept is its interview, with nothing recorded in advance about
where it is likely to be weak.

## Resources

## Related

[[threads-and-scheduling]] · [[parallelism-vs-concurrency]]
