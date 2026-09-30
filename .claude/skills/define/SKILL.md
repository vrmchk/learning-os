---
name: define
description: Answer "what is X?" for a general term — kernel, SDK, page, DNS, container — with a short, plain entry in glossary.md: what it is, how to say it out loud, what not to confuse it with. Use this whenever the user asks what a word or acronym means, "what is X", "what does X stand for", "how do I explain X", or says they don't know a term that came up in a note, an interview or a teach session. No session, no drill, no level. If the user wants the concept itself taught in depth, that is `teach`, not this.
---

# define

A lookup, not a lesson. The glossary exists so a term met once can be found
again and said out loud — rationale in `BOOTSTRAP.md` §6, "The glossary".
This skill **never changes a level**, never queues anything, and never drills.

`CLAUDE.md` holds the vocabulary and the rules. This skill owns the format of
`glossary.md`; `teach` and `interview` write entries in this format.

## 0. Sync

If the repo has a remote, `git pull --ff-only`. If it fails or the tree is
dirty, say so and ask before continuing.

## 1. Look it up

Read `glossary.md`. Match on the heading and on any alias in the entry's first
line (an acronym and its expansion are the same term).

- **Entry exists** — show it. If the user's question shows the entry is
  missing something they needed, improve the entry in place.
- **No entry** — write one (§2), then show it.

If the user asked several terms, handle each; one commit covers them all.

## 2. The entry

```markdown
### SDK
*General · first met: [[threads-and-scheduling]]*

**What it is:** Software Development Kit — a package a vendor ships so you can
build against their product: a library to call, plus docs, samples and often
tools.

**Say it like this:** "An SDK is the vendor's ready-made code for talking to
their product. Instead of calling their API or device directly, you reference
their library and call its methods — the Stripe SDK, the AWS SDK, a card
reader's native driver library."

**Not to confuse with:** an API — the API is the contract (what you can call);
the SDK is code that calls it for you.
```

- **Heading** — the term as people say it: `### Kernel object`, `### SDK`,
  `### HTTP 429`. Headings are what `[[glossary#…]]` links resolve to, so never
  rename one that is linked; add an alias to the first line instead.
- **First line, italic** — the field, then `first met:` with a wikilink to the
  note or session where the term came up, if one exists. Fields: `General`,
  `Hardware`, `OS`, `Networking`, `Web`, `Databases`, `DevOps`, `Cloud`,
  `Security`, `Windows`, `.NET`. Add aliases here: `*OS · also: time quantum*`.
- **What it is** — one or two plain sentences. No term that is not itself
  either explained in the sentence or in the glossary already.
- **Say it like this** — what you would say in an interview, in quotes, with
  one concrete example. Three sentences at most.
- **Not to confuse with** — optional; the neighbouring term people mix it up
  with, and the one-line difference.
- **Deeper** — optional; `[[concept]]` for a concept note that treats this term
  in depth. Only a note that exists (`CLAUDE.md`, "Never write a wikilink to a
  file that does not exist").

Length: the whole entry fits on a phone screen. If it cannot, the term is a
concept — see §3.

## 3. Rules

- **Alphabetical.** Insert the entry in heading order, case-insensitive.
  Numbers and symbols sort first.
- **One entry per term.** Check before adding; improve rather than duplicate.
- **Accurate over complete.** A plain sentence that is true beats a thorough
  one that needs three more terms to read.
- **No URLs.** Links enter the vault only through `study`'s verification.
- **Terms inside entries** — if an entry needs another term that has an entry,
  link it: `[[glossary#Kernel]]`. If that term has no entry, either explain it
  in the sentence or add its entry too.
- **Promotion.** If the user wants to go deeper than an entry, or the term
  keeps coming up as the centre of a question, say so in one line and propose
  it as a concept: which topic and cluster it belongs to (a new topic is an
  excursion, `CLAUDE.md`, "Focus and excursions"). The concept is then taught by
  `teach`; once its note exists, add it under *Deeper*. Never add a mastery row
  from here without the user agreeing.

## 4. Write-back

1. `glossary.md` — the new or improved entries, in place.
2. Commit, offered: `define: <term>[, <term>…]`.

Nothing else. No log line, no queue row, no gap, no mastery change: a lookup is
not a session. (A term that *was* a gap is closed by the interview that
re-tests it, not by being defined.)

## 5. Report

The entry itself, in chat, as written. Nothing before it and at most one line
after it — a promotion suggestion, if there is one.

## 6. Never

- Never grade, queue or drill a term.
- Never write a lesson. An entry that needs sections is a concept.
- Never invent a link or a source.
- Never rename a heading that something links to.
