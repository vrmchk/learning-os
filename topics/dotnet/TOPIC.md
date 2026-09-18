---
topic: dotnet
name: .NET
created: 2026-09-07
---

# .NET

Runtime and language depth, and the framework behaviour that gets asked about.
I can already build things; the gap is knowing what happens underneath when
they misbehave, and being able to show it in an interview.

*Changed 2026-09-18.* This used to read "runtime and language depth, **not
framework surface area**". Cluster order is now set by interview frequency
rather than by dependency, and that evidence puts EF Core, dependency injection
and ASP.NET Core — framework surface area — above the runtime internals this
topic was built around. Rationale and the limits of the evidence:
`BOOTSTRAP.md` §4, "Reordered by interview evidence".

Referenced by path, never by wikilink — every topic has a `TOPIC.md`.

## Clusters

Nine, enumerated in `mastery.md`. Row order within a cluster is the suggested
order; the first row is where an untouched cluster is entered.

| Cluster | Slug | Concepts |
|---|---|---|
| Memory and GC | `memory-and-gc` | 13 |
| C# language internals | `csharp-language-internals` | 10 |
| Async and threading | `async-and-threading` | 12 |
| Concurrency | `concurrency` | 10 |
| Runtime and type system | `runtime-and-type-system` | 9 |
| Performance and diagnostics | `performance-and-diagnostics` | 11 |
| Dependency injection and hosting | `di-and-hosting` | 8 |
| Data access and EF Core internals | `data-access-and-ef-core` | 11 |
| HTTP, networking, and resilience | `http-and-networking` | 6 |

**Add when wanted:** ASP.NET Core pipeline (middleware order, routing, model
binding, filters, Kestrel threading, `HttpContext` across awaits) — now ranked
**6th** in `ROADMAP.md`, to be created as a real cluster on its first session
rather than pre-scaffolded; I/O, buffers, and serialization (`Pipelines`,
`IBufferWriter`, `System.Text.Json` internals); cloud SDKs.

## Suggested path

Not enforced. The proposal rules in `CLAUDE.md` pick when no focus cluster is
set; set one in `ROADMAP.md` to commit to a stage.

**Reordered 2026-09-18 by interview frequency**, replacing the dependency
ordering below. The ranked table with the evidence per cluster lives in
`ROADMAP.md`; the rationale and the limits of that evidence are in
`BOOTSTRAP.md` §4.

1. **Async and threading** — the only cluster rated major by every source
   surveyed, and harder at senior level.
2. **Performance and diagnostics** — production incident diagnosis, a bucket
   that does not exist below senior. Makes Memory and GC pay.
3. **Dependency injection and hosting** — smallest cluster, "near-certain"
   questions, unblocks 4.
4. **Data access and EF Core internals** — named the senior-versus-mid filter
   by three independent sources.
5. **Concurrency** — asked as primitive choice, not memory model.
6. **ASP.NET Core pipeline** — not a cluster yet; create on first use.
7. **C# language internals** — assumed baseline at senior, rarely asked alone.
8. **HTTP, networking, and resilience** — lowest verified question density.
9. **Memory and GC** — closed at 6 of 13 rows; remainder on request.
10. **Runtime and type system** — one outlier source, no first-hand support.

**The dependency order this replaced**, kept because it is still true about
what *builds on* what, and is the right order if the goal ever swings back from
interviews to production debugging: Memory and GC (everything allocates) → C#
language internals (know what the code lowers to) → Async and threading (needs
both) → Concurrency (needs async) → Runtime and type system (explains the
numbers) → Performance and diagnostics (needs 1, 3, 5 to read the tools) →
Dependency injection and hosting (needs disposal and background services) →
Data access and EF Core (needs `DbContext` lifetime and the async query
pipeline) → HTTP, networking and resilience.

Where the two orders disagree most: Performance and diagnostics moves from
sixth to second, and Runtime and type system from fifth to last.

## Definition of done

Cold and unaided at a whiteboard:

1. Draw the generational GC and say what triggers and pauses each collection
   kind. *(Substantially met 2026-09-18 — five concepts at L2, one at L3.)*
2. Take a production symptom to a cause with named tools: memory climbing
   across restarts, or a timeout at 15% CPU. Say which counter or command you
   would pull **before** naming the cause.
3. Trace a continuation through the thread pool and explain what
   `ConfigureAwait` changes, what deadlocks sync-over-async, and how you would
   bound concurrency over a downstream service.
4. Take an EF Core query from `IQueryable` to SQL and back to tracked
   entities, and name where each layer silently costs a round trip.
5. Choose a synchronisation primitive for a stated scenario and defend it
   against the alternatives.

Each demonstrated unprompted in a session and linked from `mastery.md`. A
description of what the topic is for, not a gate.

*Rewritten 2026-09-18 to match the interview-frequency ordering.* Two items
changed on evidence rather than preference. The old item 2 was "draw the async
state machine and trace a continuation through the thread pool" — no source
surveyed asks for the state machine as a question in its own right, including a
first-hand account from a named .NET engineer whose whole post is about the
async question he asks; it is background competence that should inform an
answer, so item 3 now asks for what the competence is *for*. The old item 3 was
"argue whether a given lock-free pattern is safe under the memory model" —
lock-free and memory-model questions surfaced mainly in general-CS sources
rather than .NET ones, so item 5 asks for the primitive choice that .NET
sources actually ask for. The previous wording is preserved in git history and
in `BOOTSTRAP.md` §4.

## Trusted sources

Names only — URLs enter the vault through `study`'s verification, never from
memory. `study` starts here.

**Primary**

- Microsoft Learn — .NET, C#, and EF Core documentation
- The .NET Blog (devblogs) — especially the yearly performance posts
- Book of the Runtime (BOTR) in `dotnet/runtime` — GC design, threading,
  type loader, JIT
- `dotnet/runtime` and `dotnet/efcore` source and design docs

**People whose long-form work is reliable**

- Stephen Toub — async internals, `ValueTask`, performance
- Maoni Stephens — GC design and configuration
- Konrad Kokosa — *Pro .NET Memory Management*
- Stephen Cleary — async guidance, `SynchronizationContext`
- David Fowler — async guidance, hosting, `HttpClient` guidance
- Joe Duffy — *Concurrent Programming on Windows*, memory model
- Matt Warren — CoreCLR internals
- Adam Sitnik — BenchmarkDotNet, benchmarking discipline
- Andrew Lock — DI, hosting, configuration
- Arthur Vickers, Shay Rojansky — EF Core internals
- Dotnetos — memory and performance talks

## Conventions

- Concept slugs are kebab-case and unique across the vault.
- Cluster slugs above are what session frontmatter uses for `cluster`.
- Sessions: `sessions/YYYY-MM-DD-<slug>.md`. Notes: `notes/<concept>.md`.
