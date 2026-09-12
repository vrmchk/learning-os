---
name: company
description: Research one company from a job description — what it builds, its stack, its interview process, verified with fetched sources — then map the stack onto the user's concept tree, write a prep plan, propose interview/teach sessions, and write the cover letter. Use this whenever the user names a company they are applying to or considering, asks "what does X do", "how do I prepare for X's interview", "write a cover letter for X", "what's their stack", or pastes a job posting with a company name. Never answer company questions or write a cover letter in chat outside this skill: unverified facts and unrecorded prep are worth nothing by the next session.
---

# company

One company, one file, every fact verified. Then the job's stack is laid over
the concept tree so the prep plan is a list of concepts with current levels,
not a pep talk. The cover letter comes last, because it needs both the
research and the inventory.

`CLAUDE.md` § Career layer holds the rules. `study` owns the verification
rule this skill copies. `cv` owns the application file; this skill writes
its `## Cover letter` and `## Interview prep` sections and nothing else in
it.

## 0. Sync

If the repo has a remote, `git pull --ff-only`. If it fails or the tree is
dirty, say so and ask before continuing.

## 1. Input

Needed: a company name and a role. Wanted: the job description, pasted or
as a URL. If there is already a `career/applications/*-<company>-*.md` file,
use its JD. If there is none and the user gave a JD, create the application
file in `cv` §9 format with only the frontmatter, `# heading`, and
`## Job description` filled — `cv` fills the rest when the user tailors.

Read, before anything else: `career/PROFILE.md`, `career/experience.md`,
`career/keywords.md`, an existing `career/companies/<company>.md`, and every
`topics/*/mastery.md`.

## 2. Research

Use `WebSearch` to find and `WebFetch` to read. Cover, in this order, and
stop when a heading has nothing findable:

1. **What they build and sell** — product, customers, business model. The
   company's own site first.
2. **Size and stage** — headcount band, founded, funding or public,
   offices. Their site, then a funding database or press.
3. **Engineering** — engineering blog, GitHub organisation, conference
   talks, open-source. This is where the real stack and the real problems
   are.
4. **Stack** — from the JD first (marked "from JD"), then from the
   engineering blog, GitHub, and other job postings by the same company.
   Say which source each item comes from.
5. **Interview process** — stages, formats, duration, what they emphasise.
   Company careers page first; candidate reports second and always marked
   `anecdotal`, with the date of the report.
6. **Culture and values** — their own words from the careers page. Used
   for behavioural prep and the cover letter, never quoted back as-is.
7. **Recent news** — last six months: launches, layoffs, leadership
   changes, incidents. Dated.
8. **Concerns** — anything the user should know before signing: layoffs,
   review patterns, funding runway. Facts with sources, not vibes.

**Verification — the `study` rule, verbatim:** a link and a fact enter the
file only if `WebFetch` returned the page in this run, the content says what
is written, and the title and date written are the ones on the page. Never
write a URL from memory. A fact with no fetched source is written as
`unverified` or not at all. If `WebFetch` is unavailable, say so, write only
what the JD and the user said, mark the file `research: partial`, and offer
to finish from a desk session.

### Format — `career/companies/<company>.md`

```markdown
---
company: acme
name: Acme Payments
researched: 2026-09-11
research: complete
roles: ["[[2026-09-11-acme-senior-dotnet-engineer]]"]
---

# Acme Payments

## What they build

Card-acquiring and payment orchestration for European e-commerce merchants;
revenue is per-transaction fees. Customers named on the site: ... —
[Acme — "About"](https://...) verified 2026-09-11.

## Size and stage

~400 employees, founded 2015, Series C 2024 ($80M) — [source — "title"](url) verified 2026-09-11.

## Engineering

- Engineering blog: [Acme Engineering](url) verified 2026-09-11 — 14 posts, latest 2026-07; themes: ledger consistency, Kafka at scale, .NET migration.
- GitHub: [github.com/acme](url) verified 2026-09-11 — 12 public repos, mostly SDKs.

## Stack

| Technology | Source | Note |
|---|---|---|
| C#, .NET 8 | JD | required |
| Kafka | JD; engineering blog 2026-03 | required; blog post on exactly-once |
| PostgreSQL | engineering blog 2025-11 | — |
| Kubernetes on AWS | GitHub workflows | — |

## Interview process

| Stage | Format | Source |
|---|---|---|
| Recruiter screen | 30 min call | careers page, verified 2026-09-11 |
| Technical | 60 min live coding, C# | anecdotal — [site — "title"](url), 2026-02 |
| System design | 60 min | anecdotal — same |
| Values | 45 min behavioural | careers page |

## Values

Their words, quoted with source: ...

## Recent news

- 2026-07-02 — ... — [source](url) verified 2026-09-11.

## Concerns

- ...

## Sources

Every URL above, one per line, with verified date.
```

