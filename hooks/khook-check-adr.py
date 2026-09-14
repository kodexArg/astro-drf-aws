#!/usr/bin/env python3
"""ADR conformance hook (PostToolUse on Write|Edit).

Enforces adr-00-adr-doctrine on every file written under adrs/: filename pattern
and the structured frontmatter keys (title, type, status, created, version, tags,
paths, related_adrs, related_agents, description, applies_when).
Exit 2 feeds violations back to the agent; internal errors exit 0.
"""

from __future__ import annotations

import json
import os
import re
import sys
import subprocess
from pathlib import Path

FILENAME = re.compile(r"^adr-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQUIRED_KEYS = (
    "title",
    "type",
    "status",
    "created",
    "version",
    "tags",
    "paths",
    "related_adrs",
    "related_agents",
    "description",
    "applies_when",
)
DESCRIPTION_MIN_WORDS = 25
DESCRIPTION_MAX_WORDS = 45


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


def get_default_version(root: Path) -> str:
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


def parse(text: str) -> tuple[dict[str, str] | None, list[str]]:
    match = re.match(r"\A---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return None, []
    fm = {}
    keys = []
    for line in match.group(1).splitlines():
        if re.match(r"^[A-Za-z_][\w-]*:", line):
            key, _, val = line.partition(":")
            k = key.strip()
            keys.append(k)
            fm[k] = val.strip().strip("\"'")
    return fm, keys


def check(path: Path, root: Path | None = None) -> list[str]:
    posix = path.as_posix()
    if "/adrs/" not in posix:
        return []
    if path.suffix != ".md":
        return []
    if root is None:
        root = project_dir().resolve()
    problems = []
    if not FILENAME.match(path.name):
        problems.append(
            f"{path.name}: ADR filenames must match adr-NN-slug.md "
            "(sequential NN, kebab-case English slug) per adr-00-adr-doctrine."
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return problems

    fm, keys = parse(text)
    if fm is None:
        problems.append(f"{path.name}: missing YAML frontmatter block (adr-00-adr-doctrine).")
        return problems

    for req in REQUIRED_KEYS:
        if req not in keys:
            problems.append(f"{path.name}: frontmatter lacks '{req}' (adr-00-adr-doctrine).")

    if fm.get("type") and fm["type"] != "adr":
        problems.append(f"{path.name}: frontmatter 'type' must be 'adr', found '{fm['type']}'.")

    status = fm.get("status")
    if status and status not in ("active", "defered", "superseded"):
        problems.append(f"{path.name}: invalid status '{status}', must be active|defered|superseded.")

    title = fm.get("title")
    if title and title != path.stem:
        problems.append(f"{path.name}: frontmatter 'title' '{title}' != filename stem '{path.stem}'.")

    version = fm.get("version")
    expected_version = get_default_version(root)
    if version and version != expected_version:
        problems.append(
            f"{path.name}: frontmatter 'version' '{version}' != harness default '{expected_version}'."
        )

    desc = fm.get("description", "").strip('"\'')
    if desc:
        words = len(desc.split())
        if not (DESCRIPTION_MIN_WORDS <= words <= DESCRIPTION_MAX_WORDS):
            problems.append(
                f"{path.name}: description is {words} words, must be {DESCRIPTION_MIN_WORDS}..{DESCRIPTION_MAX_WORDS}."
            )

    return problems


def main() -> int:
    root = project_dir().resolve()
    problems: list[str] = []

    # Case 1: CLI arguments provided (e.g. python3 hooks/khook-check-adr.py adrs/adr-00-adr-doctrine.md)
    if len(sys.argv) > 1:
        targets = []
        for arg in sys.argv[1:]:
            if arg in ("--all", "-a"):
                targets.extend(sorted((root / "adrs").glob("adr-*.md")))
            else:
                p = Path(arg).resolve()
                if p.is_dir():
                    targets.extend(sorted(p.glob("adr-*.md")))
                else:
                    targets.append(p)
        for t in targets:
            problems.extend(check(t, root))

    # Case 2: Interactive terminal with no args -> check all ADRs
    elif sys.stdin.isatty():
        adrs_dir = root / "adrs"
        if adrs_dir.is_dir():
            for t in sorted(adrs_dir.glob("adr-*.md")):
                problems.extend(check(t, root))

    # Case 3: Piped stdin (Claude / agent tool hook JSON)
    else:
        try:
            content = sys.stdin.read().strip()
            if not content:
                return 0
            payload = json.loads(content)
            file_path = payload.get("tool_input", {}).get("file_path", "")
            if not file_path:
                return 0
            target = Path(file_path).resolve()
            if not target.is_relative_to(root):
                return 0
            problems = check(target, root)
        except Exception:
            return 0

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
