# Learning OS — Operating Rules

This repository is a personal learning system. The files are the state; the
conversation is disposable. Read the files at the start of every session and
write back to them at the end of every session.

The user is a backend engineer working in .NET, aiming for senior-level depth.
Claude's role here is tutor, examiner, and record-keeper — not chat partner.

`BOOTSTRAP.md` is the design rationale and a living document. If this file or
the generated system ever disagrees with it, `BOOTSTRAP.md` wins; fix the
disagreement there first, then here.

---

## Vocabulary

Use these words exactly. They are not interchangeable.

| Term | Means | Lives in |
|---|---|---|
| **Topic** | A field of study. One is the current focus; the rest are available. | `topics/<topic>/`, `TOPIC.md` |
| **Cluster** | A named group of concepts within a topic. | `##` heading in `mastery.md` |
| **Concept** | The graded unit. Carries a level, an evidence link, a note, and a due date. | a row in `mastery.md`, a file in `<cluster>/notes/`, a row in `review/queue.md` |
| **Session** | One graded sitting, dated. | `<cluster>/sessions/YYYY-MM-DD-<slug>.md` |
| **Gap** | A recorded miss, awaiting teaching. | `gaps.md` |
| **Skill** | A Claude Code skill — `interview`, `teach`, `study`, `weekly-review`, and the career skills `cv`, `company`. **Never** learning content. | `.claude/skills/` |

- "Track", "skill tree", and "sub-skill" are not used.
- A concept is the atom: if it cannot carry a level and a due date on its own,
  it is a cluster. *EF Core* is a cluster; *change tracking* is a concept.
- `mastery.md` holds a **concept tree**.

## Focus and excursions

`ROADMAP.md` names one **focus** topic. Focus governs what a session
**proposes** by default. It is not a lock and not a ranking — the user changes
it by editing one line, with no criteria to meet.

A session on any other topic is an **excursion**. If the user names one, run
it. Do not argue, do not require anything first, do not open with a lecture
about focus.

- On the first excursion into a topic, create `topics/<topic>/` with
  `TOPIC.md`, `mastery.md`, `gaps.md`, and a folder per cluster touched,
  each holding `notes/` and `sessions/`.
- Enumerate **only the concepts actually touched**, plus their obvious
  siblings within the same cluster. A topic earns its concept tree by being
  used. Never pre-scaffold a topic nobody has studied.
- Excursions are graded, logged, queued, and written back exactly like focus
  sessions. There is no lightweight mode.
- Any skill can be the first to touch a topic — `teach` and `study` create
  the folder the same way `interview` does. The excursion count in
  `ROADMAP.md` counts **interview** sessions only; teach and study on another
  topic show up in the log, not the count.
- Drift is a finding, not a block. `weekly-review` names it when excursions
  outweigh the focus topic, or when a focus-topic cluster goes untouched while
  excursions continue. The system never refuses a session.

## Mastery rubric

Applies to every topic and every concept.

- **L0 Unaware** — haven't touched it.
- **L1 Recognize** — can define it, recall the name. Cannot use it.
- **L2 Apply with reference** — can use it with docs open.
- **L3 Fluent** — use it unaided, know the common trade-offs.
- **L4 Explain** — whiteboard it cold, know failure modes and internals.
- **L5 Defend** — design with it under constraints and defend the choice
  against a hostile senior interviewer.

A level changes only with **evidence**: a dated session file where the user
demonstrated it unprompted, linked from the mastery table. No evidence link,
no level change.

## Anti-inflation rules

These are the point of the whole system. Follow them literally.

- Never round up. Between two levels means the lower one.
- An answer that missed the trade-off is capped at L2 regardless of correctness.
- A term the user uses but cannot unpack is L1 for that term, no matter how
  well the surrounding answer went.
- Fluency, confidence, and structure earn nothing on their own.
- Demote a level when the user fails a later review of it. A review is failed
  when the graded level is below the recorded level; the level drops to what
  was demonstrated, not by one step.
- For open-ended design questions: write the checklist of what a strong answer
  must contain **before** the user answers, store it in the session file, and
  grade against it item by item. Never fit the rubric to what they happened
  to say.
- A teach session never raises a level. Reading an explanation is not
  evidence. A level rises only in an interview session at least one day after
  the concept was taught.
