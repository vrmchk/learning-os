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

Recognise `exam` from the argument (`exam`, `exam mode`, `no feedback`, `don't
correct me`) or from the user asking to be measured rather than taught.
Coached is also what the words `coached`, `show ideal answers`, `with
feedback` and `coached mode` select, and what a request for corrections as you
go means.
Say which mode is running in the same line as the proposal:
*"Proposing `gc-modes` — rule 1, overdue 2 days. Coached mode."*

The mode changes **one thing**: when the feedback arrives. Proposal rules,
targets, question mix, probing, coverage caps, the rubric, the three-lows stop
rule, self-assessment, and the whole of §4 are identical.

| | exam | coached |
|---|---|---|
| Between question and answer | nothing | nothing |
| After the answer and its probes | next question | where it fell short, then the model answer |
| Grades | after self-assessment | after self-assessment |
| Level changes, write-back | full | full |
| Frontmatter | `coached: false` | `coached: true` |
| Calibration checkpoint | counts | counts |

**Coached mode, exactly:**

1. Ask the question. Probe as normal. **No correction inside a question** — a
   probe is part of the question, so the feedback waits until probing is done.
2. Then, before the next question: a short **"Where you were short"** list —
   what was wrong, what was missing, what was right — and a **model answer** at
   the length a person could say out loud. Same content as `teach`'s model
   answers; this is not a second lecture on the concept.
3. Grade silently as always. **Never reveal the level**, not even loosely
   ("that was about an L2"). The correction says what was missing, not what it
   scored.
4. **Never re-test a corrected point later in the session.** An answer repeated
   back from a model answer is not unaided evidence. Move to another part of
   the concept, and if that leaves nothing askable, switch concept.
5. In the session file: set `coached: true`, and put one paragraph under the
   proposal line saying the format was coached, that the self-assessment
   followed the corrections, and which later questions were constrained by
   rule 4.

The reason for the default, and the cost accepted by letting coached sessions
count for calibration, is in `BOOTSTRAP.md` §6, "Two interview modes", and
§9: a coached session teaches better and measures worse, and the system now
prefers the sessions that get run.

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
6. **Plan the mix** before asking anything: 6 depth / 2–3 adjacent or
   prerequisite / 1–2 cold recall from the queue. If the queue has nothing
   due, cold-recall slots go to depth. Write the plan in your head, not in
   chat. Dispute re-asks (§3) do not count toward the ten.

## 2. Asking

One question at a time. Wait for the full answer. Nothing between the
question and the answer — in both modes. Coached feedback comes after the
probes, never inside them.

For **every** question, before it is asked, fix two things and keep them:

- the **concept** it tests (one wikilink; a question may touch others, but
  one is graded)
- the **target level** it is pitched at — the highest level a complete answer
  could demonstrate. A question about *what* a term means targets L1; *how to
  use it* L2; *when and what it costs* L3; *what happens underneath and how
  it fails* L4; *design under constraints and defend* L5.

- the **kind**: `depth`, `adjacent`, `cold recall`, or `discovery`.

An awarded grade can never exceed the target. To earn L4 the question must be
pitched at L4.

**Coverage caps the target.** Before pitching a question above L2, check the
concept's note: the Mechanism, Failure modes or Trade-offs sections must
actually treat the thing you are about to ask about. A single clause in passing
is not coverage. If the note only mentions it, the ceiling is L2. If there is
an `open` gap row or a recorded drill miss on that exact point, it is `teach`'s
job — skip it, or ask it as `discovery`.

**Discovery questions** find holes; they do not measure. Pitch at L1, label the
heading `discovery`, grade and record as normal, and write the miss to
`gaps.md`. They are excluded from the concept grade (§4.2) and from the stop
rule below. A discovery question can neither raise nor lower a level, so asking
one is never a way to damage a number. It is how an untested corner gets found
and handed to `teach`.

