---
name: teach
description: Explain one concept from the gaps file layer by layer — what it is, using it, trade-offs, how it works, where it breaks, in practice — pausing for questions between layers, write the concept note, drill three questions immediately, and queue it for review at +1 day. Use this whenever the user asks to be taught, wants something explained, says "teach me X", "explain X", "I don't get X", "walk me through X", or when the interview skill stops a session for two consecutive ladders at L1 or lower. Also use it when they ask what a gap means. Never explain a concept at length outside this skill — an explanation that is not written to a note and drilled is forgotten by the next session.
---

# teach

Explain, write, drill, queue. Four steps, always all four. Reading an
explanation is not evidence of anything, so this skill **never changes a
level** — it makes the next interview possible.

`CLAUDE.md` holds the vocabulary and the rules. `interview` owns the formats
of `mastery.md`, `gaps.md`, `review/queue.md`, and `review/log.md`; this skill
writes to them in those formats. This skill owns the **note** format.

## 0. Sync

If the repo has a remote, `git pull --ff-only`. If it fails or the tree is
dirty, say so and ask before continuing.

## 1. Pick the concept

1. If the user named a concept, use it. Resolve it to a concept slug in
   `mastery.md`; if it is not there, say which cluster it belongs to and add
   the row at L0 (plain text — it becomes a link when the note is written).
   If the **topic** has no folder yet, create it exactly as `interview` §6
   does for an excursion, then continue; do not bump the excursion count.
2. If not, read the focus topic's `gaps.md` and propose, in this order:
   1. `regressed` gaps, oldest first — these were taught once and failed
   2. `open` gaps, oldest first
   3. any concept at L0 or L1 in the focus cluster, if one is set
   Name the rule: *"Proposing `card-table` — rule 2, open since 2026-09-14."*
3. One concept per run. If the user asks for a cluster, pick the concept
   whose gap is oldest and say the rest will follow.

Read the concept's existing note if there is one, its gap rows, and every
session file that links it — the misses say exactly what to teach. Teach to
the misses, not to the textbook table of contents.

## 2. Explain — in layers

Teach in the order the interview asks (`interview/SKILL.md` §2, the ladder):
from what the thing is, down to how it works, never the other way round.
Rationale: `BOOTSTRAP.md` §6, "Teaching in layers" (decided 2026-09-30).

In this order, with these headings, in chat:

1. **What it is** — the problem it solves and what it does about it, in plain
   words. Why it exists: what goes wrong without it. No internals, no
   implementation names. A reader who knows nothing else about the concept
   can follow this section alone. Target rung 1.
2. **Using it** — where you meet it in everyday code: what you write, what
   calls it for you, a short code example. Still no internals. Target rung 2.
