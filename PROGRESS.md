# Progress

Generated 2026-09-20 by `scripts/progress.ps1`. Do not edit — regenerate.

**Focus:** .NET · cluster: async-and-threading

## Calibration checkpoint

Interview sessions: **5 / 5** (of which 2 coached).
Self-flagged-weak answers graded L3+: **0**.

## Softness — last 5 interview sessions

| Session | Date | Mode | Target avg | Awarded avg | Gap | Disputes |
|---|---|---|---|---|---|---|
| [[2026-09-08-gc-generations]] | 2026-09-08 | exam | 2.70 | 0.30 | 2.40 | 0 |
| [[2026-09-12-gc-triggers-and-budgets]] | 2026-09-12 | exam | 2.80 | 1.60 | 1.20 | 0 |
| [[2026-09-13-gc-triggers-and-budgets]] | 2026-09-13 | exam | 3.40 | 2.40 | 1.00 | 0 |
| [[2026-09-17-gc-generations-and-loh]] | 2026-09-17 | coached | 3.40 | 2.30 | 1.10 | 0 |
| [[2026-09-18-finalization-and-stack-layout]] | 2026-09-18 | coached | 2.80 | 2.20 | 0.60 | 0 |

Older half → newer half: target 2.75 → 3.20 (+0.45), awarded 0.95 → 2.30 (+1.35).

## .NET

93 concepts · average **L0.14** · last evidence 2026-09-18

| L0 | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| 87 | 0 | 5 | 1 | 0 | 0 |

| Cluster | Concepts | Avg | L0 | ≥L3 | Last evidence |
|---|---|---|---|---|---|
| Memory and GC | 13 | L1.00 | 7 | 1 | 2026-09-18 |
| C# language internals | 10 | L0.00 | 10 | 0 | — |
| Async and threading | 18 | L0.00 | 18 | 0 | — |
| Concurrency | 7 | L0.00 | 7 | 0 | — |
| Runtime and type system | 9 | L0.00 | 9 | 0 | — |
| Performance and diagnostics | 11 | L0.00 | 11 | 0 | — |
| Dependency injection and hosting | 8 | L0.00 | 8 | 0 | — |
| Data access and EF Core internals | 11 | L0.00 | 11 | 0 | — |
| HTTP, networking, and resilience | 6 | L0.00 | 6 | 0 | — |

**Gaps:** open 41 · studying 0 · taught 3 · verified 8 · regressed 0

Open for more than 7 days:

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

8 scheduled · **4 overdue** · 4 due in the next 7 days.

| Concept | Topic | Due | Days overdue |
|---|---|---|---|
| [[gc-generations]] | dotnet | 2026-09-20 | 0 |
| [[gc-triggers-and-budgets]] | dotnet | 2026-09-20 | 0 |
| [[large-object-heap]] | dotnet | 2026-09-20 | 0 |
| [[threads-and-scheduling]] | dotnet | 2026-09-20 | 0 |

Due soon: [[finalization-and-freachable-queue]] 2026-09-21 · [[parallelism-vs-concurrency]] 2026-09-21 · [[stack-vs-heap-layout]] 2026-09-21 · [[boxing]] 2026-09-24

## Activity

| Window | Interview | Teach | Study | Review |
|---|---|---|---|---|
| Last 7 days | 2 | 4 | 0 | 1 |
| Last 30 days | 5 | 9 | 0 | 1 |
| All time | 5 | 9 | 0 | 1 |

Excursions: 0 of 5 interview sessions.
Last session: 2026-09-20 — teach — parallelism-vs-concurrency.
Last weekly review: [[2026-09-18]].