For **open-ended design questions** (target L4–L5, "how would you…", "design
a…"), write the checklist of what a strong answer must contain **before**
asking. Three to six items, each a specific thing the answer must say. It goes
into the session file verbatim, and the answer is graded against it item by
item. Never revise the checklist after the answer.

**Probing.** A vague answer gets at least two probes — *why?* and *what breaks
if…?* — before it is graded. Probes are part of the same question. Stop
probing when the answer is either clearly demonstrated or clearly not; do not
lead the user to it.

**"hint"** — give one hint, then let them continue. The question is capped at
L2: a hinted answer is not unaided.

**"pass"** — record it, award per the first-contact rule (cannot define →
L0; can define but not use → L1), move on. Say nothing else.

**Three consecutive graded questions at L1 or lower** → end the session here.
Do the full write-back for what was asked (§4), then tell the user you are
switching to `teach` for the concept with the lowest grade, and run it.
`discovery` questions do not count toward the three: three L1s on material
nobody has taught means it is new, not that teaching has failed.

Stop at ten questions. Claude cannot measure wall-clock; if the user says time
is up, stop at once and grade what was answered.

## 3. Grading

Grade each answer as it is completed, **silently**. Record the grade; say
nothing about it. Grades are revealed only after self-assessment — in coached
mode too, where the correction says what was missing and never what it scored.

Apply `CLAUDE.md`'s anti-inflation rules literally. The ones that bite most:

- Between two levels → the lower one.
- Missed the trade-off → cap L2, even if everything said was correct.
- Used a term, could not unpack it when probed → L1 for that term. Record the
  term in the miss.
- Fluent, confident, well-structured → worth nothing. Grade the content.
- Awarded ≤ target, always.
- A `discovery` question is graded and recorded like any other, but it is
  excluded from the concept grade in §4.2.

Write the one-line reason at grading time, naming the rule if a cap applied.

**Self-assessment.** After the last answer, before any grade is shown, ask
exactly this: *"Before I show grades — which answers did you think were
weak?"* Record the list. Then reveal the grades table.

**Disputes.** If the user disagrees with a grade, do not change it and do not
debate it. Ask two or three further questions on the same concept at the same
target level, grade those, and set the final grade from the whole picture.
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
questions: 10
avg_target: 3.2
avg_awarded: 2.4
concepts: [gc-generations, large-object-heap, gc-modes]
self_flagged: [3, 7]
disputes: 0
---

# 2026-09-14 — GC generations

**Proposed by rule:** 5 — lowest-level concepts in focus topic
**Override:** none

## Q1 — [[gc-generations]] — target L3 — depth

**Question:** What decides whether an object is allocated in gen 0, and what
has to be true for it to survive to gen 1?

**Answer:** Said allocation is always gen 0 except large objects. Said
survival is "if it's still referenced when a GC happens". Did not mention the
allocation budget or the card table when probed.

**Probes:**
1. *Why gen 0 and not straight to gen 2?* → "because it's cheaper" — could
   not say why it is cheaper.
2. *What breaks if a gen-2 object references a gen-0 object?* → did not know
   the write barrier / card table exists.

**Awarded:** L2 — correct on the surface, missed the mechanism (card table)
and the trade-off (why generational at all). Cap: missed trade-off.

## Q2 — [[large-object-heap]] — target L4 — depth

**Question:** ...

**Checklist:**
- [ ] threshold is 85,000 bytes
- [x] LOH is collected only with gen 2
- [ ] LOH is not compacted by default and why
- [ ] `GCSettings.LargeObjectHeapCompactionMode` exists

**Answer:** ...

**Probes:** ...

**Awarded:** L1 — one of four checklist items. Used "fragmentation" but could
not say what fragments or why compaction is off.

...

## Self-assessment

User flagged as weak: Q3, Q7

## Grades

| Q | Concept | Target | Awarded | Self-flagged | Dispute |
|---|---|---|---|---|---|
| 1 | [[gc-generations]] | L3 | L2 | — | — |
| 2 | [[large-object-heap]] | L4 | L1 | — | — |
| 3 | [[gc-modes]] | L3 | L3 | weak | — |
| 4 | [[gc-generations]] | L3 | L2 | — | L1 → L2: re-asked ×2, named the budget on the second |

## Level changes

| Concept | Before | After | Reason |
|---|---|---|---|
| [[gc-generations]] | L0 | L2 | min of Q1 L2, Q4 L2 |
| [[large-object-heap]] | L0 | L1 | first contact, could define |
| [[gc-modes]] | L3 | L3 | held; evidence refreshed |

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
- `Checklist` appears only for design questions, and only as written before
  the answer.
- `Self-flagged` is `weak` or `—`. `Dispute` is `—` or `<orig> → <final>:
  <reason>`.
- The kind in each `## Q<n>` heading is `depth`, `adjacent`, `cold recall` or
  `discovery`. The Grades table format does not change — the progress script
  parses it — so `discovery` is recorded in the heading only, and the Level
  changes table says which questions were excluded and why.

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
its **graded** questions in this session, after disputes. Questions whose
heading says `discovery` are excluded from this minimum: they record a hole,
they do not set a level. If every question on a concept was `discovery`, the
level does not move and the evidence link is still written. Then:

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
- Never grade in chat before self-assessment.
- Never change a grade because the user argued. Re-ask instead.
- Never skip a write-back step because the session was short.
- Never award above target.
- Never invent a question the user did not answer, or an answer they did not
  give, to fill the file.
- Never write `[[concept]]` before the concept's note file exists.
