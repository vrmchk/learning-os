---
concept: async-state-machine
topic: dotnet
cluster: async-and-threading
created: 2026-10-02
taught: 2026-10-02
---

# Async state machine

## What it is

A method that waits on I/O must give its thread back while it waits — that is
the point of async. But a normal method keeps its locals and its position on
the thread's own stack; give the thread away and they are gone.

So the C# compiler rewrites every `async` method into a **state machine**: a
small object that remembers *which step it is on* (a number) and *the locals it
still needs*, plus one method that runs the next step. With that, the method
can stop at an `await`, return to its caller, and later continue from exactly
that point — on any thread.

Without it you either block (hold the thread for the whole wait) or write the
callbacks by hand, splitting the method yourself — how async I/O was done
before C# 5. The state machine is the compiler writing those callbacks for you.

## Using it

*So the compiler does the rewrite. What do you actually write, and where does
it show up?*

You never write it — you write `async` and `await`:

```csharp
public async Task<int> GetOrderCountAsync(int userId)
{
    Console.WriteLine("A");                        // during the call, on the caller's thread
    var user = await _db.FindUserAsync(userId);    // may pause here
    Console.WriteLine("B");                        // later, possibly on another thread
    return user.Orders.Count;
}

var task = GetOrderCountAsync(5);   // "A" is already printed when this returns
int count = await task;
```

Three behaviours, seen from outside:

- **The call runs synchronously** on the caller's thread up to the first
  `await` that actually has to wait. Calling an async method queues nothing.
