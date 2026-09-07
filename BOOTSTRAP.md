# Learning OS — Bootstrap Brief

> Hand this file to Claude Code from the repository root and say:
> *"Read BOOTSTRAP.md and build the system it describes. Build it one section
> at a time and show me each file before moving on."*
>
> Keep this file after the build. It is the design rationale — if the system
> drifts or needs rebuilding, this is the source, not the generated files.
> It is a living document: when a design decision changes, change it here
> first, then in the generated files.

---

## 1. Goal

A personal learning system that survives context window overflow.

I am a backend engineer working in .NET, aiming for senior-level depth.
I want Claude as the tutor, the examiner, and the record-keeper across several
technical topics — not as a chat partner I re-explain myself to every session.

The system must answer, without me having to remember any of it:

- What am I supposed to be learning right now, and why that and not something else?
- What have I actually proven I know, as opposed to read about?
- What did I fail recently, and when is it due for another attempt?
- Am I getting better, or is the grading getting softer?

## 2. Approach

Plain markdown files are the state. Everything else is a viewer or a syncer.

| Layer | Tool | Role |
|---|---|---|
| State | markdown files in this repo | The only source of truth |
| Agent | Claude Code | The only thing that writes state |
| Reading | Obsidian (this folder opened as a vault) | Wikilinks, backlinks, graph view |
| History and sync | git + private GitHub repo | Undo, multi-machine, honest study log |
| Mobile | Claude Code via the Claude mobile app | Run sessions away from the desk |
| Dashboard | `scripts/progress.ps1` | Computes `PROGRESS.md` from the state files. A viewer, not state — and not written by the grader. |

Deliberately excluded: Obsidian Sync (git covers desktop; mobile sessions run
through Claude Code, not the vault), Notion, and any database. Anything that
Claude cannot read and rewrite as a file does not hold state.

The reason this works is the same reason `CLAUDE.md` works in a code project:
the conversation is forgotten, the files are re-read. Rules and goals live in
the files, so they survive.

## 3. Vocabulary

These words are used exactly and are not interchangeable. They go into
`CLAUDE.md` and every skill uses them.

| Term | Means | Lives in |
|---|---|---|
| **Topic** | A field of study. One is the current focus; the rest are available. | `topics/<topic>/`, `TOPIC.md` |
| **Cluster** | A named group of concepts within a topic. | `##` heading in `mastery.md` |
| **Concept** | The graded unit. Carries a level, an evidence link, a note, and a due date. | a row in `mastery.md`, a file in `notes/`, a row in `review/queue.md` |
| **Session** | One graded sitting, dated. | `sessions/YYYY-MM-DD-<slug>.md` |
| **Gap** | A recorded miss, awaiting teaching. | `gaps.md` |
| **Skill** | A Claude Code skill — `interview`, `teach`, `weekly-review`. Never learning content. | `.claude/skills/` |

The test for a concept: if it cannot carry a level and a due date on its own,
it is a cluster. *EF Core* is a cluster; *change tracking* is a concept.
*CI/CD* is a cluster; *pipeline caching* is a concept.

`mastery.md` holds a **concept tree**. "Skill tree", "sub-skill", and "track"
are not used anywhere in this system.

## 4. Topics

One topic is the **focus** at any time. Focus decides what a session proposes
by default — it is not a lock, and it is not a ranking. I change focus by
editing one line in `ROADMAP.md`; no criteria have to be met first.

The list below is what came to mind first. It is not an order, and it is not
closed. Topics, clusters, and concepts get added when I want them, and the
order in which they are interviewed and taught is decided as I go, not here.

| Topic | Notes |
|---|---|
| .NET | **Current focus.** Working stack. I have honest priors here, so it is the right place to find out whether the grading is calibrated. |
| System design | High interview leverage. |
| DevOps | Adjacent to daily work, currently shallow. |
| Web fundamentals | Underpins both frontend and system design. |
| Frontend | Breadth, not depth. Lower bar than the rest. |
| Interview prep | Draws on all of the above. |

### Excursions

A session on a topic other than the focus is an **excursion**. It is graded,
logged, queued, and written back exactly like a focus session — there is no
lightweight mode.

