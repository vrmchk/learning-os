---
concept: parallelism-vs-concurrency
topic: dotnet
cluster: async-and-threading
created: 2026-09-19
taught: 2026-09-20
---

# Parallelism vs concurrency

## Mechanism

Not synonyms, and the distinction is the whole concept:

- **Concurrency** — multiple operations **in progress** over overlapping time
  windows. A property of program *structure*. Needs no second core.
- **Parallelism** — multiple operations **executing at the same instant** on
  different cores. A property of *execution*. Requires more than one core.

The framing interviewers quote (Rob Pike): concurrency is about dealing with
many things at once; parallelism is about doing many things at once.

```
ONE core — concurrent, NOT parallel:
  A▓▓▓▓░░░░░░░A▓▓▓░░░░░░░░A▓▓▓ done      ▓ running
       B░░░▓▓▓▓▓B░░░▓▓▓▓▓▓▓B▓▓▓ done      ░ in progress, not running
  ──────────────────────────────▶ time

TWO cores — parallel:
  core0  A▓▓▓▓▓▓▓▓▓▓▓▓
  core1  B▓▓▓▓▓▓▓▓▓▓▓▓
```

A and B are *in progress* throughout in both. Only the second has them
*running* simultaneously.

### The two questions that decide the tool

1. Is the work **CPU-bound** or **I/O-bound**?
2. Does it **hold a thread** while in progress?

| Work | Holds a thread while in progress? | Tool |
|---|---|---|
| CPU-bound | **Yes**, the whole time — something must execute instructions | threads, thread pool, `Parallel` |
| I/O-bound | **No** — the device is working, not the CPU | `async`/`await` |

### "There is no thread"

```
await httpClient.GetAsync(url);

1. The call hands the request to the OS — overlapped I/O registered with
   a completion port (Windows), or epoll/io_uring (Linux). Returns
   immediately. Nothing waits.

2. The compiler-generated state machine returns control to the caller.
   The pool thread that ran the method goes back to the pool and runs
   other work.

3. ... network latency, say 200 ms ...
   NIC receives bytes → kernel → completion queued → the pool picks a
   thread and resumes the state machine at MoveNext().

Between 2 and 3 there is NO THREAD for this operation. Not blocked, not
sleeping. None. The network card and kernel are doing the work.
```

This is why 10,000 concurrent HTTP calls need ~8 threads while 10,000
concurrent *blocking* HTTP calls need 10,000.

### `Task.Run` and `await` are opposites

- **`Task.Run(f)`** — *occupies* a pool thread while `f` runs.
- **`await SomethingAsync()`** — *releases* the thread for the duration of the
  wait.

**`Task.Run` does not allocate a thread.** It queues a work item to the pool.
An idle pool thread picks it up; if none is idle the pool may inject one at its
own pace (~1–2/sec after the initial burst), or the item simply waits.
`Task.Factory.StartNew(..., TaskCreationOptions.LongRunning)` is the one that
hints for a dedicated thread.

Occupying a thread is a **precondition** for parallelism, not parallelism
itself. Whether parallelism results depends on several items running at once on
several cores — one `Task.Run` on a single-core box is concurrency and nothing
more.

`async` by itself creates **no thread and no parallelism**. It is a way of not
holding a thread, nothing more.

### Parallelism in .NET

- `Parallel.For` / `Parallel.ForEach` / PLINQ — data parallelism, partitions
  items across pool threads.
- `Task.WhenAll` over **CPU-bound** `Task.Run` calls — task parallelism.
- `Task.WhenAll` over **I/O-bound** async calls — **concurrency, not
  parallelism**. No extra threads. A favourite interview probe.

`Task.WhenAll` is a **combinator, not a scheduling mechanism**: it completes
when N tasks complete and has no opinion about threads. What the tasks *are*
decides the outcome. For CPU-bound work `Parallel.ForEach`/PLINQ generally beat
`WhenAll` + `Task.Run`, because they partition into chunks instead of
allocating a `Task` per item.

### How async actually scales

Little's Law: `operations in flight = arrival rate x latency`. At 500 rps and
200 ms, 100 operations are in flight at any moment. Traffic fixes that number.
The only question is what one in-flight operation costs.

| | Blocking | Async |
|---|---|---|
| Represented by | an OS thread | a state-machine object |
| Address space | ~1 MB | 0 |
| RAM | 8–32 KB stack + kernel object | ~100–300 bytes of heap |
| Kernel object | yes | no |
| Scheduler entry | yes | no |
| Created in | ~100 µs, pool injects 1–2/sec | an allocation |

**Async decouples operations-in-flight from thread count.** The cost of holding
a paused operation falls ~4 orders of magnitude, moving the limit off an
expensive OS resource onto a cheap one. At 10,000 in flight: blocking needs
10,000 threads (~10 GB address space, unreachable anyway at 1–2 injections/sec);
async needs ~2 MB of state machines plus enough threads for the CPU slices —
if each request is 200 ms waiting and 1 ms CPU, ~8 threads cover it.

What did **not** change: total CPU work, and the latency of any single request.
Async buys the ability to *hold* 10,000 operations, not to finish one sooner.

## Failure modes

- **"I made it async so it's faster."** Async makes a single operation
  marginally **slower** — state-machine allocation and completion dispatch. It
  improves **scalability**, how many operations one box holds in flight, never
  the latency of one. Saying "faster" is a tell.
- **`async` on CPU-bound work.** `async Task<int> Compute() => Heavy();` — no
  `await`, so it runs synchronously and blocks the caller exactly as before.
  The compiler warns. Marking a method `async` offloads nothing.
