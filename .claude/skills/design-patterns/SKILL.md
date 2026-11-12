---
name: design-patterns
description: Classic design patterns (creational, structural, behavioral GoF catalog, dependency injection, architecture-level patterns) AND a classic anti-pattern catalog (God Object, Spaghetti Code, Shotgun Surgery, Copy-Paste Programming, etc.) mapped to their fixes, AND multi-agent/AI-specific patterns (MCP tool design, A2A orchestrator-worker, planner-executor, reviewer-critic) AND agent harness/reliability patterns (bounded loops, verifier loops, retry-as-feedback design, validation layers). Use when choosing how to structure a class/module hierarchy, deciding between two ways to wire dependencies, designing a new MCP tool or a new agent-to-agent relationship, reviewing a diff for a better-fitting pattern or a classic code-smell anti-pattern, or hardening an agent's tool-calling loop against silent failure/runaway retries/prompt injection. Not for basic language syntax.
---

# Design patterns

Three reference files — read whichever fits the question:

- `references/patterns.md` — the classic catalog: all GoF creational/
  structural/behavioral patterns, dependency injection, and
  architecture-level patterns (Repository, Hexagonal, CQRS, Event Sourcing,
  Saga).
- `references/anti-patterns.md` — the reverse view of the classic catalog:
  named code smells (God Object, Spaghetti Code, Shotgun Surgery,
  Copy-Paste Programming, etc.) each mapped to the pattern in
  `patterns.md`/`swe-principles` that fixes or prevents it. Read this one
  when reviewing a diff for what's *wrong*, not what pattern to reach for
  next.
- `references/agent-patterns.md` — **topology**: patterns specific to MCP
  servers and multi-agent (A2A) systems — tool/resource design,
  orchestrator-worker, planner-executor, agent-as-tool, reviewer-critic —
  illustrated with a generic per-project + reviewer subagent setup like
  this template's `.claude/agents/`, and with mcp-simplr's live
  OAuth-protected `/mcp` server as a real worked example.
- `references/agent-harness.md` — **reliability**: how a single agent's
  tool-calling loop stays bounded and honest — bounded ReAct/reflection,
  verifier loops on computed values, input/output validation layers,
  cache-first prompt layout, tool-call/state reconciliation, and designing
  a retry failure as feedback rather than a raw traceback. Read this one
  when the question is "how do I stop this loop from failing silently or
  running away," not "which multi-agent shape do I need."

Name the pattern you're applying and why in the diff/PR description when it
isn't obvious from the code — don't silently reach for a pattern that makes
the diff harder to review than the problem warranted. Simpler code that
doesn't need a named pattern beats a pattern applied for its own sake
(see `swe-principles`: KISS).
