from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPATCH_HOOK = ROOT / ".claude" / "hooks" / "dispatch_guardians.py"
AGNOSTIC_SCRIPT = ROOT / "docs" / "hooks" / "guardian-dispatch"
AGENTS_DIR = ROOT / "docs" / "agents"
API_HOOK = ROOT / ".claude" / "hooks" / "require_api_read.py"
PR_FLOW_HOOK = ROOT / ".claude" / "hooks" / "require_pr_flow.py"

# The single source of truth is now each guardian's own frontmatter `watch:`
# list, read live by docs/hooks/guardian-dispatch (adr-03-guardians rule 8).
# There is no second, hand-kept copy anymore — this dict only names which
# guardian filenames are expected to exist, so a seed helper can copy them
# into an isolated tempdir project for the tests below.
GUARDIAN_FILES = (
    "astro-drf-aws-prd.md",
    "astro-drf-aws-adr.md",
    "astro-drf-aws-api.md",
)


def seed_agents(project_dir: Path) -> None:
    """Copy the real guardian definitions (with their live `watch:`
    frontmatter) and the agnostic script into an isolated tempdir project,
    so the delegated hook has a real watchlist source to read."""
    agents_dst = project_dir / "docs" / "agents"
    agents_dst.mkdir(parents=True, exist_ok=True)
    for name in GUARDIAN_FILES:
        shutil.copy(AGENTS_DIR / name, agents_dst / name)
    hooks_dst = project_dir / "docs" / "hooks"
    hooks_dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(AGNOSTIC_SCRIPT, hooks_dst / "guardian-dispatch")


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise AssertionError(msg)


def ok(msg: str) -> None:
    print(f"ok  {msg}")