3. **Trade-offs** — when to reach for it, what it costs, the alternatives and
   what they cost. The costs are stated here as facts ("it allocates", "it
   holds a thread"); *why* they cost that is the next layer. This is where an
   interview first separates people; never skip it. Target rung 3.
4. **How it works** — the machinery underneath: the real moving parts, built
   on what the first three layers established. ASCII diagrams where the shape
   matters. Target rung 4.
5. **Where it breaks** — failure modes and edge cases: how it goes wrong in
   production, what the symptom looks like, how to tell it apart from its
   neighbours. Target rung 4.
6. **In practice** — one worked scenario that needs every layer above: the
   situation, the reasoning in order, the decision and what it costs. Numbers
   where numbers decide it. Target rung 5.

**Bridges.** Each section after the first opens with one sentence that picks
up the question the previous one left open — *"So the pool hands out threads.
Where does the work it runs come from?"* A section that could be read without
the one before it is fine; a section that starts cold is not.

**Terms.** No term is used before it is explained.

- A new term gets a plain one-line definition where it first appears — what it
  is, not what it is made of.
- *What it is* and *Using it* introduce almost no new terms. *Trade-offs* and
  each later section introduce **at most three**. If a layer needs more, it is
  doing two jobs; split it.
- A term that belongs to another concept (the async state machine, a
  `SynchronizationContext`) gets a one-line gloss and is marked as a later
  concept — *"the compiler turns the method into a small object that can pause
  and resume; that is `async-state-machine`, tier 2"*. Never dropped in as
  though known.
- Before writing, read the user's gap rows and session misses for terms they
  used without unpacking. Those get the definition even if they seem basic.
- Every general term defined this way also belongs in `glossary.md` (§5 step
  2). If an entry already exists, the note still gives the one-line definition
  where the term first appears — the note must read on its own — and may link
  the entry: `[[glossary#Kernel]]`.

**Pauses.** After about every two layers — after *Using it*, after *How it
works*, and before *In practice* — stop and ask exactly: *"Questions on this,
or next layer?"* Answer any question in the same layered voice, then continue.
This is a place for the user to ask, **not** a comprehension check: never ask
"does that make sense", never quiz, never ask the user to restate anything.

Length: enough to whiteboard from, not a chapter — six short sections, not six
long ones. If the concept genuinely needs more than about two screens across
all layers, split it and say so — the second half becomes its own concept.

## 3. Write the note

`topics/<topic>/<cluster>/notes/<concept>.md`, where `<cluster>` is the
kebab-case slug from `TOPIC.md` and matches the note's `cluster:` frontmatter.
Create the cluster folder if this is its first use. One concept per file. If the file
exists, replace the six layer sections — or, in a note written before
2026-09-30, the old Mechanism / Failure modes / Trade-offs sections, which are
removed and rewritten as the six layers — and keep everything else (drills,
model answers, resources, related).

```markdown
---
concept: gc-generations
topic: dotnet
cluster: memory-and-gc
created: 2026-09-15
taught: 2026-09-15
---

# GC generations

## What it is

...

## Using it

...

## Trade-offs

...

## How it works

...

## Where it breaks

...

## In practice

...

## Drill — 2026-09-15

| Q | Question | Answer (summary) | Result |
|---|---|---|---|
| 1 | What is the card table for? | Said "tracks old-to-young refs" — correct | hit |
| 2 | What marks a card? | Said "the GC" — it is the write barrier on the mutator side | miss |
| 3 | Why not scan all of gen 2 instead? | Named the cost; did not connect it to pause time | miss |

Drill results do not change a level.

## Resources

## Related

[[large-object-heap]] · [[gc-modes]] · [[write-barrier]]
```

### Stub

The minimum note. `interview` and `study` create it on first touch so that
every `[[concept]]` wikilink in the vault resolves — an unresolved link is a
ghost node in the graph. A stub is exactly this, nothing more:

```markdown
---
concept: gc-generations
topic: dotnet
cluster: memory-and-gc
created: 2026-09-14
---

# GC generations

## What it is

## Using it

## Trade-offs

## How it works

## Where it breaks

## In practice

## Resources

## Related
```

No `taught` key, no drill section, empty headings. Creating a stub also
turns the concept's cell in `mastery.md` from plain text into `[[concept]]`.
Teaching later fills the stub in place.

Rules:

- Frontmatter keys are fixed. `taught` is the date of the most recent teach;
  a stub omits it.
- The six layer sections are written from the explanation just given,
  tightened, with their bridges and term definitions kept — the note must read
  in the same order and at the same pace as the chat did. Answers given during
  the pauses go into the layer they belong to if they filled a real hole. Not a
  transcript of the chat.
- A stub created before 2026-09-30 has the old empty headings; teaching it
  replaces them with the six layers.
- Each teach appends a new `## Drill — <date>` section; earlier drills stay.
- Each teach appends a `## Model answers — <date>` section, after the drill
  sections and before `## Resources`: one `### Q<n> (<session date>) — target
  L<n>, awarded L<n>` block per interview question graded below target, each
  with the model answer and a closing line naming what the graded answer
  lacked. Earlier model-answer sections stay.
- `## Resources` is owned by `study`. Leave it empty or as is; optionally
  append one or two *verified* links under it following `study`'s format.
- `## Related` lists wikilinks to sibling concepts. Every link must resolve to
  an **existing note file** under `topics/**/notes/` at any cluster. A sibling that has no
  note yet is not linked — leave it out, or create its stub first. Never link
  a name that is only a mastery row, and never invent one.
- If the concept's `mastery.md` cell is still plain text, turn it into
  `[[concept]]` when the note is written.
- Concept file names are unique across the vault, whatever cluster folder
  they sit in — Obsidian resolves wikilinks by name, not path. Check
  `topics/**/notes/`
  before creating one.

## 4. Drill

Immediately after the note is written, three questions, one at a time, on
what was just explained. Wait for each answer. No hints.

Pitch: one at L2 (apply), one at L3 (trade-off), one at L4 (mechanism or
failure mode), **asked in that order** — the same climb as an interview ladder
(`interview/SKILL.md` §2), so the practice has the shape of the exam. Word
them plainly, the way an interviewer would; no scenario-first framing below
L4. Unlike an interview ladder, a miss does not stop the drill: all three are
asked. Record each as `hit` or `miss` in the drill table — no
levels, no grades, no discussion of levels. A miss here is expected; it says
what the interview will probe.

After the third answer, say which ones missed and why, in one line each.

Every drill miss becomes an `open` gap row (§5.2). A miss recorded only in the
drill table is invisible to `interview`, which is how the same miss gets
interviewed twice with nothing taught in between.

### Model answers

Then, in the same run, write out what a strong answer would have been to each
**interview** question on this concept that was graded below its target. Read
them from the session files that link the concept. One block per question: the
question as asked, the grade it got, and the answer that would have earned the
target, at the length a person could actually say out loud. Close each with the
two or three things the graded answer was missing.

This is not a second explanation. It is the shape of a good answer to a
specific question, which is exactly what being graded does not teach. It goes
in the note under `## Model answers — <date>` and into chat.

## 5. Write-back — in this order

1. **Note** — §3, with the drill table filled in.
2. **Glossary** — every general term the explanation defined (and every term
   the user asked about in a pause) gets an entry in `glossary.md`, in
   `define`'s format (`define/SKILL.md` §2), with `first met:` linking this
   note. Improve existing entries rather than duplicating. Terms that are
   this concept's own vocabulary — the thing being taught — do not need one;
   general words the user will meet again elsewhere do.
3. **Gap** — in `gaps.md`, set every `open` or `regressed` row for this
   concept to `taught`, `Updated` = `YYYY-MM-DD [[note-name]]`. If there was
   no gap row, add one dated today with `Miss` = "taught on request" and
   status `taught`. Then add one **new `open` row per drill miss**, dated
   today, `Miss` = the specific thing missed, `Session` = `[[note-name]]`.
   A drill miss is a known untaught miss; it must be visible to `interview`'s
   proposal and coverage rules, not buried in the drill table.
4. **Queue** — in `review/queue.md`, set the concept's `Last` = today,
   `Next` = today + 1 day, regardless of its level. Insert if absent, re-sort.
5. **Log** — append to `review/log.md`:
   `| 2026-09-15 | dotnet | teach | gc-generations | 3 | — | — | 1 hit 2 miss | [[gc-generations]] |`
6. **Dashboard** — `pwsh scripts/progress.ps1`.
7. **Commit** — offer `teach: <concept>`.

Mastery is not touched. `Since`, `Level`, `Evidence` stay as they were.

## 6. Report

One sentence: the concept, the drill result, and the interview date.
*"Taught `gc-generations`; 1 of 3 drill questions hit; due for interview
2026-09-16."*

## 7. Never

- Never raise a level. Not for a perfect drill.
- Never leave an interview question that was graded below target without a
  model answer.
- Never write a note without drilling. Never drill without writing the note.
- Never teach two concepts in one run because they are "related".
- Never open with internals, and never use a term before its one-line
  definition. What it is and Using it come first, every time.
- Never turn a pause into a quiz.
- Never invent a source or a link. Links go through `study`'s verification
  or do not go in.
