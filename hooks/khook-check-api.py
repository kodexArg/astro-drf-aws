#!/usr/bin/env python3
"""API contract hook (PostToolUse on Write|Edit).

Enforces that every route literal declared in code corresponds to an endpoint
row in docs/API.md. Exit 2 feeds the violation back to the agent; any internal error
exits 0 (fail-open).

Usage:
  # Via Claude hook stdin (PostToolUse)
  # Or via CLI:
  python3 hooks/khook-check-api.py path/to/urls.py
  python3 hooks/khook-check-api.py --all
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROW = re.compile(
    r"^\|\s*(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|WS)\s*\|\s*`(/[^`]*)`",
    re.MULTILINE,
)
ROUTE = re.compile(r"""(?:re_)?path\(\s*r?["']([^"']*)["']""")
REGISTER = re.compile(r"""\.register\(\s*r?["']([^"']*)["']""")
TS_ROUTE = re.compile(r"""(?:router|app)\.(?:get|post|put|patch|delete)\(\s*["']([^"']+)["']""")


def project_dir() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(out.stdout.strip())
    except Exception:
        return Path(__file__).resolve().parents[1]


def _protected_branch(cwd: str = ".") -> bool:
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        return out in ("main", "", "HEAD")
    except Exception:
        return True


def declared_paths() -> list[str] | None:
    api = project_dir() / "docs" / "API.md"
    try:
        return ROW.findall(api.read_text(encoding="utf-8"))
    except OSError:
        return None


def literal_segments(route: str) -> list[str]:
    route = route.strip().lstrip("^").rstrip("$")
    segments = []
    for part in route.split("/"):
        if not part or part.startswith(("<", ":", "${")) or not re.fullmatch(r"[a-zA-Z0-9_-]+", part):
            continue
        segments.append(part)
    return segments


def _declared_segment_lists(declared: list[str]) -> list[list[str]]:
    return [[s for s in p.strip("/").split("/") if s] for p in declared]


def _is_ordered_subsequence(needle: list[str], haystack: list[str]) -> bool:
    it = iter(haystack)
    return all(seg in it for seg in needle)


def is_route_module(path: Path) -> bool:
    name = path.name
    if not (name == "urls.py" or name.endswith("_urls.py") or name in ("routes.ts", "routes.js", "api.ts")):
        return False
    if name.startswith("test_") or name.endswith(("_test.py", ".test.ts", ".spec.ts")):
        return False
    parts = set(path.parts)
    return not (parts & {".claude", ".venv", "node_modules", "site-packages"})


def check(path: Path) -> list[str]:
    if not is_route_module(path):
        return []
    try:
        code = path.read_text(encoding="utf-8")
    except OSError:
        return []
    declared = declared_paths()
    if declared is None:
        return []
    declared_segments = _declared_segment_lists(declared)
    problems = []
    
    extracted_routes = ROUTE.findall(code) + REGISTER.findall(code) + TS_ROUTE.findall(code)
    for route in extracted_routes:
        segments = literal_segments(route)
        if not segments:
            continue
        if not any(_is_ordered_subsequence(segments, dsl) for dsl in declared_segments):
            problems.append(
                f"{path.name}: route '{route}' is not declared in docs/API.md — "
                "its full segment sequence appears in no endpoint row; an endpoint "
                "is valid if and only if it is declared there. Add the row first, then the route."
            )
    return problems


def payload_target(payload: dict) -> Path | None:
    tool_input = payload.get("tool_input", {}) or {}
    raw = tool_input.get("file_path") or tool_input.get("path") or ""
    if not raw:
        return None
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.resolve()
    return (project_dir() / candidate).resolve()


def main() -> int:
    try:
        # Dual mode: CLI args vs stdin
        args = [a for a in sys.argv[1:] if not a.startswith("-")]
        if "--all" in sys.argv:
            root = project_dir()
            problems = []
            for p in root.rglob("*.py"):
                problems.extend(check(p))
            for p in root.rglob("*.ts"):
                problems.extend(check(p))
            if problems:
                print("\n".join(problems), file=sys.stderr)
                return 2
            print("ok  all code routes match docs/API.md")
            return 0

        if args:
            problems = []
            for a in args:
                target = Path(a)
                if not target.is_absolute():
                    target = project_dir() / target
                problems.extend(check(target))
            if problems:
                print("\n".join(problems), file=sys.stderr)
                return 2
            return 0

        if sys.stdin.isatty():
            return 0

        if not _protected_branch(str(project_dir())):
            return 0

        payload = json.load(sys.stdin)
        target = payload_target(payload)
        if target is None or not target.is_relative_to(project_dir().resolve()):
            return 0
        problems = check(target)
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 2
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
