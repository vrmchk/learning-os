---
topic: dotnet
name: .NET
created: 2026-09-07
---

# .NET

Runtime and language depth, not framework surface area. I can already build
things; the gap is knowing what happens underneath when they misbehave.

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
binding, filters, Kestrel threading, `HttpContext` across awaits); I/O,
buffers, and serialization (`Pipelines`, `IBufferWriter`, `System.Text.Json`
internals); cloud SDKs.

## Suggested path

Not enforced. The proposal rules in `CLAUDE.md` pick when no focus cluster is
set; set one in `ROADMAP.md` to commit to a stage.

1. **Memory and GC** — everything else allocates. The vocabulary for every
   later "what does this cost" question.
2. **C# language internals** — know what the code you wrote actually compiles
   to before asking what the runtime does with it.
3. **Async and threading** — needs 1 (state machine allocations) and 2
   (closures, lowering).
4. **Concurrency** — needs 3; the memory model questions assume you can
   already trace a continuation.
5. **Runtime and type system** — JIT, generics, dispatch. Explains the
   numbers you will see in 6.
6. **Performance and diagnostics** — the tools that turn a symptom into a
   cause. Needs 1, 3, 5 to interpret what they show.
7. **Dependency injection and hosting** — where most production lifetime bugs
   live; needs 2 (disposal) and 3 (background services).
8. **Data access and EF Core internals** — needs 7 (`DbContext` lifetime) and
   3 (async query pipeline).
9. **HTTP, networking, and resilience** — needs 7 and 3; socket exhaustion
   and stale DNS are the classic "misbehaves underneath" failures.

## Definition of done

Cold and unaided at a whiteboard:

1. Draw the generational GC and say what triggers and pauses each collection
   kind.
2. Draw the async state machine and trace a continuation through the thread
   pool.
3. Argue whether a given lock-free pattern is safe under the memory model.
4. Reason from a described production symptom to a runtime cause.
5. Trace a LINQ query from expression tree to SQL and back to tracked
   entities, and say where each layer can silently cost a round trip.

Each demonstrated unprompted in a session and linked from `mastery.md`. A
description of what the topic is for, not a gate.

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
