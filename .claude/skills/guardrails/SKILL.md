---
name: guardrails
description: The 5-tier guardrail framework (structural/runtime/approval/prompt/observability) for how a rule actually gets enforced — blocking tooling vs. CI-visible vs. reviewer/human judgment vs. documented convention — plus a worked example of tracking a repo's real status per tier. Use when deciding whether a new rule needs a pre-commit hook or CI check versus just a CLAUDE.md mention, when setting up or changing CI/pre-commit, when the reviewer subagent needs to know whether tooling already caught something or it must check manually, or when asked what's actually enforced versus merely documented in a repo.
---

# Guardrail tiers

Reference: `references/guardrails.md`.

Read it before proposing a new rule anywhere in this workspace — decide
which tier it actually belongs in (don't write a [STRUCTURAL]-sounding
rule into a `CLAUDE.md` if nothing can enforce it; call it [PROMPT] and
say so). Read it before touching CI or pre-commit config, since it teaches
you how to track what's already buildable versus genuinely blocked on
something else.
