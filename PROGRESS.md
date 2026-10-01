# Progress

Generated 2026-10-01 by `scripts/progress.ps1`. Do not edit — regenerate.

**Focus:** .NET · cluster: async-and-threading

## Calibration checkpoint

Interview sessions: **7 / 5** (of which 4 coached).
Self-flagged-weak answers graded L3+: **0**.

## Softness — last 7 interview sessions

| Session | Date | Mode | Target avg | Awarded avg | Gap | Disputes |
|---|---|---|---|---|---|---|
| [[2026-09-08-gc-generations]] | 2026-09-08 | exam | 2.70 | 0.30 | 2.40 | 0 |
| [[2026-09-12-gc-triggers-and-budgets]] | 2026-09-12 | exam | 2.80 | 1.60 | 1.20 | 0 |
| [[2026-09-13-gc-triggers-and-budgets]] | 2026-09-13 | exam | 3.40 | 2.40 | 1.00 | 0 |
| [[2026-09-17-gc-generations-and-loh]] | 2026-09-17 | coached | 3.40 | 2.30 | 1.10 | 0 |
| [[2026-09-18-finalization-and-stack-layout]] | 2026-09-18 | coached | 2.80 | 2.20 | 0.60 | 0 |
| [[2026-09-30-async-and-threading-tier-1-2]] | 2026-09-30 | coached | 3.80 | 1.50 | 2.30 | 0 |
| [[2026-09-30-async-and-threading-tier-1]] | 2026-09-30 | coached | 4.00 | 1.50 | 2.50 | 0 |

Older half → newer half: target 2.97 → 3.50 (+0.53), awarded 1.43 → 1.88 (+0.44).

## .NET

93 concepts · average **L0.19** · last evidence 2026-09-30

| L0 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| 84 | 1 | 7 | 1 | 0 | 0 |

| Cluster | Concepts | Avg | L0 | ≥L3 | Last evidence |
|---|---|---|---|---|---|
| Memory and GC | 13 | L1.00 | 7 | 1 | 2026-09-18 |
| C# language internals | 10 | L0.00 | 10 | 0 | — |
| Async and threading | 18 | L0.28 | 15 | 0 | 2026-09-30 |
| Concurrency | 7 | L0.00 | 7 | 0 | — |
| Runtime and type system | 9 | L0.00 | 9 | 0 | — |
| Performance and diagnostics | 11 | L0.00 | 11 | 0 | — |
| Dependency injection and hosting | 8 | L0.00 | 8 | 0 | — |
| Data access and EF Core internals | 11 | L0.00 | 11 | 0 | — |
| HTTP, networking, and resilience | 6 | L0.00 | 6 | 0 | — |

**Gaps:** open 48 · studying 0 · taught 12 · verified 10 · regressed 0

Open for more than 7 days:

