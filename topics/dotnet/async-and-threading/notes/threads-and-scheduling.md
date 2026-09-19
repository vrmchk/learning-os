---
concept: threads-and-scheduling
topic: dotnet
cluster: async-and-threading
created: 2026-09-18
taught: 2026-09-19
---

# Threads and scheduling

## Mechanism

**A thread is an OS object.** `System.Threading.Thread` is a managed wrapper
over a real kernel thread, 1:1 — .NET has no green threads or fibres. The **OS
scheduler**, not the CLR, decides which thread runs on which core and when.

Each thread owns:

```
Thread
├── stack            ~1 MB reserved address space (Windows default)
├── kernel object    scheduling state, priority, handle
├── register context saved on every switch (RIP, RSP, general + SIMD)
└── TLS              thread-local storage slots
```

### Reserved, committed, touched

A **page** is the unit the MMU and OS manage memory in — 4 KB on x64 (huge
pages of 2 MB or 1 GB exist for special cases). Code only sees virtual
addresses; page tables map virtual pages to physical ones and the TLB caches
those mappings. Three states:

```
RESERVED   address range claimed, no physical memory, costs only address space
COMMITTED  backing promised (RAM or page file), still no physical page assigned
TOUCHED    first read/write → page fault → OS assigns a real 4 KB physical page
```

So a thread's "1 MB stack" is **1 MB of reserved address space**. A thread
whose call stack never exceeds 12 KB holds **three** physical pages. Real RAM
per thread is typically 8–32 KB of touched stack plus the kernel object.
"1,000 threads = 1 GB" is true of *address space*, not RAM — a bookkeeping and
address-space ceiling, not a memory bill.

### Green threads and fibres, and why .NET has neither

Both mean a unit of execution scheduled in **user mode by a runtime**, not by
the kernel — many multiplexed onto few OS threads (**M:N**, against .NET's
1:1).

| | OS thread | Green thread |
|---|---|---|
| Switch cost | ~1–10 µs, kernel transition | ~10–100 ns, a function call |
| Stack | ~1 MB reserved, fixed at creation | ~2–8 KB, grows on demand |
| Scheduled by | Kernel | Language runtime |
| Practical ceiling | thousands | millions |

Live examples: Go goroutines, Java 21 virtual threads (Project Loom), Erlang
processes. **Fibre** is the Windows term (`ConvertThreadToFiber`,
`SwitchToFiber`) and is strictly **cooperative** — a fibre runs until it
explicitly yields.

Fibres were tried in .NET — SQL Server could host the CLR in fibre mode — and
abandoned. They break everything assuming thread affinity: `lock` ownership is
tracked per OS thread, thread-local storage, and native libraries requiring
calls from one thread.

**`async`/`await` solves the same problem by a different route.** Go gives a
pending operation a cheap *stack*; C# gives it a cheap *object* — the compiler
rewrites the method into a state machine, so a paused operation is a few
hundred bytes on the heap with **no stack at all**. Same goal, compiler
transform instead of runtime scheduler.

### Scheduling

Preemptive and time-sliced. A runnable thread gets a quantum of tens of
milliseconds; the kernel reclaims the core when it expires, when a
higher-priority thread becomes runnable, or when the thread blocks. Code never
controls when it is descheduled. Priority is a hint, not a guarantee, and using
it to fix a design problem is an anti-pattern.

```
  ┌─────────┐   quantum expires / preempted   ┌─────────┐
  │ RUNNING │ ──────────────────────────────► │  READY  │
  │ on core │ ◄────────────────────────────── │ wants a │
  └────┬────┘        scheduler picks it       │  core   │
       │                                      └─────────┘
       │ blocks on I/O, lock, Sleep, Wait          ▲
       ▼                                           │
  ┌─────────────┐                                  │
  │   BLOCKED   │ ─────────────────────────────────┘
  │ not         │   the thing it waited on completes
  │ schedulable │
  └─────────────┘
```

A **blocked** thread burns no CPU but still holds its stack, kernel object and
address space for the whole wait. Blocking is not free; it is only not
*CPU*-expensive. That fact is the foundation of the rest of this cluster.

