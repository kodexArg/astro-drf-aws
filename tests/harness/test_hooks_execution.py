#!/usr/bin/env python3
"""Validates hook configurations and execution behavior."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = ROOT / "hooks"
SETTINGS_JSON = ROOT / ".claude" / "settings.json"


SESSION_START_REQUIRED = (
    "hooks/khook-repo-health.py",
    "hooks/khook-load-ssot.py",
    "hooks/khook-mvmcp-freshness.py",
)


def test_settings_json_hooks_exist():
    assert SETTINGS_JSON.is_file(), ".claude/settings.json not found"
    data = json.loads(SETTINGS_JSON.read_text(encoding="utf-8"))
    hooks_config = data.get("hooks", {})

    checked = 0
    session_cmds = []
    for event, event_hooks in hooks_config.items():
        for group in event_hooks:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                match = re.search(r'\$CLAUDE_PROJECT_DIR/([^\s"]+)', cmd)
                assert match, f"Could not parse script path from command: {cmd}"
                rel_path = match.group(1)
                script_path = ROOT / rel_path
                assert script_path.is_file(), f"Settings references missing script: {rel_path}"
                checked += 1
                if event == "SessionStart":
                    session_cmds.append(rel_path)
    assert checked > 0, "No hooks configured in .claude/settings.json"
    for required in SESSION_START_REQUIRED:
        assert required in session_cmds, f"SessionStart missing {required}"


def test_hooks_standalone_execution():
    # stdin=DEVNULL: PostToolUse hooks read Claude JSON from stdin; an open
    # unwritten pipe makes sys.stdin.read() hang until timeout.
    for hook_file in sorted(HOOKS_DIR.glob("khook-*")):
        if hook_file.suffix == ".py":
            res = subprocess.run(
                [sys.executable, str(hook_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
                stdin=subprocess.DEVNULL,
            )
            assert res.returncode == 0, f"Hook {hook_file.name} failed with code {res.returncode}: {res.stderr}"
        elif hook_file.name != "khook-pre-commit":
            res = subprocess.run(
                [str(hook_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
                stdin=subprocess.DEVNULL,
            )
            assert res.returncode in (0, 1), f"Executable hook {hook_file.name} crashed with code {res.returncode}"


def test_guardian_dispatch_bundle():
    script = HOOKS_DIR / "khook-guardian-dispatch"
    assert script.is_file(), "khook-guardian-dispatch missing"
    # Test against HEAD~1 (or working tree) to verify guardian detection and bundle payload
    res = subprocess.run(
        [sys.executable, str(script), "--bundle", "HEAD~1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode in (0, 1), f"khook-guardian-dispatch --bundle crashed: {res.stderr}"
    if res.returncode == 1:
        assert "--- bundle (adr-27-guardians-and-delivery) ---" in res.stdout, "Missing bundle header in output"
        assert "## adr_index" in res.stdout, "Missing adr_index in bundle output"




def test_adr_linter_cli():
    script = HOOKS_DIR / "khook-check-adr.py"
    assert script.is_file(), "khook-check-adr.py missing"
    res = subprocess.run(
        [sys.executable, str(script), "--all"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0, f"khook-check-adr.py --all flagged errors: {res.stderr}"


if __name__ == "__main__":
    test_settings_json_hooks_exist()
    test_hooks_standalone_execution()
    test_guardian_dispatch_bundle()
    test_adr_linter_cli()
    print("ok  all hooks and runtime configurations valid")
