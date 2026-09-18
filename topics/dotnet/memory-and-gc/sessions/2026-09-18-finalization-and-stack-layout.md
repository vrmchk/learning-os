---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-18
mode: interview
coached: true
excursion: false
questions: 5
avg_target: 2.8
avg_awarded: 2.2
concepts: [finalization-and-freachable-queue, stack-vs-heap-layout]
self_flagged: [4, 5]
disputes: 0
---

# 2026-09-18 — Finalization and stack layout

**Proposed by rule:** 1 — overdue queue items; both concepts due 2026-09-18
**Override:** none at proposal. After Q5 the user asked to stop rather than
continue in this cluster, stating a preference to work in other clusters. The
session was cut at five questions by that choice, not by the stop rule.

Coached mode. After each answer and its probes the shortfall and a model answer
were given; grades were withheld until after self-assessment, so the
self-assessment was made with the corrections already known. This session is
therefore excluded from the calibration checkpoint. Rule 4 of coached mode
constrained Q5: the finalizer thread's concurrency with application threads had
been corrected in Q1, so it was not weighted in Q5's grade.

## Q1 — [[finalization-and-freachable-queue]] — target L2 — depth

**Question:** A `NativeBuffer` class holds an `IntPtr` from `Marshal.AllocHGlobal`
and declares `~NativeBuffer()`. A method does `new NativeBuffer()` and returns;
nobody calls anything on it. Walk the instance from `new` to its memory being
back on the heap, and say what a `Dispose()` calling `GC.SuppressFinalize(this)`
would change.

**Answer:** Opened with "if it had Dispose and the code called it, the memory
would be freed immediately", and "if the code had the disposer and not called
it, nothing would change for us" — the second half correct. Then traced: at
`new` the object is "marked and added to finalize queue"; at a collection it has
no live references "but it has a reference to finalize queue", so it is moved to
the freachable queue; after the GC finishes the finalizer thread "clears all the
objects from freachable queue in a random order". Said `SuppressFinalize` means
the object "is not added to finalize queue".

**Probes:**
1. *At the moment `Dispose()` returns, what has been freed and what has not?* →
   "the native memory is freed, the object itself stays on the heap until GC
   happens" — correct.
2. *After the finalizer thread has run `Finalize`, what has to happen before the
   bytes are reusable?* → "we can't reuse the memory straight away, the object
   is collected only during next garbage collection, because after finalizer
   runs we mark this object as unreachable" — correct.

**Awarded:** L2 — the queue-to-queue mechanism, the dedicated finalizer thread
and the absence of ordering were all unaided, and the two-GC point came on one
probe. Missed the reason the object survives: the freachable queue is a **root**,
so the object and its whole graph are re-marked live and **promoted**, which is
what makes the second collection a gen 1 or gen 2 one. Direction of the
finalization-queue reference inverted. `SuppressFinalize` described as preventing
registration rather than flagging an existing entry to be skipped. Opening claim
that `Dispose` frees "the memory" needed a probe to separate native from managed.

## Q2 — [[stack-vs-heap-layout]] — target L2 — depth

**Question:** Given `class Order { DateTime Created; decimal[] Amounts; Customer
Buyer; }` and a method with `Order o = new Order(); o.Amounts = new decimal[50];
DateTime cutoff = ...; bool ok = Validate(o, cutoff);` — say where the bits live
for `o`, `Created`, the `decimal[50]` and its elements, `Buyer`, and the locals
`cutoff` and `ok`. Then state the general rule being applied.

**Answer:** All five placements correct. `o` a reference on the stack, the
`Order` on the heap, `Created` inline inside the `Order`, a reference to the
`decimal[]` inline in the object with the array and its elements on the heap,
and — volunteered, not asked — the `Customer` split: inline if a struct, a
reference plus a separate heap object if a class. `cutoff` and `ok` on the stack,
`cutoff` copied into the callee. Rule given as "reference types live on the heap
and value types live inline inside where they are created; if it is a field in
the object it's on the heap, if it's a variable or parameter it will be on the
stack".

**Probes:** none — the answer was specific and complete at the target; probing
would have been leading.

