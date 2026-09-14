#!/usr/bin/env python3
"""markdown-vault MCP freshness guard (SessionStart).

The markdown-vault MCP is the first source of truth for docs/ content.
A stale index answers confidently about prose that no longer matches, so this
hook compares the newest docs/*.md mtime against the project-local index and
warns when the vault has drifted. It never blocks; any internal error exits 0.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".obsidian", ".vscode", ".claude"}


def project_dir() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    return Path(__file__).resolve().parents[1]


def newest_docs_mtime(docs: Path) -> float:
    newest = 0.0
    if not docs.is_dir():
        return newest
    for dirpath, dirnames, filenames in os.walk(docs):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                try:
                    newest = max(newest, (Path(dirpath) / name).stat().st_mtime)
                except OSError:
                    pass
    return newest


def main() -> int:
    try:
        root = project_dir()
        index = root / ".mvmcp" / "data" / "index.db"
        if not index.exists():
            # Index does not exist yet (normal on fresh clone)
            return 0
        newest = newest_docs_mtime(root / "docs")
        if newest > index.stat().st_mtime:
            print(
                "MARKDOWN-VAULT MCP — REINDEX FIRST: docs/ has changed since the "
                "vault index was last built. It is STALE; refresh before "
                "trusting its search/read/backlinks. Call the markdown-vault "
                "`reindex` tool or re-index the vault."
            )
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
