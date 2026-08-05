#!/usr/bin/env python3
"""ADR conformance hook (PostToolUse on Write|Edit).

Enforces adr-00-adr-doctrine on every file written under .claude/rules/ or
docs/adrs/: filename pattern, the seven required frontmatter fields, and the
five level-2 sections (CONTEXT / ASSERTIONS / FORBIDDEN / REJECTED / RELATED,
FORBIDDEN and REJECTED optional, present only when non-empty). Exit 2 feeds
the violation back to the agent; any internal error exits 0.
"""

import json
import os
import re
import sys
from pathlib import Path

FILENAME = re.compile(r"^adr-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
REQUIRED_KEYS = ("title", "type", "category", "use_case", "created", "modified", "tags")
ALLOWED_CATEGORIES = ("frontend", "backend", "devops", "harness", "project")
REQUIRED_SECTIONS = ("CONTEXT", "ASSERTIONS")
FINAL_SECTION = "RELATED"
SECTION_ORDER = ("CONTEXT", "ASSERTIONS", "FORBIDDEN", "REJECTED", "RELATED")


def project_dir():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def parse(text):
    match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not match:
        return None, text
    fm = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm, match.group(2)


def section_headings(body):
    return re.findall(r"^##\s+([A-Z]+)\s*$", body, re.MULTILINE)


def check(path):
    posix = path.as_posix()
    if "/.claude/rules/" not in posix and "/docs/adrs/" not in posix:
        return []
    if path.suffix != ".md":
        return []
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

    fm, body = parse(text)
    if fm is None:
        problems.append(f"{path.name}: missing frontmatter block (adr-00-adr-doctrine).")
        return problems

    for key in REQUIRED_KEYS:
        if key not in fm:
            problems.append(f"{path.name}: frontmatter lacks '{key}' (adr-00-adr-doctrine).")
    if fm.get("type") and fm["type"] != "adr":
        problems.append(f"{path.name}: frontmatter 'type' must be 'adr', found '{fm['type']}'.")
    category = fm.get("category")
    if category and category not in ALLOWED_CATEGORIES:
        problems.append(
            f"{path.name}: frontmatter 'category' must be one of "
            f"{ALLOWED_CATEGORIES}, found '{category}'."
        )

    headings = section_headings(body)
    for required in REQUIRED_SECTIONS:
        if required not in headings:
            problems.append(f"{path.name}: missing required '## {required}' section (adr-00-adr-doctrine).")
    if FINAL_SECTION not in headings:
        problems.append(f"{path.name}: missing required '## {FINAL_SECTION}' section (adr-00-adr-doctrine).")

    present_order = [h for h in headings if h in SECTION_ORDER]
    expected_order = [h for h in SECTION_ORDER if h in present_order]
    if present_order != expected_order:
        problems.append(
            f"{path.name}: level-2 sections out of order — expected the subsequence "
            f"{expected_order}, found {present_order} (adr-00-adr-doctrine)."
        )

    unknown = [h for h in headings if h not in SECTION_ORDER]
    if unknown:
        problems.append(
            f"{path.name}: unrecognized level-2 section(s) {unknown}; only "
            f"{list(SECTION_ORDER)} are valid (adr-00-adr-doctrine)."
        )

    return problems


def main():
    try:
        payload = json.load(sys.stdin)
        file_path = payload.get("tool_input", {}).get("file_path", "")
        if not file_path:
            return 0
        target = Path(file_path).resolve()
        if not target.is_relative_to(project_dir().resolve()):
            return 0
        problems = check(target)
    except Exception:
        return 0
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