**Awarded:** L2 — every placement asked for was right, including the array
elements inline rather than as fifty objects. Held at target rather than above
it: the rule was stated as a type-based dichotomy rather than "a value lives
where its container lives", which is the form that survives closures, `await`
hoisting and boxing; and enregistration was not mentioned, so "on the stack" was
given as certain where slot-or-register is the accurate answer.

## Q3 — [[finalization-and-freachable-queue]] — target L4 — depth

**Question:** A `Session` class assigns `_handle = Native.Open(cs)` and then
`_conn = Connect(cs)`, which throws when the host is unreachable; `~Session()`
calls `Native.Close(_handle)` then `_conn.Abort()`. The caller catches and
retries in a loop. What happens to the partly-constructed instances? What
happens to the process if `Native.Close` throws? If the process is shut down
with some still pending, does the cleanup run?

**Answer:** The object becomes unreachable immediately; it was registered as
finalizable at `new`, so at the next collection it moves to the freachable queue
and is finalized — "but since the connection was never created", the finalizer
throws and "our application process will be terminated". Same conclusion for a
throwing `Native.Close`. On shutdown: "in such cases cleanup won't run" —
attached to the crash, not to the exit rule.

**Probes:**
1. *Assume a harmless finalizer body. Clean shutdown with entries still in the
   freachable queue — does the cleanup run?* → "no, finalizers don't run at
   process exit in .NET 5+" — exact.
2. *The finalizer closes the handle first, then throws. With four hundred
   instances queued, what is cleaned up at the instant the process dies?* →
   "only the first one's handle was closed, the rest leaked" — exact.

**Awarded:** L3 — the point most answers miss was unaided: registration happens
at `new`, before the constructor body completes, so a throwing constructor still
schedules a finalizer over fields that were never assigned, and an unhandled
exception on the finalizer thread terminates the process. Both probes answered
precisely on the first attempt. Short of L4 because the third part of the
question as asked was answered with the crash rather than the standing
process-exit rule, which had to be drawn out by probe.

## Q4 — [[stack-vs-heap-layout]] — target L3 — depth

**Question:** `struct Counter { int _n; void Increment(); int Value; }` held in a
`class Meter` as `private readonly Counter _hits`, with `Record() =>
_hits.Increment()`. `Record()` is called a million times and `Hits` returns 0.
Why, and what is the compiler emitting at the call site? What changes if
`readonly` is dropped? Separately: a 64-byte struct passed by value through five
call layers in a hot path — what does it cost and what would you change?

**Answer:** "I can't tell what happens under the hood for sure, but I suggest
that because the hits field is marked as read-only it cannot be modified and it
stays immutable, so when we call increment it is called on the copy of the field
instead of original one." Dropping `readonly` "would be possible to replace the
value on each call". For the 64-byte struct: "it would allocate 320 bytes per
each call which is pretty heavy and I would use `in` or `ref` modifier to avoid
those copying".

**Probes:**
1. *Who creates that copy and when — once at construction, or a million times?*
   → "a million times, once per Record call" — correct.
2. *If that struct's members are not marked `readonly`, what does `in` do at each
   member access inside the callee?* → "Not sure."

**Awarded:** L2 — correctly diagnosed the copy and its per-call frequency, and
named the right direction for the large struct. Cap: missed trade-off. Could not
price `in` on a non-`readonly` struct — it re-introduces a defensive copy at
every member access, which can cost more than passing by value — and did not
name `readonly struct` or `readonly` members as the actual fix. "Allocate 320
bytes" conflates by-value stack copying with heap allocation. The mechanism was
described by inference rather than named: the compiler emits a defensive copy to
a stack temporary because a non-`readonly` member may mutate `this` and a
`readonly` field may not be mutated.

## Q5 — [[finalization-and-freachable-queue]] — target L3 — depth

**Question:** `class ImageDecoder` holds `IntPtr _native` and `~ImageDecoder()`
calling `Native.DestroyDecoder(_native)`; `Decode` forwards to a long
`Native.DecodeFrame(_native, input)`. Fine in Debug and in testing; in
production under load it intermittently crashes inside `DecodeFrame` with an
access violation on an already-destroyed handle. What is happening, why does the
release build make it appear, and what are two fixes — which would you ship?

