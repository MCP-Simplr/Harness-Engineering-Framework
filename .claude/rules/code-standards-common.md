---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
---

# Code-level standards — common (reviewer-checked convention, not linter-enforced, unless you wire up the tooling — see `guardrails`)

Until you have a linter/type-checker/coverage tool wired into CI, nothing
below is mechanically blocked — the `reviewer` subagent checks these by
reading the diff, not a linter. Treat a violation as a real finding, not a
style nit; if the same one keeps recurring, that's the signal to actually
add the lint config (`guardrails`' buildable → structural promotion path),
not to keep noting it by hand forever.

- File length: soft target ≤300 lines, hard flag past ≤500.
- Function/method length: soft target ≤20 lines, hard flag past ≤50.
- Function parameters: ≤5 — bundle more into a typed model (backend) or
  a props/options object (frontend) instead of adding another positional
  arg.
- Nesting depth: ≤4 levels — an early return or an extracted function
  beats a fifth level of indentation.
- No magic numbers in business logic — a bare threshold like `0.73`
  becomes a named constant with a comment on where the number came from.
- Duplicated logic (3+ near-identical repetitions) is a refactor signal —
  see `swe-principles`' DRY note ("duplicated knowledge, not duplicated
  text") before abstracting.
- **Imports live at the top of the file**, not inside a function body.
  Exceptions are narrow and each needs a comment saying which one applies:
  breaking a genuine circular import, an optional/conditional dependency
  the project doesn't always have installed, or a deliberately deferred
  heavy import (e.g. a large ML library) gated behind a rarely-used code
  path for startup-time reasons. "It's only used in this one function" is
  not a reason — that's what imports are for.

Python-only mechanical rules (PEP 8 naming, typed-model-over-dict,
`constants.py`) live in `.claude/rules/python-code-standards.md` instead —
read that one too if you're editing a `.py` file.