On the first excursion into a topic, its folder is created and only the
concepts actually touched are enumerated, plus their obvious siblings in the
same cluster. A topic earns its concept tree by being used, not by being
planned. Empty scaffolding is how these systems die.

Excursions are not failures. But `weekly-review` names the pattern when
excursions outweigh the focus topic, or when a focus-topic cluster sits
untouched while excursions continue — leaving a topic exactly when it gets
hard is the failure mode this system exists to make visible.

### .NET — starting scope

Runtime and language depth first, not framework surface area. I can already
build things; the gap is knowing what happens underneath when they misbehave.

Starting clusters for the concept tree, in suggested path order — extend
freely. Full enumeration is in `topics/dotnet/mastery.md`.

- **Memory and GC** — generations and their triggers, GC modes, LOH, card
  table, pauses and latency modes, regions, finalization, stack vs heap
  layout, boxing, `Span`/`Memory`/`stackalloc`, pinning.
- **C# language internals** — what the compiler lowers: struct copy
  semantics, `ref`/`in`, closures, `yield`, disposal, exception cost,
  strings, equality contracts, records and patterns, NRT.
- **Async and threading** — the generated state machine, `Task` vs
  `ValueTask`, `SynchronizationContext` and `ConfigureAwait`, thread pool
  internals and starvation, async deadlock modes, cancellation,
  `ExecutionContext`, continuations, `IAsyncEnumerable`, channels.
- **Concurrency** — the .NET memory model and reordering, `volatile` and what
  it does not guarantee, `Interlocked` and CAS, `lock`/`Monitor` internals,
  async-compatible locks, concurrent collections and their costs, lock-free
  patterns.
- **Runtime and type system** — IL and method tables, JIT and tiered
  compilation, generics at runtime, dispatch, assembly loading, variance,
  reflection vs source generators, interop layout, NativeAOT.
- **Performance and diagnostics** — benchmarking discipline, allocation
  reduction, reading a memory profile, GC metrics, `dotnet-counters`/
  `-trace`/`-dump`, logging cost, distributed tracing, symptom to cause.
- **Dependency injection and hosting** — lifetimes, captive dependencies,
  scopes in background services, host lifecycle and shutdown, options,
  disposal order, keyed services, configuration precedence.
- **Data access and EF Core internals** — connection pooling, `DbContext`
  lifetime, change tracking, query translation and client evaluation, loading
  strategies and N+1, projections, `SaveChanges`, concurrency tokens,
  transactions and execution strategies, compiled queries, migrations.
- **HTTP, networking, and resilience** — `HttpClient` lifetime and
  `SocketsHttpHandler`, `IHttpClientFactory`, DNS and connection pooling,
  HTTP/2–3, timeouts and cancellation, retry pipelines.

Order is soft: row order within a cluster is the suggested order, `TOPIC.md`
carries the suggested cluster path with reasons, and the focus cluster in
`ROADMAP.md` is the only steering knob. Nothing is gated.

Not on the starting list, add when wanted: ASP.NET Core pipeline; I/O,
buffers, and serialization; cloud SDKs.

**Definition of done for .NET** — cold and unaided at a whiteboard: draw the
generational GC and say what triggers and pauses each collection kind; draw
the async state machine and trace a continuation through the thread pool;
argue whether a given lock-free pattern is safe under the memory model; reason
from a described production symptom to a runtime cause; trace a LINQ query
from expression tree to SQL and back to tracked entities, and say where each
layer can silently cost a round trip.

"Done" is a description, not a gate. It says what the topic is for; it does
not decide when I may study something else.

## 5. Mastery rubric

Applies to every topic and every concept. The wording of the levels matters
more than anything else in this system, because it is the only thing standing
between me and a file full of flattering numbers.

- **L0 Unaware** — haven't touched it.
- **L1 Recognize** — can define it, recall the name. Cannot use it.
- **L2 Apply with reference** — can use it with docs open.
- **L3 Fluent** — use it unaided, know the common trade-offs.
- **L4 Explain** — whiteboard it cold, know failure modes and internals.
- **L5 Defend** — design with it under constraints and defend the choice
  against a hostile senior interviewer.

A level changes only with **evidence**: a dated session file where I
demonstrated it unprompted, linked from the mastery table.

### Anti-inflation rules