**A context switch** saves registers, swaps kernel stacks, and across processes
swaps the address space. Direct cost is a few microseconds; the indirect cost
is usually larger, because the incoming thread runs with cold L1/L2 caches and
a partly invalid TLB.

**Parallelism is bounded by cores.** On 8 cores exactly 8 threads run at any
instant. Thread 9 adds context switches, not throughput. More threads help only
when existing threads are **blocked**, never when they are busy.

### Foreground vs background

One difference, with teeth:

- **Foreground** — the CLR keeps the process alive until the thread finishes.
  `Main` returning is not enough.
- **Background** — the CLR does not wait. At shutdown these threads are
  **terminated abruptly**: no `finally`, no `using` disposal, no `catch`. Work
  in flight is lost.

```csharp
var t = new Thread(Work);      // foreground by DEFAULT
t.IsBackground = true;         // opt in to background
```

Every thread-pool thread, every `Task.Run`, and every timer callback is
**background**. Neither default is what a worker wants: foreground hangs
shutdown, background kills work mid-write. The correct pattern is background
**plus** cooperative shutdown — a `CancellationToken` to ask it to stop and a
bounded wait for it to finish.

**A thread cannot be killed.** `Thread.Abort` throws
`PlatformNotSupportedException` on .NET Core and later. Cooperative
cancellation is the only mechanism, which is why `CancellationToken` is a
tier-1 concept rather than a convenience.

## Failure modes

- **Thread-per-request.** 1,000 concurrent I/O-bound requests on 1,000 threads:
  ~1 GB reserved address space, 1,000 kernel objects, a scheduler juggling them
  — while nearly all sit BLOCKED doing nothing. This is the problem `async` was
  invented to solve, and the honest answer to "why do we need async at all".
- **Oversubscription.** More runnable threads than cores. Symptom: **CPU pinned
  at 100%**, throughput flat or falling, latency variance exploding. The high
  CPU is what separates it from starvation.
- **Blocking a pool thread.** The pool is a fixed, shared, slowly-growing set
  sized on the assumption that work items are short:

  ```
  1. Pool starts at roughly core count.                       say 8
  2. 100 requests arrive; each handler calls .Result on a
     500 ms HTTP call.
  3. All 8 threads are BLOCKED — not slow, blocked. They
     cannot pick up work item 9.
  4. Items 9..100 sit in the queue. CPU near 0%.
  5. The pool injects threads at roughly 1–2 per second.
  6. Each new thread takes an item, calls .Result, blocks too.
  7. Latency in seconds, CPU 5%, thread count past 100.
  ```

  Signature: **thread count climbing while CPU stays low** — the inverse of
  oversubscription. Self-inflicted: the work was I/O and needed no thread at
  all. With `await`, 100 concurrent requests need roughly 8 threads. Covered
  properly by `thread-pool-starvation`.
- **Thread leak.** Threads created and never finished, or parked forever.
  Symptom: thread count climbing monotonically with no plateau.
- **The forgotten foreground thread.** Work completes, the process will not
  exit, nothing is logged. A container that never terminates and is SIGKILLed
  after the grace period.
- **`StackOverflowException`** kills the process and cannot be caught — each
  stack is finite and fixed at thread creation. See [[stack-vs-heap-layout]].

## Trade-offs

| | Dedicated `Thread` | Thread pool | `async`/`await` |
|---|---|---|---|
| **For** | Long-running or special work | Short CPU-bound work items | I/O-bound waiting |
| **Costs** | ~1 MB reserved, ~100 µs to create, you own its lifetime | No lifetime control; blocking one hurts every other user | State-machine allocation, viral through the call stack |
| **Use when** | Runs for minutes or forever; needs a custom stack size, priority or apartment state; must not occupy a pool thread | Bursty, short, CPU-bound | Anything waiting on network, disk or another process |

### Which downside actually binds

Depends on the workload, and the two limits bind in different situations.

- **CPU-bound:** the **core count** binds; memory is irrelevant. You never want
  more than ~core-count threads, so 8–16 × 1 MB is nothing. Extra threads here
  actively hurt — context switches and cold caches.
