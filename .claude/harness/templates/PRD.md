<!--
Product Requirements Document template.
Paste this into a new GitHub Issue body (label it type:prd), fill in, get
human sign-off before opening the scoped ticket. See .claude/harness/workflow.md §1.
-->

# PRD: <feature name>

**Project:** `<one of the projects in the root CLAUDE.md workspace map>`
**Status:** draft | approved | superseded
**Author:** <human>
**Date:** <YYYY-MM-DD>

## Problem

What's broken or missing, for whom, and why it matters now. Not the
solution — the problem.

## Goal

What "solved" looks like, in outcomes a non-engineer would recognize.
Explicitly list what's **out of scope**. If this implies building auth,
identity, or payments, check
[.claude/harness/module-catalog.md](../module-catalog.md) first — don't
default to "we build it" without checking what's already available.

## Users / callers

Who or what exercises this — end user, another agent (A2A), an MCP client,
a scheduled job.

## Success criteria

Measurable. If you can't measure it, say what proxy you'll accept instead.

## Constraints

Anything that shapes the solution before a TRD exists: compliance, an
existing schema (your shared data-layer project, if any), budget, deadline,
an external service already in use (payment processor, auth provider,
hosting provider, cloud project).

## Open questions

Anything blocking approval. This section should be empty before status
moves to `approved`.

---
**Human sign-off:** _pending / approved by <name> on <date>_
