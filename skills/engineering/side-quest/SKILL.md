---
name: side-quest
description: Run an off-the-record, context-aware tangent inside the current session. Nothing from it reaches memory, docs, or the project, and the main work disregards it once it ends. Use whenever the user mentions a "side quest", "sidequest", or "side-quest", invokes /side-quest or /sidequest, or ends one ("end the side quest", "back to the main quest").
metadata:
  version: "1.0.0"
  source: https://github.com/joshfng/skills
---

# Side Quest

An off-the-record tangent with full knowledge of the session so far. The user does
nothing special to start or end it. The quest's text stays in context, so the discipline
is yours: it leaves no trace on disk, and nothing from it carries over into the main work.

## Start

1. Print `⟢ SIDE QUEST: <topic>` on its own line. Ask for the topic if none was given.
2. One line: say "back to the main quest" to end it.
3. Begin. Use everything already in context.

## During

- **No persistent writes.** Write nothing to memory (the auto-memory directory,
  `MEMORY.md`), `CLAUDE.md` or `AGENTS.md`, `docs/`, READMEs, ADRs, or task files.
- **No project writes.** Do not create, edit, or delete files in the project tree. Make
  no commits, branches, stashes, or installs. Read anything.
- **Scratchpad only.** Put throwaway files in the session scratchpad directory, or in a
  `mktemp -d` directory when the host gives no scratchpad.
- **Stay in the quest.** If the user drifts back to the main task, ask whether to end
  the quest first.

## End

1. Offer a takeaway of one to three lines. If the user accepts, state it: it is the only
   part of the quest the main work may use.
2. Print `⟢ SIDE QUEST END`, then pick up the main work where it left off.

## After

Everything between the markers, other than an accepted takeaway, is void:

- Never cite it, act on it, or let it change a later answer.
- Never write it to memory or docs, even when asked to "remember what we discussed"
  later. Say it was a side quest and ask whether to promote that part explicitly.
- Leave it out of any summary, including a compaction summary.
