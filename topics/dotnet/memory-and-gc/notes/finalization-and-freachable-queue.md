---
concept: finalization-and-freachable-queue
topic: dotnet
cluster: memory-and-gc
created: 2026-09-12
taught: 2026-09-17
---

# Finalization and the freachable queue

## Mechanism

### Two unrelated cleanup paths

```csharp
class NativeBuffer : IDisposable
{
    private IntPtr _ptr = Marshal.AllocHGlobal(1_000_000);   // native memory, invisible to the GC

    public void Dispose()          // path 1: deterministic, called by your code
    {
        Marshal.FreeHGlobal(_ptr);
        GC.SuppressFinalize(this);
    }

    ~NativeBuffer()                // path 2: finalizer, called by the runtime
    {
        Marshal.FreeHGlobal(_ptr);
    }
}
```

- **`Dispose()`** — an ordinary method. Runs when your code calls it (directly
  or via `using`), **on your thread, immediately**. The GC knows nothing about
  it.
- **Finalizer** (`~NativeBuffer()`) — compiles to an override of
  `Object.Finalize()`. Never called by your code. The **runtime** calls it on
  **one dedicated thread**, some time after a GC finds the object unreachable.
  A safety net for when nobody called `Dispose`.
- **The GC never calls `Dispose`.** A finalizer does whatever its body says.

### Lifecycle of a finalizable object

A **finalizable object** is an instance of a type that overrides `Finalize`.

1. **At `new`.** The runtime records a pointer to it in the **finalization
   queue** — a runtime-internal list of every live finalizable object.
   Registration takes the allocator's slow path. **This list is not a root**;
   being on it keeps nothing alive.
2. **GC #1 — the object is unreachable.**

```
 mark from roots ──► NativeBuffer not marked (dead)
        │
        v
 scan the finalization queue: entries pointing at unmarked objects?
        │  yes — NativeBuffer
        v
 move the entry ──► FREACHABLE QUEUE   ("f-reachable": reachable only for finalization)
        │
        v
 the freachable queue IS a root, so mark again from it:
 NativeBuffer and EVERYTHING IT REFERENCES are live again
        │
        v
 they survive this GC and are promoted (gen 0 -> gen 1)
        │
        v
 GC finishes and signals the finalizer thread
```

3. **The finalizer thread** — one per process, dedicated. Dequeues objects from
   the freachable queue one at a time and calls `Finalize()`.
   - Runs **concurrently with application threads, after the GC completes** —
     cleanup is **not** done when the GC is done.
   - **No ordering** between objects.
   - After `Finalize()` returns the entry is removed; the object is unreachable
     again.
4. **GC #2 of its new generation.** No queue, no root — reclaimed. That
   generation is now gen 1 or gen 2, so this can be much later.

**Minimum cost of a missed `Dispose`:** two GCs, one promotion, one finalizer
run — for the object and everything it references.

### What `Dispose` changes

- **`GC.SuppressFinalize(this)`** flags the object so the GC skips its
  finalization-queue entry. It dies in **one** GC like any other object — no
  freachable step, no promotion.
- **`GC.ReRegisterForFinalize(obj)`** clears that flag.
- **`GC.WaitForPendingFinalizers()`** blocks until the freachable queue drains.
  For tests, not production.

### The undisposed `FileStream`

- `FileStream` holds a **`SafeFileHandle`**, a small class wrapping the OS
  handle, with its own finalizer.
- Scope exit does nothing.
- At the next GC of the generation holding them, both are unreachable. Both are
  finalizable, so both move to the freachable queue.
- The **finalizer thread** runs `SafeFileHandle`'s finalizer, which closes the
  OS handle — not the opening thread, not the thread pool.
- Until then the file stays open and locked.

### SafeHandle and critical finalizers

- **`SafeHandle`** — abstract class wrapping one OS handle, finalizer already
  written and hardened. Derives from **`CriticalFinalizerObject`**: its
  finalizer is prepared ahead of time and critical finalizers run after
  ordinary ones. A class holding a `SafeHandle` needs **no finalizer of its
  own**.
- **.NET Core / .NET 5+ do not run finalizers at process exit.** Anything
  pending at shutdown is never finalized.

## Failure modes

- **Handle leak that looks like nothing.** Undisposed files, sockets, DB
  connections stay open until a GC happens and the finalizer thread gets to
  them. Symptom: "file in use", connection-pool timeouts, socket exhaustion,
  with memory looking fine. Worst in low-allocation services, which rarely GC.
- **Blocked finalizer thread.** There is one. A finalizer that blocks — a lock,
  `.Result` on a `Task`, a slow network close — stalls every pending finalizer
  in the process. The freachable queue grows and **everything reachable from
  those objects** stays alive. Symptom: steady memory growth, eventually
  `OutOfMemoryException`.
  - vs an ordinary leak: in a dump, SOS `!finalizequeue` shows a large "ready
    for finalization" count and the finalizer thread's stack is in a wait. An
    ordinary leak shows a real strong path from a static in `!gcroot`.
