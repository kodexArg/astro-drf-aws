#!/usr/bin/env python3
"""API mention gate (UserPromptSubmit).

A prompt that plausibly touches the route surface forces a fresh read of
docs/API.md before acting: the file is the only source of valid endpoints
and may have changed since session start.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

MENTION = re.compile(
    r"/api/|\bendpoints?\b|\bviewsets?\b|\bserializers?\b|\burls\.py\b|\broutes?\.(?:ts|js)\b|\b(?:add|adds|adding|chang\w*|remov\w*|declar\w*)\b[\s\S]{0,30}\bapi\b|\bapi\b[\s\S]{0,30}\b(?:add|adds|adding|chang\w*|remov\w*|declar\w*)\b",
    re.IGNORECASE,
)


def project_dir() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    return Path(__file__).resolve().parents[1]


def main() -> int:
    try:
        if sys.stdin.isatty():
            return 0
        payload = json.load(sys.stdin)
        prompt = payload.get("prompt", "")
        if not MENTION.search(prompt):
            return 0
        print(
            "API gate: this prompt mentions the API. Before acting on it, Read "
            "docs/API.md — it is the single source of truth for valid endpoints and "
            "the in-memory copy may be stale. Every endpoint decision must match "
            "its rows; a needed endpoint missing there gets its row added first."
        )
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
