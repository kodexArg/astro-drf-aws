#!/usr/bin/env python3
"""Validates the Agent Definition Contract defined in adr-26-agent-contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / "agents"
ADRS = ROOT / "adrs"
CHANGELOG = ROOT / "CHANGELOG.md"

REQUIRED_KEYS = ("name", "description", "model", "tools", "related_adrs", "version")
COSMETIC_KEYS = ("color",)
SANCTIONED_MODELS = ("inherit",)
DESCRIPTION_MIN_WORDS = 25
DESCRIPTION_MAX_WORDS = 60
QUICK_EXIT = re.compile(r"quick[ -]?exit", re.IGNORECASE)


def split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def top_level_keys(fm: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", fm, re.MULTILINE)]


def scalar(fm: str, key: str) -> str | None:
    match = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.MULTILINE)
    return match.group(1).strip() if match else None


def sequence(fm: str, key: str) -> list[str]:
    inline = scalar(fm, key)
    if inline is None:
        return []
    inline = inline.strip()
    if inline.startswith("["):
        return [i.strip().strip("\"'") for i in inline[1:-1].split(",") if i.strip()]
    if inline:
        return [i.strip().strip("\"'") for i in inline.split(",") if i.strip()]
    items = []
    tail = fm[fm.index(f"\n{key}:") + 1 :] if f"\n{key}:" in fm else fm
    for line in tail.splitlines()[1:]:
        if re.match(r"^\s*-\s+", line):
            items.append(line.split("-", 1)[1].strip().strip("\"'"))
        elif line.strip() and not line.startswith((" ", "\t")):
            break
    return items


def get_expected_version() -> str:
    if CHANGELOG.is_file():
        m = re.search(r"^version:[ \t]*(.*)$", CHANGELOG.read_text(encoding="utf-8"), re.MULTILINE)
        if m and m.group(1).strip().strip("\"'"):
            return m.group(1).strip().strip("\"'")
    return "v0.1.0"


def test_agent_contracts_and_bidirectional_symmetry():
    failures = []
    if not AGENTS.is_dir() or not any(AGENTS.glob("*.md")):
        return  # Agents will be moved and validated

    adr_slugs = {p.stem for p in ADRS.glob("adr-*.md")}
    agent_edges = {}
    expected_version = get_expected_version()

    for path in sorted(AGENTS.glob("*.md")):
        rel = path.relative_to(ROOT)
        fm, body = split_frontmatter(path.read_text(encoding="utf-8"))
        if not fm:
            failures.append(f"{rel}: missing frontmatter")
            continue

        keys = top_level_keys(fm)
        for req in REQUIRED_KEYS:
            if req not in keys:
                failures.append(f"{rel}: missing key `{req}`")

        name = scalar(fm, "name")
        if name != path.stem:
            failures.append(f"{rel}: name `{name}` != filename `{path.stem}`")

        tools = sequence(fm, "tools")
        if not tools:
            failures.append(f"{rel}: empty tools sequence")

        desc = scalar(fm, "description") or ""
        words = len(desc.split())
        if not (DESCRIPTION_MIN_WORDS <= words <= DESCRIPTION_MAX_WORDS):
            failures.append(f"{rel}: description word count {words} outside {DESCRIPTION_MIN_WORDS}..{DESCRIPTION_MAX_WORDS}")

        if not QUICK_EXIT.search(body):
            failures.append(f"{rel}: missing Quick exit declaration in body")

        version = scalar(fm, "version")
        if version != expected_version:
            failures.append(f"{rel}: version `{version}` != expected `{expected_version}`")

        declared_adrs = set(sequence(fm, "related_adrs"))
        for slug in declared_adrs:
            if slug not in adr_slugs:
                failures.append(f"{rel}: related_adrs names unknown `{slug}`")
        agent_edges[path.stem] = declared_adrs

    adr_edges = {}
    for path in sorted(ADRS.glob("adr-*.md")):
        fm, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        declared_agents = set(sequence(fm, "related_agents"))
        adr_edges[path.stem] = declared_agents

    for agent, adrs in agent_edges.items():
        for adr in adrs:
            if adr in adr_edges and agent not in adr_edges[adr]:
                failures.append(f"one-sided edge: {agent} -> {adr} missing reverse in {adr}")

    for adr, agents in adr_edges.items():
        for agent in agents:
            if agent in agent_edges and adr not in agent_edges[agent]:
                failures.append(f"one-sided edge: {adr} -> {agent} missing reverse in {agent}")

    assert not failures, "\n".join(failures)


if __name__ == "__main__":
    test_agent_contracts_and_bidirectional_symmetry()
    print("ok  agent contracts and symmetry valid")
