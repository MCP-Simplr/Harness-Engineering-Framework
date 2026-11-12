# Multi-agent & MCP/A2A design patterns — reference

Patterns for structuring tool-calling agents, MCP servers, and multi-agent
systems — as distinct from the classic OOP patterns in `patterns.md`. The
multi-agent taxonomy below follows Google Cloud's "Choose a design pattern
for your agentic AI system" (docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system);
each entry is mapped to a generic equivalent of what a workspace like this
one typically runs, so you can recognize which pattern a ticket is really
asking for instead of reinventing terminology.

## Choosing a pattern

The source doc groups patterns by what the workflow needs:

- **Deterministic, predictable steps** → Sequential, Parallel, or Iterative
  Refinement.
- **Complex reasoning / dynamic routing** → Single-Agent, Coordinator,
  Hierarchical Task Decomposition, or Swarm.
- **Cycles of refinement** → ReAct, Loop, Review & Critique, or Iterative
  Refinement.
- **Special requirements** → Human-in-the-Loop or Custom Logic.

Default to the simplest pattern that fits — Single-Agent or a plain
function covers most tickets in a typical repo. Reach for a multi-agent
pattern only when the task genuinely has independent sub-tasks, needs a
distinct model for verification, or needs a human checkpoint — not because
multi-agent sounds more sophisticated (see `swe-principles`: KISS).

## The patterns

- **Single-Agent System** — one model, its tools, and a system prompt,
  handling a task end-to-end. Ideal for early-stage work and anything that
  doesn't need independent parallel sub-tasks. This is the default shape
  for a ticket worked directly in a Claude Code session, and for a typical
  MCP server's own tool-calling loop — one agent driving it, no sub-agents.
