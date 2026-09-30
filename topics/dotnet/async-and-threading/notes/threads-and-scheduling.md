---
concept: threads-and-scheduling
topic: dotnet
cluster: async-and-threading
created: 2026-09-18
taught: 2026-10-01
---

# Threads and scheduling

## What it is

When a program runs, something has to execute its instructions one after
another — call this method, then that one, remember where to return to. A
**thread** is one such line of execution. A program can have many threads,
each working through its own code, so it can do several things at once or keep
going while one part waits.

Each thread needs its own scratch space — its local variables and the chain of
"which method called which, and where to return". That is the **stack** from
the GC topic ([[stack-vs-heap-layout]]); every thread has its own.

Threads belong to the **operating system**, not to .NET. A
`System.Threading.Thread` is a thin wrapper around exactly one OS thread — one
to one. That is why creating one is relatively expensive: you are asking the OS
to set up a real thread.

The OS also decides **when** each thread runs. A machine has a few **cores**
(the parts of the CPU that actually execute instructions), usually far fewer
than there are threads. The OS **scheduler** decides which thread gets a core
now and for how long. Not .NET, and not the thread pool — the pool only decides
which *job* goes to which of its threads; when that thread gets a core is the
OS's call.

## Using it

*So a thread is something the OS runs your code on. Where do you meet threads
in everyday .NET code?*

Mostly you don't create them — they are already there:

- Every ASP.NET Core request runs on a thread from the **thread pool**, a set of
  threads .NET keeps alive for reuse ([[thread-pool-internals]]).
- `Task.Run(...)` hands a job to the pool; one of its threads runs it.

Creating a thread yourself is rare and deliberate:

```csharp
var worker = new Thread(ProcessQueueForever) { IsBackground = true };
worker.Start();
```

- **Foreground or background.** A `new Thread` is **foreground** by default —
  the process will not exit until it finishes. **Background** threads (every
  pool thread, every `Task.Run`) are killed immediately when the process exits:
  no `finally`, no cleanup.
- **You cannot kill a thread from outside.** On .NET Core `Thread.Abort` throws
  `PlatformNotSupportedException`. The only way to stop a thread is to *ask* it,
  and its own code must check the request — normally a `CancellationToken`
  ([[cancellation-tokens]], tier 2).

So a thread you own is normally **background + a cancellation token + a short
bounded wait on shutdown**: it neither holds the process open nor gets killed
mid-write.

**PLINQ does not give you a dedicated thread.** It splits the data into chunks
and runs them on *pool* threads.

## Trade-offs

*So the pool usually gives you a thread, and occasionally you create one. When
is creating your own right, and what does each option cost?*

A thread is **blocked** when it waits for something — a network response, a
lock, `Thread.Sleep`, `.Result` — and cannot continue until it arrives. A
blocked thread uses no CPU but still exists and still holds everything a thread
holds.

| | Your own `Thread` | Thread pool | `async`/`await` |
|---|---|---|---|
| **Good for** | Work tied to one specific thread, or running forever | Short jobs, CPU work | Waiting on I/O — network, disk, DB |
| **Costs** | ~100 µs to create; ~1 MB **reserved address space**; you own its lifetime and shutdown | Shared with the whole process — block one of its threads and everyone slows | A small heap object per call that waits; async "all the way up" |

**Reserved address space** — a range of memory *addresses* set aside for the
stack. Not 1 MB of RAM; why, in the next layer.

**When your own thread genuinely wins.** "Heavy CPU work" is the weak answer —
the pool handles CPU jobs fine. The real cases involve something tied to **the
thread itself**, or work that never ends:

1. **Thread affinity** — a native library (hardware driver, OpenGL, some native
   DB drivers) requires every call from the same OS thread. After an `await`
   you don't control which thread you're on, so async cannot do this at all.
2. **COM / STA** — COM is an old Windows component technology still behind
   Office automation and some Windows APIs; STA is its rule that an object may
   only be called from the thread that created it. The thread is marked before
   it starts: `t.SetApartmentState(ApartmentState.STA)`. WinForms and WPF UI
   threads are STA. Rare in backend code.
