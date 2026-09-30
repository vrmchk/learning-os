---
name: interview
description: Run a graded learning session — ask questions one at a time, grade each against the L0–L5 rubric, and write everything back to the vault. Use this whenever the user wants to be quizzed, tested, examined, drilled, interviewed, or asked "what should I work on"; whenever they say "let's do a session", "quiz me", "test me on X", or name a concept and want to be asked about it. This is the ONLY way a level in mastery.md can change. Never run an ad-hoc quiz outside this skill, and never grade without doing the full write-back.
---

# interview

A graded session, end to end. Grading and write-back live here so there is no
way to be tested without being scored, or scored without it being recorded.

`CLAUDE.md` holds the rubric, the anti-inflation rules, and the session
protocol. This file adds the mechanics and the exact file formats. If they
ever disagree, `CLAUDE.md` wins.

## 0. Mode

One parameter, `exam` or `coached`. **Default `coached`** (changed
2026-09-18) — if the user said nothing, do not ask, just run `coached`.

Recognise `exam` from the argument (`exam`, `exam mode`, `mock`, `mock
interview`, `no feedback`, `don't correct me`) or from the user asking to be
measured rather than taught. Coached is also what the words `coached`, `show
ideal answers`, `with feedback` and `coached mode` select, and what a request
for corrections as you go means.
Say which mode is running in the same line as the proposal:
*"Proposing `gc-modes` — rule 1, overdue 2 days. Coached mode."*

`exam` is the **mock interview** (repositioned 2026-09-30): the occasional
full rehearsal, not the routine. Suggest one in a single line — never run it
unasked — only when the user mentions an upcoming real interview, or when the
newest `weekly-review` report finds coached grades running above exam grades on
the same concepts.

The mode changes **two things**: when the feedback arrives, and when the
self-assessment is taken. Proposal rules, ladders, targets, mix, probing,
coverage caps, the rubric, the consecutive-lows stop rule, and the whole of §4
are identical.

| | exam | coached |
|---|---|---|
| Between question and answer | nothing | nothing |
| When a ladder stops | next ladder | one-word rating, then where it fell short, then the model answer |
| Self-assessment | once, after the last answer | the per-ladder rating, before each correction |
| Grades | after self-assessment | at the end |
| Level changes, write-back | full | full |
| Frontmatter | `coached: false` | `coached: true` |
| Calibration checkpoint | counts | counts |

**Coached mode, exactly:**

1. Climb the ladder. Probe as normal. **No correction inside a ladder** —
   rungs and probes are all part of it, so the feedback waits until the climb
   stops.
2. **Rating first.** Ask exactly: *"Before I say anything — solid, shaky, or
   missed?"* Record the word. Nothing about the answer is said before it is
   given. A ladder rated shaky or missed is self-flagged.
3. Then, before the next ladder: a short **"Where you were short"** list —
   what was wrong, what was missing, what was right — and a **model answer** for
   the rung that stopped the climb, at the length a person could say out loud.
   If every planned rung was cleared, only what was missing, if anything. Same
   content as `teach`'s model answers; this is not a second lecture on the
   concept.
4. Grade silently as always. **Never reveal the level**, not even loosely
   ("that was about an L2"). The correction says what was missing, not what it
   scored.
5. **Never re-test a corrected point later in the session.** An answer repeated
   back from a model answer is not unaided evidence. Move to another part of
   the concept, and if that leaves nothing askable, switch concept.
6. In the session file: set `coached: true`, and put one paragraph under the
   proposal line saying the format was coached, that each rating was given
   before its correction, and which later questions were constrained by rule 5.

The reason for the default, and what remains of the measurement cost, is in
`BOOTSTRAP.md` §6, "Two interview modes", and §9: ladders and the rating before
feedback close most of the gap; corrections on earlier concepts can still help
on later ones, which is why `exam` survives.

## 1. Before the first question

1. **Sync.** If the repo has a remote, run `git pull --ff-only`. If it fails or
   the tree is dirty, say so and ask before continuing — never silently
   overwrite a phone session with a desk session.
2. **Read** `ROADMAP.md`, `review/queue.md`, and the focus topic's
   `mastery.md` and `gaps.md` — or the named topic's, if the user has already
   said what they want. Today's date is the session date; never guess it —
   check the system clock.
