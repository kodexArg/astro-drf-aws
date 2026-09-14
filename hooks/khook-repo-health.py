#!/usr/bin/env python3
"""Repo health guard (SessionStart).

Reports repository CI state, main's last verdict, open PR status, unmerged branches,
working tree status, and strictly verifies harness symlink integrity.
Fail-open: any network blip or gh unavailability exits 0.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

TIMEOUT = 8


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


def run_cmd(cmd: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()
    except Exception:
        return None


def get_repo_name(root: Path) -> str | None:
    out = run_cmd(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"], root)
    return out


def check_symlink_integrity(root: Path) -> list[str]:
    """Verifies that all runtime projections are strictly valid symlinks to root SSOTs."""
    issues = []
    expected_links = {
        ".claude/rules": "adrs",
        ".claude/agents": "agents",
        ".claude/hooks": "hooks",
        ".claude/skills": "skills",
        ".agents/agents": "agents",
        ".grok/skills": "skills",
    }
    for rel_link, target_name in expected_links.items():
        link_path = root / rel_link
        target_path = root / target_name
        if not link_path.exists():
            issues.append(f"MISSING: {rel_link} does not exist (expected symlink to {target_name})")
        elif not link_path.is_symlink():
            issues.append(f"ANTI-PATTERN: {rel_link} is a real directory/file, not a symlink! Causes drift from {target_name}")
        elif link_path.resolve() != target_path.resolve():
            issues.append(f"MISALIGNED: {rel_link} points to {link_path.resolve()}, expected {target_path.resolve()}")
    return issues


def check_ci_status(root: Path, repo: str) -> str:
    out = run_cmd(["gh", "api", f"repos/{repo}/actions/permissions"], root)
    if not out:
        return "UNKNOWN (API unreachable)"
    try:
        if not json.loads(out).get("enabled", False):
            return "DISABLED repo-wide (actions permissions enabled: false)"
    except Exception:
        return "UNKNOWN"

    out = run_cmd(["gh", "api", f"repos/{repo}/actions/workflows"], root)
    if not out:
        return "permitted repo-wide; per-workflow state UNKNOWN"
    try:
        workflows = json.loads(out).get("workflows", [])
    except Exception:
        return "permitted repo-wide; per-workflow state UNKNOWN"
    if not workflows:
        return "permitted repo-wide; NO WORKFLOWS defined"

    off = sorted(w.get("name", "?") for w in workflows if w.get("state") != "active")
    if not off:
        return f"ENABLED ({len(workflows)} workflows active)"
    if len(off) == len(workflows):
        return f"DISABLED — every workflow is off ({', '.join(off)})"
    return f"PARTIAL — {len(off)} of {len(workflows)} workflows off ({', '.join(off)})"


def check_last_main_run(root: Path) -> str:
    out = run_cmd(
        ["gh", "run", "list", "--branch", "main", "--limit", "1", "--json", "status,conclusion,name,createdAt"],
        root,
    )
    if not out:
        return "none available"
    try:
        runs = json.loads(out)
        if not runs:
            return "none found"
        run = runs[0]
        conclusion = run.get("conclusion") or run.get("status")
        return f"{run.get('name', 'CI')}: {conclusion} ({run.get('createdAt', '')})"
    except Exception:
        return "unknown"


def check_open_prs(root: Path) -> list[str]:
    out = run_cmd(["gh", "pr", "list", "--state", "open", "--json", "number,title,headRefName"], root)
    if not out:
        return []
    try:
        prs = json.loads(out)
        return [f"#{p['number']} '{p['title']}' ({p['headRefName']})" for p in prs]
    except Exception:
        return []


def check_unmerged_branches(root: Path) -> list[str]:
    out = run_cmd(["git", "branch", "--no-merged", "main"], root)
    if not out:
        return []
    return [b.strip().lstrip("* ") for b in out.splitlines() if b.strip()]


def check_working_tree(root: Path) -> tuple[str, int]:
    branch = run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"], root) or "unknown"
    status_out = run_cmd(["git", "status", "--porcelain"], root)
    dirty_count = len([l for l in status_out.splitlines() if l.strip()]) if status_out else 0
    return branch, dirty_count


def main() -> int:
    root = project_dir()
    branch, dirty = check_working_tree(root)
    symlink_issues = check_symlink_integrity(root)

    print("=== REPO HEALTH ===")
    print(f"Branch: {branch} ({dirty} uncommitted change(s))")

    if symlink_issues:
        print("\n⚠️  SYMLINK INTEGRITY WARNINGS:")
        for issue in symlink_issues:
            print(f"  - {issue}")
    else:
        print("Harness Symlinks: All runtime projections intact (.claude, .agents, .grok -> root SSOTs)")

    repo = get_repo_name(root)
    if repo:
        ci = check_ci_status(root, repo)
        last_run = check_last_main_run(root)
        prs = check_open_prs(root)
        unmerged = check_unmerged_branches(root)

        print(f"GitHub Repo: {repo}")
        print(f"CI Workflows: {ci}")
        print(f"Last main Run: {last_run}")
        if prs:
            print(f"Open PRs ({len(prs)}):")
            for pr in prs[:5]:
                print(f"  - {pr}")
        if unmerged:
            print(f"Unmerged Branches ({len(unmerged)}): {', '.join(unmerged[:5])}")

    print("===================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
