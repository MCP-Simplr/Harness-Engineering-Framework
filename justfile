# Task runner for the whole workspace. Install `just`: https://github.com/casey/just
# Run `just` with no args to list every recipe.
#
# This is a SKELETON — the recipe names below (project-a, project-b) are
# placeholders; rename them to your real project names. The organizing
# idea worth keeping: one canonical entry point (`just <recipe>`) wrapping
# scripts/*.sh for Python-style services and plain `npm run` for Node
# frontends, grouped by workspace domain, with inline comments explaining
# *why* a recipe is built the way it is — not just what it runs.

set shell := ["bash", "-cu"]

default:
    @just --list

# ── Python workspace (uv, or your own equivalent) ───────────────────────────

# Install/sync every Python project into one shared .venv.
sync:
    uv sync --all-packages

# Example: run project-a's backend. Rename/duplicate per real project.
run-project-a:
    ./scripts/run-project-a.sh

# Example: pytest for project-a. Explain any non-obvious cwd/--project
# choice inline the way you'd explain any other design decision.
test-project-a:
    cd project-a && uv run pytest

# ── Database / shared data layer (if you have one) ──────────────────────────

db-upgrade:
    ./scripts/db-upgrade.sh

db-revision message:
    ./scripts/db-revision.sh "{{message}}"

db-downgrade:
    ./scripts/db-downgrade.sh

# ── Node projects ────────────────────────────────────────────────────────

run-project-b:
    cd project-b && npm run dev

lint-project-b:
    cd project-b && npm run lint

test-project-b:
    cd project-b && npm run test

build-project-b:
    cd project-b && npm run build

# ── Repo-wide tooling ────────────────────────────────────────────────────

# One-time local setup — wires up the warn-only pre-commit hook.
install-hooks:
    git config core.hooksPath .githooks

# Warn-only dangling-reference check: staged deletions vs HEAD, grepped
# against the index (what the commit will actually contain, not the
# working tree). This is what .githooks/pre-commit runs automatically;
# call it directly to check before staging, or pass a `range` of two refs
# as one quoted arg to check deletions between two refs instead.
check-dangling-refs range="":
    uv run python scripts/check_dangling_refs.py {{ if range == "" { "" } else { "--range " + range } }}

test-scripts:
    uv run python -m pytest scripts/tests

# ── Full prod-like stack (root docker-compose.yml, if you have one) ────────

up:
    docker compose up --build

down:
    docker compose down
