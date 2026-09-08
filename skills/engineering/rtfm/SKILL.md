---
name: rtfm
description: Read the project's own documentation before planning, answering, or writing code. Use when the user says "rtfm", "RTFM", "read the manual", "read the docs", or "check the docs", and before starting any task in a repo that carries a docs/ directory.
metadata:
  version: "1.0.0"
  source: https://github.com/joshfng/skills
---

# RTFM

Read the project's documentation first. Project docs beat inference from source, and they
beat your priors about how a tool "usually" works: this repo may have decided otherwise,
and the reason is likely written down.

## Steps

1. **Find the docs.** Check in this order, stopping at the first that exists:
   `docs/`, `doc/`, `documentation/`, `.agents/`, `wiki/`. Also read root-level
   `CONTEXT.md`, `ARCHITECTURE.md`, `ADR`/`adr/` directories, and `CONTRIBUTING.md`
   when present.
2. **Triage before reading.** List the tree (`find docs -name '*.md' | sort`) and pick
   by filename against the task at hand. Do not read the whole tree.
3. **Read the ones that pertain, in full.** Partial reads of a design doc produce
   confident wrong answers.
4. **Then plan.** Reconcile what the docs say with what the code does before proposing
   anything.

## Rules

- **Docs are context, not gospel.** When the docs and the code disagree, say so
  explicitly and name both, rather than silently picking one.
- **Prefer project docs over web search** for anything project-specific: conventions,
  deploy steps, environment setup, domain vocabulary.
- **Say what you read.** Name the files you used, so the answer can be checked.
- **Say when there is nothing.** If no docs directory exists, state that in one line and
  proceed from the code. Do not invent a docs tree, and do not offer to write one unless
  asked.