3. **Weekly check.** If `review/weekly/` has no report or its newest is more
   than seven days old, and at least two interview sessions have happened
   since, say so in one line and offer `weekly-review`. Do not run it
   unasked; the user came for a session.
4. **Propose** one concept or cluster and **name the rule that chose it**:
   1. overdue queue items (`next` ≤ today), oldest first
   2. gaps with status `regressed`
   3. the focus cluster, if `ROADMAP.md` sets one
   4. the lowest-level concepts in the focus topic, in row order
   5. the cluster with the oldest `since` dates
   Concepts with an **untaught** `open` gap are **not proposed** — testing an
   untaught miss again just records the same miss. Untaught means the
   concept's note has no `taught:` date. A concept that **has** been taught is
   proposable even with open gaps — that is what re-testing is for, and
   "Coverage caps the target" in §2 decides how hard each specific point may
   be asked. A `regressed` gap never blocks; it is rule 2 above. Mention
   blocked concepts in one line ("3 untaught gaps waiting for `teach`") and
   move on. Say the rule in one line:
   *"Proposing `thread-pool-starvation` — rule 1, overdue 3 days."*
5. **Let the user override**, including onto another topic. If the topic
   folder does not exist, this is an excursion — see §6.
6. **Plan the mix** before asking anything: four to six ladders — two to four
   depth / one or two adjacent or prerequisite / one cold recall from the
   queue. If the queue has nothing due, the cold-recall ladder goes to depth.
   Adjacent ladders may be chosen during the session to follow something the
   user said. Write the plan in your head, not in chat. Dispute re-asks (§3)
   do not count toward the six.

## 2. Asking

One question at a time. Wait for the full answer. Nothing between the
question and the answer — in both modes. Coached feedback comes after the
ladder stops, never inside it.

### The ladder

A graded question is a **ladder** on one concept — the shape of a real
technical interview: explain it, then use it, then its costs, then its edges,
and only then a practical problem. Rationale and the transcript it came from:
`BOOTSTRAP.md` §6, "Question ladders".

| Rung | Asks | Target | Sounds like |
|---|---|---|---|
| 1 Explain | what it is, why it exists | L1 | "What is boxing? Why does it exist?" |
| 2 Use | how you would use it, what it looks like in code | L2 | "Where does it happen in everyday code?" |
| 3 Trade-offs | when to reach for it, what it costs, vs the alternatives | L3 | "What does it cost, and what do generics change?" |
| 4 Mechanism and failure | what happens underneath, edge cases, what breaks | L4 | "What does the box look like in memory? Where does it bite unexpectedly?" |
| 5 Scenario | a practical or design problem under constraints, defended | L5 | "A hot path allocates 3 GB/min. Find the boxing and fix it — defend the fix." |

- **Always start at rung 1**, even for a concept recorded at L3+. Early rungs
  are short: one question, no ceremony.
- **Climb while cleared.** A rung is cleared when its answer fully meets its
  level after probing. Stop at the first rung that is not cleared. Never skip
  a rung, and never open with a scenario or an edge case.
- **Word questions like an interviewer.** Plain and direct, the way the rung
  table reads. A rung may hook onto the user's previous answer ("you said the
  pool injects slowly — why?").
- **Top rung = target.** Before rung 1, fix the ladder's target: rung 5 unless
  coverage caps it lower (below). Write it into the session file first.
- After a ladder stops, optionally ask **"have you used it in practice?"**.
  Record the answer in one line under the ladder. It is never graded.
- The **next ladder** should, where it can, follow from something the user
  said — an adjacent concept they named, or a term they used loosely. That is
  how an interview moves, and it makes adjacent ladders earn their place.

For **every** ladder, before rung 1, fix and keep:

- the **concept** it tests (one wikilink; rungs may touch others, but one is
  graded)
- the **target level** — the top rung planned
- the **kind**: `depth`, `adjacent`, `cold recall`, or `discovery`

An awarded grade can never exceed the target. To earn L4 the ladder must reach
rung 4.

