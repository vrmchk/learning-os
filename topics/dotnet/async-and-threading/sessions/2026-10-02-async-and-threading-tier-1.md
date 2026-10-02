---
topic: dotnet
cluster: async-and-threading
date: 2026-10-02
mode: interview
coached: true
excursion: false
questions: 4
avg_target: 3.5
avg_awarded: 2.8
concepts: [thread-pool-internals, threads-and-scheduling, parallelism-vs-concurrency, semaphoreslim-and-async-locks]
self_flagged: [2, 4]
disputes: 0
---

# 2026-10-02 — Async and threading, tier 1 (after the layered re-teach)

**Proposed by rule:** 1 — overdue/due queue items; the three async concepts are due today. Rule 1 strictly puts the six memory-and-gc items first (overdue since 2026-09-20); the user chose the async three, and the GC backlog goes to `weekly-review`.
**Override:** user — the three concepts re-taught on 2026-10-01

Coached format, ladders. After each ladder the user rated it in one word
before any correction; those ratings are the self-assessment. Coached rule 5
constrained Q3: its rung 5 (the quantified batch design) rests on CPU work
stopping scaling at the core count, which was corrected after Q2, so Q3 was
capped at L4.

Points with an open drill miss from 2026-10-01 are not asked: `SetMinThreads` sizing and when raising it is wrong; the pool-exhaustion deadlock mechanism; the native-SDK thread-affinity design; the lost-update mechanism and memory visibility; the cost of `Task.Run` per item. That caps Q1 at L4.

## Q1 — [[thread-pool-internals]] — target L4 — depth

**Rung 1 — Explain (L1):** *What is the thread pool, and why does .NET have one?* → reuses threads instead of deleting them after each operation; creating a thread is costly — an OS object behind each .NET thread, creation can take longer than the work, and 1 MB of address space reserved for the stack. — **cleared**

**Rung 2 — Use (L2):** *In a typical ASP.NET Core API where nobody writes `Task.Run`, what still runs on the pool? Name the sources.* → incoming requests; "the code which continues after the await"; `Parallel.For`.

**Probes:**
1. *Leaving requests and your own code aside — what else fires on its own and runs on the pool?* → "I/O completions maybe".
2. *Why does an I/O completion need a pool thread — what runs then?* → the program is notified the awaited I/O finished "and we can proceed further with the code after that await".

— **cleared**: requests, continuations after `await` (stated correctly this time), I/O completions tied to resuming the continuation. Miss recorded: timer callbacks not named.

**Rung 3 — Trade-offs (L3):** *Everything in the process shares that one pool. What does the sharing cost you — and when is the pool the wrong place for a piece of work?* → blocking items starve everyone: past about the core count the pool adds "one or two threads" a second, those block too, "CPU is low and thread pool size keeps growing" — so don't block pool threads. Wrong place: long-running work goes to a separate thread; a library or SDK that requires its own thread. Also named oversubscription as a sharing failure, without saying how sharing causes it.

— **cleared**: the cost of sharing (one blocking item takes a thread from everyone, slow growth), and two of the three wrong-place cases (long-running work, thread-bound SDK). Not mentioned: I/O waiting belongs to `await` rather than a pool thread; giving up control of priority, stack size and order.

**Rung 4 — Mechanism (L4):** *How does a pool thread decide which work item to run next — and how does the pool decide when to add a thread?* → a global queue on the pool and a local queue per thread; a thread checks its local queue first "because the cache on the core is already related to this thread", then the global queue, then steals from other threads' local queues. Threads are added immediately up to the core count; past that, when threads are blocked or busy and work waits, one is added "every half a second".

**Probes:**
1. *When stealing, newest or oldest item — why?* → the oldest, because the owning thread is better placed to process its newer items.
2. *Apart from the half-second check, does anything else change the thread count, and to what end?* → described `SetMinThreads` for bursts and that removing blocking code or moving work off the request path is usually the better fix. Did not name hill climbing — the feedback loop measuring completions per second and moving the count up or down toward maximum throughput — nor idle threads retiring.

— **cleared**: both queues, the order and the cache reason, stealing the oldest item, instant creation up to about core count and the ~500 ms injection. Miss recorded: hill climbing.

**Rating:** solid ("closer to solid")

**Awarded:** L4 — rungs 1–4 cleared; the ladder's top rung (target capped at L4 by the open `SetMinThreads` drill miss).

## Q2 — [[threads-and-scheduling]] — target L5 — depth

Hooked to Q1: the user said some SDKs require a thread of their own.

**Rung 1 — Explain (L1):** *You said some SDKs need a thread of their own. What is a thread, underneath — and who decides when it actually runs?* → a wrapper over an OS thread; 1 MB of reserved address space for the stack, an OS kernel object, saved registers; "the OS scheduler decides when a thread runs". — **cleared** (unaided, no probes needed)

**Rung 2 — Use (L2):** *When you do create a thread yourself, what does the code look like — and what do you have to get right so the app still shuts down cleanly?* → pass the method to run as a constructor parameter; the background/foreground property — foreground holds the process open until its work finishes, background threads are terminated straight away when the process exits; so make it background and pass it a cancellation token.

