# Roadmap

Last updated: 2026-09-18

## Focus

**Focus topic:** .NET
**Focus cluster:** async-and-threading

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

**Clusters**, in **interview-frequency order** — reordered 2026-09-18 from the
original dependency order. Rationale, the evidence, and the limits of that
evidence: `BOOTSTRAP.md` §4, "Reordered by interview evidence". Still soft;
nothing is gated.

| # | Cluster | Rows | Why here |
|---|---|---|---|
| 1 | Async and threading | 12 | The only topic rated major by **every** structured source surveyed, and rated harder at senior level. The recurring questions are scenario-shaped: thread-pool starvation ("times out under load, CPU at 15%"), sync-over-async deadlock, bounded concurrency over a downstream API, cancellation. |
| 2 | Performance and diagnostics | 11 | "Production incident diagnosis" is a question bucket that does not exist at junior level at all. Also the cluster that makes Memory and GC pay: "walk me through finding the leak" is answered with `dotnet-counters` then `dotnet-dump`, `dumpheap -stat` and `gcroot`, none of which is in the vault yet. |
| 3 | Dependency injection and hosting | 8 | Captive dependency and `IServiceScopeFactory` in background services were called "near-certain" in a senior loop and appeared in every source covering DI. Smallest cluster on the list, highest hit-rate per concept, and it unblocks the `DbContext` lifetime questions in 4. |
| 4 | Data access and EF Core internals | 11 | Named **the** senior-versus-mid filter by three independent sources, and given the largest single share in an evidence-weighted split. N+1, captive `DbContext`, `AsNoTracking`, concurrency conflicts, migrations at scale. Plain SQL indexing questions land here too. |
| 5 | Concurrency | 10 | Rated harder at senior, but the asked form is "pick between `lock`, `SemaphoreSlim` and `Interlocked` and defend it", not the memory model. The deep end — ABA, lock-free and wait-free structures, acquire/release semantics — surfaced mainly in general-CS sources, not .NET ones. Expect to stop short of the last few rows. |
| 6 | ASP.NET Core pipeline | — | **Cluster does not exist yet**; create it on the first session, do not pre-scaffold. Middleware order, filters versus middleware, `HttpContext` across an `await`, the Options-pattern variants, Kestrel and reverse proxies. Ranked here and not higher because the sources themselves frame middleware ordering as separating *junior from mid*, not mid from senior. |
| 7 | C# language internals | 10 | Rated major by most sources but explicitly **less** asked as standalone questions at senior level — treated as assumed baseline, resurfacing inside performance questions (struct versus class, boxing). Much of it is already implied by the Memory and GC work. |
| 8 | HTTP, networking, and resilience | 6 | Lowest verified question density of any cluster here. The valuable material — idempotency, retries, circuit breakers — turned up inside *architecture* questions rather than as an HTTP-client topic. See the note below on socket exhaustion. |
| 9 | Memory and GC — remainder | 4 | Closed as a working cluster on 2026-09-18; see below. |
| 10 | Runtime and type system | 9 | JIT, IL, metadata, reflection, generics at runtime, Native AOT. Concentrated in a **single outlier source** that treats "senior" as harder trivia; absent from every source calibrated against real loops and from all first-hand accounts. Lowest priority on the list. |

Still not on the list, add when wanted: I/O, buffers, and serialization; cloud
SDKs.

**A verified negative worth recording.** The canonical `HttpClient` /
socket-exhaustion question — the one everyone assumes is a .NET interview
staple — could not be found as a phrased interview question in any compilation
actually fetched; two fetches returned an explicit "not found" for it. Know the
mechanism, but it is not evidence-backed as a high-frequency question, and
cluster 8 is ranked accordingly.

#### System design — the highest-value work is not a .NET cluster

Every research agent independently found **system design to be the most
senior-exclusive topic in the dataset**: absent from junior-tier material
entirely, and the only subject the first-hand accounts confirm as a *separate
interview round* rather than a harder question. The recurring content is
distributed-systems judgment — idempotent consumers and the outbox pattern, why
not two-phase commit, saga orchestration versus choreography, eventual
consistency, service boundaries, cascading failure and bulkheads.

`System design` is a topic in the table above with no folder and zero sessions.
On this evidence it outranks clusters 5 through 10 of .NET. A cluster ordering
cannot express that, which is the honest limitation of this whole section.

**Open decision, not taken here:** whether to start `System design` as a
parallel track now or leave it until the .NET clusters above are done. Starting
it means excursions will outnumber focus sessions, and `weekly-review` will
name that as drift every week until the focus topic changes — correctly, by its
own rules. That is a reason to change the focus topic deliberately rather than
to avoid the work.

#### Memory and GC — closed as a working cluster, 2026-09-18

Stopped at 6 of 13 rows graded: `gc-generations`, `gc-triggers-and-budgets`,
`large-object-heap`, `stack-vs-heap-layout`,
`finalization-and-freachable-queue` at L2, `boxing` at L3. Cluster average
L1.23.

Reason: the 2026-09-18 survey found **zero mentions of deep GC internals — card
tables, write barriers, LOH compaction mechanics, GC regions,
finalization-queue mechanics — across all sixteen sources** one agent fetched,
including the two most GC-heavy. Interviews ask about memory *diagnostically*,
and that material lives in Performance and diagnostics.

Four rows remain unworked and keep their L0 levels:

- `gc-modes` — **the exception, worth finishing on request.** Server versus
  workstation GC and DATAS did appear as asked questions. Cheap, one session.
- `span-and-memory` — asked, but in a *performance* framing ("how do `Span<T>`
  and `Memory<T>` improve performance"). Pick it up inside cluster 2.
- `stackalloc-and-ref-structs` — thin evidence; pair with `span-and-memory` or
  leave.
- `card-table-and-write-barrier` — **zero evidence of ever being asked.** Joins
  the three already deprioritised.

Deprioritised on 2026-09-13 and unchanged: `gc-pauses-and-latency-modes`,
`gc-regions-and-configuration`, `pinning-and-gc-handles`.

Nothing is deleted and no level moves. Everything here comes back on request.

Note for `weekly-review`: this is a second reprioritisation by interview value,
made while levels were rising — two concepts moved L1 to L2 on the day the
cluster was closed. It is not avoidance of material that got hard. The earlier
decision it supersedes follows.

#### Memory and GC — working order, decided 2026-09-13 (superseded)

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

~~Unresolved: the topic's stated goal is production-debugging depth, while this
ordering optimises for interviews.~~ **Resolved 2026-09-18 in favour of
interviews**, in `BOOTSTRAP.md` §4 first, then here and in `TOPIC.md`.

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
