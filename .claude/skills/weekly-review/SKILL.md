---
name: weekly-review
description: Audit the learning system for the past week and write a blunt report — volume, level movement, stagnant concepts, what the user is avoiding, excursion drift, and whether grades are climbing while difficulty is not. Use this whenever the user asks how they are doing, for a review, a retrospective, a weekly, "am I improving", "what am I avoiding", "is the grading too soft", or when they accept the interview skill's offer of a review because more than seven days have passed since the last file in review/weekly/. It never runs inside another skill uninvited. It proposes roadmap edits and never applies them.
---

# weekly-review

Read everything, compute, name things. This skill writes one report and one
log line and changes nothing else. It is instructed to be blunt: the user
built this system to find out what they are avoiding and whether the grading
is drifting, and a review that softens either finding has failed at its only
job.

## 0. Sync

If the repo has a remote, `git pull --ff-only`. If it fails or the tree is
dirty, say so and ask before continuing.

## 1. Period

From the day after the last file in `review/weekly/` to today. If there is
none, from the first row in `review/log.md`. Say the period in the report.
If the period has fewer than two interview sessions, say that first and keep
the rest short — there is not enough data to conclude much, and pretending
otherwise is the same failure as inflating a grade.

## 2. Read

- `ROADMAP.md` — focus topic, focus cluster, excursion counts
- `review/log.md` — every row in the period, and the four weeks before it for
  trends
- `review/queue.md` — what is overdue as of today
- every `topics/*/mastery.md`
- every `topics/*/gaps.md`
- frontmatter of every session file in the period (`avg_target`,
  `avg_awarded`, `self_flagged`, `disputes`, `excursion`, `concepts`) and,
  for the softness check, the previous four weeks' as well
- the previous weekly report's Proposals section, to say which were acted on

## 3. Compute

Every number below goes in the report with the concepts it came from. No
number without names.

**Volume.** Sessions by mode (interview / teach / study / review) and by
topic. Questions asked. Compared to the previous period.

**Level movement.** Raised, demoted, held — per concept, with before → after
and the session link. Net movement per cluster. Concepts at each level per
topic, now vs. period start.

**Stagnant.** Concepts graded in **three or more** interview sessions with
no level change across them. List with the level they are stuck at and the
sessions. These are where the user is plateauing, and usually where the
misses repeat.

**Avoidance.** In the focus topic:
- clusters with no interview question in the period; and how many periods
  running
- L0 rows never touched, by cluster — name the cluster with the most
- gaps `open` for more than seven days with no `teach` or `study`
- gaps `regressed` that have not been re-taught
- queue items overdue by more than their interval (an L2 item due 2026-09-10
  and untouched on 2026-09-17 is overdue by more than its 3-day interval)

**Excursion drift.** Share of interview sessions that were excursions, this
period and cumulative. Which focus-topic clusters were untouched **while**
excursions happened. If excursions outnumber focus sessions in the period,
say so as the first line of this section.

**Softness.** This is the check the whole system exists for. Over the last
eight weeks of interview sessions:
- trend of `avg_awarded` vs trend of `avg_target`. Awarded climbing while
  target is flat or falling is the drift signal. State both slopes plainly.
- self-flagged-weak answers that received **L3 or above** — list each, with
  session and question. Cumulative count since the start, because the
  calibration checkpoint in `ROADMAP.md` reads this number.
- disputes: count and direction. Upward finals piling up is a second drift
  signal.
- share of L3+ grades whose reason line does not name a trade-off. That
  should be zero; if it is not, name them.

**Regressions.** Every gap that moved to `regressed` in the period — concept,
taught date, failed date, the miss both times. These are the
highest-signal events in the system; they go near the top.

**Calibration checkpoint.** Interview sessions so far, out of five. If five or
more, state whether the checkpoint condition has been met and quote the
evidence.

## 4. Write the report

`review/weekly/YYYY-MM-DD.md`:

```markdown
---
date: 2026-09-21
period_start: 2026-09-15
period_end: 2026-09-21
sessions: 4
interviews: 3
excursions: 1
raised: 3
demoted: 1
regressed: 1
self_flagged_l3_plus: 1
---

# Weekly review — 2026-09-21

Period 2026-09-15 → 2026-09-21. 4 sessions: 3 interview (1 excursion), 1 teach.

## The one thing

<The single worst finding, in two sentences. A regression if there is one;
otherwise the strongest avoidance or drift signal.>

## Regressions

...

## Softness

avg_awarded over 8 weeks: 1.9 → 2.4 (+0.5). avg_target: 3.1 → 3.0 (−0.1).
Awarded is climbing faster than target. <name the sessions>

Self-flagged weak, graded L3+: Q3 in [[2026-09-14-gc-generations]] (L3,
"gc-modes"). Cumulative: 1.

Disputes: 1, final higher than original.

L3+ grades without a trade-off in the reason line: 0.

## Level movement

| Concept | Before | After | Session |
|---|---|---|---|

## Stagnant

## Avoidance

## Excursions

## Volume

## Proposals

Not applied. Edit `ROADMAP.md` to accept.

1. Set focus cluster to `async-and-threading` — untouched two periods
   running while `memory-and-gc` got 14 of 20 questions.
2. ...

## Previous proposals

1. <proposal from last week> — acted on / ignored
```

Rules:

- Frontmatter keys are fixed; the progress script reads them.
- Sections appear in this order. An empty section says "none" — it is not
  omitted, because its absence next week would be ambiguous.
- Every finding names concepts, numbers, and session links. "Async is a bit
  neglected" is not a finding. "`async-and-threading`: 0 questions in 14
  days, 9 of 11 rows at L0, oldest open gap 2026-09-08" is.
- No praise. No "good progress". No "keep it up". Movement is reported as
  numbers; the user can decide how to feel about them.
- Proposals are concrete edits to `ROADMAP.md` — a focus change, a cluster to
  add or split, a concept to retire to a cluster — each with the finding
  that motivates it. Never apply them.

## 5. Write-back

1. The report, §4.
2. Append to `review/log.md`:
   `| 2026-09-21 | — | review | weekly | — | — | — | +3 −1 =4 | [[2026-09-21]] |`
3. `pwsh scripts/progress.ps1`.
4. Offer `review: weekly 2026-09-21`.

Nothing else changes. Not the roadmap, not mastery, not gaps.

## 6. Report in chat

Three lines: the one thing, the softness verdict, the first proposal. Then
the file path. Do not repeat the report.

## 7. Never

- Never soften a finding because the week was hard.
- Never apply a proposal.
- Never conclude from fewer than two interview sessions.
- Never leave out a section.