- **Allocation outruns finalization.** Fast finalizers, but finalizable objects
  are created faster than one thread can drain them. Same growth, no stuck
  stack.
- **Exception in a finalizer.** Unhandled on the finalizer thread → the process
  terminates.
- **Finalizer touches other managed objects.** No ordering: the `FileStream` it
  wants to flush may already be finalized. Release only the **unmanaged**
  resource owned directly.
- **Finalized while still in use.** The JIT ends a reference's liveness at its
  last use, so the finalizer can run while a native call still uses the
  handle. Fix: `GC.KeepAlive(obj)` after the call, or `SafeHandle`, which
  ref-counts across P/Invoke. See [[stack-vs-heap-layout]].
- **Partly constructed objects.** Registration happens at `new`, so if the
  constructor throws, the finalizer still runs later on fields that were never
  set.
- **Resurrection.** A finalizer storing `this` somewhere reachable revives the
  object; its finalizer will not run again unless re-registered. Almost always
  a bug.

## Trade-offs

- **`Dispose` / `using`:** deterministic, on your thread, zero GC cost. Weakness:
  every caller must remember it.
- **Finalizer:** safety net that works when callers forget. Paid for with:
  - slow-path allocation
  - every instance survives at least one extra GC and is promoted, **with its
    whole object graph** — short-lived data sent to gen 2
  - one shared thread for the whole process
  - no timing guarantee, no ordering, nothing at process exit
- **`SafeHandle`:** the safety net pre-built. Cost: one small extra object per
  handle.
- **What to write:**
  1. **Holds only managed disposables** (`FileStream`, `DbConnection`) →
     `IDisposable`, **no finalizer**. Their own finalizers or `SafeHandle`s are
     the net.
  2. **Owns a raw OS handle or native memory** → wrap it in a `SafeHandle`
     subclass; the outer class again gets `IDisposable` and no finalizer.
  3. **Hand-written finalizer** only where `SafeHandle` does not fit, with the
     full `Dispose(bool disposing)` pattern: `Dispose()` calls `Dispose(true)`
     then `GC.SuppressFinalize(this)`; the finalizer calls `Dispose(false)`,
     which releases unmanaged state only.
- **Never for flushing, logging or telemetry.** Those need deterministic
  `Dispose` or a shutdown hook — a finalizer may never run, and runs on a
  thread you do not own.

## Drill — 2026-09-17

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | Review a `CsvExporter` finalizer that writes the buffer, flushes and disposes its `FileStream`; what is wrong, and what to write instead? | Named no ordering (stream may already be finalized) and blocking the finalizer thread. Gave no replacement; claimed the finalizer allocates "during garbage collection" | miss |
| 2 | Native codec handle, thousands per minute, some undisposed: `IDisposable` only vs hand-written finalizer vs `SafeHandle` — choose and price the others | Chose `SafeHandle`; (a) leaks. (b) vs (c) only "standard, more optimised" — no per-instance finalization cost at this rate, no cost of (c), no P/Invoke ref-counting | miss |
| 3 | Memory climbs to OOM at flat allocation rate; ~400k ready for finalization, finalizer thread in `Task.Wait` inside `~TelemetryBatch()` — trace it and tell it apart from a static leak | "Something is stuck in the freachable queue and the finalizer can't free this memory"; static-held memory is not reclaimed. No single finalizer thread, no freachable queue as a root keeping graphs alive and promoted, no dump signature | miss |

Drill results do not change a level.

## Model answers — 2026-09-17

### Q7 (2026-09-12) — target L2, awarded L1

**Question:** You open a `FileStream`, never call `Dispose`, and never use a
`using`. The local variable goes out of scope. When does the OS file handle get
released, and what decides that?

**Model answer:** Scope exit does nothing. `FileStream` holds a
`SafeFileHandle`, which has a finalizer. At the next GC of the generation they
live in, both are unreachable; the GC finds their finalization-queue entries and
moves them to the freachable queue. That queue is a root, so both survive this GC
and are promoted. After the GC finishes, the process's single dedicated finalizer
thread runs `SafeFileHandle`'s finalizer, which closes the OS handle. Release
therefore depends on when that generation is next collected and when the
finalizer thread reaches the object — not the opening thread, not the thread
pool, and `Dispose` is never called. The memory is reclaimed at a later GC; if
the process exits first, nothing runs.

**Lacked:** the finalizer, not `Dispose`, as the mechanism; the dedicated
finalizer thread; survival of the first GC through the freachable queue.

## Resources

## Related

[[stack-vs-heap-layout]] · [[gc-generations]] · [[gc-triggers-and-budgets]]
