---
topic: dotnet
---

# .NET — gaps

Newest first. Never deleted. Status: open → studying | taught → verified | regressed.

| Date | Concept | Miss | Session | Status | Updated |
|---|---|---|---|---|---|
| 2026-09-13 | [[large-object-heap]] | drill miss: chooses pooling over forced compaction for the right reason, but does not price the option chosen — complexity, plus use-after-return or never-returned buffers | [[large-object-heap]] | open | — |
| 2026-09-13 | [[large-object-heap]] | drill miss: links per-request large buffers to more frequent gen 2 collections without naming the separate LOH budget as the trigger, and does not say why gen 0 and gen 1 counts are unchanged | [[large-object-heap]] | open | — |
| 2026-09-12 | [[boxing]] | drill miss: identifies the boxing in a struct-keyed dictionary but not its scale — does not know the fallback comparer boxes BOTH operands per comparison, nor that the hash dispatch boxes too (~7 per lookup, not 1) | [[boxing]] | open | — |
| 2026-09-12 | [[boxing]] | drill miss: picks the generic constraint over the interface parameter for the right reason, but cannot say what it costs — one JIT instantiation per value type, and the loss of a single heterogeneous call site | [[boxing]] | open | — |
| 2026-09-12 | [[gc-triggers-and-budgets]] | drill miss: cannot say what capping `GCHeapCount` does to per-heap budgets, nor that the container heap hard limit defaults to 75% of the container limit | [[gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[boxing]] | believes `List<int>` boxes on add and read, and that a boxed copy lives on the stack | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-12 [[boxing]] |
| 2026-09-12 | [[finalization-and-freachable-queue]] | attributes finalizer work to the originating thread, then to the thread pool; no finalizer queue, no finalizer thread; conflates the finalizer with `Dispose` | [[2026-09-12-gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[large-object-heap]] | does not know the 85,000-byte threshold, and cannot say the LOH is swept rather than compacted or what that costs | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-13 [[large-object-heap]] |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot unpack Server versus Workstation GC: no per-core heaps, no per-heap budgets, no 75% heap hard limit | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-12 [[gc-triggers-and-budgets]] |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot say what work in a collection scales with survivors; collection cost described as "checking references" | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-12 [[gc-triggers-and-budgets]] |
| 2026-09-08 | [[gc-triggers-and-budgets]] | cannot name the gen 0 allocation budget as the trigger; model is "end of request" | [[2026-09-08-gc-generations]] | taught | 2026-09-08 [[gc-triggers-and-budgets]] |
| 2026-09-08 | [[stack-vs-heap-layout]] | states the heap object is freed by the GC at the moment the method returns; does not separate the reference variable from the object | [[2026-09-08-gc-generations]] | open | — |
| 2026-09-08 | [[gc-generations]] | attributes collection cost to "number of references" rather than the size of the live set; cannot say why generational collection is cheaper | [[2026-09-08-gc-generations]] | taught | 2026-09-13 [[gc-generations]] |
| 2026-09-08 | [[gc-generations]] | believes the GC runs on scope exit and when memory is low; cannot say what actually triggers a collection | [[2026-09-08-gc-generations]] | taught | 2026-09-13 [[gc-generations]] |
