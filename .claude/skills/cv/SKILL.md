---
name: cv
description: Build, tailor, check, and maintain the user's CV and LinkedIn profile for applicant tracking systems (ATS) and recruiter search. Use this whenever the user mentions their CV, resume, LinkedIn, headline, About section, ATS, a CV template, keywords for a job, a job description they want to apply to, or asks how to describe their experience, achievements, or skills. Every CV claim comes from career/experience.md — if the inventory is empty, this skill builds it first. Never draft CV bullets, a LinkedIn section, keyword advice, or template opinions in chat outside this skill: it goes into the career files or it is lost by the next session.
---

# cv

The CV is a view. `career/experience.md` — the achievement inventory — is the
state. This skill fills the inventory, renders views of it (master CV,
tailored CVs, LinkedIn sections), checks those views against what an ATS
actually does, and keeps a list of what to improve next.

`CLAUDE.md` § Career layer holds the rules. `BOOTSTRAP.md` §10 holds the
rationale. This file holds the mechanics and the exact file formats.

**What an ATS actually does.** It parses the file into fields — name,
contact, titles, employers, dates, skills — and a recruiter then searches and
filters those fields, usually by title, skill keywords, location, and years.
Auto-rejection comes from knockout questions on the application form, not
from a keyword percentage. So a CV has three gates, in this order:

1. **Parse** — the fields come out right. Broken by columns, tables, text
   boxes, icons, headers/footers, images, unusual fonts, creative headings.
2. **Search** — the recruiter's exact words are present. Broken by synonyms,
   missing acronym/full-form pairs, a title that does not match the search.
3. **Skim** — a human reads it for six seconds: current title, current
   employer, the first two bullets, the skills line. Broken by weak verbs,
   no numbers, walls of text.

No vendor publishes a score. `scripts/cv-check.py` prints one; it is a
heuristic and is reported as one.

## 0. Sync

If the repo has a remote, `git pull --ff-only`. If it fails or the tree is
dirty, say so and ask before continuing.

## 1. Read

- `career/PROFILE.md` — targets, constraints, contact block, improvements
- `career/experience.md` — the inventory
- `career/keywords.md` — the bank
- `career/cv/master.md`, `career/cv/templates.md`, `career/linkedin.md`
- `career/log.md` — last five rows
- every `topics/*/mastery.md` — for the honesty cross-check (§13)

Today's date comes from the system clock. Never guess it.

## 2. Pick the mode

| The user says | Mode | Needs first |
|---|---|---|
| "tell me about your experience", "let's fill the inventory", first run | `inventory` | — |
| "is this template ok", "which template", "evaluate this CV file" | `template` | — |
| "build my CV", "write my CV", "master CV" | `master` | inventory with ≥ 1 role |
| "tailor for this job", pastes a JD, "apply to X" | `tailor` | master |
| "keywords", "what should I add for X jobs", pastes several JDs | `keywords` | — |
| "LinkedIn", "headline", "About section", "profile" | `linkedin` | inventory |
| "check my CV", "run the check", attaches a file | `check` | — |
| "what else", "how else can you help", "improve" | `improve` | — |

If the prerequisite is missing, say so in one line and run the prerequisite
first. One mode per run unless the user asks for the whole pipeline. When
they do, the order is inventory → keywords → master → check → linkedin.

Ask before starting a mode only if the input is genuinely missing — a JD for
`tailor`, a file for `template` or `check`. Otherwise start.

## 3. Inventory (mode `inventory`)

A structured interview, one role at a time, newest first. The inventory is
what makes every later mode honest, so it is built slowly and completely.

**Per role, get:** company, title as it appeared on paper, dates (month and
year), location and remote status, domain, team size and who the user
reported to, the stack, and one paragraph of scope — what the system was,
what the user owned.

**Then achievements.** For each, ask in this order, one at a time:

1. *What was the problem or the state before?*
2. *What did you do, specifically, with which technology?*
3. *What changed, and what is the number?* — latency, throughput, error
   rate, cost, revenue, users, time saved, incidents, team size, releases,
   data volume, test coverage, uptime.
4. *How do you know the number?* — measured, from a dashboard, from a
   report, estimated. Estimated numbers get a `~` and status `estimated`.
   No number at all gets status `none` and the achievement still goes in;
   a true unquantified bullet beats a fabricated metric.
5. *Who else was on it?* — so the bullet says "led", "built", or
   "contributed to" truthfully.

Push for numbers twice: *"Roughly how many?"*, *"What was it before?"* Then
stop. Never suggest a number. Never round an estimate into a fact.