**Probes:**
1. *Cancelling at shutdown — enough on its own? What happens to the item it is halfway through if the process exits right after?* → "I don't know and I'm not sure if we studied it". It is in the note's *Using it*: background + token + a short bounded wait (`Join` with a timeout) on shutdown.

— **cleared**: thread creation, foreground vs background with the consequence of each, cooperative cancellation through a token. Miss recorded: no bounded wait after cancelling, so the in-flight item is still killed at exit.

**Rung 3 — Trade-offs (L3):** *Someone wraps CPU-heavy work in `await Task.Run(...)` inside an ASP.NET Core controller "so it doesn't block". What does that buy — and when do more threads stop helping at all?* → buys nothing: the code was already on the pool from the moment the request arrived; better to take CPU-heavy work off the request path into background processing. "Our code will be broken anyway" — not unpacked.

**Probes:**
1. *It does move the work to another pool thread — what happens to the original thread meanwhile, and what did the hop cost?* → the original thread can take other requests, but another thread is occupied for the same time, so net nothing; "the amount of threads in the pool will climb regardless"; does not know what the hop costs.
2. *For CPU-heavy work, at what point do more threads stop helping, and what if you add them anyway?* → more threads help for short bursts, not when requests keep climbing; you must compute the processors needed from requests per second × processing time, and scaling costs money; too many leads to oversubscription with CPU very high and "a lot of threads ... all of them just waiting as blocked"; best to optimise the CPU work or move it off the request path.

— **not cleared**; climb stops. The `Task.Run` half is right. The second half misses the point: for CPU-bound work, threads stop helping at about the **core count** — beyond it each extra runnable thread adds context switches and cold caches, not throughput. Describes oversubscribed threads as "blocked"; they are runnable and competing for cores, which is why CPU is pinned. Conflates CPU-bound work with the blocked-thread burst case (thread count climbing). The capacity arithmetic (rate × CPU time against cores) was named in outline — the right instinct, but not this rung's question. The hop's cost (an extra queued work item and a thread switch, while the request still waits) not known.

**Rating:** shaky

**Awarded:** L2 — rungs 1–2 cleared, rung 3 missed where extra threads stop helping CPU work (trade-off cap).

## Q3 — [[parallelism-vs-concurrency]] — target L4 — depth

Hooked to Q2: the user reached for CPU-bound work against scaling. Target capped at L4: rung 5 would be the quantified batch design, whose sizing rests on "CPU work stops scaling at the core count" — corrected after Q2, so not re-testable this session (coached rule 5).

**Rung 1 — Explain (L1):** *You keep separating CPU-heavy work from waiting. Put names on it — what is concurrency, what is parallelism, and how do they differ?* → concurrency is "managing several tasks at the same time", parallelism "actually executing several tasks at the same time"; cutting potatoes while the water boils vs several people cooking different dishes; in .NET concurrency via async tasks, parallelism via multiple threads. — **cleared**

**Rung 2 — Use (L2):** *Concretely: you have to process 10,000 small CPU-heavy items, and separately make 10,000 calls to an external API. What do you write for each, and what does `Task.WhenAll` actually do in the second one?* → `Parallel.ForEach` in chunks on the pool for the CPU items; `Task.WhenAll` for the API calls "but I will also pass a parameter to limit how many requests can be run at the same time". `WhenAll` means "proceed when all of the items inside of it are finished"; said the calling thread "returns to thread pool only after all the tasks inside of it are finished".

**Probes:**
1. *`Task.WhenAll` has no limit parameter — what would you write to cap it at 50?* → `Parallel.ForEachAsync` or `SemaphoreSlim`.
2. *While the 10,000 calls are in flight, where is the thread that called `await Task.WhenAll`?* → "it returns back to the pool and can be reused".

— **cleared**: the right tool for each side, a bound on the I/O side named correctly under the first probe, and the calling thread released during the wait under the second. Miss recorded: first stated that the thread awaiting `WhenAll` is held until every call completes.

**Rung 3 — Trade-offs (L3):** *A colleague says "we made the endpoint async, so now it's faster." What does async actually buy — and what does it cost, per call and to the codebase?* → buys scalability: while waiting on a DB or API call the thread returns to the pool to serve other requests. Per call: "generate an async state machine at compile time". Codebase: if one method is async, every caller up the tree must become async.

**Probes:**
1. *The state machine is generated once at compile time — what does each call that actually waits pay at runtime?* → a callback when the call finishes, and "this callback also runs on the thread pool".
2. *While paused with no thread running it, where do its locals live, and what does that cost?* → locals "are boxed and stored on the heap", costing "boxing and unboxing".

— **cleared**: scalability with its mechanism, async as viral, and under probing the two runtime costs — continuation scheduling onto the pool, and the locals moved to the heap. Misses recorded: still opens the per-call cost with "compile time"; describes each local as boxed and unboxed — they are fields of one state-machine object moved to the heap once, on the first real suspension, not boxed individually and unboxed on each access; harder stack traces not named.