**Coverage caps the target.** Before planning rungs 3–5, check the concept's
note. The note's sections follow the ladder (`teach/SKILL.md` §2): rung 3 needs
the thing asked about treated in *Trade-offs*, rung 4 in *How it works* or
*Where it breaks*, rung 5 in *In practice*. A note written before 2026-09-30
still has *Mechanism*, *Failure modes* and *Trade-offs*; any of those covers
rungs 3–4, and rung 5 needs the scenario's parts covered there. A single clause in passing is not
coverage. If the note only mentions it, the ladder tops out at L2. If there is
an `open` gap row or a recorded drill miss on that exact point, it is `teach`'s
job — aim the rung at a different covered point, drop the rung so the ladder
tops out below it, or ask it as `discovery`, which ends the climb and is
excluded from the ladder's grade.

**Discovery questions** find holes; they do not measure. Pitch at L1, label
`discovery`, grade and record as normal, and write the miss to `gaps.md`. A
discovery question is either a one-rung ladder on untaught material (the
heading says `discovery`) or a single uncovered rung at the top of a ladder
(the rung says `discovery`). Either way it is excluded from the concept grade
(§4.2) and from the stop rule below. It can neither raise nor lower a level. It
is how an untested corner gets found and handed to `teach`.

For **rung 5** and any other open-ended design question, write the checklist
of what a strong answer must contain **before** asking it. Three to six items,
each a specific thing the answer must say. It goes into the session file
verbatim, and the answer is graded against it item by item. Never revise the
checklist after the answer.

**Probing.** A vague answer on any rung gets at least two probes — *why?* and
*what breaks if…?* — before the rung is judged. Probes belong to the rung. Stop
probing when the rung is clearly cleared or clearly not; do not lead the user
to it.

**"hint"** — give one hint, then let them continue. The ladder is capped at
L2: a hinted answer is not unaided, and no rung above 2 can be cleared after
it.

**"pass"** — the rung is not cleared; the climb stops. If it was rung 1, award
per the first-contact rule (cannot define → L0). Say nothing else in exam mode.

**Two consecutive graded ladders at L1 or lower** → end the session here. Do
the full write-back for what was asked (§4), then tell the user you are
switching to `teach` for the concept with the lowest grade, and run it.
`discovery` ladders do not count: L1s on material nobody has taught mean it is
new, not that teaching has failed.

Stop at six ladders. Claude cannot measure wall-clock; if the user says time
is up, stop at once and grade what was answered — a ladder cut short is graded
on the rungs it reached.

## 3. Grading

Judge each rung as it is completed, **silently** — cleared or not. Record it;
say nothing about it. Grades are revealed only after self-assessment — in
coached mode too, where the correction says what was missing and never what it
scored.

**A ladder's grade is the target level of the highest rung cleared with no
rung missed below it.** Rungs 1–3 cleared, rung 4 missed → L3. Rung 1 missed →
L0 if the user cannot define it, L1 if they defined it but the answer fell
short of explaining why it exists. Nothing above the last cleared rung counts,
however good a later remark was.

Apply `CLAUDE.md`'s anti-inflation rules literally, **rung by rung**. The ones
that bite most:

- A rung half-answered is not cleared. Between two levels → the lower one.
- Missed the trade-off → rung 3 is not cleared, so the ladder caps at L2, even
  if everything said was correct.
- Used a term, could not unpack it when probed → L1 for that term. Record the
  term in the miss.
- Fluent, confident, well-structured → worth nothing. Grade the content.
- Awarded ≤ target, always.
- A `discovery` question is graded and recorded like any other, but it is
  excluded from the concept grade in §4.2.

Write the one-line reason at grading time, naming the rung that stopped the
climb and the rule if a cap applied.

**Self-assessment.** In `coached` mode it is the per-ladder rating (§0 step
2), already taken; do not ask again at the end — reveal the grades table once
the last ladder's correction is done. In `exam` mode, after the last answer and
before any grade is shown, ask exactly this: *"Before I show grades — which
answers did you think were weak?"* Record the list by ladder number, then
reveal the grades table.

**Disputes.** If the user disagrees with a grade, do not change it and do not
debate it. Ask two or three further questions on the same concept at the
disputed rung, grade those, and set the final grade from the whole picture.
Record original, final, and the reason. The user can trigger this once per
concept per session.

## 4. Write-back — mandatory, in this order

Do all of it before saying anything to the user.