The file is rewritten on a later run; earlier verified facts are kept
unless the new fetch contradicts them, in which case the new one wins and
the old is noted as `superseded YYYY-MM-DD`. Slugs are kebab-case; if a
slug collides with a concept note anywhere in the vault, prefix
`company-`.

## 3. Stack → concept tree

For every technology and practice in the JD and the Stack table, find the
matching concept rows and clusters in `topics/*/mastery.md`. Build the map:

| JD item | Weight | Concept(s) in tree | Level | Gap status | Prep |
|---|---|---|---|---|---|
| async/await internals | must | async-state-machine, configureawait-and-synchronizationcontext | L0, L0 | — | interview |
| Kafka | must | — (not in any tree) | — | — | study, then interview as excursion into `system-design` |
| EF Core | must | change-tracking, query-translation | L1, L0 | open | teach first |

Rules:

- `Prep` is `interview` when the concept is L2+ or untested with no open
  gap (measure first); `teach` when there is an `open` or `regressed` gap;
  `study` when the concept is absent from every tree and the user has never
  used it (the map says which topic folder it would belong to).
- Order the plan by weight, then by distance between the level the role
  needs and the current level. Say what the role needs: a senior backend
  interview asks L3–L4 on the core stack.
- **Never edit `topics/`.** Absent concepts are proposed, and `interview`,
  `teach`, or `study` create the rows when the user runs them. Propose the
  first session in one line: *"Run `interview` on the Async and threading
  cluster — 4 must-have items there, all L0."*

## 4. Prep plan

Written into the application file under `## Interview prep`, in this order:

1. **Stack map** — the table from §3.
2. **Session plan** — three to six lines, each a concrete `interview`,
   `teach`, or `study` run with the concept or cluster, in order.
3. **Likely technical questions** — eight to twelve, derived from the JD's
   must-haves and the engineering blog's themes, each tagged with the
   concept it tests and a target level. These are not answered here; they
   are what `interview` will ask.
4. **Behavioural** — four to six questions derived from the values section,
   each with the inventory achievement ID that best answers it. No scripted
   answers; the ID is the answer's source.
5. **Questions to ask them** — five, specific to what the research found
   (a blog post, a migration, a news item). Generic questions are not
   written.
6. **Logistics** — stages from §2.5, what to have ready.

## 5. Cover letter

Written only when the user asks for one, into `## Cover letter` in the
application file, and only after §2 and the inventory exist.

Rules:

- 250–350 words, four paragraphs, plain text, no headings, no bullets.
- **Paragraph 1** — the role, and one specific thing about the company
  from §2 that a template could not contain (a blog post, a product
  detail, a stated problem). Not "I am excited to apply".
- **Paragraph 2** — two achievements from the inventory, by ID in a
  comment, chosen because they match the JD's top two must-haves. Numbers
  as in the inventory, `~` kept.
- **Paragraph 3** — what the user would do in the first months, tied to
  something the research found they are doing. One sentence on why this
  company over others, true.
- **Paragraph 4** — close, availability, contact from PROFILE.
- JD keywords appear naturally, each once. No "passionate", "dynamic",
  "leverage", "synergy", "fast-paced", "team player", "hit the ground
  running". No restating the CV.
- Nothing about the company that is not in `career/companies/<company>.md`
  with a source. Nothing about the user that is not in the inventory.
- Below the letter: `Achievements used: ACME-1, ACME-2. Company facts used:
  <two source titles>.`

Offer one alternative opening paragraph if the user asks; do not write
three versions unasked.

## 6. Write-back — in this order

1. `career/companies/<company>.md` (§2 format).
2. The application file's `## Interview prep` and, if asked, `## Cover
   letter`. Add the application wikilink to the company file's `roles`.
3. `career/log.md`, one row:
   `| 2026-09-11 | company | research+prep | acme — stack map 9 items, 4 sessions proposed, 11 sources | [[acme]] |`
4. Offer the commit: `career: company — <company>`. Do not push unless
   asked.

## 7. Report

Three lines: what the company does in one sentence, the biggest gap between
the role's stack and the concept tree, and the first session to run. The
file is the recap.

## 8. Never

- Never write a company fact without a source fetched in this run, or
  without marking it `unverified`.
- Never write a URL from memory.
- Never write a cover-letter claim that is not an inventory row.
- Never edit `topics/`, `review/`, `mastery.md`, or a level. Propose
  sessions; do not run them from inside this skill — say which to run next
  and stop.
- Never fill the application file's `## Keywords`, `## Tailoring
  decisions`, or `## Check` — those are `cv`'s.
- Never present anecdotal interview reports as the process. Mark them.
- Never write a generic cover letter. If the research found nothing
  specific, say so and ask whether to send without one.
