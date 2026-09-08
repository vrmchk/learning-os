---
name: teach
description: Explain one concept from the gaps file — mechanism, then failure modes, then trade-offs — write the concept note, drill three questions immediately, and queue it for review at +1 day. Use this whenever the user asks to be taught, wants something explained, says "teach me X", "explain X", "I don't get X", "walk me through X", or when the interview skill stops a session for three consecutive L1s. Also use it when they ask what a gap means. Never explain a concept at length outside this skill — an explanation that is not written to a note and drilled is forgotten by the next session.
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

## 2. Explain

In this order, with these headings, in chat:

1. **Mechanism** — what actually happens, at the level below the API. Names
   of the real moving parts (the card table, the state machine's `MoveNext`,
   the sync block index). Diagrams in ASCII where the shape matters.
2. **Failure modes** — how it goes wrong in production, what the symptom
   looks like, and how to tell it apart from its neighbours.
3. **Trade-offs** — what it costs, what the alternatives cost, when a senior
   engineer would choose each. This is the section interviews grade on;
   never skip it.

Length: enough to whiteboard from, not a chapter. If the concept genuinely
needs more than a screen or two, split it and say so — the second half
becomes its own concept.

Do not quiz during the explanation. Do not ask "does that make sense".

## 3. Write the note

`topics/<topic>/notes/<concept>.md`. One concept per file. If the file
exists, replace the Mechanism / Failure modes / Trade-offs sections and keep
everything else.

```markdown
---
concept: gc-generations
topic: dotnet
cluster: memory-and-gc
created: 2026-09-15
taught: 2026-09-15
---

# GC generations

## Mechanism

...

## Failure modes

...

## Trade-offs

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

## Mechanism

## Failure modes

## Trade-offs

## Resources

## Related
```

No `taught` key, no drill section, empty headings. Creating a stub also
turns the concept's cell in `mastery.md` from plain text into `[[concept]]`.
Teaching later fills the stub in place.

Rules:

- Frontmatter keys are fixed. `taught` is the date of the most recent teach;
  a stub omits it.
- Mechanism / Failure modes / Trade-offs are written from the explanation
  just given, tightened. Not a transcript of the chat.
- Each teach appends a new `## Drill — <date>` section; earlier drills stay.
- `## Resources` is owned by `study`. Leave it empty or as is; optionally
  append one or two *verified* links under it following `study`'s format.
- `## Related` lists wikilinks to sibling concepts. Every link must resolve to
  an **existing note file** in `topics/**/notes/`. A sibling that has no
  note yet is not linked — leave it out, or create its stub first. Never link
  a name that is only a mastery row, and never invent one.
- If the concept's `mastery.md` cell is still plain text, turn it into
  `[[concept]]` when the note is written.
- Concept file names are unique across the vault. Check `topics/**/notes/`
  before creating one.

## 4. Drill

Immediately after the note is written, three questions, one at a time, on
what was just explained. Wait for each answer. No hints.

Pitch: one at L2 (apply), one at L3 (trade-off), one at L4 (mechanism or
failure mode). Record each as `hit` or `miss` in the drill table — no
levels, no grades, no discussion of levels. A miss here is expected; it says
what the interview will probe.

After the third answer, say which ones missed and why, in one line each.

## 5. Write-back — in this order

1. **Note** — §3, with the drill table filled in.
2. **Gap** — in `gaps.md`, set every `open` or `regressed` row for this
   concept to `taught`, `Updated` = `YYYY-MM-DD [[note-name]]`. If there was
   no gap row, add one dated today with `Miss` = "taught on request" and
   status `taught`.
3. **Queue** — in `review/queue.md`, set the concept's `Last` = today,
   `Next` = today + 1 day, regardless of its level. Insert if absent, re-sort.
4. **Log** — append to `review/log.md`:
   `| 2026-09-15 | dotnet | teach | gc-generations | 3 | — | — | 1 hit 2 miss | [[gc-generations]] |`
5. **Dashboard** — `pwsh scripts/progress.ps1`.
6. **Commit** — offer `teach: <concept>`.

Mastery is not touched. `Since`, `Level`, `Evidence` stay as they were.

## 6. Report

One sentence: the concept, the drill result, and the interview date.
*"Taught `gc-generations`; 1 of 3 drill questions hit; due for interview
2026-09-16."*

## 7. Never

- Never raise a level. Not for a perfect drill.
- Never write a note without drilling. Never drill without writing the note.
- Never teach two concepts in one run because they are "related".
- Never invent a source or a link. Links go through `study`'s verification
  or do not go in.
