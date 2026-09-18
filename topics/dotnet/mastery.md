---
topic: dotnet
---

# .NET — mastery

One row per concept. Levels change only with an evidence link to a session
file. Row order within a cluster is the suggested order. Never delete a row.
A concept is plain text until its note exists, then a wikilink — never link a
file that is not there.

## Memory and GC

Generations, triggers, heaps, and what the allocator and collector actually do.

Row order is the suggested working order and proposal rule 4 reads it. Reordered
2026-09-13 by the user's decision. The last three — `gc-pauses-and-latency-modes`,
`gc-regions-and-configuration`, `pinning-and-gc-handles` — are **deprioritised**,
not dropped: judged niche for the roles being targeted, to be revisited **on the
user's request** once the rest of the cluster is done. No rule forbids proposing
them; they simply sit last, so nothing reaches them first. Never delete a row.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| [[stack-vs-heap-layout]] | L2 | 2026-09-18 | [[2026-09-18-finalization-and-stack-layout]] |
| [[finalization-and-freachable-queue]] | L2 | 2026-09-18 | [[2026-09-18-finalization-and-stack-layout]] |
| span-and-memory | L0 | — | — |
| gc-modes | L0 | — | — |
| card-table-and-write-barrier | L0 | — | — |
| stackalloc-and-ref-structs | L0 | — | — |
| [[gc-generations]] | L2 | 2026-09-17 | [[2026-09-17-gc-generations-and-loh]] |
| [[gc-triggers-and-budgets]] | L2 | 2026-09-13 | [[2026-09-17-gc-generations-and-loh]] |
| [[large-object-heap]] | L2 | 2026-09-17 | [[2026-09-17-gc-generations-and-loh]] |
| [[boxing]] | L3 | 2026-09-17 | [[2026-09-17-gc-generations-and-loh]] |
| gc-pauses-and-latency-modes | L0 | — | — |
| gc-regions-and-configuration | L0 | — | — |
| pinning-and-gc-handles | L0 | — | — |

## C# language internals

What the compiler lowers your code to, before the runtime ever sees it.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| value-vs-reference-semantics | L0 | — | — |
| ref-returns-and-ref-locals | L0 | — | — |
| closures-and-captured-variables | L0 | — | — |
| iterators-and-yield-lowering | L0 | — | — |
| disposal-patterns | L0 | — | — |
| exceptions-cost-and-filters | L0 | — | — |
| string-internals | L0 | — | — |
| equality-and-hashing-contracts | L0 | — | — |
| records-and-pattern-matching-lowering | L0 | — | — |
| nullable-reference-types | L0 | — | — |

## Async and threading

Threads and the primitives that coordinate them, then what replaces a blocked
thread and every way a continuation goes wrong.

Planned in tiers on 2026-09-18 — the first cluster built this way. Method:
`CLAUDE.md`, "Cluster planning"; rationale: `BOOTSTRAP.md` §4, "How a cluster
is planned". Row order is tier order and proposal rule 4 reads it, so no
override by hand should be needed.

**Exit test for tier 1** — answer both unaided before moving to tier 2:

1. Pick between `lock`, `SemaphoreSlim` and `Interlocked` for a stated
   shared-state scenario and defend the choice against the other two.
2. Say why async is not multithreading, and what `Task.Run` actually does.

**Exit test for the cluster:** "your API times out under load but CPU sits at
15%" — diagnosed by naming the counter before naming the cause — and "explain
how `.Result` deadlocks, and why the same code does not deadlock in a console
app".

**Tier 1 — Foundations.** Threads and the primitive family. Deliberately thin;
it exists to make tier 2 teachable, not as a course in parallel programming.
`Parallel.For`, PLINQ and TPL Dataflow were considered and dropped — the
2026-09-18 survey found no interview evidence for them.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| threads-and-scheduling | L0 | — | — |
| parallelism-vs-concurrency | L0 | — | — |
| thread-pool-internals | L0 | — | — |
| lock-and-monitor-internals | L0 | — | — |
| interlocked-and-cas | L0 | — | — |
| semaphoreslim-and-async-locks | L0 | — | — |

The last three moved here from **Concurrency** on 2026-09-18: they are
foundations for this cluster, and the evidence says the asked form is the
primitive choice above, not the memory model. What stayed in Concurrency is the
deep end.

**Tier 2 — Most asked.** Ranked by the 2026-09-18 interview survey.
`async-state-machine` leads this tier rather than the cluster: no source
surveyed asks for it standalone, but it is what makes the four rows under it
answerable at depth, so it is taught as the mechanism and graded as support.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| async-state-machine | L0 | — | — |
| synchronization-context-and-configureawait | L0 | — | — |
| async-deadlocks | L0 | — | — |
| thread-pool-starvation | L0 | — | — |
| cancellation-tokens | L0 | — | — |
| task-whenall-and-bounded-concurrency | L0 | — | — |
| async-exceptions-and-async-void | L0 | — | — |
| task-vs-valuetask | L0 | — | — |