- **I/O-bound:** **memory and scheduler overhead** bind, and core count is
  irrelevant because the threads are waiting, not computing. This is the case
  that kills web services.

One sentence for the real downside:

> A thread is a very expensive way to represent an operation that is merely
> waiting.

10,000 pending operations as threads: ~10 GB of address space, 10,000 kernel
objects, a scheduler managing all of them. The same 10,000 as `async` state
machines: ~1–2 MB of heap objects and **zero** threads. That ratio is the whole
argument for `async`, and it has nothing to do with speed.

### Task vs Thread

- **Threads give parallelism** — more than one core at once. Bounded by core
  count. For CPU-bound work.
- **`async` gives concurrency without threads** — not holding a thread while
  waiting. Unbounded by core count, because nothing is occupied. For I/O.
- **`Task` is neither.** It is a *handle to work in progress*. It may run on a
  pool thread, or be nothing but a callback registered on an I/O completion
  port with no thread behind it. "Task vs Thread" is a category error as a
  comparison, and saying so is the strong answer.

### When a dedicated `Thread` genuinely wins

"CPU-bound" is the textbook answer and it is incomplete. The real cases:

- **Thread affinity demanded by a native library** — hardware and instrument
  drivers, OpenGL contexts, some native DB drivers require every call from the
  same OS thread. `async` gives no control over which thread resumes after an
  `await`, so this is structurally impossible with `async`. One dedicated
  thread plus a work queue fed to it.
- **COM / STA apartment state** — Office interop, Windows shell APIs, WPF and
  WinForms UI. Apartment state belongs to an OS thread and is set before start:
  `t.SetApartmentState(ApartmentState.STA)`.
- **A custom stack size** — a deeply recursive parser that blows 1 MB:
  `new Thread(Parse, 16 * 1024 * 1024)`. No equivalent exists for a pool thread
  or an async method.
- **A loop running for the process lifetime** — a queue consumer, a device
  poller. It never returns, so it must never occupy a pool thread. `new Thread`,
  or `Task.Factory.StartNew(..., TaskCreationOptions.LongRunning)`, which
  quietly creates a dedicated thread instead of using the pool.
- **A third-party SDK with no async API that blocks for minutes.** It cannot be
  made async — there is no async API underneath to await. The only choice is
  *where* it blocks: on a thread you own, not one the pool needs.
- **Elevated priority for a latency-sensitive loop** — audio capture, telemetry
  sampling. Priority belongs to a thread, not to a `Task`.

**The common mistake in the other direction:** in an ASP.NET Core handler,
wrapping CPU-bound work in `Task.Run` buys nothing. The handler is *already* on
a pool thread; the work moves from one pool thread to another, adding a hop
while the first thread waits for the second. For genuine CPU-bound throughput
the answer is bounded parallelism, backpressure, or scaling out — not
`Task.Run`.

**Adding threads to a saturated CPU-bound system makes it slower** — more
context switches, colder caches, same core count.

## Drill — 2026-09-19

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `new Thread(ProcessQueueForever)` started in `Main`; the pod stops serving on SIGTERM but never exits and is SIGKILLed after the grace period. Cause, minimal fix, and why the minimal fix is not shippable? | Named the foreground thread as the cause, background as the fix, and a `CancellationToken` for proper termination — all three unaided. Said "the main thread cannot be finished"; it is the *process* that cannot exit, `Main` may return normally. | hit |
| 2 | ASP.NET Core handler doing a 200 ms CPU resize at ~300 rps on 8 cores, wrapped in `await Task.Run(...)` "so it won't block". What does that buy, and what would you do instead? | Passed and asked for the explanation. | miss |
| 3 | Service A: CPU 98%, 34 threads stable, throughput falling. Service B: CPU 9%, 96 threads rising 1–2/sec. Name each failure and say what in the thread model produces that signature. | Named oversubscription and thread-pool starvation correctly and immediately. Gave no mechanism for either signature, which was the second half of the question. | miss |

Drill results do not change a level.

## Resources

## Related

[[stack-vs-heap-layout]]
