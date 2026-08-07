
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude" / "hooks" / "check_variables.py"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise AssertionError(msg)


def ok(msg: str) -> None:
    print(f"ok  {msg}")


def run_hook(project_dir: Path, file_path: Path) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_input": {"file_path": str(file_path)}})
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
    )


def make_project(tmp_path: Path, declared: list[str]) -> Path:
    project = tmp_path / "project"
    docs = project / "docs"
    docs.mkdir(parents=True)
    rows = "\n".join(f"| `{name}` | example | dev | some var |" for name in declared)
    (docs / "VARIABLES.md").write_text(
        "# VARIABLES\n\n"
        "| Name | Source | Env | Notes |\n"
        "|---|---|---|---|\n" + rows + "\n",
        encoding="utf-8",
    )
    return project


def assert_hook(
    rel_path: str,
    content: str,
    expect_rc: int,
    declared: list[str] | None = None,
    expect_in_stderr: str | None = None,
) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = make_project(Path(tmp), declared or [])
        target = project / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        proc = run_hook(project, target)
        if proc.returncode != expect_rc:
            fail(
                f"{rel_path}: expected exit {expect_rc}, got {proc.returncode} "
                f"stderr={proc.stderr!r}"
            )
        if expect_in_stderr and expect_in_stderr not in proc.stderr:
            fail(f"stderr must name {expect_in_stderr!r}; got {proc.stderr!r}")


def test_env_helper_read_undeclared_is_caught() -> None:
    assert_hook(
        "backend/config/settings.py",
        'DEBUG = _env_bool("MISSING_HELPER_VAR", False)\n',
        expect_rc=2,
        declared=["DECLARED_VAR"],
        expect_in_stderr="MISSING_HELPER_VAR",
    )
    ok("_env_bool() undeclared read is caught (regression guard)")


def test_env_helper_read_declared_passes() -> None:
    assert_hook(
        "backend/config/settings.py",
        'ALLOWED_HOSTS = _env_list("ALLOWED_HOST", "").split(",")\n'
        'HOST = _env("ALLOWED_HOST", "")\n',
        expect_rc=0,
        declared=["ALLOWED_HOST"],
    )
    ok("_env()/_env_list() declared reads pass")


def test_literal_os_environ_still_caught() -> None:
    assert_hook(
        "backend/app/views.py",
        'import os\nSECRET = os.environ.get("SOME_LITERAL_VAR")\n',
        expect_rc=2,
        expect_in_stderr="SOME_LITERAL_VAR",
    )
    ok("literal os.environ.get() undeclared read is still caught")


def test_repo_root_tests_dir_is_exempt() -> None:
    assert_hook(
        "tests/test_aws_infra.py",
        'import os\n'
        'PROFILE = os.environ.get("AWS_PROFILE", "kodex")\n'
        'REGION = os.environ.get("AWS_REGION", "us-east-1")\n',
        expect_rc=0,
    )
    ok("repo-root tests/ tooling env reads are exempt (issue #138)")


def test_backend_test_files_still_swept() -> None:
    assert_hook(
        "backend/apps/users/test_cognito_live.py",
        'import os\nSECRET_ID = os.environ.get("SOME_APP_TEST_VAR")\n',
        expect_rc=2,
    )
    ok("backend app test files remain in the sweep")


def test_harness_scripts_are_exempt() -> None:
    assert_hook(
        "scripts/mvmcp.py",
        'import os\n'
        'HOST = os.environ.get("MARKDOWN_VAULT_MCP_HOST", "127.0.0.1")\n',
        expect_rc=0,
    )
    ok("scripts/ harness tooling env reads are exempt")


def test_committed_env_template_still_swept() -> None:
    assert_hook(".env.example", "SOME_UNDECLARED_VAR=value\n", expect_rc=2)
    ok("root .env* templates remain in the sweep")


def test_frontend_tree_is_swept() -> None:
    assert_hook(
        "frontend/src/pages/index.astro",
        'const url = process.env.SOME_FRONTEND_VAR ?? "";\n',
        expect_rc=2,
    )
    ok("frontend/ service tree remains in the sweep")


def main() -> int:
    tests = [
        test_env_helper_read_undeclared_is_caught,
        test_env_helper_read_declared_passes,
        test_literal_os_environ_still_caught,
        test_repo_root_tests_dir_is_exempt,
        test_backend_test_files_still_swept,
        test_harness_scripts_are_exempt,
        test_committed_env_template_still_swept,
        test_frontend_tree_is_swept,
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
