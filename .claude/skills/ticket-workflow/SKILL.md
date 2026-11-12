---
name: ticket-workflow
description: How to pick up, work, and close a GitHub Issue ticket in this repo — branch naming, linking PRD/TRD, status labels, handoff to the reviewer subagent. Use when starting work on a ticket, opening a new ticket, or moving one between status:todo/in-progress/review/done.
---

# Ticket workflow

This repo tracks scoped work units as GitHub Issues on
`<your-org>/<your-repo>` (one repo, one tracker — adapt this if you use
per-project repos instead), labelled `project:<name>` + `status:*`. See
`.claude/harness/workflow.md` §2 for how this fits the overall pipeline,
and `.claude/harness/templates/TICKET.md` for the ticket shape.

## Picking up a ticket

1. `gh issue view <n>` — confirm it has a `project:<name>` label matching
   the directory you're about to work in, a linked PRD/TRD (or an explicit
   "no PRD/TRD — small fix" note), and acceptance criteria you can actually
   check.
2. `gh issue edit <n> --add-label status:in-progress --remove-label status:todo`
3. Branch: `git checkout -b <project>/<issue-number>-<short-slug>` (e.g.
   `<project-a>/42-fix-something`).
4. Work inside that project's directory. Its `CLAUDE.md` (auto-loaded) has
   run/test/lint commands.

## Closing out

1. Run the acceptance criteria's specified tests/lint yourself — don't hand
   off assuming they pass.
2. `gh issue edit <n> --add-label status:review --remove-label status:in-progress`
3. Hand off to the `reviewer` subagent (`.claude/agents/reviewer.md`) rather
   than requesting the human's approval directly — the reviewer's verdict
   is what the human checkpoint responds to (`.claude/harness/agentic-rules.md`).
4. Only after the human explicitly approves: commit, `gh issue edit <n>
   --add-label status:done --remove-label status:review`, and — if
   asked — push/merge. If merging to `main` deploys the changed project
   automatically in your setup, see `.claude/harness/workflow.md` §6.

## Opening a new ticket

Use `.github/ISSUE_TEMPLATE/ticket.md` (`gh issue create` picks it up
automatically). Every ticket needs exactly one `project:<name>` label and
either a linked PRD/TRD section or an explicit "no PRD/TRD" note — don't
open an un-scoped ticket and figure out the project label later.
