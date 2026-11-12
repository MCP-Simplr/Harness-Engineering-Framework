# Software engineering principles — reference

## SOLID

- **Single Responsibility** — a module/class changes for one reason. A
  clean example: a `repository.py` (data access) vs. an
  `orchestration.py` (LLM/business orchestration) split within the same
  service — follow that kind of split once it exists rather than merging
  concerns back together.
- **Open/Closed** — extend via new implementations of an existing interface,
  not by branching on type inside existing code. If you catch yourself
  writing `if source_type == "internal": ... elif source_type ==
  "external": ...` instead of registering a new case with a factory (e.g. a
  `SourceFactory`), that's a sign a Strategy (see `design-patterns`) or a
  new service module is the better fit than another branch.
- **Liskov Substitution** — a subtype must honor the base type's contract
  (same preconditions or weaker, same postconditions or stronger). Breaking
  this is usually invisible until a caller written against the base type
  breaks — exactly the failure mode a new implementation registered with a
  factory needs to avoid: it must honor the same contract its siblings
  already do, or callers written against the base type break.
- **Interface Segregation** — a caller shouldn't depend on methods it
  doesn't use. A fat "God service" class forces every caller to take on
  every dependency; split by what's actually consumed.
- **Dependency Inversion** — depend on an abstraction the caller defines,
  not a concrete implementation the callee provides. This is *why* dependency
  injection matters (see `design-patterns`) — it's the mechanism, DIP is the
  reason.

## DRY / YAGNI / KISS — in tension, on purpose

- **DRY** (Don't Repeat Yourself) targets duplicated *knowledge*, not
  duplicated *text*. Two functions that happen to look similar today but
  encode different business rules (e.g. two different estimate
  calculations that both "derive a number from comparable data" but by
  different underlying logic) are not a DRY violation — abstracting them
  prematurely couples two things that should be free to diverge.
- **YAGNI** (You Aren't Gonna Need It) — don't build the generic version for
  a second use case that doesn't exist yet. Ship the concrete thing the
  ticket asks for; generalize when the second real caller shows up.
- **KISS** — prefer the boring solution. In an agent-heavy codebase, the
  boring solution is often "a plain function," not "a new orchestration
  graph node" or "a new agent." Reach for agent/graph machinery only when
  the task genuinely needs multi-step tool-calling or branching
  conversation state — not for a deterministic calculation. If a ticket
  needs a pure numeric calc (a rate, a total, a score), write it as plain
  code in its own module rather than routing it through an LLM call.

## Coupling & cohesion

- Prefer high cohesion (a module's contents are all about one thing) and low
  coupling (modules depend on as little of each other's internals as
  possible). A shared data-model package existing as a separate library —
  rather than each service keeping its own copy of the models — is this
  tradeoff already made correctly: one point of coupling (the schema)
  instead of duplicated, drifting definitions.
- Coupling through a well-defined interface (an HTTP API, a typed function
  signature) is fine and often necessary. Coupling through shared mutable
  state, reached-into internals, or copy-pasted logic is the kind to avoid.

## Error handling philosophy

- Fail loudly and close to the source. Swallowing an exception to keep a
  request "succeeding" turns a 500 into corrupted data downstream — worse,
  not better.
- Distinguish errors a caller can act on (validation failure → 4xx with a
  specific message) from ones they can't (upstream service down → 5xx,
  logged with enough context to debug without reproducing).
- At any agent-to-agent HTTP boundary you add, decide explicitly what
  happens when the callee is unreachable or times out — don't let it
  surface as an unhandled exception three layers up.
- Validate at the boundary (API request, external data source), trust your
  own internals afterward. Re-validating everywhere is noise, not safety.
- A bare `except Exception:` is a design decision, not a shortcut — it
  needs a comment saying why nothing narrower fits, a log call, and
  explicit handling (re-raise, or a documented fallback). An empty or
  silent catch is never acceptable — see the `guardrails` skill's
  anti-patterns list for what the reviewer flags on sight.
- A protective check that computes an answer nobody reads is not a
  protective check. If a function returns `is_valid`/`should_block`/similar,
  every call site must consume it (`if`, `not`, `assert`) — a check whose
  return value is silently dropped is worse than no check, because it reads
  as safety that isn't there.
- A defensive fallback must still satisfy its declared return type. Don't
  reach for `# type: ignore` to make a fallback compile — either construct
  a structurally valid value or change the signature, and if `# type:
  ignore` is genuinely unavoidable, link the issue that tracks removing it.
- Errors are diagnostic, not decorative. Include the operation being
  attempted, the sanitised inputs, and which contract/precondition was
  violated — "failed" with no context is a debugging tax on whoever reads
  the log next.

## Code-level standards have moved

The mechanical, file-type-specific rules formerly here (file/function
length, naming, typed-model-over-dict, `constants.py`, imports-at-top,
etc.) now live in `.claude/rules/code-standards-common.md` and
`.claude/rules/python-code-standards.md`, loaded automatically by Claude
Code — for the orchestrating session and for subagents alike — when a
matching file is `Read`/`Write`/`Edit`-ed, which is why they moved out of
this skill: a worker subagent has no `Skill` tool and so could never
trigger this file by description match, but it does have the
`Write`/`Edit` tools that trigger a path-scoped rule. `reviewer.md` reads
both rule files directly by path too, the same way it reads this file,
since explicit-by-path is its only option regardless.