- **Sequential Pattern** — specialized agents run in a fixed order, each
  one's output feeding the next. Use for structured, repeatable pipelines
  where the steps never change. The `code-review` skill's find → verify
  flow, and this template's own ticket lifecycle (project subagent →
  `reviewer` → human), are sequential by design — don't let steps run out
  of order (e.g. don't let a human approve before the reviewer has run).
- **Parallel Pattern** — independent sub-tasks run at the same time and get
  synthesized afterward. Use when project subagents' work is genuinely
  independent — e.g. dispatching two tickets for two projects that don't
  touch each other's code at the same time. Don't parallelize two agents
  that will both touch a shared data-layer project or the same HTTP
  contract in the same window — see "the whiteboard problem" below.
- **Loop Pattern** — a fixed (non-AI) control loop reruns an agent sequence
  until a termination condition is met. Define the exit condition up front;
  an agent retrying against its own test failures without a bounded retry
  count is exactly how this pattern runs away.
- **Review and Critique Pattern** — a generator produces output, a
  separate critic checks it against explicit criteria and can request
  revisions. This is exactly `.claude/agents/reviewer.md`: it never
  generates or fixes code, only evaluates the project subagent's output
  against the ticket's acceptance criteria and `agentic-rules.md`, using a
  different (more capable) model deliberately, so it isn't the same
  reasoning re-checking itself.
- **Iterative Refinement Pattern** — one or more agents progressively
  improve a stored result across cycles until a quality bar or iteration
  limit is hit. Fits multi-round reviewer feedback: project subagent
  revises, resubmits, reviewer re-checks — cap the rounds; an unbounded
  revise/re-review cycle is a cost and latency risk, and after 2–3 rounds
  it usually means the ticket's acceptance criteria were ambiguous, not
  that the code needs more passes.
- **Coordinator Pattern** — a central agent decomposes a request into
  sub-tasks and dispatches each to a specialized agent, choosing routing
  dynamically. This is the human (or the orchestrating Claude Code
  session) dispatching tickets to the per-project subagents via the
  `Agent` tool — the coordinator role isn't automated by default in this
  template, a human/orchestrating session plays it.
- **Hierarchical Task Decomposition** — a root agent recursively delegates
  through multiple levels for large, ambiguous, open-ended problems. Not
  needed by default here — a flat structure (coordinator → one layer of
  project subagents → reviewer) is deliberately simpler than a multi-level
  hierarchy. Reach for this only if a ticket is genuinely too large/
  ambiguous for one project subagent to own, and split it into smaller
  tickets first if you can instead.
- **Swarm Pattern** — specialized agents communicate all-to-all with no
  central orchestrator, refining a solution collaboratively. High quality,
  highest cost/complexity, and the pattern most exposed to unproductive
  loops. Not used by default here; if a problem seems to need agent
  "debate," check whether it's actually better served by a human making the
  call at a checkpoint instead (see Human-in-the-Loop, below).
- **ReAct (Reason and Act)** — a single agent loops through
  thought → action → observation until it's done, reasoning about tool
  results as it goes. This is the shape of ordinary tool-calling agent
  work (an MCP server's own tool-calling loop, and Claude Code sessions
  generally) — most tickets don't need a named multi-agent pattern beyond
  this.
- **Human-in-the-Loop Pattern** — the workflow pauses at a defined
  checkpoint for a person to review and approve before continuing. This is
  `.claude/harness/agentic-rules.md`'s human-checkpoint rule and the four
  gates in `.claude/harness/workflow.md` §6 (PRD/TRD sign-off, ticket
  kickoff, pre-merge review, deploy) — non-negotiable, not optional
  per-ticket.
- **Custom Logic Pattern** — hand-written branching orchestration when none
  of the above fit. At its simplest this is just a service URL and an HTTP
  client for a single fixed caller/callee, not a workflow that needs a
  named pattern — see Agent-to-agent connectivity, below, for when to reach
  for it.

## MCP server design

- **Tool vs. resource vs. prompt** — an MCP server exposes three different
  primitive kinds; picking the right one matters more than how you
  implement it. A *tool* is an action with side effects or real
  computation — the model decides when to call it. A *resource* is
  read-only context the client can attach without a model decision (a
  document, a schema). A *prompt* is a reusable, parameterized instruction
  template. Don't model a pure data fetch as a tool if a resource fits — it
  removes an unnecessary model decision point.
- **Real worked example — mcp-simplr's `/mcp` server.** mcp-simplr
  (https://mcp-simplr.au, see `.claude/harness/module-catalog.md`) runs an
  OAuth-protected MCP server exposing `list_services`, `get_service_status`,
  `subscribe_service`, and `unsubscribe_service` — four coarse-grained
  tools, one per distinct action, each returning a structured result rather
  than requiring the model to assemble one from several smaller calls.
  Worth reading as a working example of the "coarse-grained tools" and
  "tool descriptions are the interface contract" points below, on a real,
  currently-running server.
- **Coarse-grained tools over chatty ones** — a tool that returns a full,
  structured response (e.g. a message plus a list of scored results plus a
  conversation id) in one call is the right grain: the model doesn't need
  to orchestrate separate fetch/score/format calls itself. Split a tool
  only when callers genuinely need the pieces independently.
- **Metering via middleware, not a tool parameter** — resolve who's
  calling (and charge them, if relevant) from the transport-level Bearer
  token via middleware injecting an identity into request state before the
  tool body runs — the tool itself never sees a billing-related parameter.
  Prefer this over threading a credit/step ID through every metered tool's
  own signature; it keeps the model's view of the tool limited to its
  actual inputs.
- **Tool descriptions are the interface contract** — the model only sees
  the tool's name/description/schema, not its implementation. Write the
  description for the model's decision-making ("when to call this"), and
  the parameter docs for correctness — treat both as seriously as a public
  API docstring.

## Agent-to-agent (A2A) connectivity

If a ticket adds a new agent-to-agent relationship:

- **Direct service call** — one agent as a plain HTTP client of another's
  API, a service-URL env var, no shared broker or registry. Prefer this for
  a new agent-to-agent relationship unless one of the patterns above is
  specifically needed — don't add message-queue or agent-registry
  infrastructure for a single caller/callee pair.
- **Agent-as-tool** — expose an entire agent behind a tool-call interface
  so a caller (human, another agent, or an MCP client) invokes it the same
  way it invokes any other tool, without knowing multiple turns/reasoning
  happen behind that call. This is how an MCP server's own tools typically
  work from the calling model's point of view — the same shape would apply
  to a new HTTP-backed agent relationship.

## Coordination across projects — the whiteboard

None of the patterns above solve visibility on their own: if two project
subagents run in Parallel and both touch a shared data-layer project or
another shared HTTP contract in the same window, nothing stops them from
conflicting. GitHub Issues alone doesn't fix this — `gh issue list --label
status:in-progress` shows *that* something is in progress, not *what
shared surface* it touches.

This template's whiteboard mechanism is **`WHITEBOARD.md`** at the repo
root — a live, gitignored scratch file (not a log) that any agent working
a cross-project or shared-boundary ticket checks before starting and
updates while working. See `.claude/harness/workflow.md`'s "Cross-project
tickets" section for the exact protocol: one ticket with both `project:*`
labels, an entry on the whiteboard, Sequential dispatch (contract owner
first, consumer second with the real reviewed contract in hand), entry
removed on merge. Don't dispatch two project subagents in Parallel for a
ticket that shares a contract — that's precisely the case this file exists
to prevent.

## Guardrails around agent output

- Never let an agent's own "looks good to me" be the last check before an
  irreversible action (commit, merge, deploy, a charge) — route through
  Review and Critique + Human-in-the-Loop (`.claude/harness/agentic-rules.md`).
- Bound what a worker agent can do (tool access, directory scope) rather
  than relying on the prompt alone to keep it in scope — the per-project
  agent definitions in `.claude/agents/` do this by giving each one a
  narrower tool/context footprint than the orchestrating session.
- Treat a tool's output as untrusted input to the next step, especially for
  anything fetched from an external source (web search, a third-party API)
  — the same instinct as validating input at a system boundary in
  `swe-principles`.
