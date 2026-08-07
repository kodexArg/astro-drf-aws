
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT / "docs" / "agents"
DISPATCH_HOOK = ROOT / ".claude" / "hooks" / "dispatch_guardians.py"
AGNOSTIC_SCRIPT = ROOT / "docs" / "hooks" / "guardian-dispatch"

# A guardian def is discovered by shape, never by a hardcoded project name
# (issue #130): its frontmatter `description:` names it a guardian.
GUARDIAN_MARKER = re.compile(r"\bguardian\b", re.IGNORECASE)
FRONTMATTER_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s?(.*)$")
# Sibling notify prose, e.g. "- **→ astro-drf-aws-adr** when ...".
NOTIFY_LINE = re.compile(r"^-\s+\*\*→\s*([A-Za-z0-9_-]+)\*\*", re.MULTILINE)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise AssertionError(msg)


def ok(msg: str) -> None:
    print(f"ok  {msg}")


def parse_frontmatter(text: str, label: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{label}: does not open with a '---' frontmatter fence")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        fail(f"{label}: frontmatter fence never closes")
    data: dict[str, str] = {}
    for line in lines[1:end]:
        m = FRONTMATTER_KEY.match(line)
        if m:
            key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
            if key == "watch":
                val = val or "yes"
            data.setdefault(key, val)
    return data


def discover_guardian_defs() -> dict[str, dict[str, str]]:
    """filename stem -> frontmatter, for every docs/agents/*.md whose
    frontmatter description names it a guardian. Generic: no literal
    project-specific guardian name is ever hardcoded here. Captures whether
    a `watch:` list is present so extract_watchlist_keys() need not re-glob
    and re-parse the same files (adr-03-guardians rule 8)."""
    found: dict[str, dict[str, str]] = {}
    for path in sorted(AGENTS_DIR.glob("*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"), path.name)
        if GUARDIAN_MARKER.search(fm.get("description", "")):
            found[path.stem] = fm
    return found


def extract_watchlist_keys(guardians: dict[str, dict[str, str]]) -> list[str]:
    """Reuses discover_guardian_defs()'s own parse, since it already
    captured `watch:` presence per file (adr-03-guardians rule 8) — no
    second glob/read of docs/agents/ or load of the agnostic script."""
    keys = [stem for stem, fm in guardians.items() if fm.get("watch")]
    if not keys:
        fail("no guardian definition carries a frontmatter watch: list")
    return keys


def test_dispatch_hook_has_no_own_watchlist() -> None:
    """dispatch_guardians.py must delegate to the agnostic script rather
    than carry a second, hand-kept watchlist dict (the retired two-place
    doctrine, formerly adr-03-guardians rule 5)."""
    text = DISPATCH_HOOK.read_text(encoding="utf-8")
    if "WATCHLISTS = {" in text or "WATCHLISTS: dict" in text:
        fail(
            f"{DISPATCH_HOOK.relative_to(ROOT)} still defines its own "
            "WATCHLISTS dict; it must delegate to "
            f"{AGNOSTIC_SCRIPT.relative_to(ROOT)} instead"
        )
    ok("dispatch_guardians.py carries no watchlist dict of its own")


def test_identity_triangle() -> None:
    guardians = discover_guardian_defs()
    if not guardians:
        fail(
            "no guardian definition found under docs/agents/*.md — the "
            "discovery rule (frontmatter description containing the word "
            "'guardian') is broken or the harness shipped with zero guardians"
        )

    watchlist_keys = extract_watchlist_keys(guardians)
    if len(watchlist_keys) != len(set(watchlist_keys)):
        fail(f"WATCHLISTS has duplicate keys: {watchlist_keys}")
    watchlist_set = set(watchlist_keys)

    stems = set(guardians)
    names = set()
    for stem, fm in guardians.items():
        name = fm.get("name")
        if not name:
            fail(f"docs/agents/{stem}.md: frontmatter has no name: field")
        names.add(name)
        if name != stem:
            fail(
                f"docs/agents/{stem}.md: filename stem {stem!r} != frontmatter "
                f"name {name!r}"
            )
        if name not in watchlist_set:
            fail(
                f"docs/agents/{stem}.md: name {name!r} has no frontmatter "
                f"watch: list ({AGNOSTIC_SCRIPT.relative_to(ROOT)}) — the "
                "dispatch hook will never nudge this guardian"
            )

    extra = watchlist_set - stems
    if extra:
        fail(
            "a frontmatter watch: list exists with no matching guardian def "
            f"under docs/agents/: {sorted(extra)} — the dispatch hook nudges a "
            "subagent_type that resolves to nothing"
        )

    if stems != names or stems != watchlist_set:
        fail(
            "guardian identity triangle mismatch: "
            f"filenames={sorted(stems)} names={sorted(names)} "
            f"watchlist_keys={sorted(watchlist_set)}"
        )

    ok(f"identity triangle (filename == name == WATCHLISTS key) for {sorted(stems)}")


def test_notify_prose_resolves() -> None:
    guardians = discover_guardian_defs()
    stems = set(guardians)
    checked = 0
    for stem in sorted(guardians):
        text = (AGENTS_DIR / f"{stem}.md").read_text(encoding="utf-8")
        for target in NOTIFY_LINE.findall(text):
            checked += 1
            if target == stem:
                fail(f"docs/agents/{stem}.md: notify prose lists itself ({target!r})")
            if target not in stems:
                fail(
                    f"docs/agents/{stem}.md: notify prose references {target!r}, "
                    "which is not an existing guardian filename/frontmatter name"
                )
    if checked == 0:
        fail(
            "no '- **→ <name>**' notify reference found across guardian "
            "defs — the notify-prose convention may have changed; update "
            "NOTIFY_LINE"
        )
    ok(f"{checked} cross-guardian notify reference(s) resolve to real guardian defs")


def main() -> int:
    tests = [
        test_identity_triangle,
        test_notify_prose_resolves,
        test_dispatch_hook_has_no_own_watchlist,
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
