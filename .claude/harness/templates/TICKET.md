<!--
Ticket template — mirrored by .github/ISSUE_TEMPLATE/ticket.md.
One scoped work unit, one project subagent, one reviewer pass.
See .claude/skills/ticket-workflow for the mechanics.
-->

## Summary

One or two sentences: what changes and why.

## Linked PRD/TRD

Link to the section this ticket implements. If there's no PRD/TRD (small
fix), say so explicitly instead of leaving this blank.

## Project

`project:<name>` label — must match one of the directories in the root
`CLAUDE.md` workspace map.

## Acceptance criteria

- [ ] Concrete, checkable outcomes — what the `reviewer` subagent verifies.
- [ ] Include the specific tests/commands that must pass, not just "tests
      pass" (e.g. `npm test -- src/feature`).
- Write these assuming the implementing agent runs on a smaller model
  (this template's worker subagents run on `haiku`) — spell out the
  specific behavior/command/field, don't rely on it inferring intent.

## Out of scope

What this ticket deliberately does not touch, to keep the diff scoped
(`agentic-rules.md`: "don't drive-by refactor unrelated code").

## Labels

`project:<name>` + `status:todo`
