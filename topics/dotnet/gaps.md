---
topic: dotnet
---

# .NET — gaps

Newest first. Never deleted. Status: open → studying | taught → verified | regressed.

| Date | Concept | Miss | Session | Status | Updated |
|---|---|---|---|---|---|
| 2026-09-15 | [[stack-vs-heap-layout]] | drill miss: cannot say how the GC knows a reference is dead before the method returns — no JIT GC info, no stack walk — gives no reason Debug keeps locals alive longer, and does not address Tier-0 code in Release | [[stack-vs-heap-layout]] | open | — |
| 2026-09-15 | [[stack-vs-heap-layout]] | drill miss: rejects a class-to-struct change for the right costs (copying, interface boxing) but cannot state what it gains — no per-element header or reference, one array instead of N objects, contiguity, less mark work — nor the conditions to approve it | [[stack-vs-heap-layout]] | open | — |
| 2026-09-15 | [[stack-vs-heap-layout]] | drill miss: places a lambda-captured local on the stack rather than in a heap closure object; nests a referenced object's contents "inside" its owner instead of following the references (`Order` → `List<int>` → `int[]`) | [[stack-vs-heap-layout]] | open | — |
| 2026-09-13 | [[gc-triggers-and-budgets]] | cannot say what to measure to confirm a change in allocation or budget; declined the measurement half of Q1 and omitted it again in the Q10 design | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[gc-triggers-and-budgets]] | Q10 design: gen 2 never identified as the p99 latency risk, and no trade-off stated for the configuration chosen | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[boxing]] | believes the boxes behind a `List<object>` sit contiguously and live on the LOH; they are 24-byte objects scattered on the small object heap. Held under two probes | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[boxing]] | states generic specialisation happens at compile time; it happens at runtime when the JIT creates the instantiation. Third occurrence | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[boxing]] | derives the 24-byte box size by assertion rather than arithmetic, and attributes the padding to a minimum width for the value field rather than 8-byte object alignment | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[gc-generations]] | describes the write barrier as checking for old-to-young references rather than recording that an old location was written | [[2026-09-13-gc-triggers-and-budgets]] | open | — |
| 2026-09-13 | [[large-object-heap]] | drill miss: chooses pooling over forced compaction for the right reason, but does not price the option chosen — complexity, plus use-after-return or never-returned buffers | [[large-object-heap]] | open | — |
| 2026-09-13 | [[large-object-heap]] | drill miss: links per-request large buffers to more frequent gen 2 collections without naming the separate LOH budget as the trigger, and does not say why gen 0 and gen 1 counts are unchanged | [[large-object-heap]] | open | — |
| 2026-09-12 | [[boxing]] | drill miss: identifies the boxing in a struct-keyed dictionary but not its scale — does not know the fallback comparer boxes BOTH operands per comparison, nor that the hash dispatch boxes too (~7 per lookup, not 1) | [[boxing]] | open | — |
| 2026-09-12 | [[boxing]] | drill miss: picks the generic constraint over the interface parameter for the right reason, but cannot say what it costs — one JIT instantiation per value type, and the loss of a single heterogeneous call site | [[boxing]] | open | — |
| 2026-09-12 | [[gc-triggers-and-budgets]] | drill miss: cannot say what capping `GCHeapCount` does to per-heap budgets, nor that the container heap hard limit defaults to 75% of the container limit | [[gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[boxing]] | believes `List<int>` boxes on add and read, and that a boxed copy lives on the stack | [[2026-09-12-gc-triggers-and-budgets]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
| 2026-09-12 | [[finalization-and-freachable-queue]] | attributes finalizer work to the originating thread, then to the thread pool; no finalizer queue, no finalizer thread; conflates the finalizer with `Dispose` | [[2026-09-12-gc-triggers-and-budgets]] | open | — |
| 2026-09-12 | [[large-object-heap]] | does not know the 85,000-byte threshold, and cannot say the LOH is swept rather than compacted or what that costs | [[2026-09-12-gc-triggers-and-budgets]] | taught | 2026-09-13 [[large-object-heap]] |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot unpack Server versus Workstation GC: no per-core heaps, no per-heap budgets, no 75% heap hard limit | [[2026-09-12-gc-triggers-and-budgets]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
| 2026-09-12 | [[gc-triggers-and-budgets]] | cannot say what work in a collection scales with survivors; collection cost described as "checking references" | [[2026-09-12-gc-triggers-and-budgets]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
| 2026-09-08 | [[gc-triggers-and-budgets]] | cannot name the gen 0 allocation budget as the trigger; model is "end of request" | [[2026-09-08-gc-generations]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
| 2026-09-08 | [[stack-vs-heap-layout]] | states the heap object is freed by the GC at the moment the method returns; does not separate the reference variable from the object | [[2026-09-08-gc-generations]] | taught | 2026-09-15 [[stack-vs-heap-layout]] |
| 2026-09-08 | [[gc-generations]] | attributes collection cost to "number of references" rather than the size of the live set; cannot say why generational collection is cheaper | [[2026-09-08-gc-generations]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
| 2026-09-08 | [[gc-generations]] | believes the GC runs on scope exit and when memory is low; cannot say what actually triggers a collection | [[2026-09-08-gc-generations]] | verified | 2026-09-13 [[2026-09-13-gc-triggers-and-budgets]] |
