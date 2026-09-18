# Roadmap

Last updated: 2026-09-07

## Focus

**Focus topic:** .NET
**Focus cluster:** none

The focus decides what a session proposes by default. It is not a lock and not
a ranking — change it by editing the two lines above. A focus cluster is
optional steering inside the topic; leave it `none` to let the proposal rules
in `CLAUDE.md` pick.

## Topics

Not an order, not closed. Topics, clusters, and concepts get added when
wanted. A topic gets a folder on first excursion or when it becomes the focus.

| Topic | Folder | Excursions | Notes |
|---|---|---|---|
| .NET | `topics/dotnet/` | — | Working stack. Honest priors here, so it is the right place to find out whether the grading is calibrated. |
| System design | — | 0 | High interview leverage. |
| DevOps | — | 0 | Adjacent to daily work, currently shallow. |
| Web fundamentals | — | 0 | Underpins both frontend and system design. |
| Frontend | — | 0 | Breadth, not depth. Lower bar than the rest. |
| Interview prep | — | 0 | Draws on all of the above. |

## .NET

Scope, resources, and the full concept tree are in `topics/dotnet/TOPIC.md`
and `topics/dotnet/mastery.md`.

**Clusters**, in suggested path order (soft — see `TOPIC.md`):

1. Memory and GC
2. C# language internals
3. Async and threading
4. Concurrency
5. Runtime and type system
6. Performance and diagnostics
7. Dependency injection and hosting
8. Data access and EF Core internals
9. HTTP, networking, and resilience

Not on the starting list, add when wanted: ASP.NET Core pipeline; I/O,
buffers, and serialization; cloud SDKs.

#### Memory and GC — working order, decided 2026-09-13

Priority for the rest of the cluster, in `mastery.md` row order:

1. `stack-vs-heap-layout` — needs teaching first; overdue and blocking
2. `finalization-and-freachable-queue` — needs teaching first; overdue and
   blocking. The Dispose-versus-finalizer question is common in interviews
3. `span-and-memory`
4. `gc-modes`
5. `card-table-and-write-barrier` — rarely asked directly, but it is what
   separates a real answer on generational cost from a recited one
6. `stackalloc-and-ref-structs` — pair it with Span

**Deprioritised, revisit on request:** `gc-pauses-and-latency-modes`,
`gc-regions-and-configuration`, `pinning-and-gc-handles`. Judged niche for the
roles being targeted. They keep their rows and their L0 levels, sit last in row
order, and come back when the user asks — not automatically on finishing the
cluster.

Note for `weekly-review`: this is a reprioritisation by interview value, made
while levels were rising, not avoidance of a cluster that got hard. Two L2s were
earned the same day.

Unresolved: the topic's stated goal is production-debugging depth, while this
ordering optimises for interviews. If interviews are the real objective, that
framing belongs in `BOOTSTRAP.md` first.

### Definition of done

Cold and unaided at a whiteboard:

1. Draw the generational GC and say what triggers and pauses each collection
   kind.
2. Draw the async state machine and trace a continuation through the thread
   pool.
3. Argue whether a given lock-free pattern is safe under the memory model.
4. Reason from a described production symptom to a runtime cause.
5. Trace a LINQ query from expression tree to SQL and back to tracked
   entities, and say where each layer can silently cost a round trip.

Each demonstrated unprompted in a session and linked from
`topics/dotnet/mastery.md`. This is a description of what the topic is for,
not a gate on studying anything else.

## Excursions

A session on a topic other than the focus. Graded, logged, queued, and written
back like any other — no lightweight mode. On first excursion the topic's
folder is created and only the concepts touched are enumerated, plus their
obvious siblings. The excursion count above goes up.

`weekly-review` names the pattern when excursions outweigh the focus topic, or
when a focus-topic cluster sits untouched while excursions continue.

## Calibration checkpoint

After five interview sessions of **either mode** — coached sessions started
counting on 2026-09-18, see `BOOTSTRAP.md` §6 and §9 — did any answer the user
self-flagged as weak receive L3 or above? The self-assessment recorded in each
session file is the data. If yes, tighten the rubric anchors in `CLAUDE.md`
before adapting this system for anyone else. A checkpoint closed largely by
coached sessions is weaker evidence than one closed by exam sessions, because
a coached self-assessment is made after the corrections were shown; the mode
column in `PROGRESS.md`'s softness table says which kind closed it.

Status is computed — see the "Calibration checkpoint" section of
`PROGRESS.md`. Nothing here to keep in sync.