### 4.0 Stub notes

For every concept graded in this session that has no file in
`topics/<topic>/<cluster>/notes/`, create its **stub** first — the format is in
`teach/SKILL.md` under "Stub". Then turn that concept's cell in `mastery.md`
from plain text into `[[concept]]`. Only now may the session file, gaps, and
queue link it. A wikilink to a file that does not exist is never written.

### 4.1 Session file

`topics/<topic>/<cluster>/sessions/YYYY-MM-DD-<slug>.md`, where `<cluster>`
is the kebab-case slug from `TOPIC.md` and matches the `cluster:` frontmatter.
Create the cluster folder if this is its first use. Slug is the proposed concept
or cluster, kebab-case. If a second session on the same day has the same slug,
append `-2`.

```markdown
---
topic: dotnet
cluster: memory-and-gc
date: 2026-09-14
mode: interview
coached: false
excursion: false
questions: 4
avg_target: 4.8
avg_awarded: 2.3
concepts: [gc-generations, large-object-heap, gc-modes]
self_flagged: [2]
disputes: 0
---

# 2026-09-14 — GC generations

**Proposed by rule:** 5 — lowest-level concepts in focus topic
**Override:** none

## Q1 — [[gc-generations]] — target L5 — depth

**Rung 1 — Explain (L1):** *What is a generational GC, and why does .NET use
one?* → "objects are grouped by age; most die young, so collecting only the
young ones is cheap." — **cleared**

**Rung 2 — Use (L2):** *What does that mean for how you write allocation-heavy
code?* → short-lived temporaries are nearly free; objects kept alive a little
too long get promoted and cost more. — **cleared**

**Rung 3 — Trade-offs (L3):** *What does generational collection cost, and
what would a non-generational GC do better?* → "it's cheaper" — could not say
what it pays for.

**Probes:**
1. *Cheaper in exchange for what?* → no answer on tracking old-to-young
   references.
2. *What breaks if a gen-2 object references a gen-0 object?* → did not know
   the write barrier / card table exists.

— **not cleared**; climb stops.

**Used it?** Tuned `GCSettings.LatencyMode` once for a batch job. Not graded.

**Awarded:** L2 — rungs 1–2 cleared, rung 3 missed the cost (card table
bookkeeping on every reference write).

## Q2 — [[large-object-heap]] — target L5 — adjacent

Hooked to Q1: the user mentioned "big arrays go somewhere else".

**Rung 1 — Explain (L1):** ... — **cleared**

**Rung 2 — Use (L2):** *When does your code put something on the LOH?* → did
not know the 85,000-byte threshold; "big objects, maybe a megabyte".

**Probes:** ...

— **not cleared**; climb stops.

**Awarded:** L1 — defined the LOH, could not say when an object lands on it.

...

## Q4 — [[gc-modes]] — target L5 — depth

... rungs 1–4 cleared ...

**Rung 5 — Scenario (L5):** *A 16-core API in a 2 GB container has p99
spikes every few seconds. Choose a GC configuration and defend it.*

**Checklist:**
- [x] Server GC by default in ASP.NET Core; one heap per core
- [x] container limit → heap hard limit at 75%
- [ ] 16 heaps in 2 GB means tiny per-heap budgets → frequent gen 0 GCs
- [ ] `GCHeapCount` or DATAS as the fix, with its cost

**Answer:** ...

— **not cleared** (two of four items).

**Awarded:** L4 — rungs 1–4 cleared, rung 5 missed the per-heap budget
arithmetic.

## Self-assessment

User flagged as weak: Q2

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-generations]] | L5 | L2 | — | — |
| 2 | [[large-object-heap]] | L5 | L1 | weak | — |
| 3 | [[gc-generations]] | L4 | L2 | — | L1 → L2: re-asked ×2 at rung 2, named the promotion cost on the second |
| 4 | [[gc-modes]] | L5 | L4 | — | — |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-generations]] | L0 | L2 | min of Q1 L2, Q3 L2 |
| [[large-object-heap]] | L0 | L1 | rung 1 cleared, rung 2 missed |
| [[gc-modes]] | L3 | L4 | Q4 cleared rung 4 |

## Misses

- [[gc-generations]] — does not know the card table / write barrier
- [[large-object-heap]] — cannot say why the LOH is not compacted
- [[gc-modes]] — used "background GC" without being able to say what runs
  concurrently with what

## Queue

| Concept | Next |
|---|---|
| [[gc-generations]] | 2026-09-17 |
| [[large-object-heap]] | 2026-09-15 |
| [[gc-modes]] | 2026-09-21 |
```

