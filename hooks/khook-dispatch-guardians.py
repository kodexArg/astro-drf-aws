#!/usr/bin/env python3
"""Guardian dispatch + ADR review nudge (PostToolUse on Write|Edit).

One prose-only PostToolUse hook, formerly two (dispatch_guardians.py and
adr_reminder.py, merged for the nudge-dedup issue). It does two jobs in a
single output block:
  - maps every written file to the guardians watching it and nudges a
    dispatch to verify the change; the watchlist is DELEGATED to
    hooks/khook-guardian-dispatch, which reads it live from each guardian's
    own frontmatter `watch:` list — the single machine copy (adr-27-guardians-and-delivery).
    This hook carries no watchlist of its own;
  - names the ADR(s) to review when a governance-sensitive file is touched
    via RULES — wikilinks and a one-line "why review" only, never rule
    restatement (adr-00 rule 1).

This is the Claude-native safety net adr-27-guardians-and-delivery describes; the
runtime-agnostic mechanism is hooks/khook-guardian-dispatch, callable by any
harness or a human with no Claude dependency.

Both jobs dedupe per session-scoped batch: each guardian/ADR is named once
per session, not once per file, via a gitignored seen-set at
$CLAUDE_PROJECT_DIR/.claude/.nudge-seen-<session_id>. Any internal error
exits 0; always exits 0 — this hook never blocks (fail-open).
"""

import fnmatch
import importlib.machinery
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path



def _load_guardian_dispatch(root):
    """Import hooks/khook-guardian-dispatch (no .py extension) as a module,
    so this hook reads the one live watchlist source instead of carrying a
    duplicate. Returns None if the script is missing — fail-open."""
    script = root / "hooks" / "khook-guardian-dispatch"
    if not script.is_file():
        return None

    try:
        loader = importlib.machinery.SourceFileLoader("guardian_dispatch_agnostic", str(script))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        return module
    except Exception:
        return None


# (globs, required tool_name or None for any, reminder text)
#
# EMPTY IN THE TEMPLATE ON PURPOSE. This table is the ADR-review nudge, and a
# nudge may only name ADRs that actually exist in this clone — a wikilink to an
# ADR the project never wrote is invented law ([[adr-25-harness-layout]] rule 2), and a
# gate with no governing ADR to point at is incomplete (same ADR, rule 3). The
# harness ships adr-00..adr-04 (discipline, constitution, harness, guardians,
# delivery); none of them govern a code path by glob, so there is nothing
# honest to nudge yet.
#
# Each clone fills this in as it writes its own ADRs. One entry per governed
# surface, wikilinks + a one-line "why review" only — never a restatement of
# the rule ([[adr-00-adr-doctrine]] rule 1). Example shape for a project that has
# written an API ADR:
#
#   (
#       ("*/models.py",),
#       None,
#       "Models touched: review [[adr-07-api-and-backend]] (a model change may "
#       "invalidate the corresponding [[API]] / [[TDD]] entry).",
#   ),
#
# The guardian-dispatch half of this hook needs no configuration — it reads
# every watchlist live from each agent's `watch:` frontmatter.
RULES = ()


def project_dir() -> Path:
    for var in ("ANTIGRAVITY_PROJECT_DIR", "CLAUDE_PROJECT_DIR", "PROJECT_ROOT"):
        val = os.environ.get(var)
        if val and Path(val).is_dir():
            return Path(val)
    try:
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if git_root:
            return Path(git_root)
    except Exception:
        pass
    return Path(__file__).resolve().parents[1]


def _matches_watchlist_entry(rel, pattern):
    if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(rel, pattern.rstrip("*") + "*"):
        return True
    # Basename fallback: an exact (non-glob) "docs/<name>.md" entry also
    # matches that same basename anywhere under docs/ (e.g. a doctrine doc
    # relocated to docs/constitution/) so a future doc move degrades safely
    # instead of silently no-op'ing this watch.
    if pattern.startswith("docs/") and "*" not in pattern:
        rel_path = Path(rel)
        if rel_path.parts and rel_path.parts[0] == "docs" and rel_path.name == Path(pattern).name:
            return True
    return False


