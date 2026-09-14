#!/usr/bin/env python3
"""Validates that every markdown file in the harness carries the mandatory frontmatter 'version'
matching the current version from root CHANGELOG.md (Assertion-01).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = ROOT / "CHANGELOG.md"

IGNORED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__", "staticfiles"}

# Product markdown (docs/API.md, BDDs, TDDs, README) is not the harness
# version contract. assertion-01 applies to these trees only.
HARNESS_TREES = (
    "adrs",
    "agents",
    "skills",
    "cicd",
    "docs/constitution",
    "docs/assertions",
    "AGENTS.md",
)


def extract_changelog_version(changelog_path: Path) -> str:
    if not changelog_path.is_file():
        raise AssertionError("Root CHANGELOG.md is missing")
    text = changelog_path.read_text(encoding="utf-8")
    
    # 1. Try from frontmatter
    fm_match = re.match(r"\A---\n(.*?)\n---", text, re.DOTALL)
    if fm_match:
        m = re.search(r"^version:[ \t]*(.*)$", fm_match.group(1), re.MULTILINE)
        if m and m.group(1).strip().strip("\"'"):
            return m.group(1).strip().strip("\"'")
            
    # 2. Try from first version heading: ## [vX.Y.Z] or ## [X.Y.Z]
    h_match = re.search(r"^##\s+\[?([vV]?\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)]?", text, re.MULTILINE)
    if h_match:
        return h_match.group(1).strip()
        
    raise AssertionError("Could not determine current version from CHANGELOG.md")


def parse_frontmatter(text: str) -> tuple[str | None, dict[str, str]]:
    match = re.match(r"\A---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return None, {}
    fm_text = match.group(1)
    fields = {}
    for line in fm_text.splitlines():
        if re.match(r"^[A-Za-z_][\w-]*:", line):
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip().strip("\"'")
    return fm_text, fields


def test_markdown_version_consistency():
    expected_version = extract_changelog_version(CHANGELOG)
    assert expected_version, "Expected version from CHANGELOG.md cannot be empty"

    failures = []
    scanned = 0

    scan_roots: list[Path] = []
    for rel in HARNESS_TREES:
        p = ROOT / rel
        if p.is_file():
            scan_roots.append(p)
        elif p.is_dir():
            scan_roots.extend(sorted(p.rglob("*.md")))

    for path in scan_roots:
        if path.suffix != ".md":
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_symlink():
            continue
            
        rel = path.relative_to(ROOT)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            failures.append(f"{rel}: failed to read file: {exc}")
            continue

        scanned += 1
        fm_text, fields = parse_frontmatter(text)
        if fm_text is None:
            failures.append(f"{rel}: missing YAML frontmatter (--- ... ---)")
            continue

        if "version" not in fields:
            failures.append(f"{rel}: missing mandatory 'version' field in frontmatter")
            continue

        actual_version = fields["version"]
        if actual_version != expected_version:
            failures.append(
                f"{rel}: version '{actual_version}' does not match CHANGELOG version '{expected_version}'"
            )

    assert scanned > 0, "No markdown files scanned"
    assert not failures, f"{len(failures)} markdown version assertion failure(s):\n" + "\n".join(failures)


if __name__ == "__main__":
    test_markdown_version_consistency()
    print(f"ok  all harness markdown files verified against CHANGELOG.md version ({extract_changelog_version(CHANGELOG)})")
