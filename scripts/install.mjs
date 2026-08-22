#!/usr/bin/env node
// Copy the bundled skill into an agent's skills directory.
//
//   npx @joshfng/opencore-expert            # install globally (~/.claude/skills)
//   npx @joshfng/opencore-expert --project  # install into ./.claude/skills
//   npx @joshfng/opencore-expert --agent cursor --agent codex
//
// This exists so the package is usable straight from npm. `npx skills add
// joshfng/opencore-expert` is the more capable route: it handles symlinks,
// updates, and every agent the skills CLI knows about.

import { cp, mkdir, rm, stat } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const AGENT_DIRS = {
  "claude-code": ".claude/skills",
  codex: ".codex/skills",
  cursor: ".cursor/skills",
  opencode: ".opencode/skills",
  windsurf: ".windsurf/skills",
  copilot: ".github/skills",
};

const SKILL_NAME = "opencore-expert";
const SOURCE = resolve(dirname(fileURLToPath(import.meta.url)), "..", "skills", SKILL_NAME);

function parseArgs(argv) {
  const agents = [];
  let global = true;
  let force = false;

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--project" || arg === "-p") global = false;
    else if (arg === "--global" || arg === "-g") global = true;
    else if (arg === "--force" || arg === "-f") force = true;
    else if (arg === "--agent" || arg === "-a") agents.push(argv[++i]);
    else if (arg === "--help" || arg === "-h") return null;
    else {
      console.error(`unknown argument: ${arg}`);
      process.exit(2);
    }
  }

  if (agents.length === 0) agents.push("claude-code");
  for (const agent of agents) {
    if (!(agent in AGENT_DIRS)) {
      console.error(`unknown agent: ${agent} (known: ${Object.keys(AGENT_DIRS).join(", ")})`);
      process.exit(2);
    }
  }
  return { agents, global, force };
}

function usage() {
  console.log(
    [
      "Usage: npx @joshfng/opencore-expert [options]",
      "",
      "  -g, --global         install to the home directory (default)",
      "  -p, --project        install to the current directory",
      "  -a, --agent <name>   target agent, repeatable",
      `                       (${Object.keys(AGENT_DIRS).join(", ")})`,
      "  -f, --force          overwrite an existing install",
    ].join("\n"),
  );
}

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

const options = parseArgs(process.argv.slice(2));
if (!options) {
  usage();
  process.exit(0);
}

if (!(await exists(join(SOURCE, "SKILL.md")))) {
  console.error(`bundled skill not found at ${SOURCE}`);
  process.exit(1);
}

const root = options.global ? homedir() : process.cwd();
for (const agent of options.agents) {
  const target = join(root, AGENT_DIRS[agent], SKILL_NAME);
  if (await exists(target)) {
    if (!options.force) {
      console.error(`${target} already exists (pass --force to overwrite)`);
      process.exitCode = 1;
      continue;
    }
    await rm(target, { recursive: true, force: true });
  }
  await mkdir(dirname(target), { recursive: true });
  await cp(SOURCE, target, { recursive: true });
  console.log(`installed ${SKILL_NAME} -> ${target}`);
}