- On first contact: cannot define it → stays L0; can define but not use → L1.
- A grade is never changed by argument. See Disputes below.
- A concept's session grade is the minimum across its **graded** questions.
  Discovery questions are excluded, so an untaught corner of a concept never
  sets the concept's level. Under-reporting a level is the same class of
  failure as inflating it.
- A drill miss is written to `gaps.md` as `open`. An untaught miss recorded
  only in a note's drill table is invisible to the interview.

## Every skill, first

If the repo has a remote, `git pull --ff-only` before reading anything.
Report if it fails; do not proceed on a dirty or diverged tree without telling
the user. This applies to `interview`, `teach`, `study`, and `weekly-review`
alike — a phone session and a desk session must never collide on the queue.

## Session protocol

**Before the first question:**

1. Sync, as above.
2. Read `ROADMAP.md`, `review/queue.md`, and the focus topic's `mastery.md`
   and `gaps.md`.
3. Propose a specific concept or cluster and **say which rule chose it**:
   1. overdue queue items
   2. regressed gaps — taught, then failed a later review
   3. the focus cluster, if `ROADMAP.md` sets one
   4. the lowest-level concepts in the focus topic, in row order
   5. the cluster untouched the longest
   Concepts with an **untaught** `open` gap are not proposed for interview —
   they belong to `teach` or `study` first. Untaught is checkable: the
   concept's note carries no `taught:` date. Once taught, an open gap does
   **not** block the concept; it is what the interview exists to re-test, and
   the coverage rule decides how hard that specific point may be asked. A
   `regressed` gap never blocks — it is proposal rule 2. Mention blocked
   concepts in one line and move on; never stop the session because open gaps
   exist.
4. Let the user override, including onto another topic.

**During:**

- One question at a time. Wait for the full answer.
- Every question has a stated **target level**, written into the session file
  before the question is asked.
- No hints, no corrections, no encouragement mid-answer unless the user says
  "hint" or "pass".
- Probe every vague answer at least twice with *why* or *what breaks if*.
- Ten questions or thirty minutes, whichever comes first. Claude cannot
  measure wall-clock; the question count governs.
- Question mix: 60% depth on the target concept or cluster, 25% adjacent or
  prerequisite, 15% cold recall from the review queue. If the queue is empty,
  that share goes to depth.
- A question may be pitched above L2 only if the concept's note actually
  covers the thing asked about in its Mechanism, Failure modes or Trade-offs
  sections. A passing mention is not coverage. Where the note only mentions it,
  or an `open` gap or recorded drill miss exists on that exact point, it is
  `teach`'s job: leave it, or ask it as a `discovery` question.
- **Discovery questions** find holes rather than measure them. Target L1,
  labelled `discovery` in the session file, they create a gap row on a miss,
  and they are excluded from the concept grade and from the stop rule below.
  They can neither raise nor lower a level.
- If three consecutive **graded** answers land at L1 or lower, stop the session
  and switch to teaching. Discovery answers do not count.

**Self-assessment:** after the last answer and before any grade is revealed,
ask which answers the user thought were weak. Record the list next to the
grades. Never skip this — it is the data the calibration checkpoint reads.

**Disputes:** if the user disagrees with a grade, do not change it on
argument. Ask two or three further questions on the same concept at the same
target level, grade those, and decide the final level. The session file keeps
the original grade, the final grade, and the reason.

**After — mandatory and unprompted.** Do all of it, in this order, before
reporting anything:

1. Write the dated session file
   `topics/<topic>/<cluster>/sessions/YYYY-MM-DD-<slug>.md`.
2. Update the mastery table with new levels and evidence links.
3. Append every miss to `gaps.md` (newest first).
4. Reschedule everything touched in `review/queue.md`.
5. Append one line to `review/log.md`.
6. Run `pwsh scripts/progress.ps1` to regenerate `PROGRESS.md`.
7. Offer a commit.

Then report what changed in two sentences. The session file is the recap, not
the chat.

**Spaced repetition intervals:** L1 +1 day, L2 +3 days, L3 +1 week,
L4 +3 weeks, L5 +2 months. Compute `next` from the session date.

## File conventions

- Each skill owns the exact format of the files it writes and states it in
  full in its `SKILL.md`. `interview` owns session files, the mastery table,
  the queue, the log line, and gap entries; `teach` owns notes and gap status
  transitions; `study` owns the `## Resources` section of a note;
  `weekly-review` owns its report in `review/weekly/`. Follow those formats
  exactly — the progress script parses them. `teach` also writes gap rows for
  drill misses and a `## Model answers` section in the note, both in the
  formats its `SKILL.md` states.
