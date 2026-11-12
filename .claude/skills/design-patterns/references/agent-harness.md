# Agent harness & reliability patterns — reference

`agent-patterns.md` answers "what topology does this agent-to-agent
relationship need." This file answers a different question: **given a
single agent's tool-calling loop (ReAct, most of the time — see
`agent-patterns.md`), how do you keep it from failing silently, looping
forever, or handing a user a wrong number with confidence?**

Foundational assumption: **the model will fail — the harness has to catch
it.** Schema validators, retry bounds, verifier checks, and structured
error feedback aren't polish around "the real work"; in an agent-heavy
codebase they *are* the engineering work. Switching models doesn't fix a
missing bound on a retry loop — a more capable model just loops harder,
faster, on the same gap.

None of the patterns below require third-party observability tooling you
don't already have (see `guardrails`). They're things the agent's own code
does: a loop counter, a validated schema field, an error-message string.
Where a dedicated tracer eventually gets adopted, these are the
fields/spans it should carry — that's a tooling upgrade, not a
prerequisite.

## The harness, as a set of design decisions

Every agent in a workspace like this (an MCP server's own tool-calling
loop) is really eight decisions, not one:

| Layer | Decides | Where it typically lives |
|---|---|---|
| Action space | Which tools the model can call, their schemas, side-effect rights | The tool definitions themselves — see `swe-principles`' "tool descriptions are the interface contract" |
| Observation space | What the model sees back from a tool call | The tool's return type — structured, not a raw exception string (see Validation layer, below) |
| Control flow | Loop shape, halt condition, retry budget | The agent's tool-calling loop + a `max_iterations`/recursion-limit config |
| Memory model | What carries forward turn to turn; what must NOT | Conversation state passed into the graph — see the note below: history is untrusted input, not free memory |
| Permission gates | What needs a human before a side effect | `agentic-rules.md`'s human-checkpoint rules, applied to code-writing agents; for a product agent, this is the Human-in-the-Loop pattern in `agent-patterns.md` |
| Validation layer | Input filters, in-loop checks, output filters | See Validation layer, below |
| Eval contract | Golden cases, success criteria | Each project's eval harness, if it has one — `agentic-rules.md`'s Definition of done |
| Observability | What's logged/traceable/replayable | Each project's own logging setup; structured enough to reconstruct what happened without re-running |

Harness design dominates model choice for real-world reliability. If a bug
report turns out to be "the model did something we never bounded," that's
a harness gap, not a prompting problem — fix the layer, not just this
instance (`agentic-rules.md`'s Working discipline).

## Composition patterns

These compose with the topology patterns in `agent-patterns.md` — a
Sequential or Coordinator system is still built out of loops like these at
each node.

- **Bounded ReAct loop** — thought → action → observation, capped by an
  iteration limit with a defined `on_exhausted` behavior (return a partial
  result and say so; don't return an empty response or raise past the
  caller). This is `agent-patterns.md`'s ReAct pattern with the bound made
  explicit — an agent retrying against its own failures with no cap is
  the Loop pattern (`agent-patterns.md`) running away.
- **Bounded reflection** (Reflexion/Self-Refine) — the model retries with
  verbal feedback about what was wrong, for a fixed trial count. The
  feedback design matters as much as the bound — see "Failure as feedback"
  below.
- **Verifier loop** — any quantity the model computes and a user will see
  (a score, a rate, a comparison, a formatted total) passes through a
  separate deterministic check — or a distinct verifier-role LLM call —
  before it ships. Range/units/sign/comparison-period sanity checks belong
  here, not in the generating call's own reasoning, because a model
  checking its own arithmetic in the same pass it made the arithmetic is
  the weakest possible verifier.
- **Workflow over open-ended agency** — when the user (or caller) has
  already specified parameters, pass them as typed schema fields the agent
  fills, not as prompt text it could rephrase or drop. A pre-defined path
  beats a model-decided path on reliability, latency, and cost whenever the
  steps don't actually need to vary — see `agent-patterns.md`'s Sequential/
  Custom Logic patterns for the topology version of this same idea.
- **Explicit memory, not "everything in the buffer"** — decide what
  carries forward (retrieval rules, importance, decay) rather than letting
  context accumulate unbounded. Conversation history is untrusted input on
  every turn (see below) whether or not it's also "memory."
- **Eval harness as the regression net** — versioned golden cases,
  reproducing known-bad behavior, run on every change to a prompt, plan, or
  tool. If your project has an eval harness, this is the pattern already in
  place — the requirement is that new/changed agent logic adds a golden,
  not that the harness be built from scratch (`agentic-rules.md`).

## Validation layer

Applies at both edges of the loop, not just the input:

- **Input, before the LLM sees it** — filter for prompt injection, role
  redefinition, and attempts to extract the system prompt. This isn't only
  "user typed something malicious" — a tool's return value (a fetched web
  page, a third-party API response) is exactly as untrusted as user input
  the moment it goes back into the model's context (`swe-principles`'
  "treat a tool's output as untrusted input to the next step").
