#!/usr/bin/env python3
"""Guardian dispatch + ADR review nudge (PostToolUse on Write|Edit).

One prose-only PostToolUse hook, formerly two (dispatch_guardians.py and
adr_reminder.py, merged for the nudge-dedup issue). It does two jobs in a
single output block:
  - maps every written file to the guardians watching it and nudges a
    dispatch to verify the change; the watchlist is DELEGATED to
    docs/hooks/guardian-dispatch, which reads it live from each guardian's
    own frontmatter `watch:` list — the single machine copy (adr-03-guardians
    rule 8). This hook carries no watchlist of its own;
  - names the ADR(s) to review when a governance-sensitive file is touched
    via RULES — wikilinks and a one-line "why review" only, never rule
    restatement (adr-00 rule 1).

This is the Claude-native safety net adr-03-guardians rule 3 describes; the
runtime-agnostic mechanism is docs/hooks/guardian-dispatch, callable by any
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
import sys
from pathlib import Path


def _load_guardian_dispatch(root):
    """Import docs/hooks/guardian-dispatch (no .py extension) as a module,
    so this hook reads the one live watchlist source instead of carrying a
    duplicate. Returns None if the script is missing — fail-open."""
    script = root / "docs" / "hooks" / "guardian-dispatch"
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
RULES = (
    (
        ("frontend/src/pages/*.astro", "frontend/src/pages/**/*.astro"),
        "Write",
        "New route: review [[adr-21-authorization-lobby]] (every route needing "
        "auth requires a Django session AND >=1 Django Group, except '/' the "
        "lobby — declare this route's gate), [[adr-08-frontend-and-design-system]] "
        "rule 9 (this file is a route/layout only — compose .svelte components, "
        "author no non-trivial markup), and [[adr-09-htmx]] (no shadow routes — "
        "any fragment route this page uses must be declared in [[API]] first).",
    ),
    (
        ("*/settings*.py",),
        None,
        "Backend settings touched: review [[adr-18-async-mandatory]] (stay "
        "ASGI/async-capable), [[adr-10-cache]] (every response carries an "
        "explicit Cache-Control), and [[adr-14-auth]] (Cognito is the only "
        "auth provider, RBAC stays in Django Groups).",
    ),
    (
        ("*/permissions.py",),
        None,
        "Permission classes touched: review [[adr-14-auth]] (RBAC is Django "
        "Groups only, never a Cognito claim) and [[adr-21-authorization-lobby]] "
        "(the lobby gate — session AND >=1 Group, except '/').",
    ),
    (
        ("compose.yaml",),
        None,
        "Compose file touched: review [[adr-13-docker-compose]] (reserved app "
        "paths, single root compose.yaml, profiles, no Redis).",
    ),
    (
        ("*/models.py",),
        None,
        "Models touched: review [[adr-21-authorization-lobby]] (AccessRequest.role "
        "-> Django Group only via the post_save signal) and [[adr-07-api-and-backend]] "
        "(a model change may invalidate the corresponding [[API]] / [[TDD]] entry).",
    ),
)


def project_dir():
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


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


def guardians_for(rel, root):
    """Reads the live watch: lists from docs/agents/*.md via the agnostic
    guardian-dispatch script — the single source (adr-03-guardians rule 8).
    Returns [] if the script cannot be loaded (fail-open, never blocks)."""
    module = _load_guardian_dispatch(root)
    if module is None:
        return []
    lists = module.watchlists(root / "docs" / "agents")
    hits = []
    for agent, patterns in lists.items():
        for pattern in patterns:
            if _matches_watchlist_entry(rel, pattern):
                hits.append(agent)
                break
    return hits


def matches_for(rel, tool_name):
    hits = []
    for index, (patterns, required_tool, text) in enumerate(RULES):
        if required_tool is not None and tool_name != required_tool:
            continue
        if any(fnmatch.fnmatch(rel, pattern) for pattern in patterns):
            hits.append((index, text))
    return hits


def session_id(payload):
    return payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or "nosession"


def seen_path(sid):
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


def main():
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        file_path = payload.get("tool_input", {}).get("file_path", "")
        if not file_path:
            return 0
        target = Path(file_path).resolve()
        root = project_dir().resolve()
        if not target.is_relative_to(root):
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