- **Parallelism applied to I/O.** `Parallel.ForEach(urls, u => Download(u).Result)`
  occupies a pool thread per item *and* blocks each one: partitioning overhead
  plus starvation. Worst of both tools.
- **Unbounded concurrency mistaken for free.**
  `await Task.WhenAll(urls.Select(GetAsync))` over 10,000 URLs will not explode
  the thread count, but it opens 10,000 simultaneous connections and takes down
  the downstream. Concurrency is **unbounded by default**; bounding it is a
  separate explicit decision. See `task-whenall-and-bounded-concurrency`.

  Bound it with a semaphore — the waiters hold no thread:

  ```csharp
  using var gate = new SemaphoreSlim(50);
  var tasks = urls.Select(async u =>
  {
      await gate.WaitAsync();
      try     { return await http.GetAsync(u); }
      finally { gate.Release(); }
  });
  await Task.WhenAll(tasks);
  ```

  Or, .NET 6+ and now idiomatic:
  `Parallel.ForEachAsync(urls, new ParallelOptions { MaxDegreeOfParallelism = 50 }, ...)`.

  Worth remembering **why** this is a trap: blocking code was bounded *by
  accident* — you ran out of pool threads and stalled. Async deletes that
  accidental safety rail, because operations became nearly free. The same
  cheapness that makes async scale is what makes bounding a deliberate act.
- **Assuming races need parallelism.** False and dangerous. **Concurrency** is
  necessary and sufficient for a race. On one core two concurrent operations
  still interleave at uncontrolled points — preemption can land between any two
  instructions, and `i++` is load/add/store. Single-core machines have races.
  Parallelism does not remove a race class, it **adds** one: memory-visibility
  races, where core 1 reads a value core 0 already wrote because the write sits
  in a store buffer or was reordered. That class cannot occur on one core, and
  it is what `volatile`, `Interlocked` and barriers exist for.
- **Assuming deadlocks need parallelism.** Two threads on one core deadlock
  fine — A holds L1 wanting L2 while B holds L2 wanting L1. The Coffman
  conditions say nothing about cores. The sync-over-async deadlock needs only
  **one** thread: it blocks on `.Result` while the continuation that would
  complete it can run only on that same blocked thread.
- **Expecting linear speedup.** 8 cores almost never gives 8x. Serial fraction,
  coordination, memory bandwidth and cache contention dominate quickly. The
  honest answer to "how much faster" is "measure it".

## Trade-offs

| Situation | Reach for |
|---|---|
| Waiting on network, disk, or a database | `async`/`await` |
| CPU work that must not block a UI thread | `Task.Run` |
| Many independent CPU items, want throughput | `Parallel.ForEach` / PLINQ |
| Many I/O operations, want them overlapped | `Task.WhenAll` **plus a bound** |
| A loop running for the process lifetime | dedicated `Thread` — see [[threads-and-scheduling]] |

**Costs:**

- **async** — a state-machine allocation per call that actually suspends (none
  when it completes synchronously, which is what `ValueTask` exists for), worse
  stack traces, and it is viral: one async leaf forces async all the way up.
- **parallelism** — partitioning and coordination overhead, non-deterministic
  ordering, false sharing, harder testing. **Bounded by core count**, so it
  cannot scale past the box.

**The framing that answers the interview question:**

> Async buys **scalability** — more operations in flight per box.
> Parallelism buys **latency** — one job finished sooner.

Different goals; using async hoping for speed, or parallelism hoping for scale,
is the error in each direction. When the work is I/O-bound async wins outright,
because parallelism has nothing to parallelise.

**When not to use async:** very short operations where the machinery costs more
than the wait, CPU-bound work, and one-shot console tools where scalability is
meaningless.

## Drill — 2026-09-20

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | 500 URLs via `Task.WhenAll(urls.Select(u => http.GetAsync(u)))` on an 8-core box, ~200 ms each, no CPU. Concurrency, parallelism, or both? How many threads, and why that number? | Said concurrency, and ~8 threads — both right. Both *reasons* wrong: gave "we do not create threads on our own explicitly" as the criterion (`Task.Run` does not either), and "up to 8 because 8 cores" as a cap. The pool grows well past core count; the count stays low because no thread is held during the wait, only for issuing and resuming. | miss |
| 2 | 10,000 records, each one ~50 ms DB call plus ~20 ms CPU transform, 8 cores, currently a serial `foreach` taking 12 minutes. Restructure it, and say what each part buys. | Design correct and unaided: separate I/O from CPU, batch rather than one-at-a-time, async for the DB calls, cap CPU parallelism at core count. `SemaphoreSlim` named — the right tool for the I/O bound specifically; `Parallel.ForEachAsync` with `MaxDegreeOfParallelism` fits the CPU side better. Second clause unanswered: no payoff quantified. 10,000 x 20 ms = 200 core-seconds / 8 = ~25 s floor; I/O 500 s serial to ~5 s at 100 concurrent; 12 min to ~30 s with CPU binding. | hit |
| 3 | Mid-request `await httpClient.GetAsync(url)`, ~200 ms. What happens to the calling thread, what executes the operation, what causes resumption? | Declined, on the grounds that the async state machine had not been taught. The walk itself *was* taught in this session's "There is no thread" section; the compiler's construction of the state machine was not, and was not asked for — that is `async-state-machine`, tier 2 row 7. | miss |

Drill results do not change a level.

## Resources

## Related

[[threads-and-scheduling]]