3. **A custom stack size** — deep recursion that would overflow 1 MB:
   `new Thread(Parse, 16 * 1024 * 1024)`.
4. **A loop for the whole life of the process** — a queue consumer, or a
   **device poller** (a loop that asks a device "anything new?" every few
   milliseconds, forever — a scale, a scanner, a sensor). On the pool it would
   occupy a pool thread permanently.
5. **A third-party SDK with no async API that blocks for minutes** — it will
   block somewhere; better on a thread you own than one the pool needs.
6. **Priority** — belongs to a thread, not a `Task`.

**Middle path:** `Task.Factory.StartNew(work, TaskCreationOptions.LongRunning)`
asks .NET for a dedicated thread instead of a pool thread, and you still get a
`Task` to await.

**Two things that do not help:**

- **Adding threads to CPU-bound work.** 8 cores run exactly 8 threads at any
  instant; thread 9 adds overhead, not speed.
- **`Task.Run` inside an ASP.NET Core handler.** The handler is already on a
  pool thread; `Task.Run` moves the work to another pool thread while the first
  waits for it. A hop, nothing gained.

## How it works

*So a thread "costs" ~1 MB and a blocked one uses no CPU — but the 1 MB is not
RAM. What is a thread made of, and how does the OS move threads on and off
cores?*

```
Thread
├── stack                1 MB of reserved addresses (Windows default)
├── kernel object        the OS's record of this thread
├── saved registers      where it was when last paused
└── thread-local storage a few per-thread slots
```

- **Kernel object.** The **kernel** is the core part of the OS that runs with
  full privileges. A *kernel object* is a small record the OS keeps in its own
  protected memory to track something — here, a thread: running, ready or
  blocked, its priority, where its saved state is. Your code never touches it;
  it gets a *handle*, an ID to pass back to the OS. Files and locks have kernel
  objects too. Every thread is one more entry the OS must keep and manage.
- **Why 1 MB is not RAM.** Memory is handed out in **pages** — 4 KB chunks.
  Reserving 1 MB only claims the *address range*; no physical memory yet. A page
  becomes real RAM the first time the thread writes into it. A thread whose calls
  never go deeper than 12 KB uses three pages. Real memory per thread is roughly
  8–32 KB plus the kernel object. "1,000 threads = 1 GB" is true of addresses,
  not RAM.
- **Only the stack is per thread.** Objects live on **one managed heap shared by
  all threads** — any thread can use any object, which is why shared objects
  need synchronisation. As a speed trick the GC gives each thread a small
  **allocation context** (a private few-KB slice of gen 0) to allocate from
  without coordinating; once created, the object is an ordinary shared object.

**How the scheduler moves threads:**

```
  ┌─────────┐   time slice used up / preempted   ┌─────────┐
  │ RUNNING │ ─────────────────────────────────► │  READY  │
  │ on core │ ◄───────────────────────────────── │ wants a │
  └────┬────┘        scheduler picks it          │  core   │
       │                                         └─────────┘
       │ waits: I/O, lock, Sleep, .Result             ▲
       ▼                                              │
  ┌─────────┐                                         │
  │ BLOCKED │ ────────────────────────────────────────┘
  └─────────┘   the thing it waited for arrives
```

A running thread gets a **time slice** of a few to tens of milliseconds. When it
runs out, when a higher-priority thread needs the core, or when the thread
blocks, the OS takes the core away. Your code never controls when.

Swapping one thread off a core and another on is a **context switch**: save the
first thread's registers into its record, load the second's. The direct cost is
a few microseconds. The bigger cost is indirect: the incoming thread's data is
not in the core's **cache** (the CPU's small, very fast memory for recently used
data), so it runs slowly until the cache warms up. More threads fighting for the
same cores means more switches and colder caches.

## Where it breaks

*So a thread is an OS record plus a stack, and the scheduler moves threads on
and off cores, paying for every switch. What goes wrong when the number of
threads does not match the work?*

Each failure has a **signature** — the combination of CPU and thread count on a
dashboard — which is how you tell them apart.