- [[parallelism-vs-concurrency]] — drill miss: classifies I/O `Task.WhenAll` as concurrency and estimates ~8 threads correctly, but both reasons are wrong — gives "we do not create threads explicitly" as the criterion rather than the work holding no thread while waiting, and treats core count as a cap on pool threads rather than a rough proxy for how many continuations run at once (since 2026-09-20)
- [[parallelism-vs-concurrency]] — drill miss: declined to trace an awaited I/O call from issue to resumption — no OS completion port or epoll registration, no release of the pool thread, no statement that nothing holds a thread during the wait, no completion dispatching `MoveNext` on a different thread. Taught in this session; distinct from `async-state-machine`, which is untaught (since 2026-09-20)
- [[parallelism-vs-concurrency]] — design answers are not quantified: restructures the batch job correctly but gives no payoff figure when asked directly. Second occurrence — see the 2026-09-19 drill miss on [[threads-and-scheduling]], where the capacity arithmetic was also absent (since 2026-09-20)
- [[finalization-and-freachable-queue]] — does not know the freachable queue is a root: cannot say the object and its whole graph are re-marked live and promoted, so the second collection is a gen 1 or gen 2 one; inverts the direction, saying the object "has a reference to the finalize queue" (since 2026-09-18)
- [[finalization-and-freachable-queue]] — describes `GC.SuppressFinalize` as preventing registration; registration already happened at `new`, and the flag makes the GC skip the existing entry (since 2026-09-18)
- [[finalization-and-freachable-queue]] — answers the clean-shutdown case with the crash; needed a probe to state that .NET 5+ does not run pending finalizers at process exit (since 2026-09-18)
- [[finalization-and-freachable-queue]] — chooses `SafeHandle` over `GC.KeepAlive` on ergonomics alone; cannot name the marshaller’s ref-counting across P/Invoke as what makes the fix structural, nor `CriticalFinalizerObject`. Second occurrence — see the 2026-09-17 drill miss (since 2026-09-18)
- [[finalization-and-freachable-queue]] — cannot say why Debug hides an early-collection bug — unoptimised code reports locals live to method end — and does not address Tier-0 in Release; passed on the probe (since 2026-09-18)
- [[stack-vs-heap-layout]] — cannot say what `in` costs on a non-`readonly` struct — a defensive copy at every member access — and does not name `readonly struct` or `readonly` members as the fix (since 2026-09-18)
- [[stack-vs-heap-layout]] — calls 5 x 64 bytes of by-value copying "allocation", and does not name the compiler’s defensive copy to a stack temporary as the mechanism behind the lost counter (since 2026-09-18)
- [[stack-vs-heap-layout]] — states the placement rule as "value types on the stack, reference types on the heap" rather than "a value lives where its container lives"; does not mention enregistration, giving "on the stack" as certain (since 2026-09-18)
- [[gc-generations]] — does not say that evicted cache entries become garbage inside gen 2, reclaimable only by a full collection; priced the options only when prompted (since 2026-09-17)
- [[gc-generations]] — states twice that survivors are compacted "to the end" of the generation; they are compacted down against gen 1 and the boundary slides up above them (since 2026-09-17)
- [[gc-generations]] — does not know that a full ephemeral segment is retired into gen 2 and a fresh one started (two probes needed), and does not place gen 2 in its own segments (since 2026-09-17)
- [[gc-generations]] — inverts the .NET 7 regions model: says each region is split across the three generations rather than each region belonging to one generation (since 2026-09-17)
- [[large-object-heap]] — cannot name what is false in calling the LOH "generation 3" — nothing ever ages into or out of it; argued instead that the shared escalation to a gen 2 collection is the falsehood (since 2026-09-17)
- [[large-object-heap]] — no discriminating measure for fragmentation: total free space rising while the largest contiguous free block stays flat; treats gen 2 and the LOH as one pool, and does not mention that adjacent free blocks coalesce (since 2026-09-17)
- [[large-object-heap]] — design answer neither costed nor bounded: no pooling and no pricing of its hazards, no incremental hashing, and no memory ceiling (concurrency x buffer size) when asked for it directly (since 2026-09-17)
- [[large-object-heap]] — does not price `StringBuilder.ToString()` — it allocates the large string and copies every chunk, so both are live at once (since 2026-09-17)
- [[stack-vs-heap-layout]] — does not apply 8-byte object alignment even when told to, and gives the array length slot as 4 bytes rather than 8; shallow versus retained size unknown (since 2026-09-17)
- [[gc-triggers-and-budgets]] — does not state that the budget is a byte count, so cannot explain why fewer allocations mean fewer collections of unchanged cost (since 2026-09-17)
- [[boxing]] — does not count the `params object[]` as an allocation separate from the boxes (three per call), and describes the `[LoggerMessage]` source generator as a compile-time level check rather than a strongly-typed delegate that removes the boxing entirely (since 2026-09-17)
- [[finalization-and-freachable-queue]] — drill miss: cannot trace a blocked finalizer thread to OOM — no single finalizer thread, no freachable queue as a root keeping the objects and their graphs alive and promoted, and no dump signature separating it from a static-rooted leak (`!gcroot` path from a static vs a ready-for-finalization count plus a waiting finalizer stack) (since 2026-09-17)
- [[finalization-and-freachable-queue]] — drill miss: picks `SafeHandle` over a hand-written finalizer only as "standard, more optimised" — cannot price the hand-written finalizer at thousands of objects per minute (slow-path allocation, extra GC and promotion of the whole graph, no ref-counting across P/Invoke) nor the `SafeHandle` cost (one extra small object per handle) (since 2026-09-17)
- [[finalization-and-freachable-queue]] — drill miss: spots no ordering and a blocked finalizer thread in a flushing finalizer, but gives no replacement (`IDisposable`, no finalizer, flush in `Dispose`, `FileStream`'s `SafeFileHandle` is the net, a finalizer may never run) and believes finalizers run during the GC (since 2026-09-17)
- [[stack-vs-heap-layout]] — drill miss: cannot say how the GC knows a reference is dead before the method returns — no JIT GC info, no stack walk — gives no reason Debug keeps locals alive longer, and does not address Tier-0 code in Release (since 2026-09-15)
- [[stack-vs-heap-layout]] — drill miss: rejects a class-to-struct change for the right costs (copying, interface boxing) but cannot state what it gains — no per-element header or reference, one array instead of N objects, contiguity, less mark work — nor the conditions to approve it (since 2026-09-15)
- [[stack-vs-heap-layout]] — drill miss: places a lambda-captured local on the stack rather than in a heap closure object; nests a referenced object's contents "inside" its owner instead of following the references (`Order` → `List<int>` → `int[]`) (since 2026-09-15)
- [[gc-triggers-and-budgets]] — cannot say what to measure to confirm a change in allocation or budget; declined the measurement half of Q1 and omitted it again in the Q10 design (since 2026-09-13)
- [[gc-triggers-and-budgets]] — Q10 design: gen 2 never identified as the p99 latency risk, and no trade-off stated for the configuration chosen (since 2026-09-13)
- [[boxing]] — believes the boxes behind a `List<object>` sit contiguously and live on the LOH; they are 24-byte objects scattered on the small object heap. Held under two probes (since 2026-09-13)
- [[boxing]] — states generic specialisation happens at compile time; it happens at runtime when the JIT creates the instantiation. Third occurrence (since 2026-09-13)
- [[boxing]] — derives the 24-byte box size by assertion rather than arithmetic, and attributes the padding to a minimum width for the value field rather than 8-byte object alignment (since 2026-09-13)
- [[gc-generations]] — describes the write barrier as checking for old-to-young references rather than recording that an old location was written (since 2026-09-13)
- [[large-object-heap]] — drill miss: chooses pooling over forced compaction for the right reason, but does not price the option chosen — complexity, plus use-after-return or never-returned buffers (since 2026-09-13)
- [[large-object-heap]] — drill miss: links per-request large buffers to more frequent gen 2 collections without naming the separate LOH budget as the trigger, and does not say why gen 0 and gen 1 counts are unchanged (since 2026-09-13)
- [[boxing]] — drill miss: identifies the boxing in a struct-keyed dictionary but not its scale — does not know the fallback comparer boxes BOTH operands per comparison, nor that the hash dispatch boxes too (~7 per lookup, not 1) (since 2026-09-12)
- [[boxing]] — drill miss: picks the generic constraint over the interface parameter for the right reason, but cannot say what it costs — one JIT instantiation per value type, and the loss of a single heterogeneous call site (since 2026-09-12)
- [[gc-triggers-and-budgets]] — drill miss: cannot say what capping `GCHeapCount` does to per-heap budgets, nor that the container heap hard limit defaults to 75% of the container limit (since 2026-09-12)

## Review queue

9 scheduled · **6 overdue** · 3 due in the next 7 days.

| Concept | Topic | Due | Days overdue |
|---|---|---|---|
| [[gc-generations]] | dotnet | 2026-09-20 | 11 |
| [[gc-triggers-and-budgets]] | dotnet | 2026-09-20 | 11 |
| [[large-object-heap]] | dotnet | 2026-09-20 | 11 |
| [[finalization-and-freachable-queue]] | dotnet | 2026-09-21 | 10 |
| [[stack-vs-heap-layout]] | dotnet | 2026-09-21 | 10 |
| [[boxing]] | dotnet | 2026-09-24 | 7 |

Due soon: [[thread-pool-internals]] 2026-10-02 · [[threads-and-scheduling]] 2026-10-02 · [[parallelism-vs-concurrency]] 2026-10-03

## Activity

| Window | Interview | Teach | Study | Review |
|---|---|---|---|---|
| Last 7 days | 2 | 2 | 0 | 0 |
| Last 30 days | 7 | 12 | 0 | 1 |
| All time | 7 | 12 | 0 | 1 |

Excursions: 0 of 7 interview sessions.
Last session: 2026-10-01 — teach — thread-pool-internals.
Last weekly review: [[2026-09-18]].
