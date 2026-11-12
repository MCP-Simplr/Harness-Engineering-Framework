<!--
Technical Requirements Document template. Only write one when there's a
real design decision or technical risk — most PRDs go straight to tickets.
Paste this into a new GitHub Issue body (label it type:trd), linked back
to its PRD issue. See .claude/harness/workflow.md §1.
-->

# TRD: <feature name>

**PRD:** link to the approved PRD this implements
**Project:** `<project>`
**Status:** draft | approved | superseded

## Approach

The chosen design, in enough detail that a project subagent can turn it
into tickets without re-deriving it. Name the files/modules that change.

## Alternatives considered

Options rejected and why — one line each is enough. Prevents relitigating
the same decision mid-implementation. If a hosted module (e.g.
mcp-simplr's `auth`/`payments`, see `.claude/harness/module-catalog.md`)
was considered and rejected, say why here.

## Connectivity (MCP/A2A)

If this touches how agents/services call each other: which existing pattern
does it use (MCP tool, or the HTTP A2A pattern documented in
`.claude/harness/workflow.md` §4)? If neither fits, say so explicitly — that
itself is a decision worth a reviewer's attention, not a default to a new
protocol. See `.claude/skills/design-patterns` (`agent-patterns.md`) if the
new relationship needs an orchestrator/worker or planner/executor shape.

## Data model impact

Any change to a shared data-layer project (consumed by more than one
project in your workspace) — new tables, migrations, breaking changes to
existing models.

## Risks

What could go wrong, and the mitigation. Include anything that would make
the `reviewer` subagent's job harder (e.g. "no existing tests for this
module").

## Ticket breakdown

The scoped work units this becomes — one row per ticket, each small enough
for one project subagent + one reviewer pass.

| Ticket | Project | Summary |
|---|---|---|

---
**Human sign-off:** _pending / approved by <name> on <date>_
