# Agentic team workflow

How the requested pipeline —

```
PRD/TRD (intent)
   ↓
Tickets (scoped work units)
   ↓
CLAUDE.md / Skills (persistent + on-demand instructions)
   ↓
MCP/A2A (tool + agent connectivity)
   ↓
Harness (orchestration, verification loop, guardrails, memory)
   ↓
Human checkpoints (approve/merge/deploy)
```

— maps onto concrete artifacts in this repo. This is the design doc; agents
don't need to read all of it (they're pointed at the specific piece they
need — see `.claude/harness/agentic-rules.md` and `.claude/skills/
ticket-workflow`).

## 1. PRD/TRD (intent)

Templates: `.claude/harness/templates/PRD.md`, `TRD.md`. A human authors and
approves one **before** a ticket exists — this is the first human
checkpoint. A PRD says *what* and *why*; a TRD (optional, for anything with
real technical risk/design decisions) says *how*. Small fixes skip this —
go straight to a ticket.

Hold it as a GitHub Issue (labelled `type:prd`/`type:trd`), same as
tickets — one tracker, full history, no separate file to keep in sync.
Write the PRD straight into the issue body using the template's headings,
paste that issue's link/number into the chat session, and say "pick this
up" — the session runs `gh issue view <n>` and follows
`.claude/skills/ticket-workflow` from there. Open the actual scoped ticket
(`type` unset, `project:<name>` set) as a separate issue linked back to it
once the PRD/TRD is approved.

## 2. Tickets (scoped work units)

GitHub Issues on this repo (`<your-org>/<your-repo>`), not per-project
repos — one issue tracker, scoped with labels:

- `project:<project-a>`, `project:<project-b>`, ... one label per project
  in your workspace map
- `status:todo` / `status:in-progress` / `status:review` / `status:done`
- `type:prd` / `type:trd` — on the intent-level issues from §1, not on
  scoped tickets themselves
- A ticket spanning more than one `project:*` label is a **cross-project
  ticket** — see the coordination rule at the end of this section.

`.github/ISSUE_TEMPLATE/ticket.md` mirrors `.claude/harness/templates/
TICKET.md`: scope, linked PRD/TRD section, acceptance criteria. See
`.claude/skills/ticket-workflow` for the mechanics (branch naming, `gh`
commands, state transitions).

### Cross-project tickets — the coordination rule

GitHub Issues shows *that* work is in progress, not *what shared contract*
it touches — not enough on its own for a fix spanning two projects with a
real contract between them (e.g. a frontend ⇄ backend API shape, or
anything touching a shared data-layer project). For those:

1. Open **one ticket** carrying both `project:*` labels, with the contract
   change itself (the API shape, the field, the schema change) as its own
   acceptance criterion — not "update the frontend" and "update the
   backend" as if they were unrelated.
2. Add an entry to **`WHITEBOARD.md`** (repo root, gitignored — see that
   file for the format) before starting: which ticket, which projects,
   what the contract actually is. Check it first for anything already in
   flight that overlaps.
3. Work it **Sequentially**: dispatch to the project that owns the
   contract first (the API/backend for a shape, the shared-data project
   for a schema), get it through `reviewer`, *then* dispatch to the
   consumer with the now-real, reviewed contract — not a guess at what it
   will look like. Update the `WHITEBOARD.md` entry's status as each side
   lands.
4. Remove the `WHITEBOARD.md` entry once the ticket is merged/closed — it
   reflects the current moment only, not history.

## 3. CLAUDE.md / Skills (persistent + on-demand instructions)

- Root `CLAUDE.md` — always loaded, workspace map + non-negotiables
  (imports `agentic-rules.md`).
- Per-project `CLAUDE.md` (one per project directory) — always loaded when
  Claude Code's cwd is inside that directory, on top of the root file.
  Project-specific: stack, run/test/lint commands, env vars, gotchas.
- Skills (`.claude/skills/*`) — large generic knowledge that would bloat
  every session if always-loaded, so it's fetched only when the trigger in
  its `SKILL.md` description matches: `swe-principles`, `design-patterns`,
  `algorithms`, `ticket-workflow`. **This trigger-matching is a `Skill`-tool
  mechanism, and only the orchestrating session has that tool** — none of
  the `.claude/agents/*.md` subagents (project agents or `reviewer`) do.
  A subagent only sees skill content that its own `.md` explicitly tells it
  to `Read` at a literal file path; it can't discover a skill by
  description the way this session can. Built-in skills with no local file
  (`security-review`, `code-review`) aren't reachable by a subagent at all —
  the orchestrating session has to run those itself.

This is the split worth keeping: agentic rules (small, always-on) vs.
generic SW knowledge (large, on-demand).

