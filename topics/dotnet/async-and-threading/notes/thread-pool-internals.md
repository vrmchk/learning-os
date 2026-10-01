---
concept: thread-pool-internals
topic: dotnet
cluster: async-and-threading
created: 2026-09-20
taught: 2026-10-01
---

# Thread pool internals

## What it is

Creating a thread is expensive — the OS sets up its record and stack, ~100 µs.
Most work in a .NET app is tiny by comparison: handling one request, running
the code after an `await`, firing a timer callback. A thread per job would
spend more on setup than on work.

The **thread pool** is .NET's answer: a set of threads created once, kept
alive, and **reused**. You hand the pool a job; one of its existing threads runs
it; when the job is done the thread goes back and takes the next one.

The pool also decides **how many threads exist**, growing and shrinking that
number itself, aiming for the most work done per second. There is one per
process, shared by everything in it.

## Using it

*So the pool is a shared set of reusable threads. Where does the work it runs
come from?*

Mostly from things you did not explicitly send there:

- **Every ASP.NET Core request** runs on a pool thread.
- **The code after an `await`.** Calling an async method does *not* put
  anything on the pool. The call runs immediately, on the caller's thread, up
  to the first `await` that actually has to wait. When that operation finishes,
  the rest of the method — its **continuation**, "the code after the `await`" —
  is handed to the pool.

  ```csharp
  public async Task<Order> GetOrder(int id)
  {
      Log("start");                        // caller's thread, immediately
      var row = await db.QueryAsync(id);   // starts the query, then returns
      return Map(row);                     // ← continuation: runs on a POOL thread
  }                                        //   when the query completes
  ```

  In ASP.NET Core that is the whole story. Desktop UI apps can send
  continuations back to the UI thread instead —
  `synchronization-context-and-configureawait`, tier 2.
- **Timer callbacks** — `System.Threading.Timer`, `PeriodicTimer` ticks.
- **I/O completions** — the "your network read finished" notifications that
  wake those continuations.

Sent explicitly:

```csharp
Task.Run(() => Compute());                      // most common
ThreadPool.QueueUserWorkItem(_ => Compute());   // the old, low-level way
Task.Factory.StartNew(() => Compute());         // pool too...
Task.Factory.StartNew(Loop, TaskCreationOptions.LongRunning);  // ...except this: own thread
```

So an API where nobody writes `Task.Run` still keeps the pool busy constantly:
every request, every resumed `await`, every timer.

## Trade-offs

*So almost everything in a .NET app runs on the pool. What does that sharing
cost, and when is it the wrong tool?*

Each job handed to the pool is a **work item**.

**Gives you:** no per-job creation cost; roughly the right number of threads
without choosing one; one shared set for every library and framework, so the
machine is not flooded with threads.

**Costs** (facts here; *why* in the next layer):

- **Shared.** A work item that blocks a pool thread takes that thread from
  everyone in the process.
- **Assumes items are short and non-blocking.** Everything about how it grows is
  tuned for that.
- **Grows slowly.** Not capped — it can run hundreds of threads — but past a
  starting number, **MinThreads** (by default about the core count), it adds
  threads gradually, ~1–2 per second, not on demand.
- **No control** over which thread runs your item, its priority, its stack
  size, or the order items run in.

| Work | Use instead | Why |
|---|---|---|
| Runs for minutes, or forever | `LongRunning` or your own `Thread` | Would occupy a pool thread permanently |
| Needs one specific thread (driver, STA) | Your own `Thread` | The pool picks any thread |
| Waits on I/O | `await` — not `Task.Run` + blocking | Waiting needs no thread at all |

`ThreadPool.SetMinThreads(n)` raises the starting number, so up to `n` threads
are created immediately instead of 1–2 per second. It helps a sudden burst; it
does **not** fix code that blocks.

## How it works

*So the pool is shared, assumes short jobs, and grows slowly past MinThreads.
How does it decide which thread runs which item, and when to add threads?*

```
ThreadPool
├── GLOBAL QUEUE        ← Task.Run from outside the pool, timers,
│                         I/O completions, incoming requests
└── LOCAL QUEUE per worker thread
                        ← work queued *by code already running on that
                          pool thread* (e.g. Task.Run inside a pool job)
```

