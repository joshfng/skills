---
name: opencore-expert
description: Expert guidance for OpenCore Hackintosh installation, ACPI patching, post-install optimization, USB mapping, SMBIOS selection, kext selection, and legacy Mac support via OpenCore Legacy Patcher (OCLP). Use when configuring config.plist, troubleshooting boot panics or OC picker issues, selecting quirks, migrating from Clover, or applying hardware-specific patches based on the Dortania guides. Trigger for any question involving hackintosh, OpenCore, OC config, kexts, SSDTs, or running macOS on unsupported hardware.
license: CC BY-NC-SA 4.0 — bundled Dortania guides, see NOTICE.md
metadata:
  version: "1.0.0"
  source: https://github.com/joshfng/opencore-expert
---

# OpenCore Expert

Procedural guidance for the full OpenCore lifecycle using Dortania guides as the source of truth.

`references/` is a verbatim copy of the upstream Dortania Markdown, one file per guide
page. `references/INDEX.md` lists every page with its title; `references/.sync-manifest.json`
records the upstream commit each page came from. Route with the tables below, fall back to
INDEX.md, then read only the file you need — never load the whole tree.

## Phase Workflow (new builds)

1. **Hardware ID** — Identify CPU generation, GPU, NIC/WiFi chipset → determines config branch
2. **macOS Compatibility** — Check `references/OpenCore-Install-Guide/macos-limits.md` for version support
3. **Base Config** — Use routing table below to pick the correct config.plist file
4. **ACPI Patching** — `references/Getting-Started-With-ACPI/`
5. **Post-Install** — USB mapping + power management: `references/OpenCore-Post-Install/`
6. **Legacy Mac (OCLP)** — For unsupported real Macs: `references/OpenCore-Legacy-Patcher/`

## Config Branch Routing

**Desktop Intel** (`references/OpenCore-Install-Guide/config.plist/`):

| CPU Generation                    | File              |
| --------------------------------- | ----------------- |
| Penryn (Core 2)                   | `penryn.md`       |
| Clarkdale (1st Gen)               | `clarkdale.md`    |
| Sandy Bridge (2nd Gen)            | `sandy-bridge.md` |
| Ivy Bridge (3rd Gen)              | `ivy-bridge.md`   |
| Haswell / Broadwell (4th–5th Gen) | `haswell.md`      |
| Skylake (6th Gen)                 | `skylake.md`      |
| Kaby Lake (7th Gen)               | `kaby-lake.md`    |
| Coffee Lake (8th–9th Gen)         | `coffee-lake.md`  |
| Comet Lake (10th Gen)             | `comet-lake.md`   |

**Laptop Intel** (`references/OpenCore-Install-Guide/config-laptop.plist/`):
Same codename files as desktop, plus: `icelake.md`, `coffee-lake-plus.md`, `arrandale.md`, `broadwell.md`

**HEDT** (`references/OpenCore-Install-Guide/config-HEDT/`):
`haswell-e.md`, `broadwell-e.md`, `skylake-x.md`, `ivy-bridge-e.md`, `nehalem.md`

**AMD** (`references/OpenCore-Install-Guide/AMD/`):

- Ryzen / Threadripper → `zen.md`
- FX series → `fx.md`

> ⚠️ Note: Alder Lake (12th Gen) and newer are not covered by these guides. Direct users to the r/Hackintosh Discord for current guidance.

## Troubleshooting Routing

| Symptom                              | Reference File                                 |
| ------------------------------------ | ---------------------------------------------- |
| OC picker won't appear / EFI issues  | `troubleshooting/extended/opencore-issues.md`  |
| Kernel panics / KP on boot           | `troubleshooting/extended/kernel-issues.md`    |
| Post-boot issues (sleep, audio, GPU) | `troubleshooting/extended/post-issues.md`      |
| Installer / userspace crashes        | `troubleshooting/extended/userspace-issues.md` |
| Misc / catch-all                     | `troubleshooting/troubleshooting.md`           |
| Enabling debug logging               | `troubleshooting/debug.md`                     |

All paths relative to `references/OpenCore-Install-Guide/`.

## Key Reference Files

| Topic                     | File                                           |
| ------------------------- | ---------------------------------------------- |
| SMBIOS model selection    | `extras/smbios.md`, `extras/smbios-support.md` |
| Kext selection            | `ktext.md`                                     |
| macOS version limits      | `macos-limits.md`                              |
| Clover config migration   | `clover-conversion/Clover-config.md`           |
| Clover boot-arg migration | `clover-conversion/Clover-boot-arg.md`         |
| Security settings         | `config.plist/security.md`                     |
| Installation process      | `installation/installation-process.md`         |

## Expert Rules

- **No GUI configurators** — Never recommend OCAT, Clover Configurator, or similar. Direct users to ProperTree for manual plist editing.
- **Quirks validation** — Always validate Quirks and Kernel Patches against the specific CPU generation.
- **ACPI best practices** — Prefer SSDT patches over full DSDT replacement.
- **USB mapping is mandatory** — Required on all builds for stable sleep/wake.
- **SMBIOS matters** — Choosing the wrong SMBIOS model causes iCloud/iMessage failures and power management issues. Always confirm SMBIOS selection.

## Search

Paths are relative to the directory holding this `SKILL.md`. To find specific settings,
quirks, or error messages, grep for the term and read the files it names:

```bash
grep -rin "XhciPortLimit" references/ --include='*.md' -l
```

Drop `-l` to see matching lines. `references/INDEX.md` maps every path to a page title when
grep gives too many hits to triage.

## Freshness

The guides change; the vendored copy does not. Check drift and refresh with:

```bash
python3 scripts/sync_dortania.py --check   # exit 1 if upstream moved
python3 scripts/sync_dortania.py           # re-pull all four repos
```

Those scripts live in the skill's source repo, not in the installed skill. If a user's
problem involves a very recent macOS release, confirm against the live guide at
<https://dortania.github.io> before committing to an answer.
