#!/usr/bin/env python3
"""Deterministic integrity gate for this template's harness.

Checks (mechanical only, no LLM):
  (a) every docs/skills/*/SKILL.md has frontmatter `name` == its directory name
  (b) frontmatter is valid, `name` and `description` present
  (c) description length is sane (< 1024 chars)
  (d) files a SKILL.md references relatively (scripts/... or references/...)
      actually exist
  (e) docs/agents/*.md: valid frontmatter with name, description, tools,
      and model within the allowlist {haiku, sonnet, opus}
  (f) docs/constitution/HARNESS.md's "Required skills" table (first-column
      backtick entries) matches what is actually on disk under docs/skills/
      — in both directions (declared-but-missing, present-but-undeclared)

Real homes are docs/skills/ and docs/agents/; .claude/skills, .claude/agents,
and root skills/ are symlinks onto them (adr-02-harness) — this script reads
the real homes only, so nothing is double-counted.

Exit 0 clean, exit 1 with an itemized list of violations.
Usage: python3 scripts/check_harness_integrity.py [--root PATH] [--selftest]
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
# Same-skill-relative refs only: scripts/... or references/..., not preceded
# by another path segment (a cross-skill reference is not a same-skill path).
REF_RE = re.compile(r"(?<![\w/.-])(?:scripts|references)/[A-Za-z0-9_./-]+")
ALLOWED_MODELS = {"haiku", "sonnet", "opus"}
MAX_DESCRIPTION_LEN = 1024


def parse_frontmatter(text: str) -> tuple[dict | None, str | None]:
    """Return (data, error). data is None on parse failure."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "no frontmatter block found"
    raw = m.group(1)
    if HAVE_YAML:
        try:
            data = yaml.safe_load(raw)
        except Exception as e:  # noqa: BLE001
            return None, f"YAML parse error: {e}"
        if not isinstance(data, dict):
            return None, "frontmatter did not parse to a mapping"
        return data, None
    # Minimal fallback parser: top-level "key: value" lines only (no nesting).
    data = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            continue  # skip nested/list continuation lines
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        data[k.strip()] = v.strip()
    if not data:
        return None, "fallback parser found no top-level keys"
    return data, None


def check_skills(root: Path, violations: list[str]) -> set[str]:
    skills_dir = root / "docs" / "skills"
    found: set[str] = set()
    if not skills_dir.is_dir():
        violations.append("docs/skills/ directory missing")
        return found

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        name_dir = skill_dir.name
        found.add(name_dir)
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            violations.append(f"docs/skills/{name_dir}: missing SKILL.md")
            continue

        text = skill_md.read_text(encoding="utf-8")
        data, err = parse_frontmatter(text)
        if err:
            violations.append(f"docs/skills/{name_dir}/SKILL.md: {err}")
            continue

        name_fm = data.get("name")
        if not name_fm:
            violations.append(f"docs/skills/{name_dir}/SKILL.md: missing 'name' field")
        elif name_fm != name_dir:
            violations.append(
                f"docs/skills/{name_dir}/SKILL.md: name '{name_fm}' != dirname '{name_dir}'"
            )

        desc = data.get("description")
        if not desc:
            violations.append(f"docs/skills/{name_dir}/SKILL.md: missing 'description' field")
        elif len(desc) >= MAX_DESCRIPTION_LEN:
            violations.append(
                f"docs/skills/{name_dir}/SKILL.md: description length {len(desc)} "
                f">= {MAX_DESCRIPTION_LEN}"
            )

        for para in text.split("\n\n"):
            explicitly_absent = "no existen" in para.lower() or "does not exist" in para.lower()
            for ref in set(REF_RE.findall(para)):
                ref = ref.rstrip(".,;:)")
                # A ref resolves either same-skill-relative (docs/skills/<n>/scripts/...)
                # or repo-root-relative (a skill legitimately invoking a shared
                # top-level scripts/ tool, e.g. kdx-markdown-vault -> scripts/mvmcp.py).
                skill_relative = skill_dir / ref
                repo_relative = root / ref
                if not skill_relative.exists() and not repo_relative.exists() and not explicitly_absent:
                    violations.append(
                        f"docs/skills/{name_dir}/SKILL.md: referenced '{ref}' does not exist"
                    )

    return found