`.claude/rules/*.md` is a related but separate native mechanism — path-
scoped by a `paths:` frontmatter glob, not description-matched like a
skill. It loads on `Read`/`Write`/`Edit` of a matching file, for the
orchestrating session *and* for subagents (this is tied to the
CLAUDE.md-hierarchy/file-tool-use loading path, not the `Skill` tool), so
it's the right mechanism for mechanical, file-type-specific rules a worker
subagent needs to see even though it has no `Skill` tool. See
`.claude/rules/code-standards-common.md` and `python-code-standards.md`.

## 4. MCP/A2A (tool + agent connectivity)

- **MCP**: root `.mcp.json` registers your own project's MCP servers for
  dev/test sessions (see the placeholder entry in this template) so their
  tools become directly invocable without going through an HTTP layer. A
  real example worth knowing about: **mcp-simplr** (https://mcp-simplr.au)
  exposes an OAuth-protected MCP server at `/mcp` with a `list_services`
  tool — see `.claude/harness/module-catalog.md`. If you become an
  mcp-simplr owner, registering it the same way lets you (or an agent) call
  `list_services` directly instead of reading docs.
- **A2A**: for a single caller/callee agent-to-agent relationship, the
  simplest shape is a plain service-URL env var + HTTP client (Custom
  Logic, in `agent-patterns.md`'s terms) — don't reach for a new protocol
  or a message broker for one pair. See `.claude/skills/design-patterns`'s
  `agent-patterns.md` for that and the richer orchestrator/worker and
  planner/executor shapes if the relationship needs more structure than a
  single HTTP call.

## 5. Harness (orchestration, verification loop, guardrails, memory)

- **Model tiers**: worker subagent (`.claude/agents/<project>.md`) =
  `haiku`; reviewer (`.claude/agents/reviewer.md`) = `opus`; orchestrator
  (the session a human runs) = `sonnet`. The first two are enforced by
  each agent file's `model:` frontmatter. **The third is not mechanically
  enforced** — there is no `.claude/agents/orchestrator.md`; the
  orchestrator is whichever session the human starts, so "orchestrator =
  sonnet" is advisory text for the human picking a model when launching
  Claude Code, not something a config field requires. Adjust any of the
  three to your own cost/capability tradeoff.
- **Orchestration**: `.claude/agents/<project>.md` — one subagent per
  project, model `haiku`. This template ships two illustrative examples
  (`example-project-a.md`, `example-project-b.md`) — add one per real
  project in your own workspace map. Each picks up a `project:<name>`
  ticket, implements it inside its project directory, self-tests, then
  hands off — it does not review its own work or commit it.
- **Verification loop**: `.claude/agents/reviewer.md`, model `opus` —
  deliberately a different, more capable model than the Haiku worker
  agents, for genuine independence rather than the same model re-reading
  its own output. Runs
  the project's tests/lint, checks the diff against `agentic-rules.md`,
  `guardrails.md`, and `swe-principles.md` (read directly by path — it has
  no `Skill` tool) and the ticket's acceptance criteria, using a
  self-contained find-then-verify methodology (it can't reach the built-in
  `code-review` skill from inside a subagent). Reports a verdict; has no
  `Edit`/`Write` tools, so it cannot "fix" what it's reviewing — that
  separation of duties is deliberate. If it requests changes, the project
  agent addresses them and resubmits for another pass. **For a diff
  touching auth/authz, payments, user input, external URLs/file paths, or
  deserialization, the orchestrating session runs the built-in
  `security-review` skill itself before or alongside dispatching to
  `reviewer`** — `reviewer` can't invoke that skill and will flag its
  absence as a blocking finding rather than improvise the pass.
- **Guardrails**: `agentic-rules.md`'s "human checkpoints" and "definition
  of done" sections, enforced by every agent's system prompt, not just
  documented and hoped for. The `guardrails` skill breaks this down into
  the full structural/runtime/approval/prompt/observability tiers and —
  the part that matters — how to work out which of those are actually
  tooling-enforced in your repo versus resting entirely on the human
  checkpoint.
- **Memory**: if your Claude Code setup has a persistent memory system,
  project agents should write a memory when they learn something
  non-obvious that isn't captured by the code or the ticket itself (a
  gotcha, a constraint, a decision rationale) — same bar as any other
  session.

## 6. Human checkpoints (approve/merge/deploy)

Four gates, in order:

1. **PRD/TRD sign-off** — before a ticket is opened.
2. **Ticket kickoff** — human (or an already-approved backlog) confirms a
   project agent should start.
3. **Pre-merge review gate** — the `reviewer` subagent's verdict is
   presented to the human, who explicitly approves the commit/merge. This
   is the one most likely to be skipped by accident; `agentic-rules.md`
   makes it a standing rule, not a per-task reminder.
4. **Deploy** — if merging to `main` *is* your deploy trigger for the
   changed project, gate 3's approval doubles as the deploy approval —
   there's no separate "now deploy" step to remember, which is exactly why
   gate 3 has to be taken seriously. If your setup has a separate deploy
   step, add it as an explicit gate 5 instead of letting it ride silently
   on gate 3.