def run_dispatch(project_dir: Path, rel: str, session: str, tool: str = "Edit"):
    seed_agents(project_dir)
    payload = json.dumps({
        "tool_name": tool,
        "session_id": session,
        "tool_input": {"file_path": str(project_dir / rel)},
    })
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    env.pop("CLAUDE_SESSION_ID", None)
    return subprocess.run(
        [sys.executable, str(DISPATCH_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
    )


def run_api(prompt: str):
    payload = json.dumps({"prompt": prompt})
    return subprocess.run(
        [sys.executable, str(API_HOOK)],
        input=payload,
        capture_output=True,
        text=True,
    )


def run_pr_flow(command: str) -> subprocess.CompletedProcess:
    """Run require_pr_flow.py with a Bash tool_input command. The CWD is a bare
    tempdir so the best-effort gh/git enrichment resolves nothing — the
    deterministic base reminder is what gets exercised here."""
    payload = json.dumps({"tool_input": {"command": command}})
    with tempfile.TemporaryDirectory() as tmp:
        return subprocess.run(
            [sys.executable, str(PR_FLOW_HOOK)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=tmp,
        )


def context_of(proc: subprocess.CompletedProcess) -> str:
    if not proc.stdout.strip():
        return ""
    return json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]


def test_guardian_named_once_across_eight_file_batch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        session = "S-batch"
        first = run_dispatch(project, "docs/adrs/adr-01.md", session)
        if "astro-drf-aws-adr" not in context_of(first):
            fail(
                "the first edit in the batch must name the ADR guardian; "
                f"got stdout={first.stdout!r}"
            )
        for n in range(2, 9):
            proc = run_dispatch(project, f"docs/adrs/adr-{n:02d}.md", session)
            if "astro-drf-aws-adr" in context_of(proc):
                fail(
                    f"edit {n} of the batch re-named the ADR guardian; the "
                    f"nudge must fire once per session, not per file. "
                    f"got stdout={proc.stdout!r}"
                )
        ok("guardian named once across an eight-file batch, not per file")


def test_api_gate_silent_on_false_positive() -> None:
    proc = run_api("the API gate is annoying")
    if proc.stdout.strip():
        fail(
            "a bare 'api' with no route-surface intent must not fire the "
            f"gate; got stdout={proc.stdout!r}"
        )
    ok("require_api_read silent on 'the API gate is annoying'")


def test_api_gate_fires_on_true_positive() -> None:
    proc = run_api("add an endpoint to the api")
    if "API.md" not in proc.stdout:
        fail(
            "a route-surface prompt must fire the gate and re-read "
            f"docs/API.md; got stdout={proc.stdout!r}"
        )
    ok("require_api_read fires on 'add an endpoint to the api'")


def load_agnostic_script():
    loader = importlib.machinery.SourceFileLoader("guardian_dispatch_agnostic", str(AGNOSTIC_SCRIPT))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_frontmatter_watch_is_the_single_source() -> None:
    """The agnostic script reads `watch:` straight from each guardian's own
    frontmatter, and the Claude-native hook resolves to the exact same
    guardian set for a representative file per guardian — proving the hook
    truly delegates rather than re-deriving its own answer."""
    module = load_agnostic_script()
    lists = module.watchlists(AGENTS_DIR)
    for name in ("astro-drf-aws-prd", "astro-drf-aws-adr", "astro-drf-aws-api"):
        if name not in lists or not lists[name]:
            fail(f"docs/agents/{name}.md: no watch: frontmatter list found")

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        session = "S-source"
        cases = (
            ("docs/constitution/PRD.md", "astro-drf-aws-prd"),
            ("docs/adrs/adr-00-adr-doctrine.md", "astro-drf-aws-adr"),
            ("docs/API.md", "astro-drf-aws-api"),
        )
        for rel, expected in cases:
            proc = run_dispatch(project, rel, session + expected)
            ctx = context_of(proc)
            if expected not in ctx:
                fail(
                    f"hook did not resolve {rel!r} to {expected!r} via the "
                    f"frontmatter watch: list; got stdout={proc.stdout!r}"
                )
    ok("frontmatter watch: lists are the single source the hook reads")


def test_pr_flow_nudges_on_worktree_remove() -> None:
    proc = run_pr_flow("git worktree remove .claude/worktrees/wf_test")
    if proc.returncode != 0:
        fail(
            "the hook must never deny a command; got "
            f"{proc.returncode} stderr={proc.stderr!r}"
        )
    out = proc.stdout.lower()
    if "rule 5" not in out or "after" not in out or "merge" not in out:
        fail(
            "git worktree remove must nudge the adr-19 rule-5 ordering "
            f"(remove after merge); got stdout={proc.stdout!r}"
        )
    ok("git worktree remove nudges the rule-5 ordering")


def test_pr_flow_silent_on_worktree_list_and_add() -> None:
    for command in ("git worktree list", "git worktree add foo bar"):
        proc = run_pr_flow(command)
        if proc.returncode != 0:
            fail(f"{command!r}: hook must never deny; got {proc.returncode}")
        if "rule 5" in proc.stdout.lower():
            fail(
                f"{command!r} must NOT fire the worktree-remove nudge "
                f"(regex false positive); got stdout={proc.stdout!r}"
            )
    ok("git worktree list/add do not trip the remove nudge")


def test_pr_flow_still_nudges_on_commit() -> None:
    proc = run_pr_flow("git commit -m x")
    if proc.returncode != 0:
        fail(f"hook must never deny a commit; got {proc.returncode}")
    if "issue -> (worktree optional) -> PR" not in proc.stdout:
        fail(
            "git commit must still print the existing issue->worktree->PR "
            f"nudge (regression guard); got stdout={proc.stdout!r}"
        )
    ok("git commit still prints the existing PR-flow nudge")


def main() -> int:
    tests = [
        test_guardian_named_once_across_eight_file_batch,
        test_api_gate_silent_on_false_positive,
        test_api_gate_fires_on_true_positive,
        test_frontmatter_watch_is_the_single_source,
        test_pr_flow_nudges_on_worktree_remove,
        test_pr_flow_silent_on_worktree_list_and_add,
        test_pr_flow_still_nudges_on_commit,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
        except AssertionError:
            failed += 1
        except Exception as exc:
            print(f"FAIL: {fn.__name__}: {exc}", file=sys.stderr)
            failed += 1

    if failed:
        print(f"\n{failed} test(s) failed", file=sys.stderr)
        return 1
    print(f"\nall {len(tests)} test(s) passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
