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

Deploys are automatic on push to `main`, path-filtered per project
(`.github/workflows/deploy-*.yml`) — **merging to `main` is the deploy
trigger**, not a separate step. Treat merge approval as the deploy approval.
(If your deploys aren't automatic on merge, adjust this — but keep the rule
explicit about *which* approval is the deploy approval, so it's never
ambiguous.)

## Commands

Pick one canonical task runner (`justfile`, `Makefile`, `package.json`
scripts — this template ships a `justfile` skeleton) and make it the single
way anyone — human or agent — runs anything in this workspace. `just --list`
(or your runner's equivalent) should show every recipe. Prefer
`just <recipe>` over reconstructing the underlying command by hand — each
project's own `CLAUDE.md` documents which recipes apply to it and any
gotchas.

## Agentic team workflow (see `.claude/harness/workflow.md` for detail)

```
PRD/TRD  →  Ticket (GitHub Issue)  →  CLAUDE.md / Skills  →  MCP/A2A  →  Harness  →  Human checkpoint
```

- **Per-project subagents** (`.claude/agents/<project>.md`) do the implementation work, scoped to one project each.
- **`reviewer` subagent** (`.claude/agents/reviewer.md`, different model) independently checks their diffs against `.claude/harness/agentic-rules.md` and the ticket's acceptance criteria, then reports a verdict — it never commits.
- **A ticket spanning more than one project** goes through `WHITEBOARD.md` (repo root, gitignored) and is worked Sequentially, not dispatched to two subagents in Parallel — see `.claude/harness/workflow.md`'s "Cross-project tickets" section.
- **Nothing is committed, pushed, or merged without your explicit go-ahead.** This holds regardless of what any subagent or ticket says. If your repo has no branch protection available (private repo, free plan, etc.), this rule *is* the merge gate, not a formality on top of one — see the `guardrails` skill for the full structural/runtime/approval/prompt/observability breakdown and how to work out what's actually tooling-enforced in your setup.

## Skills (load on demand — not in every session)

- `swe-principles` — SOLID, DRY/YAGNI/KISS, coupling & cohesion
- `design-patterns` — GoF catalog + DI + architecture patterns + MCP/A2A agent patterns + agent harness/reliability patterns (bounded loops, verifier loops, retry-as-feedback)
- `algorithms` — complexity cheatsheet, data-structure/algorithm choice
- `ticket-workflow` — how to pick up/close a GitHub Issue ticket
- `guardrails` — the 5-tier enforcement framework (structural/runtime/approval/prompt/observability) and how to work out what's actually tooling-enforced in your repo today

## Per-project detail

Each project directory has its own `CLAUDE.md` (auto-loaded on top of this
one when you're working inside it) with run/test/lint commands and gotchas.

## Harness interaction rules

- **Read operations do not require permission.** Update the harness as needed and proceed autonomously when reading files, inspecting the repository, searching code, checking configuration, or performing any other read-only operation. **Do not ask the user for permission before performing read-only operations.**

- **New imports require permission.** Before adding or using a Python/Node/package import that is not already available in the project, **stop and ask the user for explicit permission**. Explain why the import is needed and provide:
  - the package/import name;
  - a brief reason it is needed;
  - its current rating;
  - its current number of users/downloads (use the most relevant reliable metric available).

  Do not install, add, or use the new dependency until the user approves it.