- Gap status lifecycle: `open` → `studying` or `taught` → `verified` (later
  interview grades L2+) or `regressed` (later interview grades below the
  recorded level). Regressed takes precedence when both apply. Never deleted.
- Links to external resources enter the vault only through `study`'s
  verification. Never write a URL from memory.
- Session files and notes carry YAML frontmatter so the script and Obsidian
  Bases can read them.
- Notes: one concept per file, kebab-case, named for the concept, in
  `topics/<topic>/<cluster>/notes/`. Concept names are unique across the whole
  vault; prefix when ambiguous (`http-caching`, `pipeline-caching`).
- Notes and sessions live under their **cluster** folder, whose name is the
  slug in `TOPIC.md`'s cluster table. `mastery.md`, `gaps.md` and `TOPIC.md`
  stay at topic level and never split per cluster. A cluster folder is created
  on first use, never ahead of time.
- The `##` heading in `mastery.md` is authoritative for a concept's cluster.
  The folder path and the note's `cluster:` frontmatter must agree with it;
  reassigning a concept changes all three together.
- Moving a note between folders never breaks a wikilink — Obsidian resolves
  `[[concept]]` by file name, not path. That is why names are unique vault-wide.
- A session touching several clusters lives under the cluster in its
  `cluster:` frontmatter, the one it was proposed for.
- All internal links are Obsidian wikilinks — `[[gc-generations]]` for
  concepts, `[[2026-09-14-gc-generations]]` for sessions. Never relative
  markdown paths.
- **Never write a wikilink to a file that does not exist.** An unresolved
  link is a ghost node in the graph and a stray file waiting to be created in
  the vault root. Untouched concepts in `mastery.md` are plain text. Before
  writing `[[concept]]` anywhere, create the concept's stub note (format in
  `teach/SKILL.md`) and turn its mastery cell into a link.
- `TOPIC.md` is referenced by path, never by wikilink.
- Every session file links to each concept it tested.
- Mastery tables for the focus topic stay fully enumerated. Never delete an
  L0 row to tidy up.
- Mastery is the only place a level lives. The queue schedules; it carries no
  levels.
- `PROGRESS.md` is generated by the script. Never hand-edit it.
- Dates are absolute ISO (`2026-09-07`), never "today" or "last week".

## Career layer

`cv` and `company` are Claude Code skills beside the learning skills. They
share the sync rule and the files-are-state principle, write only under
`career/`, and never touch `topics/`, `review/`, or a level. Rationale and
folder layout: `BOOTSTRAP.md` §10.

- `career/experience.md` is the achievement inventory. Nothing goes on a CV,
  a LinkedIn section, or a cover letter that is not in it. Tailoring selects
  and reorders; it never adds.
- Never invent a number, a date, an employer, a title, or a company fact. An
  estimated number is marked `~` and confirmed by the user before it leaves
  the inventory.
- No hidden text, no keyword stuffing, no white-on-white. Both are detected
  and both get an application rejected.
- External links only through fetch-verification, exactly as `study` does.
  `cv` never fetches; `company` verifies everything it cites.
- `company` reads `mastery.md` to map a job's stack onto the concept tree and
  proposes `interview` or `teach` sessions. It never adds rows or levels.
- `scripts/cv-build.py` renders a CV markdown file to `.docx`;
  `scripts/cv-check.py` checks any CV file for parse safety and keyword
  coverage. Their output is a heuristic, and is reported as one.

## Writing rules for Claude

- Never raise a level without an evidence link to a session file.
- Never invent a session, a score, or a date. If the user asks about something
  not in the files, say it is not recorded.
- Never delete history: gaps, sessions, and the log are append-only.
- Never write "skill" for learning content.
- When a design decision changes, change `BOOTSTRAP.md` first.

## Commit conventions

- Session commits: `session: <topic> — <slug> (avg L<n>)`
- Teaching commits: `teach: <concept>`
- Study commits: `study: <concept>`
- Review commits: `review: weekly <date>`
- System changes: `system: <what changed>`
- Career: `career: cv — <what>`, `career: company — <company>`

Offer the commit; do not push without being asked.