These are the point of the whole system. They go into `CLAUDE.md` verbatim.

- Never round up. Between two levels means the lower one.
- An answer that missed the trade-off is capped at L2 regardless of correctness.
- A term I use but cannot unpack is L1 for that term, no matter how well the
  surrounding answer went.
- Fluency, confidence, and structure earn nothing on their own.
- Demote a level when I fail a later review of it.
- For open-ended design questions: write the checklist of what a strong answer
  must contain **before** I answer, store it in the session file, and grade
  against it item by item. Never fit the rubric to what I happened to say.

## 6. Session protocol

**Before the first question:** `git pull --ff-only` if the repo has a remote,
so a phone session and a desk session do not collide on the queue. Read the
roadmap, the review queue, and the relevant mastery and gaps files. Propose a
specific concept or cluster and **say which rule chose it**, in this order:

1. overdue queue items
2. regressed gaps — taught, then failed a later review
3. untaught gaps — these redirect to `teach`, not `interview`
4. the focus cluster, if one is set in the roadmap
5. the lowest-level concepts in the focus topic
6. the cluster that has gone untouched the longest

Then let me override, including onto another topic.

**During:** one question at a time, wait for the full answer. Each question is
pitched at a stated **target level** — written into the session file before
the question is asked — because "am I improving or is the grading softening"
is only answerable if difficulty was recorded at the time. No hints, no
corrections, no encouragement mid-answer unless I say "hint" or "pass". Probe
every vague answer at least twice with *why* or *what breaks if*. Ten questions
or thirty minutes, whichever comes first; Claude cannot measure wall-clock, so
the question count governs. Question mix: 60% depth on the target concept or
cluster, 25% adjacent or prerequisite, 15% cold recall from the queue — and if
the queue is empty, that share goes to depth. If three consecutive answers
land at L1, stop the session and switch to teaching.

**Self-assessment:** after the last answer and before any grade is revealed,
Claude asks which answers I thought were weak, and records the list next to
the grades. This is the data the calibration checkpoint reads.

**Disputes:** if I disagree with a grade, Claude does not change it on
argument. It asks two or three further questions on the same concept at the
same target level, grades those, and decides the final level itself. The
session file keeps the original grade, the final grade, and the reason.

**After — mandatory, unprompted:** write the dated session file, update the
mastery table with evidence links, append misses to the gaps file, reschedule
everything touched in the review queue, append one line to the log, run the
progress script, and offer a commit. Then report what changed in two
sentences — the session file is the recap, not the chat.

**Spaced repetition intervals:** L1 +1 day, L2 +3 days, L3 +1 week,
L4 +3 weeks, L5 +2 months.

**Rules that follow from the above:**

- A teach session never raises a level. Reading an explanation is not
  evidence. A level rises only in an interview session at least one day
  after the concept was taught.
- A review is failed when I grade below the recorded level. The level drops
  to what I demonstrated, not by one step.
- On first contact: if I cannot define a concept it stays L0; if I can define
  it but not use it, L1.

## 7. Structure to build

```
learning-os/
├── CLAUDE.md              # operating rules: vocabulary, rubric, protocols, conventions
├── ROADMAP.md             # focus topic, topic list, definitions of done
├── PROGRESS.md            # generated by the script — never hand-edited
├── .gitignore
├── .claude/skills/
│   ├── interview/SKILL.md
│   ├── teach/SKILL.md
│   ├── study/SKILL.md
│   └── weekly-review/SKILL.md
├── scripts/
│   └── progress.ps1       # reads mastery, queue, log, session frontmatter → PROGRESS.md
├── topics/dotnet/
│   ├── TOPIC.md           # scope, definition of done, trusted sources
│   ├── mastery.md         # concept tree, one row per concept, all at L0
│   ├── gaps.md            # misses, newest first, never deleted
│   ├── notes/             # one concept per file
│   └── sessions/          # YYYY-MM-DD-slug.md, transcript + scores
└── review/
    ├── queue.md           # concept | topic | last | next
    ├── log.md             # append-only, one line per session
    └── weekly/            # YYYY-MM-DD.md, one per weekly review
```

Build only the `dotnet` topic now. Other topics get folders on first
excursion or when they become the focus — never before.

