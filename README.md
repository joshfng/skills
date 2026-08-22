# opencore-expert

An [Agent Skill](https://agentskills.io) for OpenCore Hackintosh work: `config.plist`
branch selection, ACPI/SSDT patching, USB mapping, SMBIOS choice, boot troubleshooting,
and OpenCore Legacy Patcher (OCLP) on unsupported Macs.

The skill ships a vendored, agent-readable copy of the
[Dortania guides](https://dortania.github.io) — 202 pages across four repositories — so
the agent routes to an exact file instead of guessing or searching the web.

## Install

```bash
# Any agent, via the skills CLI (recommended — handles updates and symlinks)
npx skills add joshfng/opencore-expert

# Claude Code plugin marketplace
/plugin marketplace add joshfng/opencore-expert
/plugin install opencore-expert@joshfng-skills

# From npm
npx @joshfng/opencore-expert            # ~/.claude/skills
npx @joshfng/opencore-expert --project  # ./.claude/skills
npx @joshfng/opencore-expert --agent cursor --agent codex

# Manually
git clone https://github.com/joshfng/opencore-expert
cp -r opencore-expert/skills/opencore-expert ~/.claude/skills/
```

## Layout

```text
skills/opencore-expert/
├── SKILL.md                    # routing tables + expert rules (~120 lines)
└── references/
    ├── INDEX.md                # every page, path → title
    ├── .sync-manifest.json     # upstream commit per repo
    ├── OpenCore-Install-Guide/
    ├── OpenCore-Post-Install/
    ├── Getting-Started-With-ACPI/
    └── OpenCore-Legacy-Patcher/
scripts/
├── sync_dortania.py            # re-pull the guides
└── install.mjs                 # npm install path
```

`SKILL.md` stays small on purpose: it is loaded in full whenever the skill activates.
The guides are read one file at a time, only when a question needs them.

## Refreshing the guides

`scripts/sync_dortania.py` pulls each upstream repo's Markdown through the GitHub API,
strips VitePress directives, HTML comments, and image payloads, and rewrites
`references/`, `INDEX.md`, and the sync manifest. Python 3.9+, no dependencies.

```bash
python3 scripts/sync_dortania.py --check              # exit 1 if upstream moved
python3 scripts/sync_dortania.py                      # refresh everything
python3 scripts/sync_dortania.py --repo OpenCore-Install-Guide
python3 scripts/sync_dortania.py --ref v1.2.3         # pin to a tag or SHA
python3 scripts/sync_dortania.py --with-master-guide  # also emit the concatenated dump
```

Review the diff before committing — upstream rewrites can change the routing tables in
`SKILL.md` (for example when a new CPU generation gets its own `config.plist` page).

## Scope

Covers Penryn through Comet Lake, HEDT, AMD Zen/FX, and OCLP. Alder Lake (12th gen) and
newer are **not** covered by the Dortania guides; the skill says so rather than
improvising.

## License and attribution

The bundled guides are Dortania's, under CC BY-NC-SA 4.0 — non-commercial use only, share
adaptations alike, attribution required. The tooling is MIT. See [NOTICE.md](NOTICE.md)
and [LICENSE](LICENSE).