**1. Oversubscription** — more threads *wanting CPU* than cores (40 CPU-heavy
threads on 8 cores). The scheduler rotates 40 threads through 8 cores; every
rotation is a context switch and a cold cache. The CPU is fully busy, but more
and more of that is switching and cache refills rather than work.
**Signature: CPU ~100%, thread count stable, throughput flat or falling,
latency jumping around.** Fix: about core-count threads doing CPU work, not
more.

**2. Thread-pool starvation** — the opposite: pool threads **blocked**, not
computing, so they cannot take new work.

```
1. Pool has ~8 threads (about one per core).
2. 100 requests arrive; each handler calls .Result on a 500 ms HTTP call.
3. All 8 threads BLOCKED waiting. Request 9 sits in the queue.
4. CPU near 0% — nobody computing, everyone waiting.
5. The pool notices no progress and adds threads, slowly — ~1–2 per second
   (why so slowly: thread-pool-internals).
6. Each new thread takes a request, calls .Result, blocks too.
7. Latency in seconds, CPU 5%, thread count climbing past 100.
```

**Signature: CPU low, thread count climbing steadily, latency terrible** — the
mirror of oversubscription. Fix: stop blocking — `await`, not `.Result`.

**3. Thread-per-request for I/O.** Each waiting request gets its own thread.
Those threads are almost always **blocked**, so they are not competing for
cores and **core count is not the limit**. What binds is the per-thread cost
from the last layer — a kernel object each, stack pages, a scheduler entry, and
on the pool the slow injection rate. A thread is a very expensive way to
represent an operation that is only *waiting*; async represents the same wait as
a small heap object and no thread.

**Smaller ones:**

- **Forgotten foreground thread** — work done, process will not exit, nothing
  logged. A container hangs on shutdown and is force-killed after the grace
  period.
- **Background thread killed mid-write** — no `finally` at exit; a half-written
  file or message. Fix: cancellation token + bounded wait on shutdown.
- **`StackOverflowException`** — recursion deeper than the stack. Kills the
  process; cannot be caught.

## In practice

*So oversubscription is too many threads wanting CPU, and starvation is threads
blocked waiting. A situation that needs all of it — and the arithmetic an
interviewer is waiting for.*

**Situation.** An ASP.NET Core endpoint resizes an uploaded image: ~**200 ms of
pure CPU** per request, **300 requests/s**, **8 cores**. It is wrapped in
`await Task.Run(() => Resize(img))` "so it won't block". Latency climbs until
requests time out.

1. **Classify.** CPU-bound — 200 ms of computing, not waiting.
2. **`Task.Run` bought nothing.** The handler was already on a pool thread; the
   resize moves to another pool thread. The same 200 ms of CPU still needs a
   core.
3. **Arithmetic first.** Demand: 300 × 0.2 s = **60 core-seconds of work per
   second**. Supply: **8 core-seconds per second**. **7.5× over capacity** —
   work piles up in queues, latency grows to timeouts, CPU pinned at 100%.
   **A capacity problem, not a threading problem**: total work and cores are
   both fixed, so no arrangement of threads, tasks or async fixes it.
4. **Options, priced:**

| Option | Buys | Costs |
|---|---|---|
| **Make each resize cheaper** — smaller output, faster library, cache repeat images | Cuts the 60 at the source; often the biggest win | Engineering time; cache memory and invalidation |
| **Scale out** — 60 ÷ 8 ≈ 8 boxes at 100%, **~10 at ~75%** | Handles the load as is | Money, roughly linear with traffic |
| **Bound and shed** — ~8 resizes at once (a `SemaphoreSlim` limits how many run concurrently; tier 1, later), reject the rest with **HTTP 429** | Protects the rest of the service | Some uploads rejected; clients retry |
| **Off the request path** — accept upload, queue a job, core-count workers resize, result delivered later | Upload latency small and stable; workers scale separately | Complexity; result not instant |

**Decision:** queue plus workers sized at about core count, workers scaled
horizontally (~10 × 8-core at this load), cache repeat resizes, and delete the
`Task.Run` — it only added a hop.

**What the interviewer listens for:** "capacity problem" *with the number*
(60 vs 8), why `Task.Run` in a handler is a no-op, and a price on every option.