**Answer:** "The JIT considers `d` dead after Decode's argument is read. What we
can do is either call GC keep alive or inherit the safe handle class and the
second option is better. I don't remember exactly why it's better, but it's a
standard approach... the only thing I can tell why it's better is because if we
add another method we would need to call GC keep alive in every method, and if
we inherit safe handle we can do it once and forget." Added that knowing the
real reason "is kind of niche" and that other clusters were the preferred use of
time.

**Probes:**
1. *Why does Debug hide it, and does Release show it from the first call?* → "I
   don't know, this is too niche." Recorded as a pass.
2. Second probe not asked — the user declined the line of questioning and asked
   to move on. Not held against the grade beyond the pass already recorded.

**Awarded:** L2 — the root cause was named unaided and correctly, which is the
hardest part of the question: liveness ends at last use, so the object is
collectable while the native call is still running. Cap: missed trade-off. The
comparison of the two fixes rests on ergonomics only; the marshaller's
**ref-counting of a `SafeHandle` across the P/Invoke boundary** — the thing that
makes the fix structural rather than a repeated incantation — was not known,
nor `CriticalFinalizerObject`. The Debug/Release half was passed: no
unoptimised-code liveness, no Tier-0.

## Self-assessment

User flagged as weak: Q4, Q5. Both were the two graded below target, and neither
was awarded L3 or above. Made after the coached corrections, so not calibration
evidence.

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[finalization-and-freachable-queue]] | L2 | L2 | — | — |
| 2 | [[stack-vs-heap-layout]] | L2 | L2 | — | — |
| 3 | [[finalization-and-freachable-queue]] | L4 | L3 | — | — |
| 4 | [[stack-vs-heap-layout]] | L3 | L2 | weak | — |
| 5 | [[finalization-and-freachable-queue]] | L3 | L2 | weak | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[finalization-and-freachable-queue]] | L1 | L2 | min of Q1 L2, Q3 L3, Q5 L2; taught 2026-09-17, one day clear |
| [[stack-vs-heap-layout]] | L1 | L2 | min of Q2 L2, Q4 L2; taught 2026-09-15 |

No discovery questions were asked, so nothing was excluded from either minimum.

## Misses

- [[finalization-and-freachable-queue]] — does not know the freachable queue is
  a root: cannot say the object and its whole graph are re-marked live and
  promoted, which is what makes the second collection a gen 1 or gen 2 one
- [[finalization-and-freachable-queue]] — describes `GC.SuppressFinalize` as
  preventing registration; registration already happened at `new`, and the flag
  makes the GC skip the existing entry
- [[finalization-and-freachable-queue]] — answers the clean-shutdown case with
  the crash; needed a probe to state that .NET 5+ does not run pending
  finalizers at process exit
- [[finalization-and-freachable-queue]] — chooses `SafeHandle` over
  `GC.KeepAlive` on ergonomics alone; cannot name the marshaller's ref-counting
  across P/Invoke, nor `CriticalFinalizerObject`. Second occurrence — see the
  2026-09-17 drill miss
- [[finalization-and-freachable-queue]] — cannot say why Debug hides an
  early-collection bug (unoptimised code reports locals live to method end) and
  does not address Tier-0 in Release; passed on the probe
- [[stack-vs-heap-layout]] — states the placement rule as "value types on the
  stack, reference types on the heap" rather than "a value lives where its
  container lives", and gives "on the stack" as certain without enregistration
- [[stack-vs-heap-layout]] — cannot say what `in` costs on a non-`readonly`
  struct (a defensive copy at every member access), and does not name `readonly
  struct` or `readonly` members as the fix
- [[stack-vs-heap-layout]] — calls 5 x 64 bytes of by-value copying
  "allocation", and does not name the compiler's defensive copy to a stack
  temporary as the mechanism behind the lost counter

## Queue

| Concept | Next |
|---|---|
| [[finalization-and-freachable-queue]] | 2026-09-21 |
| [[stack-vs-heap-layout]] | 2026-09-21 |
