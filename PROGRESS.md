# Progress

Generated 2026-09-19 by `scripts/progress.ps1`. Do not edit — regenerate.

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

**Gaps:** open 38 · studying 0 · taught 2 · verified 8 · regressed 0

Open for more than 7 days:

- [[boxing]] — drill miss: identifies the boxing in a struct-keyed dictionary but not its scale — does not know the fallback comparer boxes BOTH operands per comparison, nor that the hash dispatch boxes too (~7 per lookup, not 1) (since 2026-09-12)
- [[boxing]] — drill miss: picks the generic constraint over the interface parameter for the right reason, but cannot say what it costs — one JIT instantiation per value type, and the loss of a single heterogeneous call site (since 2026-09-12)
- [[gc-triggers-and-budgets]] — drill miss: cannot say what capping `GCHeapCount` does to per-heap budgets, nor that the container heap hard limit defaults to 75% of the container limit (since 2026-09-12)

## Review queue

7 scheduled · **0 overdue** · 7 due in the next 7 days.

Due soon: [[gc-generations]] 2026-09-20 · [[gc-triggers-and-budgets]] 2026-09-20 · [[large-object-heap]] 2026-09-20 · [[threads-and-scheduling]] 2026-09-20 · [[finalization-and-freachable-queue]] 2026-09-21 · [[stack-vs-heap-layout]] 2026-09-21 · [[boxing]] 2026-09-24

## Activity

| Window | Interview | Teach | Study | Review |
|---|---|---|---|---|
| Last 7 days | 3 | 5 | 0 | 1 |
| Last 30 days | 5 | 8 | 0 | 1 |
| All time | 5 | 8 | 0 | 1 |

Excursions: 0 of 5 interview sessions.
Last session: 2026-09-19 — teach — threads-and-scheduling.
Last weekly review: [[2026-09-18]].
