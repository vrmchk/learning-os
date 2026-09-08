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

| Concept | Level | Since | Evidence |
|---|---|---|---|
| gc-generations | L0 | — | — |
| gc-triggers-and-budgets | L0 | — | — |
| gc-modes | L0 | — | — |
| large-object-heap | L0 | — | — |
| card-table-and-write-barrier | L0 | — | — |
| gc-pauses-and-latency-modes | L0 | — | — |
| gc-regions-and-configuration | L0 | — | — |
| finalization-and-freachable-queue | L0 | — | — |
| stack-vs-heap-layout | L0 | — | — |
| boxing | L0 | — | — |
| span-and-memory | L0 | — | — |
| stackalloc-and-ref-structs | L0 | — | — |
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

The state machine, the thread pool, and every way a continuation goes wrong.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| async-state-machine | L0 | — | — |
| task-vs-valuetask | L0 | — | — |
| synchronization-context-and-configureawait | L0 | — | — |
| thread-pool-internals | L0 | — | — |
| thread-pool-starvation | L0 | — | — |
| async-deadlocks | L0 | — | — |
| cancellation-tokens | L0 | — | — |
| execution-context-and-asynclocal | L0 | — | — |
| task-continuations-and-scheduling | L0 | — | — |
| async-exceptions-and-async-void | L0 | — | — |
| iasyncenumerable | L0 | — | — |
| channels-and-producer-consumer | L0 | — | — |

## Concurrency

The memory model, the primitives, and what each one does not guarantee.

| Concept | Level | Since | Evidence |
|---|---|---|---|
| dotnet-memory-model | L0 | — | — |
| volatile-and-memory-barriers | L0 | — | — |
| interlocked-and-cas | L0 | — | — |
| lock-and-monitor-internals | L0 | — | — |
| semaphoreslim-and-async-locks | L0 | — | — |
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
