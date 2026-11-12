---
paths:
  - "**/*.py"
---

# Code-level standards — Python-only (reviewer-checked convention, not linter-enforced, unless you wire up the tooling — see `guardrails`)

Cross-cutting rules that also apply to TypeScript (file/function length,
magic numbers, imports-at-top, etc.) live in `.claude/rules/
code-standards-common.md` instead — read both when editing a `.py` file.
Same caveat as that file: nothing below is mechanically blocked yet; the
`reviewer` subagent checks these by reading the diff. Treat a violation as
a real finding, not a style nit; if the same one keeps recurring, add the
lint config instead of keeping hand-checking it forever.

- Naming follows **PEP 8**: `snake_case` for functions, methods, and
  variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for module-level
  constants; full words over cryptic abbreviations; boolean names prefixed
  `is_`/`has_`/`should_`.
- **Prefer a typed model (e.g. Pydantic) over a bare `dict` or manual
  env-loading, wherever it actually buys type-checking/validation.** A
  dict payload crossing a boundary (API request/response, a tool's
  input/output, config loaded from the environment) should be a typed
  model, not `dict[str, Any]` threaded through the call chain — the model
  documents the shape, validates it at the boundary, and gives every
  caller autocomplete instead of hoping the keys match. Same logic for
  config: a settings library that reads env vars and validates
  types/required-ness at startup is a better fit than a hand-rolled
  `os.getenv(...)` pattern once a project has more than a couple of
  settings — the manual version silently returns `None`/a wrong-typed
  string on a missing or malformed var, the validated version fails at
  startup with a clear message. Don't reach for it where a plain value is
  genuinely simpler (a single local constant, a one-off internal tuple) —
  this is about boundaries and config, not "wrap everything in a model."
- **Hardcoded values live in a project's `constants.py` (or equivalent),
  not scattered inline.** This is stricter than the magic-numbers rule in
  `code-standards-common.md`: even a named local constant
  (`DEFAULT_TIMEOUT_SECONDS = 30` sitting at the top of whichever module
  happens to need it first) should live in that project's constants
  module once it's referenced from more than one module, or once it's the
  kind of value someone would reasonably look for in one place (timeouts,
  retry counts, fee percentages, size limits, external service URLs that
  aren't secrets). A constant genuinely local to one function's internal
  logic and meaningless outside it can stay put — use judgment, but
  default to centralizing rather than leaving the reviewer to find the
  third scattered copy of the same number.
