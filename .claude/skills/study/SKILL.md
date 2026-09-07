---
name: study
description: Find and verify reading and viewing material for a concept or cluster so the user can self-study instead of being taught, then record it and queue the concept for an interview. Use this whenever the user asks for resources, articles, docs, links, papers, talks, videos, "what should I read on X", "where do I learn X", "recommend something on X", or says they want to research a topic themselves. Never answer a request for resources with bare links in chat — links go through this skill's verification and into the vault, and the concept gets an interview date, or the self-study never gets tested.
---

# study

Self-study that never gets tested is invisible to this system. This skill
exists to make sure it gets tested: find good material, **verify every link**,
write it into the note, and put the concept on the queue.

This skill **never changes a level** and never explains the concept — that is
`teach`. It owns the `## Resources` section of a note.

## 1. Pick the concept

1. If the user named a concept, resolve it to a slug in `mastery.md`. If it
   is not there, say which cluster it belongs to and add the row at L0.
2. If they named a cluster, pick up to three concepts in it — `regressed`
   gaps first, then `open` gaps, then lowest level — and say which.
3. If they named nothing, propose from the focus topic's `gaps.md`: `open`
   gaps oldest first. Name the rule.

Read the concept's note, gap rows, and the misses in linked session files.
The misses decide what the resources need to cover. A gap that says "cannot
say why the LOH is not compacted" wants a resource about compaction and
fragmentation, not a general GC overview.

## 2. Find

Start from the topic's **Trusted sources** list in `TOPIC.md`. Prefer, in
order:

1. Primary — official docs, the runtime's own design docs (BOTR), source
   comments, the people who wrote the thing.
2. Deep secondary — long-form posts by known practitioners, conference talks
   by them, books.
3. Everything else — only if 1 and 2 have nothing on the specific miss.

Use `WebSearch` to find candidates and `WebFetch` to read them. Aim for three
to five resources, mixed by form where it helps: a doc page, a deep post, a
talk. Fewer is fine. For each, decide *which part* — a section, a chapter, a
timestamp range — not the whole thing.

## 3. Verify — non-negotiable

A link enters the vault only if **all** of these held in this run:

- `WebFetch` returned the page successfully.
- The fetched content is actually about the concept and covers the miss.
- The title and author written down are the ones on the fetched page.

If `WebFetch` is unavailable in this environment (some mobile sessions), say
so, give the candidates in chat marked **unverified**, and **do not write
them to the note**. Offer to verify next time from a desk session.

Never write a URL from memory. Never write a link because it "should exist".
An LLM-suggested URL that 404s is worse than no link — it costs the user a
trip and their trust in every other link in the vault.

## 4. Write-back — in this order

### 4.1 Note

`topics/<topic>/notes/<concept>.md`. If it does not exist, create a stub in
`teach`'s note format with frontmatter (`concept`, `topic`, `cluster`,
`created`; no `taught`), empty Mechanism / Failure modes / Trade-offs
headings, and the Resources section. If it exists, only touch
`## Resources`.

```markdown
## Resources

- [Stephen Toub — "How Async/Await Really Works in C#"](https://devblogs.microsoft.com/dotnet/how-async-await-really-works/) — post, read from "Compiler transformation" to the end, ~40 min. Draws the state machine your interview miss was about. Verified 2026-09-07.
- [.NET docs — Task-based asynchronous pattern](https://learn.microsoft.com/dotnet/standard/asynchronous-programming-patterns/task-based-asynchronous-pattern-tap) — docs, "Choosing the return type" section only, ~10 min. Verified 2026-09-07.
- [NDC — "Async internals" (talk)](https://www.youtube.com/...) — video, 12:00–34:00, ~22 min. The whiteboard walk-through. Verified 2026-09-07.
```

One line per resource, in this shape:
`- [Author or site — "Title"](url) — <form>, <which part>, ~<time>. <one clause on why this one>. Verified <date>.`

Append under existing resources; do not remove earlier ones. If a resource
was already there, do not add it again.

### 4.2 Gap

In `gaps.md`, set every `open` or `regressed` row for the concept to
`studying`, `Updated` = `YYYY-MM-DD [[note-name]]`. If there was no gap row,
add one dated today, `Miss` = "self-study on request", status `studying`.

### 4.3 Queue

In `review/queue.md`: `Last` = today, `Next` = today + 3 days, regardless of
level. Insert if absent, re-sort. The user can ask for a different date; +3
is the default because reading takes longer than being taught and forgets
faster than being drilled.

### 4.4 Log

Append to `review/log.md`:
`| 2026-09-07 | dotnet | study | thread-pool-starvation | — | — | — | 3 resources | [[thread-pool-starvation]] |`

### 4.5 Dashboard and commit

`pwsh scripts/progress.ps1`, then offer `study: <concept>`.

## 5. Report

One sentence per concept: how many resources, total estimated time, interview
date. *"3 resources for `thread-pool-starvation`, ~70 min; interview due
2026-09-10."*

## 6. Never

- Never write an unverified link. Not with a caveat, not "to fix later".
- Never summarise the resources in place of the user reading them — that
  turns `study` into a worse `teach`.
- Never change a level or a `taught` date.
- Never skip the queue step. That is the whole point.