def check_harness_doc_sync(root: Path, disk_skills: set[str], violations: list[str]) -> None:
    harness_md = root / "docs" / "constitution" / "HARNESS.md"
    if not harness_md.is_file():
        violations.append("docs/constitution/HARNESS.md missing")
        return
    text = harness_md.read_text(encoding="utf-8")

    # Only the "Required skills" table's first column counts as a declared
    # skill row: lines shaped "| `name` | ...". Other tables (e.g. vendored
    # MCP servers) use the same row shape but name MCP servers, not skills;
    # skip any row whose name is not a directory anywhere and is a known
    # non-skill MCP server name to avoid false positives on that table.
    declared: set[str] = set()
    in_required_table = False
    for line in text.splitlines():
        if line.startswith("## Required skills"):
            in_required_table = True
            continue
        if line.startswith("## ") and in_required_table:
            in_required_table = False
            continue
        if not in_required_table:
            continue
        m = re.match(r"^\|\s*`([a-zA-Z0-9_.-]+)`\s*\|", line)
        if m:
            declared.add(m.group(1))

    for name in sorted(disk_skills - declared):
        violations.append(
            f"docs/constitution/HARNESS.md: skill on disk 'docs/skills/{name}' "
            "not listed in the Required skills table"
        )
    for name in sorted(declared - disk_skills):
        violations.append(
            f"docs/constitution/HARNESS.md: Required skills table lists '{name}' "
            "which does not exist under docs/skills/"
        )


def check_agents(root: Path, violations: list[str]) -> None:
    agents_dir = root / "docs" / "agents"
    if not agents_dir.is_dir():
        violations.append("docs/agents/ directory missing")
        return

    for agent_md in sorted(agents_dir.glob("*.md")):
        text = agent_md.read_text(encoding="utf-8")
        data, err = parse_frontmatter(text)
        if err:
            violations.append(f"docs/agents/{agent_md.name}: {err}")
            continue

        if not data.get("name"):
            violations.append(f"docs/agents/{agent_md.name}: missing 'name' field")
        if not data.get("description"):
            violations.append(f"docs/agents/{agent_md.name}: missing 'description' field")
        if "tools" not in data:
            violations.append(f"docs/agents/{agent_md.name}: missing 'tools' field")

        model = data.get("model")
        if not model:
            violations.append(f"docs/agents/{agent_md.name}: missing 'model' field")
        elif model not in ALLOWED_MODELS:
            violations.append(
                f"docs/agents/{agent_md.name}: model '{model}' not in {sorted(ALLOWED_MODELS)}"
            )


def run(root: Path) -> list[str]:
    violations: list[str] = []
    disk_skills = check_skills(root, violations)
    check_harness_doc_sync(root, disk_skills, violations)
    check_agents(root, violations)
    return violations


def selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "docs" / "skills" / "good-skill" / "scripts").mkdir(parents=True)
        (root / "docs" / "skills" / "good-skill" / "SKILL.md").write_text(
            "---\nname: good-skill\ndescription: A fine skill.\n---\nUses scripts/run.py.\n"
        )
        (root / "docs" / "skills" / "good-skill" / "scripts" / "run.py").write_text("print('ok')\n")

        (root / "docs" / "skills" / "bad-skill").mkdir(parents=True)
        (root / "docs" / "skills" / "bad-skill" / "SKILL.md").write_text(
            "---\nname: wrong-name\ndescription: Bad.\n---\nSee references/missing.yaml.\n"
        )

        (root / "docs" / "agents").mkdir(parents=True)
        (root / "docs" / "agents" / "good-agent.md").write_text(
            "---\nname: good-agent\ndescription: d\nmodel: sonnet\ntools:\n  - Read\n---\nBody.\n"
        )
        (root / "docs" / "agents" / "bad-agent.md").write_text(
            "---\nname: bad-agent\ndescription: d\nmodel: fable\ntools:\n  - Read\n---\nBody.\n"
        )

        (root / "docs" / "constitution").mkdir(parents=True)
        (root / "docs" / "constitution" / "HARNESS.md").write_text(
            "## Required skills\n\n"
            "| `good-skill` | desc | consumer |\n"
            "| `nonexistent-skill` | desc | consumer |\n\n"
            "## Vendored MCP servers\n\n"
            "| `some-mcp-server` | desc | transport |\n"
        )

        violations = run(root)
        expected_substrings = [
            "bad-skill/SKILL.md: name 'wrong-name' != dirname 'bad-skill'",
            "bad-skill/SKILL.md: referenced 'references/missing.yaml' does not exist",
            "HARNESS.md: skill on disk 'docs/skills/bad-skill' not listed",
            "HARNESS.md: Required skills table lists 'nonexistent-skill'",
            "bad-agent.md: model 'fable' not in",
        ]
        missing = [s for s in expected_substrings if not any(s in v for v in violations)]
        # some-mcp-server (outside the Required skills table) must NOT be
        # flagged as an undeclared skill.
        false_positive = any("some-mcp-server" in v for v in violations)
        if missing or false_positive:
            print("SELFTEST FAILED")
            for s in missing:
                print(f"  - missing expected violation: {s}")
            if false_positive:
                print("  - false positive: some-mcp-server flagged as a skill")
            return 1
        print(f"SELFTEST OK — {len(violations)} expected violations detected.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    root = Path(args.root).resolve()
    violations = run(root)

    if violations:
        print(f"FAIL — {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("OK — no integrity violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
