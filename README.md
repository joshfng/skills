# joshfng/skills

[Agent Skills](https://agentskills.io) for backend and platform work, in one shared repo.

## Skills

### Engineering

- [rtfm](./skills/engineering/rtfm/SKILL.md) — read the project's own documentation
  before planning, answering, or writing code. Triggers on `/rtfm`, `RTFM`, or any ask to
  check the docs.
- [side-quest](./skills/engineering/side-quest/SKILL.md) — an off-the-record,
  context-aware tangent that leaves nothing in memory, docs, or the main work.
  Triggers on `/side-quest` or any mention of a side quest.

### Hardware

- [opencore-expert](./skills/hardware/opencore-expert/SKILL.md) — OpenCore Hackintosh work:
  `config.plist` branch selection, ACPI/SSDT patching, USB mapping, SMBIOS choice, boot
  troubleshooting, and OpenCore Legacy Patcher (OCLP) on unsupported Macs. Ships a
  vendored, agent-readable copy of the [Dortania guides](https://dortania.github.io) —
  202 pages across four repositories — so the agent routes to an exact file instead of
  guessing or searching the web.

## Install

Two routes. Pick one: installing both leaves every skill duplicated.

### Claude Code: the plugin

```bash
/plugin marketplace add joshfng/skills
/plugin install joshfng-skills@joshfng
```

A managed, read-only bundle covering every promoted skill.

### Codex, and other agents: skills.sh

```bash
npx skills@latest add joshfng/skills
```

Pick the skills you want, and which coding agents to install them on. This copies
editable skill files into the project. For a single skill:

```bash
npx skills@latest add joshfng/skills --skill=opencore-expert
npx skills@latest update opencore-expert
```

## Layout

```text
skills/
├── engineering/    # daily code work (promoted)
├── hardware/       # bare-metal, firmware, and OS-install skills (promoted)
├── in-progress/    # beta: public on purpose, not shipped in the plugin
└── deprecated/     # no longer used
scripts/
├── link-skills.sh          # symlink every skill into the local agent skill dirs
├── list-skills.sh          # list every SKILL.md in the repo
├── sync-plugin-version.mjs # mirror package.json's version into plugin.json
└── sync_dortania.py        # re-pull the Dortania guides for opencore-expert
```

Promoted buckets ship in the Claude Code plugin and are listed in
`.claude-plugin/plugin.json`'s `skills` array. `in-progress/` and `deprecated/` are not.

## Local development

```bash
scripts/link-skills.sh   # symlink all skills into ~/.claude/skills and ~/.agents/skills
```

Each entry is a symlink into this repo, so a `git pull` keeps installed skills current.
Re-run after adding, removing, or renaming a skill.

## License and attribution

The tooling is MIT. Bundled third-party content keeps its own license: the Dortania
guides under `skills/hardware/opencore-expert/references/` are CC BY-NC-SA 4.0,
non-commercial use only, share adaptations alike, attribution required. See
[NOTICE.md](./NOTICE.md) and [LICENSE](./LICENSE).
