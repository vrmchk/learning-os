# CV templates — evaluations

Owned by the `cv` skill, mode `template`. One row per template evaluated
against the ATS checklist in `.claude/skills/cv/SKILL.md` §5. The baseline
is what `scripts/cv-build.py` generates; a designer template earns a `use`
only by failing zero hard rules.

| Date | Template | Source | Format | Hard rules failed | Verdict | Notes |
|---|---|---|---|---|---|---|
| 2026-09-11 | baseline (cv-build.py) | scripts/cv-build.py | .docx | 0 | use | single column, Calibri 11, Heading styles, contact in body, no tables/images/header; verified with scripts/cv-check.py on a sample |
