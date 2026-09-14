#!/usr/bin/env python3
"""ADR trigger-index preload hook (SessionStart).

Gives force to the ABC gate's 'does it comply with the ADRs?' requirement.
Reads frontmatter only (title, status, description) and provides a fast index
of active ADRs so the agent knows which rules apply to the task.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
FIELD = {
    "title": re.compile(r'^title:\s*"?([^"\n]+)"?\s*$', re.MULTILINE),
    "status": re.compile(r'^status:\s*(\w+)\s*$', re.MULTILINE),
    "description": re.compile(r'^description:\s*"(.*)"\s*$', re.MULTILINE),
}


import subprocess


def project_dir() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    try:
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if git_root:
            return Path(git_root)
    except Exception:
        pass
    return Path(__file__).resolve().parents[1]



def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    block = match.group(1)
    out = {}
    for key, pattern in FIELD.items():
        found = pattern.search(block)
        if found:
            out[key] = found.group(1).strip()
    return out


def main() -> int:
    try:
        root = project_dir()
        adrs = root / "adrs"
        if not adrs.is_dir():
            return 0
        lines = []
        for path in sorted(adrs.glob("adr-*.md")):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            fm = parse_frontmatter(text)
            if not fm or "title" not in fm:
                continue
            slug = fm["title"]
            if fm.get("status") == "defered":
                lines.append(f"{slug}: (defered — no content)")
            else:
                lines.append(f"{slug}: {fm.get('description', '(no description)')}")
        if not lines:
            return 0
        print(
            "ADR Trigger Index (adr-00-adr-doctrine.md rule 3 — frontmatter only, "
            "no bodies loaded; read the ADR itself before relying on a rule it "
            "states):\n\n" + "\n".join(lines)
        )
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