Aim for three to six achievements per role; more for the current role. Ask
also about: production incidents handled, things designed from scratch,
migrations, mentoring and hiring, cross-team work, cost reductions, anything
a manager praised. Stop when the user says the role is covered.

Also collect once: education, certifications with dates, languages with
level, publications or talks, open-source, and the contact block.

### Format — `career/experience.md`

```markdown
---
updated: 2026-09-11
roles: 2
---

# Experience inventory

The only source a CV claim may come from. Achievements are never deleted;
mark `retired: yes` in the row instead. Number status: `confirmed` |
`estimated` (write the number with `~`) | `none`.

## Acme Payments — Senior Backend Engineer

- **Dates:** Mar 2022 – Present
- **Location:** Kyiv, Ukraine (remote)
- **Domain:** fintech, card payments
- **Team:** 6 engineers, reported to Head of Engineering
- **Stack:** C#, .NET 8, ASP.NET Core, EF Core, PostgreSQL, RabbitMQ, Redis, Azure, Docker, Kubernetes, GitHub Actions
- **Scope:** Owned the payment-orchestration service (12 k tx/day) and its
  integrations with three acquirers. Led two engineers on the ledger rewrite.

### Achievements

| ID | Before / problem | Action (what, with which tech) | Result | Number status | Keywords | Used in |
|---|---|---|---|---|---|---|
| ACME-1 | p95 checkout latency 420 ms, timeouts at peak | Added Redis read-through cache for merchant config, moved acquirer calls to async pipeline with Polly retries | p95 420 → 90 ms; timeout rate 2.1% → 0.1% | confirmed | ASP.NET Core, Redis, Polly, async, performance | master, linkedin |
| ACME-2 | Ledger in monolith, releases blocked by shared DB | Extracted ledger into its own service with outbox pattern over RabbitMQ; zero-downtime cutover | ~40% fewer deploy conflicts; 0 data-loss incidents in 12 months | estimated | microservices, outbox, RabbitMQ, EF Core, migration | master |

## Education

| Degree | Institution | Dates | Notes |
|---|---|---|---|

## Certifications

| Name | Issuer | Date | ID / URL (verified) |
|---|---|---|---|

## Languages

| Language | Level (CEFR) |
|---|---|

## Other

- Talks, publications, open-source, communities — one line each, dated.
```

IDs are `<COMPANY-PREFIX>-<n>`, never reused. `Used in` lists which views
carry the achievement: `master`, `linkedin`, or the application slug.

## 4. Bullet rules

Used by `master`, `tailor`, and `linkedin`. Each bullet is one achievement
row rendered as one sentence.

- **Shape:** strong verb + what was built or changed + with which technology
  + measurable result. *"Cut p95 checkout latency from 420 ms to 90 ms by
  adding a Redis read-through cache and moving acquirer calls to an async
  Polly pipeline (ASP.NET Core, .NET 8)."*
- **Length:** one to two lines, ≤ 220 characters. No sub-bullets.
- **Verbs:** led, built, designed, migrated, cut, reduced, raised, shipped,
  automated, introduced, owned, scaled, rewrote, debugged, mentored. Never
  "responsible for", "helped", "worked on", "involved in", "participated",
  "duties included". No pronouns. Past tense for past roles, present for the
  current one.