**Rung 4 — Mechanism (L4):** *Walk me through `await httpClient.GetAsync(url)` from the call to the line after it. During the ~200 ms the request is on the network, what is holding it — and what wakes the method up again?* → asked whether it had been taught (it had: the note's *How it works*), then: the request starts on a pool thread; at the `await` the request "is handed to the OS and the call returns immediately"; the thread returns to the pool to do other work; "while we're waiting ... no thread is blocked"; on the reply "the OS notifies us and the continuation ... gets back to the pool and some other thread picks it up".

**Probes:**
1. *Through what OS mechanism — and in the 200 ms, what is doing the work if no thread is?* → "the OS is doing the work"; does not know the mechanism and called it "too niche of a knowledge to remember".

— **cleared**: the full walk, unaided — handed to the OS, immediate return, thread released, no thread during the wait, OS notification, continuation queued to the pool and run on another thread. Miss recorded: the I/O completion port (Windows) / `epoll` (Linux) not named.

**Rating:** solid ("closer to solid")

**Awarded:** L4 — rungs 1–4 cleared; the ladder's top rung (target capped at L4 by coached rule 5 after Q2).

## Q4 — [[semaphoreslim-and-async-locks]] — target L1 — discovery

Hooked to Q3 rung 2: the user named `SemaphoreSlim` to cap concurrent API calls. Untaught (no note; stub created at write-back), so a one-rung discovery ladder: excluded from grades and from the stop rule.

**Rung 1 — Explain (L1):** *What is a semaphore — `SemaphoreSlim` in .NET — and why would you use one instead of a `lock`?* → `lock` lets only one thread into the block, and is built on `Monitor` (`Monitor.Enter` and the rest); a semaphore "limits the amount of threads which the process can run" — one for a lock, several for a semaphore. `SemaphoreSlim` is better than `Semaphore` because the regular one uses only OS blocking while the slim one uses lighter "programmable" blocking first, falling back to OS blocking for long waits. — **cleared** (defined, with why it exists). Misses: does not name `WaitAsync()` — that `SemaphoreSlim` can be awaited while a `lock` cannot contain an `await` — which is the reason to choose it in async code; describes it as limiting the process's threads rather than how many callers are inside one section.

**Rating:** shaky

**Awarded:** L1 — discovery: excluded from the concept grade.

## Self-assessment

User rated: Q1 solid, Q2 shaky, Q3 solid, Q4 shaky

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[thread-pool-internals]] | L4 | L4 | — | — |
| 2 | [[threads-and-scheduling]] | L5 | L2 | weak | — |
| 3 | [[parallelism-vs-concurrency]] | L4 | L4 | — | — |
| 4 | [[semaphoreslim-and-async-locks]] | L1 | L1 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[thread-pool-internals]] | L1 | L4 | Q1 cleared rungs 1–4; re-taught 2026-10-01, a day clear |
| [[threads-and-scheduling]] | L2 | L2 | held; Q2 cleared rungs 1–2, missed rung 3 again |
| [[parallelism-vs-concurrency]] | L2 | L4 | Q3 cleared rungs 1–4; re-taught 2026-10-01, a day clear |
| [[semaphoreslim-and-async-locks]] | L0 | L0 | Q4 is `discovery` — excluded; level does not move |

## Misses

- [[thread-pool-internals]] — does not name timer callbacks as a source of pool work
- [[thread-pool-internals]] — does not name hill climbing (the throughput feedback loop that moves the thread count up and down) or idle threads retiring
- [[threads-and-scheduling]] — after cancelling an owned thread at shutdown, no bounded wait (`Join` with a timeout), so the in-flight item is still killed
- [[threads-and-scheduling]] — does not say CPU-bound work stops gaining from threads at the core count; describes oversubscribed threads as blocked rather than runnable; conflates it with the blocked-thread burst case; cannot price the `Task.Run` hop
- [[parallelism-vs-concurrency]] — first said the thread awaiting `Task.WhenAll` is held until every call completes (corrected under a probe)
- [[parallelism-vs-concurrency]] — opens async's per-call cost with "compile time"; describes locals as each boxed and unboxed rather than fields of one state machine moved to the heap once; harder stack traces not named
- [[parallelism-vs-concurrency]] — cannot name the I/O completion port / `epoll` as what delivers the completion
- [[semaphoreslim-and-async-locks]] — discovery: does not know `WaitAsync()` is why `SemaphoreSlim` is used in async code (a `lock` cannot span an `await`); says it limits the process's threads rather than callers inside one section

## Queue

| Concept | Next |
|---|---|
| [[threads-and-scheduling]] | 2026-10-05 |
| [[thread-pool-internals]] | 2026-10-23 |
| [[parallelism-vs-concurrency]] | 2026-10-23 |

[[semaphoreslim-and-async-locks]] is not queued: untaught, and its open gap
sends it to `teach` first.