Rules for the file:

- Each `## Q<n>` is one **ladder**; `questions` in the frontmatter counts
  ladders, and `avg_target` / `avg_awarded` average the ladders' targets and
  grades. Sessions before 2026-09-30 counted single questions; the two are not
  comparable (`BOOTSTRAP.md` §6).
- Every rung asked gets its own `**Rung n — <name> (Lx):**` line: the question
  in italics, the answer summarised, then **cleared** or **not cleared**.
  Probes sit under the rung they belong to. Rungs not reached are not written.
- `**Used it?**` appears only if asked, and is never graded.
- In a coached session each ladder carries a `**Rating:** solid | shaky |
  missed` line, written after the last rung and before the correction. The
  `## Self-assessment` section then reads `User rated: Q1 solid, Q2 shaky, …`
  and `self_flagged` lists the shaky and missed ladders. In an exam session it
  reads `User flagged as weak: …` as before.
- Frontmatter keys and order are fixed; the progress script reads them.
  `cluster` is the kebab-case of the cluster heading in `mastery.md`.
  `coached` is `true` only for a coached session (§0); it no longer affects the
  calibration checkpoint, and drives the mode column in the softness table.
  `excursion` is true when `topic` is not the focus topic in `ROADMAP.md`.
  `self_flagged` and `concepts` are YAML lists; empty is `[]`.
- Every graded concept appears as a wikilink at least once. That is what
  makes backlinks the real gap list.
- Answers are **summarised**, quoting the key claims verbatim. Not a
  transcript; enough that a reader can check the grade.
- `Checklist` appears only for rung 5 or another design question, and only
  as written before the answer.
- `Self-flagged` is `weak` or `—`. `Dispute` is `—` or `<orig> → <final>:
  <reason>`.
- The kind in each `## Q<n>` heading is `depth`, `adjacent`, `cold recall` or
  `discovery`. The Grades table format does not change — the progress script
  parses it — so `discovery` is recorded in the heading (or on the rung) only,
  and the Level changes table says which ladders or rungs were excluded and
  why.

### 4.2 Mastery table

`topics/<topic>/mastery.md`:

```markdown
---
topic: dotnet
---

# .NET — mastery

## Memory and GC

| Concept | Level | Since | Evidence |
|---|---|---|---|
| [[gc-generations]] | L2 | 2026-09-14 | [[2026-09-14-gc-generations]] |
| large-object-heap | L0 | — | — |
```

The `Concept` cell is plain text until the concept's note exists, and a
wikilink from then on. The progress script reads both. Never link a concept
that has no note — see §4.0.

For each graded concept, the session grade is the **minimum** awarded across
its **graded** ladders in this session, after disputes — each ladder's grade
being its highest cleared rung (§3). Ladders whose heading says `discovery` are
excluded from this minimum: they record a hole, they do not set a level. If
every ladder on a concept was `discovery`, the level does not move and the
evidence link is still written. Then:

- higher than recorded → raise, set `Since` to today, `Evidence` to this
  session — **unless** the concept's note has `taught:` equal to today. A
  level rises only in an interview at least one day after teaching; record
  the grade in the session file, keep the level, and say why in `Reason`.
- lower than recorded → **demote to the demonstrated level** (not one step),
  set `Since` to today, `Evidence` to this session, and mark the gap
  `regressed` (§4.3)
- equal → keep `Since`, set `Evidence` to this session

Never add a level without an evidence link. Never delete a row. A concept
graded that is not yet in the table gets a row in the right cluster; a new
cluster gets a `##` heading.

### 4.3 Gaps

`topics/<topic>/gaps.md`, newest first — insert directly under the header
row:

```markdown
---
topic: dotnet
---

# .NET — gaps

Newest first. Never deleted. Status: open → studying | taught → verified | regressed.

| Date | Concept | Miss | Session | Status | Updated |
|---|---|---|---|---|---|
| 2026-09-14 | [[gc-generations]] | does not know the card table / write barrier | [[2026-09-14-gc-generations]] | open | — |
```

