---
name: k-role-party
description: >
  Grok Role Party — multi-issue orchestrator that runs the Hunter → Mage →
  Warrior/Archer party against open GitHub issues, prioritizes easy→hard, opens one PR
  per issue into main, and never fails silently. Use when operator says "k-role-party",
  "grok party", "role party", "hunt the backlog", or wants the Grok-native multi-issue orchestrator
  for the delivery cast. Slash: /k-role-party.
version: v0.1.0
---

# k-role-party — Grok Role Party Conductor

One **orchestrator** (this session). Many **issues**. Same cast as Claude's
`skills/k-triage-and-fix/` — Hunter, Falcon, Hound, Mage, Warrior, Archer,
Priest, Shadow, guardians, Bard — but the control plane is the Grok/agent main session,
not a single-shot JavaScript workflow script.

**Sibling (do not replace):** `skills/k-triage-and-fix/` is the single-issue delivery
engine. This skill is the multi-issue campaign orchestrator for the same
cast, with cross-issue queue ownership and collision prevention.

## Why this is used

| Dimension | Role Party Multi-Issue Orchestrator |
|---|---|
| Issue queue | **Orchestrator owns the queue** — prioritizes, serializes, and reorders mid-campaign |
| Inter-run collision | **File-set ∩ open-PR diffs** before every camp; shared surfaces are **serial-only** |
| Branch freshness | Rebase each hunt on latest `main`; if an open PR owns a needed file, **defer** that issue |
| Epic gating | **Epic gate in forest** — comments indicating epics → split/comment, never build |
| Blind review retry | **One rebuild retry** after shadow `needs-work` (hard cap 1), then bard |
| Failure reporting | Same retreat contract: comment + `blocked` + `Abandon-Reason:` — never silent failure |
| Scope boundaries | **Harness issues handled by hand, alone** — never through the automated party |

Reliability stems from: **model tier, tool grant, and closed contract schemas**.

## Run it

```
/k-role-party
# or: "run the role party on open issues"
# or: "k-role-party #12 #15"
```

## The Workflow Shape

```
orchestrator   queue sort · collision map · epic gate · serial plan
      ↓
forest         hunter ─┬─ falcon ──┐     spawn parallel
                       └─ hound ───┤
                          task ────┘     assembled by orchestrator
      ↓
tavern         domain routing → mage + familiars (mouse/owl/cat)
      ↓
camp           warrior ║ archer   (only non-empty slices; own worktrees)
               priest             secrets gate on combined diff
      ↓
stalking       shadow             zero-tools blind review
               [optional] one rebuild if needs-work
      ↓
tribunal       guardian:adr ║ prd   deny-by-default
      ↓
plaza          bard → PR | comment | new issue | retreat
```

## Per-Issue Protocol

### 0. Preflight (orchestrator)
```bash
gh auth status
git rev-parse --abbrev-ref HEAD
gh issue list --state open --limit 100 --json number,title,createdAt,labels
gh pr list --state open --json number,title,headRefName,files
```

### 1. Forest
Dispatch in parallel:
- `kwf-hunter` — issue inspection, size & difficulty rating.
- `kwf-falcon` — duplicate & regression check.
- `kwf-hound` — relevant codebase slice discovery.

### 2. Tavern
Dispatch `kwf-mage` with assembled context. Mage uses `kwf-mouse` to look up binding ADRs.

### 3. Camp
Spawn builder nodes (`kwf-warrior`, `kwf-archer`, etc.) in isolated worktrees:
`git worktree add ../kwf-<slice>-<issue> -b kwf/<issue>-<slice> origin/main`
Combine diffs, run `kwf-priest` for secrets check.

### 4. Stalking
Dispatch `kwf-shadow` for blind code review against combined diff.
- `holds` -> proceed to tribunal.
- `needs-work` -> maximum 1 rebuild retry.

### 5. Tribunal
Run guardians (`kbot-adr`, `kbot-prd`) with `python3 hooks/khook-guardian-dispatch --bundle`.

### 6. Plaza
`kwf-bard` opens PR targeting `main` with summary and links to issue.
