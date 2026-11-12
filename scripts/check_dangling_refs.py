#!/usr/bin/env python3
"""
Warn-only detector for dangling references to paths/names deleted in a
commit.

The defect class this catches: a comment/docstring elsewhere in the repo
still describing deleted code as if it existed — either by name (e.g. a
deleted class `PaymentConfig`) or by path (e.g. a deleted
`some_service/pyproject.toml`). Grepping for the deleted *name* alone
misses instances that reference the deleted *path* instead, and vice
versa — this script sweeps both, and sweeps the WHOLE repo rather than
just the deleting commit's own diff, because a dangling reference can live
in a file the deleting commit never touched.

Two candidate classes, per file deleted in the range under inspection:

1. Path candidates — the file's full repo-relative path, plus (for a
   directory removed in its entirety) that directory's own path and
   basename.
2. Name candidates — for a deleted `.py`/`.ts`/`.tsx`/`.js`/`.jsx` file,
   its top-level `class`/`def`/exported-symbol names. A short stoplist
   skips generic names (`main`, `client`, `index`, ...) that would just be
   noise against a repo this size.

Each candidate is then `git grep`'d against the repo. This is a detection
tool only — in default (non-strict) mode it exits 0 whenever every
underlying git command itself succeeded, hit or no hit, and never blocks a
commit; a human/reviewer classifies each hit (some are legitimate
historical narration, e.g. a changelog entry, and should stay untouched).
Pass --strict to make it exit 1 when a candidate has a hit, if this is
ever wired into a hard-fail CI job rather than a warn-only pre-commit
hook. Either way it exits 2 if a git command itself failed (bad ref,
shallow clone missing history, ...) — a tool failure is never reported as
"nothing found".

Doesn't see through renames: a moved-not-deleted file is classified `R` by
git's default rename detection, not `D`, so its old path/names aren't
checked — a deliberate scope limit, not a bug.

Usage:
    # Pre-commit hook default: staged deletions vs HEAD, grepped against
    # the index (i.e. what the resulting commit will actually contain).
    python scripts/check_dangling_refs.py

    # Ad hoc / CI: deletions between two refs, grepped against the range's
    # own HEAD argument (not necessarily whatever is currently checked
    # out).
    python scripts/check_dangling_refs.py --range <base-sha> <head-sha>
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Generic identifiers that would be pure noise to grep for repo-wide —
# extracted names shorter than 4 chars or matching this list are dropped.
NAME_STOPLIST = {
    "main", "run", "get", "set", "init", "config", "client", "base",
    "utils", "default", "index", "app", "test", "tests", "types", "type",
}

# Never surface hits inside the checker's own source or hook wrapper —
# both legitimately reference example deleted names in comments/docstrings
# for illustration.
EXCLUDE_PATHSPECS = [":(exclude)scripts/check_dangling_refs.py", ":(exclude).githooks/pre-commit"]

# A candidate producing more hits than this gets its hit list truncated in
# the report (not dropped — an earlier version silently hiding
# over-threshold candidates made --strict blind to them). This keeps the
# common-word-collision case (a deleted "billing" or "api" subdirectory's
# bare basename matching this repo's own domain vocabulary everywhere)
# from dumping dozens of lines per candidate, without a hand-maintained
# stoplist of domain words.
MAX_HITS_TO_REPORT = 8

PY_NAME_RE = re.compile(r"^(?:async\s+def|def|class)\s+([A-Za-z_]\w*)", re.MULTILINE)
TS_NAME_RE = re.compile(
    r"^export\s+(?:default\s+)?(?:abstract\s+)?(?:class|function|interface|type|const|let)\s+([A-Za-z_]\w*)",
    re.MULTILINE,
)
SOURCE_EXTENSIONS = {".py": PY_NAME_RE, ".ts": TS_NAME_RE, ".tsx": TS_NAME_RE, ".js": TS_NAME_RE, ".jsx": TS_NAME_RE}


class GitError(RuntimeError):
    """A git subprocess exited with a code its caller didn't expect. Distinct
    from "ran fine, found nothing" (e.g. `git grep`'s exit 1) — see run()'s
    ok_codes. Exists so a git failure (bad ref, missing history, ...) can
    never be silently reported as an empty, successful-looking result."""


def run(args: list[str], ok_codes: tuple[int, ...] = (0,)) -> str:
    # encoding/errors explicit: git show/grep output for deleted-file content
    # or matched lines can be non-UTF-8 or fail to round-trip through the
    # platform's default codec (e.g. Windows' cp1252) — errors="replace"
    # keeps this a best-effort text scan rather than a crash on stray bytes.
    result = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode not in ok_codes:
        raise GitError(f"git {' '.join(args)} exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def deleted_files(base: str | None, head: str | None) -> list[str]:
    if base is None:
        # Pre-commit hook mode: staged deletions vs HEAD.
        out = run(["diff", "--cached", "--name-only", "--diff-filter=D"])
    else:
        out = run(["diff", "--name-only", "--diff-filter=D", base, head])
    return [line for line in out.splitlines() if line.strip()]


def pre_image_content(path: str, base: str | None) -> str:
    rev = base if base is not None else "HEAD"
    return run(["show", f"{rev}:{path}"])


def extract_names(path: str, content: str) -> set[str]:
    pattern = SOURCE_EXTENSIONS.get(Path(path).suffix)
    if not pattern or not content:
        return set()
    names = set()
    for match in pattern.finditer(content):
        name = match.group(1)
        if len(name) >= 4 and name.lower() not in NAME_STOPLIST:
            names.add(name)
    return names


def existing_directories(rev: str | None) -> set[str]:
    """All directory paths still present in the target tree — HEAD's tree
    for --range mode (so "still exists" means at the post-deletion revision
    being checked, not whatever happens to be on disk right now), or the
    index (via `git ls-files`) for the pre-commit default — what the
    resulting commit will actually contain, not the working tree."""
    if rev:
        out = run(["ls-tree", "-d", "-r", "--name-only", rev])
        dirs = set(out.splitlines())
    else:
        out = run(["ls-files"])
        dirs = set()
        for f in out.splitlines():
            parts = Path(f).parts[:-1]
            for depth in range(1, len(parts) + 1):
                dirs.add("/".join(parts[:depth]))
    return {d for d in dirs if d}


def deleted_directory_candidates(paths: list[str], existing_dirs: set[str]) -> set[str]:
    """
    For each deleted file, walk its ancestor directories from the immediate
    parent up. The first ancestor still present in existing_dirs means every
    ancestor above it also still exists (deletions are inside it) — stop
    there. Any ancestor NOT in existing_dirs was wholly removed; add its
    full path (mirrors "see some_package/config.py"-style path references)
    and, if its basename is distinctive enough to be worth a repo-wide grep
    (not a generic word, and not a name that ALSO still exists as a
    directory basename elsewhere in the tree — e.g. "src" or "api", which
    every deleted package under a typical repo layout tends to contain and
    would otherwise flood every hit list with unrelated matches), its bare
    basename too (mirrors "see some_package" with no path).
    """
    existing_basenames = {Path(d).name for d in existing_dirs}
    candidates: set[str] = set()
    for path in paths:
        parts = Path(path).parts[:-1]
        for depth in range(len(parts), 0, -1):
            ancestor = "/".join(parts[:depth])
            if ancestor in existing_dirs:
                break
            candidates.add(ancestor)
            basename = Path(ancestor).name
            if len(basename) >= 4 and basename.lower() not in NAME_STOPLIST and basename not in existing_basenames:
                candidates.add(basename)
    return candidates


def grep_repo(needle: str, rev: str | None, cached: bool) -> list[str]:
    # -w: word-boundary match, not bare substring. Without it, short
    # candidates like a deleted "_app"/"_oauth"/"_auth" test helper collide
    # with every unrelated occurrence of that substring inside a longer
    # identifier — hundreds of junk hits per candidate on a repo of any
    # size. Path candidates still match fine (a `/` is a non-word
    # boundary), and `SomeClass.method()`-style call sites still match
    # (`.` is a non-word boundary too).
    args = ["grep", "-n", "-F", "-w", "-e", needle]
    if cached:
        # Default (pre-commit) mode: grep what will actually be committed
        # (the index), not the working tree, which can differ (unstaged
        # edits, partially-staged hunks).
        args.append("--cached")
    if rev:
        args.append(rev)
    args.append("--")
    args.extend(EXCLUDE_PATHSPECS)
    # `git grep` exits 1 for "ran fine, no match" — not an error. Only 2+
    # (bad pattern, bad rev, bad pathspec, ...) should raise.
    out = run(args, ok_codes=(0, 1))
    return [line for line in out.splitlines() if line.strip()]


def main() -> int:
    # Matched lines can contain characters outside the console's active
    # codepage (e.g. an em dash on Windows' default cp1252) — reconfigure
    # rather than crash mid-report on a hit that was otherwise fine to show.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--range", nargs=2, metavar=("BASE", "HEAD"), help="check deletions between two refs instead of staged changes")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any candidate has a hit (default: warn-only, exits 0 unless a git command itself failed)")
    args = parser.parse_args()

    base, head = (args.range if args.range else (None, None))
    range_mode = base is not None
    # cached=True (default/pre-commit mode) greps the index — what the
    # resulting commit will actually contain — not the working tree, which
    # can differ. range_mode greps the range's own HEAD argument instead,
    # not necessarily whatever is currently checked out.
    grep_rev = head if range_mode else None

    try:
        paths = deleted_files(base, head)
        if not paths:
            return 0
        existing_dirs = existing_directories(grep_rev)
    except GitError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    tool_errors = False

    path_candidates: dict[str, str] = {}  # candidate -> the deleted path it came from
    for path in paths:
        path_candidates[path] = path
    for dir_candidate in deleted_directory_candidates(paths, existing_dirs):
        path_candidates.setdefault(dir_candidate, dir_candidate)

    name_candidates: dict[str, str] = {}  # candidate -> the deleted path it came from
    for path in paths:
        try:
            content = pre_image_content(path, base)
        except GitError as e:
            print(f"[ERROR] couldn't read pre-deletion content of {path}: {e}", file=sys.stderr)
            tool_errors = True
            continue
        for name in extract_names(path, content):
            name_candidates.setdefault(name, path)

    hits_found = False
    report_lines: list[str] = []
    for candidate, source in {**path_candidates, **name_candidates}.items():
        try:
            hits = grep_repo(candidate, grep_rev, cached=not range_mode)
        except GitError as e:
            print(f"[ERROR] grep for '{candidate}' failed: {e}", file=sys.stderr)
            tool_errors = True
            continue
        if not hits:
            continue
        hits_found = True
        if len(hits) > MAX_HITS_TO_REPORT:
            # Truncated, not dropped — silently discarding over-threshold
            # candidates would also make --strict blind to them. A high
            # hit count is still worth a human glance; it just isn't worth
            # a full dump.
            shown = hits[:MAX_HITS_TO_REPORT]
            report_lines.append(
                f"\n[WARNING] possible dangling reference to '{candidate}' (deleted via {source}) "
                f"— {len(hits)} hits, showing first {MAX_HITS_TO_REPORT}:"
            )
            report_lines.extend(f"    {hit}" for hit in shown)
            report_lines.append(f"    ... and {len(hits) - MAX_HITS_TO_REPORT} more")
        else:
            report_lines.append(f"\n[WARNING] possible dangling reference to '{candidate}' (deleted via {source}):")
            report_lines.extend(f"    {hit}" for hit in hits)

    for line in report_lines:
        print(line)
    if hits_found:
        # stdout, not stderr, and after every [WARNING]/[ERROR] line above:
        # interleaving can race between two independently-buffered streams
        # (a real `git commit` included) if this were printed earlier.
        print(
            "\nThese are warnings, not failures — some hits are legitimate historical "
            "narration (changelog entries, migration docstrings). A human/reviewer "
            "classifies each one."
        )

    if tool_errors:
        return 2
    if hits_found and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
