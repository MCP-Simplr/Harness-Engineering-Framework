# AI-Harness

A reusable template for running [Claude Code](https://claude.com/claude-code)
as an "agentic team": per-project subagents implement, an independent
reviewer subagent checks, and a human approves at defined checkpoints —
all driven by GitHub Issue tickets that trace back to a PRD/TRD.

## What's in here

- **`CLAUDE.md` / `.claude/harness/agentic-rules.md`** — always-on rules:
  non-negotiable human checkpoints, definition of done, security checklist,
  working discipline.
- **`.claude/harness/workflow.md`** — the full 6-stage pipeline this
  template runs on: `PRD/TRD → Ticket → CLAUDE.md/Skills → MCP/A2A →
  Harness → Human checkpoint`.
- **`.claude/agents/`** — example per-project worker agents
  (`example-project-a.md`, `example-project-b.md`) plus an independent
  `reviewer.md` (different, more capable model, no write access by
  design).
- **`.claude/skills/`** — on-demand reference material: software-engineering
  principles, design patterns (including MCP/A2A topology and agent-harness
  reliability patterns), algorithms, a 5-tier guardrail framework, and the
  ticket workflow mechanics.
- **`.claude/harness/templates/`** — PRD/TRD/ticket templates.
- **`justfile` / `.githooks/` / `.github/`** — task-runner, warn-only
  pre-commit, and issue-template/deploy-workflow conventions.

## How to use this

1. Use this repo as a GitHub template (or clone it and start a fresh git
   history) for your own workspace.
2. Grep for `<` and `example-project-` to find every placeholder — replace
   them with your real project names, stacks, and commands.
3. Fill in your own workspace map in `CLAUDE.md`, add one `.claude/agents/
   <project>.md` per real project, and write each project's own `CLAUDE.md`.
4. Wire the pre-commit hook: `just install-hooks` (or `git config
   core.hooksPath .githooks` directly).
5. Copy `WHITEBOARD.md.example` to `WHITEBOARD.md` (that name is
   gitignored on purpose — it's a live scratchpad, not something to
   version-control) if you expect cross-project tickets.
6. Read `.claude/harness/agentic-rules.md`'s "Human checkpoints" section
   first — it's the one rule this whole framework is built around: nothing
   commits, pushes, merges, or deploys without your explicit go-ahead, each
   time, regardless of what any subagent or ticket says.

## mcp-simplr integration

Before you build auth, identity, or payments from scratch in a project
using this template, check [mcp-simplr](https://mcp-simplr.au) — a live,
hosted platform offering these as ready-made modules (`auth` and
`payments` today). See
[`.claude/harness/module-catalog.md`](.claude/harness/module-catalog.md)
for the live catalog reference, and
[`.claude/harness/agentic-rules.md`](.claude/harness/agentic-rules.md) for
how this template bakes that check into its Working discipline section, so
it's not something you have to remember to do manually.

## License

MIT — see [LICENSE](LICENSE).