### The four skills

- **`interview`** — runs a graded session end to end and does the write-back.
  Grading lives inside this skill, not in a separate one, so there is no way to
  run a session and skip the scoring.
- **`teach`** — explains a concept from the gaps file (mechanism first, then
  failure modes, then trade-offs), writes the note, then immediately drills
  three questions on it and queues it at +1 day.
- **`study`** — for when I want to read or watch on my own instead of being
  taught. Finds three to five resources for a concept or cluster, **verifies
  every link by fetching it** before writing it down, records them in the
  concept note, marks the gap `studying`, and queues the concept for an
  interview at +3 days. Self-study that never gets tested is invisible to the
  system, so this skill's job is to make sure it gets tested.
- **`weekly-review`** — audits the system: volume, level movement, concepts
  stagnant across three or more sessions, topics, clusters and gaps I am
  avoiding, excursion drift, and whether average scores are climbing while
  difficulty is not. Blunt by instruction. Writes its report to
  `review/weekly/`. It may propose roadmap edits but not make them.

Skill files use YAML frontmatter with `name` and `description`. The
description is the trigger, so it must state plainly when to use the skill and
be slightly insistent about it.

Each skill **owns the format of the files it writes** and states it in full:
`interview` owns the session file, the mastery table, the queue, the log line,
and the gap entry; `teach` owns the note and gap status transitions; `study`
owns the `## Resources` section of a note; `weekly-review` owns its report.
Session files and notes carry YAML frontmatter (`topic`, `cluster`, `date`,
`mode`, and so on) so the progress script can parse them and Obsidian's Bases
can query them. Formats are exact because the script depends on them; that is
a feature.

Gap status lifecycle: `open` → `studying` or `taught` → `verified` when a
later interview grades the concept at L2 or above, or `regressed` when it
grades below the recorded level. Never deleted.

### File conventions

- Notes: one concept per file, kebab-case, named for the concept. Concept
  names are unique across the whole vault — Obsidian resolves wikilinks by
  file name, so two topics cannot both have `caching.md`. Prefix when
  ambiguous: `http-caching`, `pipeline-caching`.
- All internal links are Obsidian wikilinks — `[[gc-generations]]` for
  concepts, `[[2026-09-14-gc-generations]]` for sessions. Never relative
  markdown paths; that breaks the graph view and the backlinks.
- Every session file links to each concept it tested. A concept with many
  backlinks from low-scoring sessions is the real gap list, visible without
  asking anyone.
- Mastery tables for the focus topic start fully enumerated at L0. Listing
  every concept up front is what makes avoidance visible — an L0 row I keep
  not touching is a signal, and the weekly review is instructed to name it.
  Excursion topics enumerate only what is touched, and fill in over time.
- Gaps are marked taught, never deleted. A taught gap that fails a later
  review is marked **regressed** — the highest-signal event in the system.
- `TOPIC.md` is referenced by path, never by wikilink: every topic has one,
  so `[[TOPIC]]` is ambiguous the moment a second topic exists.
- Mastery is the only place a level lives. The queue schedules; it does not
  carry levels. The dashboard is computed from both.
- `.gitignore` covers `.obsidian/workspace.json`,
  `.obsidian/workspace-mobile.json`, `.obsidian/cache`, `.trash/`, OS junk,
  and editor folders. The rest of `.obsidian/` is committed so vault config
  travels between machines.
- Commit message for sessions: `session: <topic> — <slug> (avg L<n>)`.

## 8. Build order

1. `CLAUDE.md` and `.gitignore` first — everything else is written under those
   rules.
2. `ROADMAP.md` with .NET as focus and the other topics listed.
3. The three skills — these fix the file formats everything else must match.
4. The `dotnet` topic files, with the concept tree fully enumerated at L0.
5. `review/queue.md` and `review/log.md`.
6. `scripts/progress.ps1`, run once against the empty state to produce the
   first `PROGRESS.md` and prove the formats parse.

Then stop. Do not run a session as part of the build.

## 9. Calibration checkpoint

After five real interview sessions, I check one thing: did any answer I
privately thought was weak receive L3 or above? If yes, the rubric anchors get
tightened before this system is adapted for anyone else. The scaffolding is
worthless if the grading is generous.