## Drill — 2026-09-19

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `new Thread(ProcessQueueForever)` started in `Main`; the pod stops serving on SIGTERM but never exits and is SIGKILLed after the grace period. Cause, minimal fix, and why the minimal fix is not shippable? | Named the foreground thread as the cause, background as the fix, and a `CancellationToken` for proper termination — all three unaided. Said "the main thread cannot be finished"; it is the *process* that cannot exit, `Main` may return normally. | hit |
| 2 | ASP.NET Core handler doing a 200 ms CPU resize at ~300 rps on 8 cores, wrapped in `await Task.Run(...)` "so it won't block". What does that buy, and what would you do instead? | Passed and asked for the explanation. | miss |
| 3 | Service A: CPU 98%, 34 threads stable, throughput falling. Service B: CPU 9%, 96 threads rising 1–2/sec. Name each failure and say what in the thread model produces that signature. | Named oversubscription and thread-pool starvation correctly and immediately. Gave no mechanism for either signature, which was the second half of the question. | miss |

Drill results do not change a level.

## Drill — 2026-10-01

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | A loop that consumes messages for the whole life of a service — how do you start it, and how do you make it stop cleanly on shutdown? | Dedicated thread; foreground rejected because it holds the process open; background plus a `CancellationToken` the loop observes. Did not add the bounded wait (`Join` with a timeout) after cancelling. | hit |
| 2 | A vendor's native card-reader SDK needs every call from the same OS thread, some calls block for seconds; async ASP.NET Core service. Why not `Task.Run` or `await`, what instead, at what cost? | Said the work must move off the request thread and that `Task.Run` would block pool threads toward starvation. Did not name thread affinity as the reason neither works — no control over which thread runs the call — nor the answer (one dedicated thread owning the SDK, fed by a queue) nor its cost (calls serialised, a bottleneck, lifetime owned). | miss |
| 3 | 8 cores, CPU 98%, 40 threads stable, throughput falling — what is happening underneath? | Oversubscription: more threads wanting CPU than cores, frequent context switches, and the core's cache refilled after every switch, so work done per CPU-second drops. | hit |

Drill results do not change a level.

## Model answers — 2026-10-01

### Q1 (2026-09-30) — target L4, awarded L2

*"We can't go thread-per-request — 1,000 threads is 1 GB of RAM." What is right and wrong, and what does a thread actually cost?* — [[2026-09-30-async-and-threading-tier-1]]

> Right in direction, wrong in the number. The 1 MB is reserved *address
> space* for the stack; physical pages are only used when touched, so an idle
> thread holds maybe 8–32 KB plus a kernel object. The real cost of
> thread-per-request for I/O is representing a *waiting* operation with an OS
> thread — ~100 µs to create, a kernel object, a scheduler entry, a stack — and
> those threads are blocked, not competing for cores, so core count isn't the
> limit; the per-thread overhead and the pool's slow injection are. Async
> represents the same wait as a few hundred bytes of heap and no thread.

Missing from the graded answer: address space versus RAM; that blocked threads
are not waiting for cores; what actually binds.

### Q2 (2026-09-30) — target L5, awarded L2

*Rung 3: when does a dedicated thread genuinely beat the pool or async, and what do you pay for it?* — [[2026-09-30-async-and-threading-tier-1-2]]

> Rarely for plain CPU work — the pool handles that. A dedicated thread wins
> when something is tied to the thread itself: a native library needing every
> call from one OS thread, STA for COM or UI, a custom stack size, or priority.
> It also wins for work that never ends — a process-lifetime consumer loop, or a
> blocking SDK with no async API — because on the pool that looks like a blocked
> thread and makes the pool inject more. You pay ~100 µs and 1 MB of address
> space per thread, no reuse, and you own the lifetime: background, a
> cancellation token, a bounded wait on shutdown. `StartNew` with `LongRunning`
> gets you the thread without giving up the `Task`.

Missing from the graded answer: the thread-bound cases; the pool mistaking
long-running work for blocked; the costs and the `LongRunning` middle path.

## Resources

## Related

[[stack-vs-heap-layout]] · [[thread-pool-internals]] · [[parallelism-vs-concurrency]] · [[cancellation-tokens]]