def guardians_for(rel: str, root: Path) -> list[str]:
    """Reads the live watchlists via the agnostic guardian-dispatch script.
    Filters to guardian roles (kbot-prd, kbot-adr)."""
    module = _load_guardian_dispatch(root)
    if module is None:
        return []
    lists = module.watchlists(root)
    hits = []
    for agent, patterns in lists.items():
        # Only guardian agents gate document/ADR health
        if agent not in {"kbot-prd", "kbot-adr", "kbot-bdd", "kbot-api"}:
            continue
        for pattern in patterns:
            if _matches_watchlist_entry(rel, pattern):
                hits.append(agent)
                break
    return hits


def matches_for(rel: str, tool_name: str) -> list[tuple[int, str]]:
    hits = []
    for index, (patterns, required_tool, text) in enumerate(RULES):
        if required_tool is not None and tool_name != required_tool:
            continue
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            hits.append((index, text))
    return hits


def session_id(payload: dict) -> str:
    raw = payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or "nosession"
    # Sanitize session id to prevent path traversal
    return re.sub(r"[^a-zA-Z0-9_-]", "", str(raw)) or "nosession"


def seen_path(sid: str) -> Path:
    return project_dir() / ".claude" / (".nudge-seen-" + sid)



def load_seen(path):
    if path.is_file():
        return set(path.read_text(encoding="utf-8").splitlines())
    return set()


def persist_seen(path, keys):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for key in keys:
            handle.write(key + "\n")


COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"


def current_branch(root: Path) -> str:
    override = os.environ.get("HARNESS_GIT_BRANCH", "").strip()
    if override:
        return override
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except Exception:
        return ""


def main():
    if sys.stdin.isatty():
        return 0
    try:
        content = sys.stdin.read().strip()
        if not content:
            return 0
        payload = json.loads(content)
        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {}) or {}
        file_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("TargetFile") or ""

        if not file_path:
            return 0

        target = Path(file_path).resolve()
        root = project_dir().resolve()
        if not target.is_relative_to(root):
            return 0

        branch = current_branch(root)
        if branch != "main" and os.environ.get("HARNESS_DISPATCH_MAIN_ONLY", "").strip() == "1":
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": f"{COLOR_RED}[HARNESS BYPASS] khook-dispatch-guardians: bypass active because current branch '{branch}' no es 'main'.{COLOR_RESET}",
                }
            }))
            return 0

        rel = target.relative_to(root).as_posix()

        sid = session_id(payload)
        path = seen_path(sid)
        seen = load_seen(path)

        new_keys = []
        new_guardians = []
        for name in guardians_for(rel, root):
            key = "guardian:" + name
            if key not in seen:
                new_keys.append(key)
                new_guardians.append(name)

        new_adr_texts = []
        for index, text in matches_for(rel, tool_name):
            key = "adr:" + str(index)
            if key not in seen:
                new_keys.append(key)
                new_adr_texts.append(text)

        if not new_keys:
            return 0

        parts = []
        if new_guardians:
            names = ", ".join(new_guardians)
            parts.append(
                f"Guardian watch: '{rel}' is watched by {names}. When this "
                "batch of edits is complete, dispatch each via the Agent tool "
                "(subagent_type = the guardian name) to verify the change; each "
                "returns status/resolution plus which sibling guardians must be "
                "informed — honor that notify list. One dispatch per guardian "
                "per batch is enough. If you ARE a guardian agent, ignore this "
                "nudge entirely."
            )
        if new_adr_texts:
            parts.append(
                f"ADR review reminder for '{rel}': " + " ".join(new_adr_texts) +
                " Review before closing this batch of edits."
            )

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": " ".join(parts),
            }
        }))
        persist_seen(path, new_keys)
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