- **Numbers** come from the `Result` cell as written. `~` stays. `none`
  status → the bullet has no number and says the scope instead ("across
  three acquirer integrations").
- **Technology names exactly as job descriptions write them**, and both
  forms once each somewhere on the page: *EF Core (Entity Framework Core)*,
  *CI/CD (continuous integration and delivery)*, *K8s* is never used alone.
  `.NET 8` not `dotnet`; `ASP.NET Core` not `asp.net core`; `C#` never
  "C sharp"; `SQL Server` and `PostgreSQL` spelled out.
- **Per role:** current role five to seven bullets, previous three to five,
  anything older than ten years two or a one-line entry. Newest first.
- **Ordering inside a role:** most relevant to the target title first, then
  by size of result.
- **Honest attribution:** "led" only if the inventory says led. "Built" for
  solo. "Contributed to" otherwise.

## 5. ATS checklist

Applied to every template and every output. The check script tests what it
can; the rest is judged by reading.

**Parse gate — hard rules**

- Single column. No tables for layout, no text boxes, no sidebars.
- No images, icons, photos, logos, charts, skill bars, rating dots.
- Contact block in the body, never in a header or footer. Name on the first
  line, then one line: email · phone · city, country · LinkedIn URL ·
  GitHub URL. Plain text URLs.
- Standard section headings, spelled exactly: `Summary`, `Skills`,
  `Experience`, `Education`, `Certifications`, `Projects`. Not "Where I've
  been", "Toolbox", "My journey".
- Each experience entry: title, company, location, dates on the first one or
  two lines, then bullets. Dates as `Mon YYYY – Mon YYYY` or `Mon YYYY –
  Present`, one format throughout.
- Fonts: Calibri, Arial, Helvetica, Georgia, Cambria, Garamond, Aptos, or
  Segoe UI, 10.5–12 pt body. No icon fonts, no ligature-heavy display fonts.
- File: `.docx` unless the posting asks for PDF; if PDF, exported from Word
  with text (never "print to image"). Filename `Firstname-Lastname-CV.docx`.
- Length: one page under about five years of experience, two pages
  otherwise. Never three.
- No hidden text, no white text, no 1-pt keyword blocks. Parsers extract
  them, recruiters see them, and the application is binned.
- Standard bullet character `•`, real paragraphs, no manual line breaks
  inside a bullet.

**Search gate**

- The target title appears verbatim in the summary's first line. If the last
  held title differs from the target title, the summary carries the target
  and the experience entry carries the real title — never rewrite a held
  title.
- Every must-have keyword from the target job descriptions appears at least
  once in Skills and at least once in an Experience bullet, in the exact
  form the JD uses.
- Each keyword at most five or six times on the page. Density above that
  reads as stuffing to both software and people.
- Years of experience with the core stack stated once in the summary
  ("8 years with C# / .NET").

**Skim gate**

- Summary: three lines, no more. Title, years, stack, one differentiator
  with a number.
- Skills: grouped lines (`Languages:`, `Backend:`, `Data:`, `Cloud & infra:`,
  `Practices:`), not a wall of commas, not a table. Ordered by relevance to
  the target.
- The first two bullets of the current role are the two strongest numbers
  in the inventory.

## 6. Template (mode `template`)

The user provides a file (`.docx` or `.pdf`) or a description, or asks which
to use.

1. If a file: run `python scripts/cv-check.py <file>` and read the
   **Structure** and **Parse** sections. Then read the file's text output
   yourself for the things the script cannot judge (heading names, order,
   reading flow).
2. Score the template against §5 as a table, one row per rule, `pass` /
   `fail` / `n/a`, with what specifically fails.
3. Verdict: `use`, `use after fixes` (list them), or `reject`. The baseline
   is the `.docx` that `scripts/cv-build.py` produces: single column,
   heading styles, standard fonts. A designer template is accepted only if
   it passes every hard rule; then it is a taste choice and the user makes
   it.
4. If the user asks for template recommendations without a file, say that
   the baseline exists and passes, and that links to external templates go
   through `study`-style verification — do not write URLs from memory.

### Format — `career/cv/templates.md`

```markdown
# CV templates — evaluations

| Date | Template | Source | Format | Hard rules failed | Verdict | Notes |
|---|---|---|---|---|---|---|
| 2026-09-11 | baseline (cv-build.py) | scripts/cv-build.py | .docx | 0 | use | single column, Calibri 11, heading styles |
| 2026-09-11 | "Modern Blue" | user file, career/cv/templates/modern-blue.docx | .docx | 3 — two-column table, icons, contact in header | reject | contact block would not parse |
```

Store evaluated user files under `career/cv/templates/` only if the user
wants them kept; otherwise just the row.

## 7. Keywords (mode `keywords`)

Input: one or more job descriptions, pasted or as files. Each JD is also
saved verbatim into an application file (§9 format) even if the user is not
applying — the bank needs its provenance.

**Extraction, per JD:**

1. Split the JD into *required* and *preferred* parts by its own headings
   ("Requirements", "Must have", "What you'll need" vs "Nice to have",
   "Preferred", "Bonus", "Plus"). No split → everything is required.
2. Pull, in these categories: `title` (the posted title and any alternates),
   `language`, `framework`, `data`, `messaging`, `cloud`, `infra`,
   `practice` (TDD, DDD, CQRS, code review, on-call…), `domain` (fintech,
   healthcare…), `certification`, `soft` (leadership, mentoring —
   low weight). Keep the JD's exact spelling as the keyword; add spelling
   variants you know are used (`EF Core` / `Entity Framework`;
   `Kubernetes` / `K8s`; `CI/CD` / `continuous integration`).
3. Record years asked for per keyword when stated.

**Bank maintenance:** update `Seen in JDs` and `Must-have in` counts. A
keyword that is must-have in three or more JDs and true for the user goes
into the master CV's Skills line and an Experience bullet, and into
LinkedIn Skills. A keyword the user does not have is kept in the bank with
`In inventory: no` — that is a learning finding, mention it and move on.

### Format — `career/keywords.md`

```markdown
---
updated: 2026-09-11
jds: 4
---

# Keyword bank

Counts are across the JDs in career/applications/. `In inventory` is whether
career/experience.md backs the claim. Never put a `no` on a CV.

| Keyword | Variants | Category | Seen in JDs | Must-have in | In inventory | In master CV | In LinkedIn |
|---|---|---|---|---|---|---|---|
| C# | — | language | 4 | 4 | yes | yes | yes |
| ASP.NET Core | ASP.NET, .NET Core | framework | 4 | 4 | yes | yes | yes |
| Kafka | Apache Kafka | messaging | 2 | 1 | no | — | — |
```

## 8. Master CV (mode `master`)

1. Confirm the target title(s) from `PROFILE.md`. If unset, ask once.
2. Select achievements: every role in the inventory, bullets per §4 counts,
   ordered per §4. Mark each used row's `Used in` with `master`.
3. Write `career/cv/master.md` in the exact format below. Sections in this
   order: contact block (frontmatter), Summary, Skills, Experience,
   Education, Certifications, then Projects or Other only if the inventory
   has them.
4. Build: `python scripts/cv-build.py career/cv/master.md`. It writes
   `career/cv/out/<Firstname-Lastname>-CV.docx` and `.txt` beside it.
5. Check: `python scripts/cv-check.py career/cv/out/<...>.docx` (add `--jd`
   with the most representative application file when one exists). Fix
   every `FAIL` in the markdown, rebuild, re-check. Record the final
   summary line in `career/log.md`.
6. Run the honesty cross-check (§13).

### Format — `career/cv/master.md`

The builder parses exactly this. Frontmatter keys are the contact block;
`name` and `email` are required. `##` is a section, `###` is an entry with
`Title — Company | Location | Dates`, `-` is a bullet, `**Label:**` starts a
skills line, blank lines separate paragraphs.

```markdown
---
name: Ihor Veremchuk
title: Senior .NET Backend Engineer
email: someone@example.com
phone: +380 00 000 0000
location: Kyiv, Ukraine
linkedin: linkedin.com/in/example
github: github.com/example
---

## Summary

Senior .NET Backend Engineer with 8 years building payment and SaaS systems
in C# / .NET 8, ASP.NET Core, and Azure. Cut p95 checkout latency 4.6× on a
12 k tx/day service and led a zero-downtime ledger extraction to
microservices.

## Skills

**Languages:** C#, SQL, TypeScript
**Backend:** .NET 8, ASP.NET Core, EF Core (Entity Framework Core), Dapper, gRPC, REST, SignalR
**Data:** PostgreSQL, SQL Server, Redis, RabbitMQ
**Cloud & infra:** Azure (App Service, AKS, Service Bus), Docker, Kubernetes, Terraform, GitHub Actions, CI/CD
**Practices:** TDD, DDD, CQRS, code review, observability (OpenTelemetry, Grafana), on-call

## Experience

### Senior Backend Engineer — Acme Payments | Kyiv, Ukraine (remote) | Mar 2022 – Present

- Cut p95 checkout latency from 420 ms to 90 ms by adding a Redis read-through cache and moving acquirer calls to an async Polly pipeline (ASP.NET Core, .NET 8).
- Led two engineers extracting the ledger into its own service with the outbox pattern over RabbitMQ; zero-downtime cutover, 0 data-loss incidents in 12 months.

### Backend Engineer — Previous Co | Lviv, Ukraine | Jun 2018 – Feb 2022

- ...

## Education

### BSc Computer Science — Lviv Polytechnic National University | Lviv, Ukraine | 2014 – 2018

## Certifications

- Microsoft Certified: Azure Developer Associate (AZ-204), 2024
```

Tailored CVs use the same format in `career/cv/tailored/`.

## 9. Tailor (mode `tailor`)

Input: a JD and a company name. Output: an application file, a tailored CV,
and a built `.docx`.

1. Save the JD verbatim in the application file. Extract keywords (§7) and
   update the bank.
2. **Fit table:** every must-have keyword → `In inventory` yes/no, and which
   achievement ID backs it. Say the coverage as a fraction. Missing
   must-haves are stated plainly; never papered over.
3. **Tailoring decisions**, each one line: summary first line carries the
   JD's title if the user genuinely fits it; reorder Skills lines and
   entries; swap in inventory achievements whose `Keywords` match the JD;
   spell technologies the JD's way; drop bullets irrelevant to this role to
   keep length. Nothing is added that is not in the inventory.
4. Write `career/cv/tailored/YYYY-MM-DD-<company>-<role>-cv.md`, build,
   check with `--jd <application file>`, fix `FAIL`s, rebuild.
5. Record the check summary in the application file. Mark used achievement
   rows' `Used in` with the application slug.

### Format — `career/applications/YYYY-MM-DD-<company>-<role>.md`

```markdown
---
company: acme
role: Senior .NET Engineer
date: 2026-09-11
source: pasted
status: draft
cv: "[[2026-09-11-acme-senior-dotnet-engineer-cv]]"
---

# Acme — Senior .NET Engineer

## Job description

(verbatim, unedited)

## Keywords

| Keyword | Weight | In inventory | Backed by | In tailored CV |
|---|---|---|---|---|
| ASP.NET Core | must | yes | ACME-1, ACME-2 | yes |
| Kafka | must | no | — | no |

Must-haves covered: 7/8. Missing: Kafka.

## Tailoring decisions

- Summary title set to "Senior .NET Engineer" (posted title; held title is Senior Backend Engineer, kept in the entry).
- ...

## Check

`cv-check` 2026-09-11: parse 0 FAIL / 1 WARN (length 1.9 pages); keywords 7/8 must, 3/5 nice. Heuristic score 84.

## Status

- 2026-09-11 draft

## Cover letter

(written by `company`)

## Interview prep

(written by `company`)
```

`status` moves `draft → applied → screening → interview → offer | rejected
| withdrawn`; the user reports transitions and this skill records them with
a dated line under `## Status` and updates the frontmatter. Slugs of company
and role are kebab-case. The `cv` link is written only after the tailored
file exists.

## 10. LinkedIn (mode `linkedin`)

Recruiter search on LinkedIn matches on headline, current and past titles,
the About text, Skills, and location, and filters by years and Open-to-Work.
So every section is filled, in the same words as the bank, within the
platform limits. The user pastes each section in by hand; this skill writes
the text and the checklist.

Sections, limits, and rules:

| Section | Limit | Rule |
|---|---|---|
| Custom URL | — | `linkedin.com/in/firstname-lastname` or nearest |
| Name | — | as on the CV; no titles or emoji in the name field |
| Headline | 220 chars | `Target title \| core stack \| one differentiator`. Not "Open to opportunities". The title recruiters type, first. |
| Location | — | the target market's city or country; recruiters filter by it |
| Industry | — | Software Development |
| About | 2,600 chars, first ~300 visible | First two lines carry the title, years, stack. Then three to five achievement lines with numbers from the inventory. Then a one-line skills list (plain text, keyword-dense but readable). Then how to reach out. First person is fine here. |
| Experience | 2,000 chars per role | Same title as on paper; company page linked; bullets from the inventory, same text as the CV. Every skill used in a role added under that role's Skills. |
| Skills | 100 max, top 3 pinned | Every `yes`-backed keyword from the bank. Pin the three the target title is searched by. Reorder so the first 10 are the target stack. |
| Featured | — | one or two: a talk, a repo, a post; the CV file is not one |
| Education, Certifications, Languages | — | filled from the inventory, with dates |
| Projects | — | only if the inventory has them |
| Recommendations | — | draft the request message for two named people; the user sends it |
| Open to Work | — | recruiters-only mode, titles = the bank's `title` keywords, locations and remote as in PROFILE |
| Profile photo, banner | — | present, plain; no checklist item beyond "exists" |

### Format — `career/linkedin.md`

```markdown
---
updated: 2026-09-11
---

# LinkedIn

Text to paste, per section, with limits and status. `status`: `draft` |
`live` (the user has pasted it) | `stale` (the inventory changed since).

## Headline — 220 — draft — 118 chars

Senior .NET Backend Engineer | C#, ASP.NET Core, Azure, PostgreSQL | Cut p95 latency 4.6× on a 12k tx/day payments service

## About — 2600 — draft — 1420 chars

...

## Experience — Acme Payments — 2000 — draft — 980 chars

...

## Skills — 100 — draft — 42 listed

Pinned: C#, ASP.NET Core, Azure
1. C#
2. ...

## Checklist

| Item | Status | Note |
|---|---|---|
| Custom URL | done | linkedin.com/in/... |
| Location set to target market | todo | |
| Open to Work (recruiters only) | todo | titles: ... |
```

Character counts are computed, not guessed: count them with Python before
writing the heading.

## 11. Check (mode `check`)

`python scripts/cv-check.py <file> [--jd <application file>] [--out
<report.md>]`. Read the whole report, then in chat give: the `FAIL`s with the
one-line fix each, the must-have coverage, and the three highest-value
`WARN`s. Write the summary line to `career/log.md`. If the file is not the
master or a tailored CV, offer to import its content into the inventory —
achievements in an old CV are inventory rows waiting to be confirmed.

## 12. Improve (mode `improve`)

Read everything under `career/` and list, in priority order, what would
move the needle next. Candidates, judged against the files not recited:

- inventory rows with `none` numbers that could be measured (a dashboard the
  user could still check, a repo with commit counts)
- keywords must-have in ≥ 3 JDs and `In inventory: no` → a learning
  finding; propose the concept for `teach` or `study` and say the CV cannot
  carry it until it is true
- LinkedIn sections `stale` or `draft`
- missing recommendations, empty Featured, no custom URL
- a GitHub profile README that mirrors the summary; pinned repos that show
  the claimed stack
- certifications that appear as keywords in the bank (AZ-204, AZ-400,
  AWS Developer) — present as an option with the time cost, not a push
- title mismatch between what the user holds and what the bank's `title`
  keywords say the market calls the role
- old tailored CVs whose application `status` is stale
- the honesty cross-check (§13) findings not yet acted on

Write the list to `career/PROFILE.md` under `## Improvements` as a table
(`Item | Why | Status | Added`), merging with existing rows, never deleting;
mark done rows `done` with the date.

## 13. Honesty cross-check

After `master`, `tailor`, or `linkedin`: for every technology named in the
output, look for a matching concept or cluster in `topics/*/mastery.md`.
List those that are `L0`–`L1` or absent from every tree. Say it in one
table in chat and append it to `PROFILE.md` § Improvements as one row:
*"CV claims X, Y, Z; untested or ≤ L1 in the concept tree — propose an
`interview` session before applying."* This is a finding, not a block: the
tree measures interview readiness, not work history. Never edit `topics/`
from this skill.

## 14. Write-back — in this order

1. The mode's own files (§3, §6–§10, §12).
2. `career/PROFILE.md` if targets, contact, or improvements changed.
3. `career/log.md`, one row:
   `| 2026-09-11 | cv | master | built and checked; 0 FAIL 2 WARN; must 7/8 | [[master]] |`
   Columns: `Date | Skill | Mode | Summary | File`. The `File` cell is a
   wikilink only when the file exists; `[[master]]` resolves to
   `career/cv/master.md`.
4. Offer the commit: `career: cv — <mode>: <what>`. Do not push unless asked.

### Format — `career/PROFILE.md`

```markdown
---
updated: 2026-09-11
---

# Career profile

## Targets

- **Titles:** Senior .NET Engineer; Senior Backend Engineer (.NET); Staff Engineer (stretch)
- **Markets:** remote EU; Ukraine; relocation: no
- **Seniority:** senior, 8 years
- **Constraints:** remote or hybrid Kyiv; B2B contract or employment; English C1
- **Domains preferred:** fintech, SaaS, infrastructure

## Contact block

- Name: ...
- Email: ...
- Phone: ...
- Location line: Kyiv, Ukraine
- LinkedIn: ...
- GitHub: ...

## Improvements

| Item | Why | Status | Added |
|---|---|---|---|
```

## 15. Report

Two sentences: what was written, and the one thing the check says to fix
next. The files are the recap.

## 16. Never

- Never write a claim, number, date, title, or employer that is not in the
  inventory. Never suggest a number to the user.
- Never rewrite a held job title. Only the summary carries the target title.
- Never add hidden text, tiny text, white text, or a keyword block. If the
  user asks for it, say why it fails and decline that one thing.
- Never use tables, columns, or icons for layout in a generated CV.
- Never write an external URL from memory. Template and tool links go
  through `study`-style verification or are not written.
- Never fetch from this skill; research is `company`.
- Never edit `topics/`, `review/`, or a level.
- Never present the check script's score as an ATS score. It is a heuristic
  and the report says so.
- Never leave a section of a mode's file unwritten because the chat covered
  it. The chat is disposable.