`task-whenall-and-bounded-concurrency` is a **new row**, added because "call a
downstream API 500 times without taking it down" and "`Task.WhenAll` versus
awaiting in a loop" recur across three sources each and no existing row held
them.

**Tier 3 — On request.** Thin or no evidence. Rows and L0 levels kept; never
proposed automatically.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| task-continuations-and-scheduling | L0 | — | — |
| iasyncenumerable | L0 | — | — |
| execution-context-and-asynclocal | L0 | — | — |
| channels-and-producer-consumer | L0 | — | — |

## Concurrency

The memory model and what each guarantee does not cover. The everyday
primitives — `lock`, `Interlocked`, `SemaphoreSlim` — moved to **Async and
threading** on 2026-09-18, where they are tier 1. What is left here is the deep
end, which the 2026-09-18 survey found thin: ABA, lock-free and wait-free
structures and acquire/release semantics surfaced mainly in general-CS sources
rather than .NET ones.

Not tiered yet. Tier it when the cluster is next picked up, per `CLAUDE.md`,
"Cluster planning".

| Concept | Level | Since | Evidence |
|---|---|---|---|
| dotnet-memory-model | L0 | — | — |
| volatile-and-memory-barriers | L0 | — | — |
| reader-writer-locks | L0 | — | — |
| concurrent-collections-costs | L0 | — | — |
| lazy-and-double-checked-locking | L0 | — | — |
| lock-free-patterns-and-immutability | L0 | — | — |
| thread-safety-of-bcl-types | L0 | — | — |

## Runtime and type system

What the CLR does with the IL: JIT, generics, dispatch, loading.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| il-metadata-and-method-tables | L0 | — | — |
| jit-and-tiered-compilation | L0 | — | — |
| generics-at-runtime | L0 | — | — |
| virtual-dispatch-and-devirtualization | L0 | — | — |
| assembly-loading-and-alc | L0 | — | — |
| variance | L0 | — | — |
| reflection-vs-source-generators | L0 | — | — |
| struct-layout-and-interop | L0 | — | — |
| native-aot-and-trimming | L0 | — | — |

## Performance and diagnostics

Measuring honestly, reading what the tools show, and getting from a symptom to a cause.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| benchmarking-discipline | L0 | — | — |
| allocation-reduction-patterns | L0 | — | — |
| linq-and-hidden-allocations | L0 | — | — |
| reading-a-memory-profile | L0 | — | — |
| gc-metrics-interpretation | L0 | — | — |
| dotnet-counters-and-eventpipe | L0 | — | — |
| dotnet-trace-and-cpu-sampling | L0 | — | — |
| dump-analysis-with-sos | L0 | — | — |
| logging-cost-and-loggermessage | L0 | — | — |
| activity-and-distributed-tracing | L0 | — | — |
| symptom-to-runtime-cause | L0 | — | — |

## Dependency injection and hosting

Lifetimes, scopes, and the generic host — where production lifetime bugs live.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| service-lifetimes | L0 | — | — |
| captive-dependencies | L0 | — | — |
| scopes-in-background-services | L0 | — | — |
| ihostedservice-lifecycle-and-shutdown | L0 | — | — |
| options-pattern-variants | L0 | — | — |
| disposal-order-and-container-ownership | L0 | — | — |
| keyed-services-and-factories | L0 | — | — |
| configuration-providers-and-precedence | L0 | — | — |

## Data access and EF Core internals

From the connection pool up through the query pipeline to the change tracker.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| ado-net-connection-pooling | L0 | — | — |
| dbcontext-lifetime-and-pooling | L0 | — | — |
| change-tracking-and-identity-map | L0 | — | — |
| query-translation-and-client-evaluation | L0 | — | — |
| loading-strategies-and-n-plus-one | L0 | — | — |
| projection-and-split-queries | L0 | — | — |
| savechanges-and-batching | L0 | — | — |
| optimistic-concurrency-tokens | L0 | — | — |
| transactions-and-execution-strategies | L0 | — | — |
| compiled-queries-and-query-cache | L0 | — | — |
| migrations-and-model-snapshot | L0 | — | — |

## HTTP, networking, and resilience

`HttpClient` and the sockets under it; the failures that only show up under load.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| httpclient-lifetime-and-socketshttphandler | L0 | — | — |
| ihttpclientfactory | L0 | — | — |
| dns-and-connection-pooling | L0 | — | — |
| http2-and-http3-in-dotnet | L0 | — | — |
| timeouts-and-cancellation-in-http | L0 | — | — |
| retries-and-resilience-pipelines | L0 | — | — |
