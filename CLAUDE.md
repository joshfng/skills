# joshfng/skills

A shared repo of agent skills. Skills live in bucket folders under `skills/`:

- `hardware/`: bare-metal, firmware, and OS-install skills
- `in-progress/`: beta, public on purpose, feedback wanted, not shipped in the plugin
- `deprecated/`: no longer used

## Conventions

Every skill is a directory containing a `SKILL.md`, optionally with sibling reference
files it loads on demand. The `SKILL.md` frontmatter needs `name` and `description`; the
`description` is what the harness matches on, so it must name the trigger conditions
explicitly.

Every skill in a **promoted** bucket (`hardware/`, and any bucket added alongside it)
must have:

1. An entry in the top-level `README.md`, with the skill name linked to its `SKILL.md`.
2. An entry in its bucket's `README.md`, same link format.
3. An entry in `.claude-plugin/plugin.json`'s `skills` array.

Skills in `in-progress/` and `deprecated/` must appear in **none** of those. The Claude
Code plugin ships exactly the promoted set.

`SKILL.md` files stay small: they are loaded in full whenever the skill activates. Bulk
content belongs in sibling files the skill routes to, read one at a time.

## Manifests

`.claude-plugin/plugin.json` defines the plugin; `.claude-plugin/marketplace.json` makes
this repo its own single-plugin marketplace. Run `claude plugin validate . --strict`
after touching either. `plugin.json`'s version mirrors `package.json`'s: run
`npm run sync-plugin-version` after a version bump, or `npm run check-plugin-version` to
verify.

`package.json` is `private: true`. Nothing here is published to npm; the install routes
are the Claude Code plugin and `npx skills@latest add joshfng/skills`.

## Local development

`scripts/link-skills.sh` symlinks every skill outside `deprecated/` into
`~/.claude/skills` and `~/.agents/skills`. Re-run it after adding, removing, or renaming
a skill. `scripts/list-skills.sh` lists every `SKILL.md` in the repo.

## Vendored content

`skills/hardware/opencore-expert/references/` is a vendored copy of the Dortania guides
(CC BY-NC-SA 4.0), refreshed by `scripts/sync_dortania.py`. Do not hand-edit files under
`references/`: they are overwritten on the next sync. Check drift with
`python3 scripts/sync_dortania.py --check`.

## Markdown

After writing or modifying any `.md` file, run `npx prettier --write <file>` then
`npx markdownlint-cli --fix <file>`, and fix anything left by hand. Fenced code blocks
need a language specifier; use `text` or `console` when none applies.
