---
topic: dotnet
---

# .NET — gaps

Newest first. Never deleted. Status: open → studying | taught → verified | regressed.

| Date | Concept | Miss | Session | Status | Updated |
|---|---|---|---|---|---|
| 2026-09-12 | [[boxing]] | believes `List<int>` boxes on add and read, and that a boxed copy lives on the stack | [[2026-09-12-gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[finalization-and-freachable-queue]] | attributes finalizer work to the originating thread, then to the thread pool; no finalizer queue, no finalizer thread; conflates the finalizer with `Dispose` | [[2026-09-12-gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[large-object-heap]] | does not know the 85,000-byte threshold, and cannot say the LOH is swept rather than compacted or what that costs | [[2026-09-12-gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot unpack Server versus Workstation GC: no per-core heaps, no per-heap budgets, no 75% heap hard limit | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-12 [[gc-triggers-and-budgets]] |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot say what work in a collection scales with survivors; collection cost described as "checking references" | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-12 [[gc-triggers-and-budgets]] |
| 2026-09-08 | [[gc-triggers-and-budgets]] | cannot name the gen 0 allocation budget as the trigger; model is "end of request" | [[2026-09-08-gc-generations]] | taught | 2026-09-08 [[gc-triggers-and-budgets]] |
| 2026-09-08 | [[stack-vs-heap-layout]] | states the heap object is freed by the GC at the moment the method returns; does not separate the reference variable from the object | [[2026-09-08-gc-generations]] | open | — |
| 2026-09-08 | [[gc-generations]] | attributes collection cost to "number of references" rather than the size of the live set; cannot say why generational collection is cheaper | [[2026-09-08-gc-generations]] | open | — |
| 2026-09-08 | [[gc-generations]] | believes the GC runs on scope exit and when memory is low; cannot say what actually triggers a collection | [[2026-09-08-gc-generations]] | open | — |
