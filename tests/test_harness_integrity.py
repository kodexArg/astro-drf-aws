from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_harness_integrity.py"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise AssertionError(msg)


def ok(msg: str) -> None:
    print(f"ok  {msg}")


def run(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
    )


def make_clean_tree(root: Path) -> None:
    (root / "docs" / "skills" / "good-skill").mkdir(parents=True)
    (root / "docs" / "skills" / "good-skill" / "SKILL.md").write_text(
        "---\nname: good-skill\ndescription: A fine skill.\n---\nNo references here.\n"
    )
    (root / "docs" / "agents").mkdir(parents=True)
    (root / "docs" / "agents" / "good-agent.md").write_text(
        "---\nname: good-agent\ndescription: d\nmodel: sonnet\ntools:\n  - Read\n---\nBody.\n"
    )
    (root / "docs" / "constitution").mkdir(parents=True)
    (root / "docs" / "constitution" / "HARNESS.md").write_text(
        "## Required skills\n\n| `good-skill` | desc | consumer |\n"
    )


def test_selftest_flag_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--selftest"], capture_output=True, text=True
    )
    if proc.returncode != 0:
        fail(f"--selftest must exit 0 on its own synthetic fixture; got {proc.returncode}, "
             f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    ok("--selftest passes against its own synthetic good/bad fixture")


def test_clean_tree_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_clean_tree(root)
        proc = run(root)
        if proc.returncode != 0:
            fail(f"a clean synthetic tree must exit 0; got {proc.returncode}, "
                 f"stdout={proc.stdout!r}")
        ok("clean synthetic tree exits 0")


def test_synthetic_name_mismatch_is_caught() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_clean_tree(root)
        # Introduce a violation: name field disagrees with the directory name.
        bad = root / "docs" / "skills" / "good-skill" / "SKILL.md"
        bad.write_text("---\nname: some-other-name\ndescription: A fine skill.\n---\nBody.\n")
        proc = run(root)
        if proc.returncode == 0:
            fail("synthetic name/dirname mismatch must fail the gate, but it exited 0")
        if "name 'some-other-name' != dirname 'good-skill'" not in proc.stdout:
            fail(f"expected the name-mismatch violation to be itemized; got {proc.stdout!r}")
        ok("synthetic name != dirname violation is caught and itemized")


def test_synthetic_bad_model_is_caught() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_clean_tree(root)
        agent = root / "docs" / "agents" / "good-agent.md"
        agent.write_text(
            "---\nname: good-agent\ndescription: d\nmodel: fable\ntools:\n  - Read\n---\nBody.\n"
        )
        proc = run(root)
        if proc.returncode == 0:
            fail("synthetic model outside the allowlist must fail the gate, but it exited 0")
        if "model 'fable' not in" not in proc.stdout:
            fail(f"expected the bad-model violation to be itemized; got {proc.stdout!r}")
        ok("synthetic disallowed model value is caught and itemized")


def test_synthetic_harness_doc_desync_is_caught() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_clean_tree(root)
        # A skill on disk with no row in HARNESS.md's Required skills table.
        (root / "docs" / "skills" / "undocumented-skill").mkdir(parents=True)
        (root / "docs" / "skills" / "undocumented-skill" / "SKILL.md").write_text(
            "---\nname: undocumented-skill\ndescription: d\n---\nBody.\n"
        )
        proc = run(root)
        if proc.returncode == 0:
            fail("an undocumented skill on disk must fail the gate, but it exited 0")
        if "'docs/skills/undocumented-skill' not listed" not in proc.stdout:
            fail(f"expected the HARNESS.md desync violation to be itemized; got {proc.stdout!r}")
        ok("synthetic HARNESS.md/disk desync is caught and itemized")


def main() -> int:
    tests = [
        test_selftest_flag_passes,
        test_clean_tree_passes,
        test_synthetic_name_mismatch_is_caught,
        test_synthetic_bad_model_is_caught,
        test_synthetic_harness_doc_desync_is_caught,
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
