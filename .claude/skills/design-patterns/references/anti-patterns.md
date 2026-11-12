# Classic anti-patterns — reference

The reverse view of `patterns.md`: named code smells, what makes each one
a problem, and which pattern in `patterns.md`/`swe-principles` fixes or
prevents it. Cross-referenced by name only — read the target file for the
actual pattern description, it isn't duplicated here. These are
code-level smells, distinct from `guardrails`' "Anti-patterns" list, which
covers process/harness-level smells (unbounded retry loops, orphaned tool
calls) — check a diff against both when plausible either applies.

- **God Object** — one class/module absorbing responsibilities that belong
  to several different concerns, so almost every change touches it. Fix:
  Single Responsibility (`swe-principles` SOLID); split by what actually
  changes together — a `repository.py` (data access) vs. an
  `orchestration.py` (business/LLM orchestration) split is this fix
  applied.
- **Spaghetti Code** — control flow driven by a growing pile of
  conditionals on type/state instead of a dispatchable shape. Fix:
  Strategy or State (`patterns.md`, behavioral) in place of the branch.
- **Shotgun Surgery** — one logical change requires edits scattered across
  many unrelated files/modules because the same concern was never
  consolidated. Fix: consolidate behind a Facade, or increase cohesion so
  the concern lives in one module (`swe-principles` coupling & cohesion).
- **Golden Hammer** — reaching for a familiar heavy tool (an agent, a
  graph framework, a database) for a problem that doesn't need it. Fix:
  KISS (`swe-principles`) — a deterministic calculation belongs in a plain
  function, not a new agent, is this fix applied.
- **Boat Anchor** — unused code, a dead dependency, or a speculative
  abstraction kept "in case it's needed." Fix: YAGNI (`swe-principles`) —
  remove it; a removal ticket beats a comment explaining why it's still
  there.
- **Copy-Paste Programming** — the same logic duplicated at 3+ call sites
  instead of extracted once. Fix: DRY (`swe-principles`) — but first apply
  its "duplicated knowledge, not duplicated text" test; extract via
  Template Method or a shared Strategy implementation once confirmed.
- **Cargo Cult Programming** — a pattern's boilerplate applied without its
  rationale (a Factory with exactly one product, a Repository that just
  forwards to the ORM with no abstraction gained). Fix: `design-patterns`'
  own rule — name the pattern you're applying and why; if you can't, you
  likely don't need it.
- **Lava Flow** — dead or obsolete code left in place because nobody's
  sure it's safe to remove. Fix: cross-ref `guardrails.md`'s anti-pattern
  "commented-out code; a TODO with no linked issue" — give dead code a
  tracked removal ticket, don't drive-by delete or leave it.
- **Magic Numbers/Strings** — an unexplained literal embedded in logic,
  as a named anti-pattern rather than just a style rule. Cross-ref
  `.claude/rules/code-standards-common.md`'s "no magic numbers" rule and
  `guardrails.md`'s matching anti-pattern entry.
- **Feature Envy** — a method that reaches into another object's data
  more than its own, a sign the logic belongs on that other object. Fix:
  Move Method / Extract Class; or encapsulate behind the owning type's own
  method (Repository pattern in `patterns.md` is this applied to data
  access specifically).
- **Premature Optimization** — adding complexity (caching, a non-trivial
  algorithm, denormalization) before measuring that the simple version is
  actually too slow. Fix: measure first — see the `algorithms` skill for
  when a non-trivial data structure/algorithm is actually warranted; also
  YAGNI (`swe-principles`).
- **Singleton Abuse / Global State** — a singleton (or module-level
  mutable state) used to avoid threading a dependency through a call
  chain, rather than because exactly one instance is a real invariant.
  Fix: Dependency Injection (`patterns.md`).
- **Primitive Obsession** — a bare `str`/`dict`/`int` standing in for a
  concept with its own validation/invariants (an email, a money amount, an
  API payload). Fix: cross-ref `.claude/rules/python-code-standards.md`'s
  "typed model over bare dict" rule; model the concept as its own type
  (a Value Object, in `patterns.md`'s architecture-pattern terms).
- **Anemic Domain Model** — data classes with no behavior, while all the
  logic that operates on them lives elsewhere as free-floating functions.
  Fix: Single Responsibility and encapsulation (`swe-principles`) — give
  the type the behavior that's actually about its own data.