A **local queue** belongs to one pool thread. Work it creates goes there first,
because the data that work needs is probably still in that core's
[[glossary#Cache]].

How a pool thread picks its next item:

```
1. take the NEWEST item from my own local queue      (cache still warm)
2. empty? take the OLDEST item from the global queue (fairness)
3. empty? STEAL the oldest item from another thread's local queue
4. nothing anywhere? wait a bit; eventually the thread retires
```

**Work stealing** is step 3: an idle thread takes work from a busy thread's
local queue, so no queue sits full while threads are idle.

How the thread count changes:

```
up to MinThreads (≈ cores)  → a new thread is created immediately when needed
above MinThreads            → a background monitor checks about every 500 ms:
                              "is queued work making no progress?" → add one
                              → hence "1–2 threads per second"
MaxThreads                  → thousands; not a practical limit
```

On top of that, **hill climbing**: the pool keeps measuring *items completed
per second* while nudging the thread count up or down, and settles where
throughput is highest — a feedback loop, not a formula, which is why it reacts
over *seconds*.

So the pool is not limited to core count. Core count is where *instant*
creation stops. A healthy async server sits near core count because nothing
blocks, so it never *needs* more — an outcome, not a cap.

## Where it breaks

*So the pool grows slowly on purpose, tuned for short non-blocking items. What
happens when the work it is handed is not like that?*

Every failure here has one root cause: **a work item holding its pool thread
for a long time**, usually by blocking.

**1. Starvation from sync-over-async.** **Sync-over-async** — calling async code
and then blocking on its result: `.Result`, `.Wait()`,
`.GetAwaiter().GetResult()`.

```
MinThreads = 8
1. 8 requests call .Result on a 500 ms HTTP call → 8 threads BLOCKED
2. Request 9 waits in the global queue — no free thread
3. Monitor adds a thread every ~500 ms; each picks up a request,
   calls .Result, blocks too
4. Queue grows faster than threads are added
→ CPU low, thread count climbing 1–2/sec, latency in seconds
```

The pool is doing what it was designed to do: it cannot tell "blocked" from
"busy", so it adds threads cautiously. **Fix: don't block** — `await` all the
way, so the thread returns to the pool while the call is in flight.

**2. `SetMinThreads` as "the fix".** For a blocking app it only buys **more
threads to block** — the curve looks better until traffic grows again. Costs
memory; set too high, it trades starvation for oversubscription. Right for a
*burst*, wrong for blocking code.

**3. Long-running work on the pool.** A 10-minute `Task.Run` or a
`while (true)` consumer holds a pool thread permanently. The pool cannot tell
"long" from "blocked", sees a thread that never returns, and injects more to
compensate. Fix: `TaskCreationOptions.LongRunning` or your own thread
([[threads-and-scheduling]]).

**4. Deadlock by pool exhaustion.** A pool item waiting on *another* pool item:

```
8 parent items, each .Wait()s on a child Task it just queued
→ 8 pool threads blocked waiting for children
→ the 8 children sit in the queues with no free thread to run them
→ nothing moves until the monitor adds threads — slowly, or never
```

`.Wait()` sometimes runs the child *inline* when it is still in the same
thread's local queue — so it passes in testing and hangs under production load.

**5. Invisible on a CPU graph.** Starvation shows as *low* CPU, so CPU alerts
never fire. The pool's **counters** — live numbers .NET publishes about itself,
read with `dotnet-counters` (performance cluster) — show it:
`dotnet.thread_pool.queue.length` rising (work waiting) and
`dotnet.thread_pool.thread.count` climbing under a flat workload.

**6. Assuming you stay on one thread.** After an `await`, or when work is
stolen, code may run on any pool thread. `[ThreadStatic]` fields and other
per-thread state do not follow you across an `await`.

## In practice

*So the root cause is always an item holding its thread, and `SetMinThreads`
fixes the ramp, not the blocking. Two services with the same symptom and
different answers.*

Both on 8 cores (MinThreads ≈ 8). Both page: *"slow in the morning, CPU low"*.

**Service A** — traffic jumps from near zero to **400 requests/s at 09:00**.
Each request makes a **100 ms call through a legacy synchronous DB driver**
(no async version yet), so it genuinely blocks. The first ~30 s are terrible,
then fine.

- Threads needed ([[glossary#Little's Law]]): 400/s × 0.1 s = **~40 blocked at
  any moment**.
- From 8 at 1–2 per second, reaching 40 takes **~16–32 s** — the bad 30
  seconds. Then it has enough and recovers.
- **Diagnosis:** a *burst* outrunning slow injection. Queue length spikes then
  drains; thread count climbs then **plateaus around 40**.
- **Fix:** `ThreadPool.SetMinThreads(48, …)` — created instantly. **Cost:** ~40
  more mostly-blocked threads, a few MB of real memory, harmless at this size.
  Long term, an async driver drops the need to about core count.

**Service B** — same 400 requests/s, but every handler calls `.Result` on a
**500 ms HTTP call**. Slow in the morning and **never recovers** while traffic
is high.

- Threads needed: 400/s × 0.5 s = **~200 blocked**.
- At 1–2 per second, **2–3 minutes** to get there, and any spike outruns it
  again. Thread count **keeps climbing**; the queue never drains.
- **Diagnosis:** sync-over-async starvation. Confirm with a dump of the process
  (`dotnet-dump`, performance cluster): hundreds of stacks sitting in `.Result`.
- **Wrong fix:** `SetMinThreads(200)` — works until traffic doubles, 200 threads
  doing nothing but wait, and the bug hidden.
- **Right fix:** `await` all the way up. Same 400 requests/s then needs about
  **8 threads** — nothing holds a thread while waiting.

**What the interviewer listens for:** pool counters before a cause (CPU is low
in both); **plateau vs keeps climbing** to tell burst from blocking;
`SetMinThreads` right for A, wrong for B, with the thread arithmetic.

## Drill — not run

Skipped at the user's request on 2026-09-29, nine days after the explanation was
given. `teach/SKILL.md` §7 says never write a note without drilling; this note is
the exception and is recorded as such rather than left looking drilled.

Consequences, so they are not discovered later: there is no evidence the
explanation landed, and no drill-miss gap rows were created — so the first real
test of this concept is its interview, with nothing recorded in advance about
where it is likely to be weak.

## Drill — 2026-10-01

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | ASP.NET Core action: `await http.GetStringAsync(url)`, then `Parse`, then `Ok`. Which parts run on a pool thread, and which thread is busy during the HTTP call? | The request starts on a pool thread; at the `await` that thread returns to the pool to take other requests; when the call completes, some pool thread picks the rest up. Correct — no thread is held during the call. | hit |
| 2 | When is `ThreadPool.SetMinThreads` the right call, when the wrong one, and what does it cost? | Right for short bursts that do not keep climbing. Said to set it "not far from core count" — it is sized to the need (rate × blocking time; ~48 for ~40 blocked on 8 cores). Did not name blocking / sync-over-async code as the case where it is wrong. Costs given as oversubscription, memory and context switches — oversubscription only if the extra threads compute. | miss |
| 3 | 8 pool items each queue a child `Task` and `.Wait()` on it, MinThreads 8. What happens, and why can it pass tests and hang in production? | Named deadlock and that `.Wait()` can run the child from the local queue in testing. Mechanism stated only as "threads waiting for each other" — not that all 8 pool threads are blocked while the children sit queued with no free thread to run them, released only by slow injection. | miss |

Drill results do not change a level.

## Model answers — 2026-10-01

### Q1 (2026-09-30) — target L5, awarded L1

*Rung 2: in everyday .NET code, what actually puts work onto the thread pool?* — [[2026-09-30-async-and-threading-tier-1-2]]

> Mostly things you don't queue yourself. Every ASP.NET Core request runs on a
> pool thread. Every `await` that actually suspends resumes its continuation on
> a pool thread when the I/O completes — the call itself runs synchronously on
> the caller's thread up to that point. Timer callbacks and I/O completion
> callbacks run there too. Explicitly, `Task.Run`, `Task.Factory.StartNew` and
> `ThreadPool.QueueUserWorkItem` queue onto it — except `StartNew` with
> `LongRunning`, which gets its own thread.

Missing from the graded answer: the continuation, not the call, as the pool
work; timer callbacks and I/O completions; the `LongRunning` exception.

## Resources

## Related

[[threads-and-scheduling]] · [[parallelism-vs-concurrency]]