- Every miss from the session becomes a row with status `open`. One row per
  distinct miss; a concept can have several.
- For a concept with a `taught` or `studying` gap, check in this order:
  1. graded **below its recorded level** → `regressed`, `Updated` =
     `YYYY-MM-DD [[session]]`, plus a new `open` row for the specific miss.
  2. otherwise graded **L2 or above** → `verified`, same `Updated` format.
  3. otherwise (L0–L1, not below recorded) → status unchanged; the miss gets
     a new `open` row.
  Regressed wins over verified: an L3 concept graded L2 has regressed, even
  though L2 would verify a fresh gap.
- `Miss` is one specific line: what was asked, what was not known. Never
  "weak on GC".

### 4.3a Glossary

Every miss that says a **term** was used without being unpacked ("used
'kernel object' without being able to say what it is") also gets an entry in
`glossary.md`, in `define`'s format (`define/SKILL.md` §2), `first met:`
linking this session. If the entry exists, leave it. The gap row stays: the
entry is for looking up, the gap is what the next interview re-tests. Terms
that are a concept in their own right — a row in `mastery.md` — do not get an
entry; they get taught.

### 4.4 Queue

`review/queue.md`, sorted by `Next` ascending:

```markdown
# Review queue

Sorted by Next, earliest first. Levels live in mastery.md.

| Concept | Topic | Last | Next |
|---|---|---|---|
| [[large-object-heap]] | dotnet | 2026-09-14 | 2026-09-15 |
| [[gc-generations]] | dotnet | 2026-09-14 | 2026-09-17 |
```

For every graded concept: `Last` = today, `Next` = today + interval for the
**new** mastery level — L1 +1d, L2 +3d, L3 +7d, L4 +21d, L5 +60d. A concept
graded L0 is queued at +1d. Insert or update the row; re-sort.

### 4.5 Log

Append one row to `review/log.md`:

```markdown
| Date | Topic | Mode | Slug | Q | Target | Awarded | Δ | File |
|---|---|---|---|---|---|---|---|---|
| 2026-09-14 | dotnet | interview | gc-generations | 10 | 3.2 | 2.4 | +2 −0 =1 | [[2026-09-14-gc-generations]] |
```

`Δ` is `+raised −demoted =held`. Excursions add `(excursion)` after the
topic.

### 4.6 Dashboard

Run `pwsh scripts/progress.ps1`. If it fails, report the error verbatim and do
not hand-edit `PROGRESS.md`.

### 4.7 Commit

Offer: `session: <topic> — <slug> (avg L<avg_awarded to one decimal>)`. Do not
push unless asked.

## 5. Report

Two sentences. What moved, what is due next. The session file is the recap;
do not repeat it in chat.

## 6. Excursions

If the user overrides onto a topic with no folder:

1. Create `topics/<topic>/` with `TOPIC.md` (one-paragraph scope stub),
   `mastery.md` (only the cluster being tested, only the concepts asked plus
   obvious siblings, all L0, all plain text — not links), `gaps.md` (header
   only), and `<cluster>/notes/` and `<cluster>/sessions/` for the one cluster
   being tested. No folders for clusters this session does not touch.
2. In `ROADMAP.md`, fill the topic's `Folder` cell and set `Excursions` to 1.
3. Run the session normally. `excursion: true` in the frontmatter.

On later excursions, increment the count. Never enumerate more of the topic
than the session touched.

## 7. Never

- Never ask which mode the user wants — the default is `coached`, and `exam`
  is theirs to name.
- Never reveal a level in a coached correction, and never re-test a point that
  was corrected earlier in the same session.
- Never grade in chat before self-assessment, and in coached mode never say a
  word about a ladder before its rating is given.
- Never change a grade because the user argued. Re-ask instead.
- Never skip a write-back step because the session was short.
- Never award above target.
- Never open a ladder on a scenario or an edge case, and never skip a rung.
  Rung 1 first, every time.
- Never invent a question the user did not answer, or an answer they did not
  give, to fill the file.
- Never write `[[concept]]` before the concept's note file exists.