- **At that `await` the method returns** an unfinished `Task`. The code after
  it is the [[glossary#Continuation]], run when the operation finishes.
- **If the awaited thing is already finished** (cache hit, completed task),
  there is no pause — the method carries on, and may return an already
  completed `Task` without ever letting go of the thread.

Where you see it: `<GetOrderCountAsync>d__4` and `MoveNext` in stack traces,
profilers and decompilers.

## Trade-offs

*So an object remembers the method's place. What does having one cost, and when
can you avoid it?*

**Generated once at compile time; paid at runtime, per call.** "Compile time"
is when the code is written, not what costs.

| The call… | Costs |
|---|---|
| **completes synchronously** — every awaited thing already done | Almost nothing. The state machine is a struct on the caller's stack and never touches the heap. A `Task<T>` for the result is still allocated (~64 B), except for a few cached values; a non-generic `Task` uses a cached completed one. |
| **actually pauses** — at least one `await` must wait | **One heap allocation per call**: the state machine moves to the heap, combined with the `Task` it returns, as one object (~100 B plus hoisted locals) — **once**, at the first real pause, reused by later pauses in the same call. Plus scheduling the continuation when the operation completes. |

- **Hoisting** — a local still needed after an `await` becomes a *field* of the
  state machine. Only those locals; one used entirely between two awaits stays
  an ordinary local. Locals are not boxed individually and unboxed on each use:
  they are plain fields of one object, which moves to the heap once.
- **Synchronous completion** — the awaited thing was already finished, so no
  pause happened. The cheap row above.
- **Elision** — `return _db.FindUserAsync(id);` without `async`/`await`. No
  state machine is generated at all.

Further costs: **stack traces** — after a resume the thread's real stack only
reaches back to the pool code that resumed it; .NET stitches the logical chain
with `--- End of stack trace from previous location ---`. And **`Span<T>` and
other stack-only types cannot cross an `await`** — a hoisted field may live on
the heap.

| Instead of… | You get | You pay |
|---|---|---|
| blocking call | no allocation, readable stack | a thread held for the whole wait |
| elision | no state machine | changed exception, `using` and stack-trace behaviour |
| `ValueTask<T>` (later: `task-vs-valuetask`, tier 2) | no `Task` allocation on synchronous completion | may be awaited only once; more rules |

## How it works

*So it is one object, moved to the heap at the first real pause. What does the
compiler generate, and what happens at runtime?*

- **`MoveNext`** — the state machine's single method: runs from wherever the
  state number says, up to the next real pause or the end.
- **Awaiter** — what `await x` talks to. `x.GetAwaiter()` returns an object with
  `IsCompleted` ("already done?"), `OnCompleted(callback)` ("call me when
  done") and `GetResult()` ("the value, or throw the exception").
- **Builder** (`AsyncTaskMethodBuilder<T>`) — a helper struct inside the state
  machine that owns the `Task`, moves the state machine to the heap when
  needed, and completes the `Task` with a result or an exception.

The method becomes a stub plus a struct (simplified from real compiler output):

```csharp
public Task<int> GetOrderCountAsync(int userId)          // the stub
{
    var sm = new <GetOrderCountAsync>d__4();              // struct, on this stack
    sm.userId = userId;  sm.<>4__this = this;
    sm.<>t__builder = AsyncTaskMethodBuilder<int>.Create();
    sm.<>1__state = -1;                                   // not started / running
    sm.<>t__builder.Start(ref sm);                        // MoveNext NOW, caller's thread
    return sm.<>t__builder.Task;
}

struct <GetOrderCountAsync>d__4 : IAsyncStateMachine
{
    public int <>1__state;
    public AsyncTaskMethodBuilder<int> <>t__builder;
    public int userId;  public Repo <>4__this;            // parameters become fields
    private TaskAwaiter<User> <>u__1;                     // the pending await

    void MoveNext()
    {
        int result;
        try
        {
            TaskAwaiter<User> awaiter;
            if (<>1__state != 0)                          // first entry
            {
                Console.WriteLine("A");
                awaiter = <>4__this._db.FindUserAsync(userId).GetAwaiter();
                if (!awaiter.IsCompleted)                 // must really wait
                {
                    <>1__state = 0;  <>u__1 = awaiter;
                    <>t__builder.AwaitUnsafeOnCompleted(ref awaiter, ref this);
                    return;                               // thread handed back
                }
            }
            else                                          // resumed
            {
                awaiter = <>u__1;  <>u__1 = default;  <>1__state = -1;
            }
            User user = awaiter.GetResult();              // value, or rethrow
            Console.WriteLine("B");                       // `user` crosses no await: not hoisted
            result = user.Orders.Count;
        }
        catch (Exception ex)
        {
            <>1__state = -2;  <>t__builder.SetException(ex);   // into the Task
            return;
        }
        <>1__state = -2;  <>t__builder.SetResult(result);      // -2 = finished
    }
}
```

A call that really pauses:

```
caller thread T1                                         pool thread T2
stub → Start → MoveNext (state -1)
  "A"; FindUserAsync starts I/O, returns unfinished Task
  IsCompleted? no → state = 0, save awaiter
  AwaitUnsafeOnCompleted:
    first real pause → builder copies the struct into
    ONE heap object, which is also the returned Task;
    registers its MoveNext as FindUserAsync's continuation
  return → stub returns the unfinished Task; T1 is free
            ... no thread: the OS holds the I/O ...
            completion port / epoll → FindUserAsync's Task completes
            → runs its continuation ─────────────────────► MoveNext (state 0)
                                                           GetResult → "B"
                                                           SetResult → our Task done
                                                           → caller's continuation runs
```

- **Exceptions never leave `MoveNext` directly** — caught, stored in the
  `Task`, rethrown by `GetResult()` at the caller's `await` with the original
  stack trace kept.
- **Each `await` adds a state number and a branch.** Five awaits: states 0–4,
  still one heap object per call.
- **Context travels with the resume.** The execution context (`AsyncLocal`,
  culture — later: `execution-context-and-asynclocal`, tier 3) always; a
  captured `SynchronizationContext`, if one exists, decides *where* the
  continuation runs (later: `synchronization-context-and-configureawait`,
  tier 2). ASP.NET Core has none, so continuations run on the pool.

## Where it breaks

*So the method is split at every `await` and exceptions travel in the `Task`.
Where does the split surprise people in production?*

**Fire-and-forget** — calling an async method and never awaiting its `Task`.
**`async void`** — an async method with no `Task`, so its exceptions have
nowhere to be stored (later: `async-exceptions-and-async-void`, tier 2).

1. **Validation that does not throw at the call.** Code before the first
   `await` is inside `MoveNext`'s `try` too, so `throw new
   ArgumentNullException(...)` lands in the `Task` and surfaces at the `await`
   — or never, if fire-and-forget. Fix where it matters: a non-async outer
   method validates and throws, then returns an async inner function's call.
2. **Elision inside `using` or `try`.** `using var reader = ...; return
   reader.ReadToEndAsync();` disposes the reader when the method returns,
   while the read is still running — intermittent `ObjectDisposedException`.
   A `try/catch` around an elided return catches nothing; the frame is missing
   from stack traces. Elide only one-line pass-throughs with nothing after
   and nothing to clean up.
3. **`async void`.** An exception is rethrown onto the pool (or a
   `SynchronizationContext`); unhandled on the pool, it **kills the process**.
   Only for event handlers.
4. **`lock` across `await`** does not compile: a lock is owned by the thread
   that took it, and the continuation may resume on another thread. This is
   why `SemaphoreSlim.WaitAsync()` exists — [[semaphoreslim-and-async-locks]].
5. **Blocking on the `Task`** (`.Result`, `.Wait()`) —
   [[glossary#Sync-over-async]]: pool starvation under load; deadlock where a
   `SynchronizationContext` needs the blocked thread to run the continuation
   (later: `async-deadlocks`, tier 2).
6. **Hoisted locals keep memory alive.** A local crossing an `await` is a field
   of the heap object, so what it references stays reachable for the whole
   wait. A 100 KB buffer held across awaits × 5,000 requests in flight ≈
   500 MB, all LOH. Symptom: memory scales with *concurrency*, falls when
   traffic drains; `!gcroot` paths run through `AsyncStateMachineBox`.
7. **Measuring in Debug.** Debug generates a **class** and hoists *every*
   local for the debugger — every call allocates, even synchronous
   completions. Measure async cost in Release.

| Symptom | Likely cause |
|---|---|
| Process dies, unhandled exception on a pool thread, no caller in the trace | `async void` (3) |
| `ObjectDisposedException`, only sometimes | elision inside `using` (2) |
| Memory rises with concurrent requests, falls when idle, rooted via state-machine boxes | hoisted large locals (6) |
| Threads climbing, CPU low, requests stuck | sync-over-async (5) |

## In practice

*So you know what each call costs and where it goes wrong. A decision that
needs all of it.*

A hot method, ~40,000 calls/s, 95% cache hits, misses ~2 ms:

```csharp
public async Task<Product> GetProductAsync(int id)
{
    if (_cache.TryGetValue(id, out Product p)) return p;   // no await reached
    p = await _db.LoadProductAsync(id);                    // real pause
    _cache.Set(id, p, TimeSpan.FromMinutes(5));
    return p;
}
```

A Release allocation profile shows `Task<Product>` and `AsyncStateMachineBox`
high by object count. Proposals: "`.Result` on misses" and "`ValueTask`
everywhere".

1. **Per path.** A hit never reaches an `await` — state machine on the stack —
   but `Product` is not a cached result, so **one `Task<Product>` (~64 B) per
   hit**. A miss pauses: **one box (~150 B with `id`, `this`, awaiter)**.
2. **Numbers.** 38,000 × 64 B ≈ 2.4 MB/s; 2,000 × 150 B ≈ 0.3 MB/s;
   **~2.7 MB/s**, all short-lived.
3. **Price against the GC.** The gen 0 budget is a **byte** count; compare
   with what the request allocates in total (headers, JSON, driver — commonly
   several KB; measure yours). At ~20 KB per request the four calls are ~0.4 KB,
   **~2%**. They die young and gen 0 cost scales with survivors. Object count
   is not GC cost.
4. **Reject `.Result`.** 2,000/s × 2 ms ≈ 4 threads blocked on average; a DB
   spike to 200 ms makes it ~400, against an injection rate of one or two per
   second — starvation, to save 0.3 MB/s.
5. **The two real options.** *Cache the `Task<Product>`* — hits return the
   stored completed task, zero allocation, internal change only, and
   concurrent misses on one id share a single load; cost: evict faulted or
   cancelled tasks, never cache a task one caller's token can cancel.
   *`ValueTask<Product>`* — zero allocation on hits, but the signature changes
   for every caller, it may be awaited once, `WhenAll` needs `.AsTask()`, and
   misses still allocate the box.

**Decision:** measure the share of allocated *bytes* first. Under a few
percent, leave it. If it matters, cache the `Task<Product>` — no public change,
one testable eviction rule. `ValueTask` only at a boundary you own end to end.
`.Result` never.

## Drill — 2026-10-02

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | `LoadAsync` prints `1`, returns early on a cache hit, else awaits HTTP and prints `3`; the caller prints `2` after the call. Order on a miss and on a hit, and which run on the caller's thread? | Miss: 1, 2, 3 — correct. Hit: "1, 3, 2", all on one thread — but the early `return s` means `3` never prints; a hit gives 1, 2 with a completed task. Also said that on a miss the initial thread "returns to the pool" at the `await`; it returns to the *caller*, which is what prints `2` | miss |
| 2 | When would you elide `async`/`await`, and what do you give up? | Passed; said the layers had covered only the `using` case | miss |
| 3 | At the first real pause, what happens to the state machine and its locals — and why do five pausing awaits still allocate one object? | Skipped at the user's request | skipped |

Drill results do not change a level.

## Model answers — 2026-10-02

No interview has graded this concept yet, so there are no below-target
questions to answer. Drill Q2, as a strong answer would say it:

> Elide only a one-line pass-through — the method does nothing but call
> another async method and return its `Task`, with nothing after the call and
> nothing to clean up. That saves the state machine and, on a pause, its
> allocation, which matters only on a hot path. What you give up: any `using`
> or `try/finally` runs when the method returns, not when the work finishes,
> so the resource is disposed under the running operation; a `try/catch`
> around the return catches nothing, since the exception arrives later inside
> the `Task`; exceptions thrown synchronously by the inner call escape at the
> call site instead of inside the `Task`; and the eliding method's frame is
> missing from the stack trace. Default to `async`/`await`; elide as a
> measured optimisation.

## Resources

## Related

[[parallelism-vs-concurrency]] · [[thread-pool-internals]] · [[semaphoreslim-and-async-locks]] · [[stack-vs-heap-layout]]