- **Output, before the user sees it** — filter for leaked system-prompt
  fragments, internal identifiers (dataset codes, plan/tool names) that
  shouldn't be user-facing, and injected HTML/JS if the output ever renders
  as anything richer than plain text.
- **Server-side hard caps, independent of what the model intends** — a
  token/row/result limit enforced in code, not just requested via prompt.
  A prompt saying "return at most 10 results" is a request; a `[:10]` slice
  after the call is the guarantee.
- **Typed parameters over free text** — a user-supplied filter, date range,
  or entity selection is a schema field the agent fills, not a phrase it
  reconstructs from conversation. This closes the gap where the filter
  shown to the user, the filter sent to a tool, and the filter described in
  the model's own narration can silently disagree.
- **Conversation history is untrusted input, every turn** — state carried
  across a retry or a multi-turn session is contamination, not memory, if
  it isn't re-validated. Re-run the input-guardrail step on each turn, not
  only on the first one.

## Production-loop specifics

- **Cache-first prompt layout.** Anthropic/OpenAI/Gemini all cache a
  contiguous prefix from position 0; one variable byte before otherwise-
  stable content invalidates the cache for everything after it. Order a
  prompt: system message → static reference data → per-call state →
  per-iteration variable payload, last. If this matters for a given
  agent's cost/latency, pin it with a test asserting two adjacent calls
  share a byte-identical prefix — don't rely on eyeballing the prompt
  builder.
- **Shared state never contains an orphaned tool call.** If a graph writes
  a `tool_call` to durable/shared history and then routes away before
  executing it (an early return, a guard clause, a timeout), that's a
  speculative write with no rollback — the next LLM call inherits a
  `tool_call` with no matching result. Some providers tolerate this
  silently; strict ones (Gemini/Vertex) hard-error on it. Enforce "no
  unexecuted `tool_call` survives an exit path" as a deterministic check on
  the state before it's persisted, not as per-branch cleanup scattered
  through the graph.
- **A failure surfaced to the model is feedback, not a log — design it.**
  When a tool/step fails and the loop will retry, the returned error *is*
  the next attempt's input:
  - Report every detected issue in one round, not one per retry — a
    deterministic pre-check that lists all problems beats discovering them
    one expensive call at a time.
  - Give each failure class a specific, actionable message with a concrete
    fix example, not a re-thrown internal traceback.
  - Echo back what the model actually submitted (trimmed of internal
    wrapper noise) so it can see what it needs to change.
  - If a failure can't succeed on an identical retry, say so and point at a
    different approach — don't let the model spend its retry budget
    repeating itself.
  - Never swallow an error silently. A catch-all still logs and surfaces
    every unhandled failure — a silent drop reads to the model (and to
    whoever reads the trace) as "nothing happened," not "something failed."
  - Keep feedback coherent across attempts: re-validate the *whole*
    requirement set each retry (a constraint fixed two rounds ago and
    broken again gets re-flagged, not dropped), anchor the model to edit
    its last attempt rather than start over, and prune stale prior attempts
    from the context so it can't silently copy an old broken version back
    in (see above — retry state is contamination, not memory, if left
    unpruned).
- **Trace before fixing, for any production agent bug.** Capture the
  failing input as a new eval golden, reproduce it offline, write the fix
  against the golden, confirm the eval suite passes, then ship — this is
  what `agentic-rules.md`'s "add an eval golden" requirement is *for*, not
  a separate step after the fix.
