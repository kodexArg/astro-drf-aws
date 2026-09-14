#!/usr/bin/env python3
"""SSOT preload hook (SessionStart).

Gives force to the AGENTS.md standing requirement: PRD and API MUST be held
in memory at all times. Injects the current contents of PRD.md and API.md
into context at session start (startup, resume, and clear alike), so the
requirement is met deterministically instead of by obedience.

Resolved by basename glob under docs/ rather than a hardcoded relative path,
so a doctrine reshuffle (e.g. docs/PRD.md -> docs/constitution/PRD.md) can
never silently no-op this preload.
Stdout is added to context; any internal error exits 0.
"""

import os
import sys
from pathlib import Path

SSOT_BASENAMES = ("PRD.md", "API.md")


def project_dir():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def find_doc(root, basename):
    docs_dir = root / "docs"
    matches = sorted(docs_dir.rglob(basename))
    return matches[0] if matches else None


def main():
    try:
        root = project_dir()
        sections = []
        for basename in SSOT_BASENAMES:
            path = find_doc(root, basename)
            if path is None:
                sections.append(f"=== {basename} === (not found under docs/ — read it manually before acting)")
                continue
            relative = path.relative_to(root).as_posix()
            try:
                sections.append(f"=== {relative} ===\n{path.read_text(encoding='utf-8').strip()}")
            except OSError:
                sections.append(f"=== {relative} === (unreadable — read it manually before acting)")
        print(
            "SSOT preload (AGENTS.md standing requirement — PRD and API are held "
            "in memory at all times; re-read them whenever they change):\n\n"
            + "\n\n".join(sections)
        )
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
