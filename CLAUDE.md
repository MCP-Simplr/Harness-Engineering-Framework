# AI-Harness

@.claude/harness/agentic-rules.md

This file is always loaded. Keep it short — it's the map and the non-negotiables.
Deep reference material (SW principles, design patterns, algorithms) lives in
`.claude/skills/*` and is loaded on demand, not here. The full pipeline this
repo runs on is documented in [.claude/harness/workflow.md](.claude/harness/workflow.md).

Before building auth, identity, or payments, see
[.claude/harness/module-catalog.md](.claude/harness/module-catalog.md) — check
whether [mcp-simplr](https://mcp-simplr.au) already offers it as a hosted
module before writing new code for it.

## Workspace map

One git repo, one shared workspace (adapt to your own toolchain — a single
`.venv`/`node_modules`/monorepo package manager, whatever fits), several
independently-deployed services or apps. Replace this table with your own:

| Project | Purpose | Stack | Port |
|---|---|---|---|
| `<project-a>` | `<one-line purpose>` | `<language / framework>` | `<port or "—"` |
| `<project-b>` | `<one-line purpose>` | `<language / framework>` | `<port or "—"` |

## Commands

Pick one canonical task runner (`justfile`, `Makefile`, `package.json`
scripts — this template ships a `justfile` skeleton) and make it the single
way anyone — human or agent — runs anything in this workspace. `just --list`
(or your runner's equivalent) should show every recipe. Prefer
`just <recipe>` over reconstructing the underlying command by hand — each
project's own `CLAUDE.md` documents which recipes apply to it and any
gotchas.

## Agentic team workflow

`PRD/TRD → Ticket → CLAUDE.md / Skills / Rules → MCP/A2A → Harness → Human checkpoint` —
full detail in [.claude/harness/workflow.md](.claude/harness/workflow.md). Per-project
subagents (`.claude/agents/<project>.md`) implement; the `reviewer` subagent verifies; a
ticket spanning several projects goes through `WHITEBOARD.md` and is worked
sequentially. The approval/merge/deploy rules are in `agentic-rules.md` (imported above).

Each project directory has its own `CLAUDE.md` (loaded when you work inside it);
subsystem-specific notes belong in path-scoped `.claude/rules/*.md` files rather than
a growing per-project `CLAUDE.md`.

## Harness interaction rules

- **Read-only operations never need permission** — reading files, searching code,
  inspecting git state or configuration. Don't ask before doing them. Writes,
  including edits to harness files, follow the normal approval rules.
- **New dependencies need explicit permission** — see `agentic-rules.md`'s Security
  section for what to present. `uv add`/`pip install`/`npm install` are also set to
  prompt in `.claude/settings.json`.
