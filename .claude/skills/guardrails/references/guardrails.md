# Guardrail tiers — reference

Five tiers of "how do we know the rules held," from hardest to softest.
Each item should be tagged with where it actually stands in *your* repo —
**on** (real, working today), **buildable** (not built yet, but nothing
blocks it), or **blocked** (needs something else first, named inline).
Don't read a tier name as a promise it's enforced — read the tag. The
table rows below are **illustrative placeholders** — replace them with
your own repo's real status, not this template's example.

A constraint worth naming up front if it applies to you: some repos can't
use GitHub's native branch protection (e.g. `gh api repos/.../branches/
main/protection` returns 403 on a private free-plan repo — "Upgrade to
GitHub Pro or make this repository public"). That's the feature that
normally makes [STRUCTURAL] mean "the merge button is physically
disabled." Without it, nothing server-side can stop a merge — so the tiers
below lean harder on **local pre-commit hooks** (they block a `git commit`
on any plan, no server involved) and on the `reviewer`/human checkpoint
actually refusing rather than a CI red X being enough on its own. See
`.claude/harness/workflow.md` §5 for how the `reviewer` subagent and human
checkpoints fit together.

## 🔒 Structural — blocks the action outright, not a reminder

| Guardrail | Status (example — replace with your own) |
|---|---|
| Formatter runs as a pre-commit hook — can't commit unformatted | **buildable** — e.g. no `.pre-commit-config.yaml` exists yet; a formatter for your language would cover it |
| Type checker blocks on any error (mypy / `tsc --noEmit`) | **blocked** — e.g. no project has a type-checker config yet, even if `tsc`/similar already runs as part of a build step |
| Test coverage threshold enforced | **blocked** — e.g. hard-blocked on "no test suite exists yet" tracked in your own issue tracker; a coverage gate today would fail 100% of changes. A numeric target is worth pre-committing to *once a suite exists*, not before — a percentage with nothing to measure it against is a [PROMPT] rule wearing a [STRUCTURAL] costume |
| Every new/changed function requires an accompanying test | **blocked** — same as above; if your repo has an LLM-eval harness in the meantime, that can be this repo's actual regression net for agent logic, standing in for unit-test coverage until a real suite lands |
| No merge without the full test suite passing | **blocked** — if no branch protection is available *and* no suite exists to run, this is a `reviewer`/human-checkpoint judgment call, not a mechanical block |
| PR requires N reviewers + a minimum review-window + CI-green before merge | **blocked, and partly N/A** if no CI validates PRs — this template's actual review gate is the `reviewer` subagent (a different, more capable model than the worker agent) followed by explicit human approval — one automated pass + one human, not two humans on a timer. Treat that sequence as the real equivalent, not a placeholder for the two-human version |
| Dependency injection required for external services | **on, by convention, not tooling** — once a DI pattern is established (e.g. FastAPI's `Depends()`), nothing stops a PR from bypassing it; this is `reviewer`-enforced, not linter-enforced, unless you add a check for it |

## ⚙️ Runtime — checked automatically, doesn't block, must be looked at

| Guardrail | Status (example) |
|---|---|
| Static analysis for dead code / unused imports on every PR | **buildable** — a linter (e.g. `ruff check`) not yet wired into CI would catch dead code and no-op assignments before a human has to |
| Diff review flags files touched outside the ticket's stated scope | **on, agent-enforced** — `agentic-rules.md`'s "keep diffs scoped to the ticket" + the `reviewer` subagent's checklist; no tooling equivalent exists unless you build one (e.g. a CI job diffing changed-files against the ticket's declared project label) |
| Security linter scans for hardcoded secrets / injection risks | **buildable** — nothing runs as CI by default; the built-in `security-review` skill covers this on demand (`agentic-rules.md`'s Security section requires the orchestrating session to run it on auth/payments/input-handling diffs), but it's invoked per-review, not a standing gate |
| Dependency/CVE scanner blocks known-vulnerable versions | **buildable** — your package manager's lockfile step may already surface yanked packages as a side effect; a real CVE scan (`pip-audit`, `npm audit`, Dependabot) may not be wired up |
| New dependency vetted for supply-chain risk before it's added (typosquatting, unmaintained, suspicious install scripts) | **on, by convention, not tooling** — `agentic-rules.md`'s Security section requires this before installing anything; the `reviewer` treats an unvetted new dependency as a finding. Nothing mechanical blocks a bad package name from being installed — `npm audit signatures` / provenance attestation checks would be the buildable tooling equivalent |
| Mutation testing / property-based spot checks | **blocked** — meaningless before a test suite exists to mutate against |

## 🧑‍⚖️ Approval gates — human or reviewer-agent judgment required

| Guardrail | Status |
|---|---|
| A second agent/human reviews every change before merge; generator can't self-approve | **on** — `.claude/agents/reviewer.md` (different, more capable model than the worker agents), plus the explicit human-approval requirement in `agentic-rules.md` |
| Architectural changes (new service, schema change, new external dependency) need explicit sign-off | **on, via PRD/TRD** — `.claude/harness/workflow.md` §1; a TRD is the mechanism, but nothing stops an agent from skipping straight to a ticket for something that should've had one — this is judgment, not enforced |
| Agent must flag and pause when a task requires deviating from existing patterns, rather than improvising silently | **on, by instruction** — each per-project agent's "reuse existing patterns first" instruction; no mechanical detection of "this diverges from the codebase's own pattern" exists |
| Refactors of shared/core code reviewed separately from the feature that motivated them | **partially on** — a shared-library project's agent definition should call out its high blast radius explicitly; the "cross-project ticket" rule in `workflow.md` covers the multi-project case, but a same-project refactor bundled into a feature PR isn't caught by anything specific |

## 📜 Prompt/Policy — style defaults, not enforced by anything

Already the bulk of what's in `agentic-rules.md`, each project's
`CLAUDE.md`, and the `.claude/skills/*` reference material:

- Naming conventions, preferred patterns (Repository, Strategy via factory,
  DI) — `swe-principles`, `design-patterns`.
- "Reuse before writing new code," diff-scoping, ticket-driven work —
  `agentic-rules.md`.
- Error-handling style, comment density matching the surrounding code —
  `swe-principles`.

These hold only as well as an agent reads and follows them — nothing
mechanical checks compliance. That's fine for style; it's a gap the moment
a [PROMPT] rule turns out to matter enough that its violation should be a
build failure instead (see Observability, below).

## 👁️ Observability — quality trends over time

| Guardrail | Status |
|---|---|
| Track test coverage trend per PR/session | **blocked** — no coverage exists to trend, until you have a suite |
| Track code churn (files repeatedly touched/reverted) | **buildable** — `git log --stat` over time gives this for free; nothing currently aggregates it |
| Track PR rejection rate per agent/ticket type | **blocked** — needs the `reviewer` subagent's verdicts to be recorded somewhere queryable; by default a verdict lives in the session transcript and is gone once the session ends |
| Log which [PROMPT] conventions get violated most often, to promote repeat offenders to [STRUCTURAL] | **buildable, manual for now** — when you notice the same `agentic-rules.md`/`CLAUDE.md` instruction getting missed repeatedly, that's the signal to move it up a tier (write a lint rule, a pre-commit hook, or a CI check) rather than restate it more firmly in prose |

## Pre-merge scan — what the `reviewer` subagent actually checks

This is the operationalized, reviewer-tier checklist behind the tables
above — every item here is 🧑‍⚖️ **Approval-gate**, checked by a person
reading the diff (the `reviewer` subagent or the human), not by a tool,
unless you've promoted a given check to real tooling. Don't present any of
this to a human checkpoint as if a machine already verified it, unless it
actually did.

- [ ] PR/ticket description is non-trivial and states intent, not
  boilerplate.
- [ ] The `reviewer` subagent has run and returned a verdict before this
  reaches the human checkpoint (`agentic-rules.md`).
- [ ] Whatever verification exists for the touched project actually ran,
  and the PR says precisely what ran, not "tests pass."
- [ ] A change to a prompt, plan, or LLM-invocation path includes a new or
  updated eval golden, if that project has an eval harness.
- [ ] No `logger.error`/`logger.warning` on a success path.
- [ ] No bare `except Exception:` without a comment, a log call, and
  explicit handling (re-raise or a documented fallback).
- [ ] No protective check whose return value is computed and then ignored.
- [ ] No `# type: ignore` without a linked issue.
- [ ] Diff is scoped to the ticket — no drive-by refactor of unrelated code.
- [ ] No secrets, API keys, or credentials anywhere in the diff, commit
  message, or ticket text.
- [ ] A changed public function's/endpoint's actual consumers were read,
  not assumed from the signature.
- [ ] New third-party dependency (if any) was vetted per `agentic-rules.md`'s
  Security section, not just recalled as "probably fine."

## Anti-patterns — instant reviewer findings, not style nits

These are process/harness-level anti-patterns (retry loops, orphaned tool
calls, logging-as-fix). For classic code-level smells (God Object,
Copy-Paste Programming, Shotgun Surgery, etc.), see `design-patterns`'
`references/anti-patterns.md` — check a diff against both when it's
plausible either applies.

If the `reviewer` subagent sees one of these, it's a **changes requested**
verdict, not a note for later:

- "Add more logs and re-deploy" offered as the entire fix for a bug.
- `logger.exception(...)` immediately followed by a return value that
  implies success.
- A check function's return value computed but never consumed (`if`,
  `not`, `assert` on it).
- `# type: ignore` with no comment and no linked issue.
- An agent retry loop with no `max_iterations` and no `on_exhausted`
  handler — an unbounded loop is a cost and latency incident waiting to
  happen, not just a code-quality nit.
- A retry loop whose feedback to the model is a raw nested traceback,
  surfaces one error per round-trip when several are detectable at once, or
  silently drops the failed unit instead of reporting it — the error
  message *is* the next attempt's input, not a log line.
- A tool-calling turn abandoned before execution (an early return, a raise,
  a timeout) left as an orphaned entry in shared/durable conversation
  state — a `tool_call` with no matching result. Harmless-looking locally,
  a hard error on strict providers.
- Commented-out code; a `TODO` with no linked issue.
- A comment that restates the code or narrates which file/module something
  moved to, instead of explaining a non-obvious *why*.
- `requests` called from inside an `async def` function (use `httpx`).
- A magic number embedded in business logic instead of a named constant.
- An `except Exception:` block with no log line and no comment.

## What this means day to day

- Don't cite this doc's [STRUCTURAL] rows as if they currently block
  anything in your repo unless you've verified they do. `agentic-rules.md`'s
  "nothing commits/merges without explicit human approval" is the actual
  backstop when little else here is mechanically enforced.
- When you're ready to promote a **buildable** row to real tooling (a
  pre-commit hook, a CI workflow), that's a real scope decision — which
  linter config, how strict, whether it should fail loudly without
  blocking (if branch protection isn't available) or just run client-side
  via pre-commit. Treat it as its own ticket, not a drive-by addition to an
  unrelated change.
