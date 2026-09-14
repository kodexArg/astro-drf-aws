#!/usr/bin/env python3
"""Default version resolver for the harness."""

from __future__ import annotations

import os
import re
from pathlib import Path


def project_root() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    return Path(__file__).resolve().parents[1]


def get_default_version(root: Path | None = None) -> str:
    """Returns the default harness version from root CHANGELOG.md (fallback: v0.1.0)."""
    if root is None:
        root = project_root()
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        try:
            text = changelog.read_text(encoding="utf-8")
            m = re.search(r"^version:[ \t]*(.*)$", text, re.MULTILINE)
            if m and m.group(1).strip().strip("\"'"):
                return m.group(1).strip().strip("\"'")
            h = re.search(r"^##\s+\[?([vV]?\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)]?", text, re.MULTILINE)
            if h:
                return h.group(1).strip()
        except Exception:
            pass
    return "v0.1.0"


if __name__ == "__main__":
    print(get_default_version())
