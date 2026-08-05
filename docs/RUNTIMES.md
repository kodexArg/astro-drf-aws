---
title: RUNTIMES
type: reference
status: active
created: 2026-08-04
tags: [harness, agents, runtimes, triage-and-fix, kwf]
---

# RUNTIMES — multi-runtime adapter for the agent cast

This is the template's answer to being agent-agnostic: the same cast under
`docs/agents/` (guardians, `orch-*`, `wf-*`, `kwf-*`) and the same
`docs/skills/triage-and-fix/` playbook must be reachable from whichever
runtime is driving the repo. Force: [[adr-02-harness]], [[adr-04-issue-delivery]].
Node contracts, phases, and tiers are owned by
`docs/skills/triage-and-fix/references/cast.md`; this file owns only *how a
runtime discovers and dispatches a node*.

The invariant across every runtime: **the main agent is the script.** `SKILL.md`
is the procedure; a runtime's native workflow/task mechanism is optional sugar
around it, never a requirement. Only two things change per runtime — the
dispatch mechanism and the model-tier string passed at dispatch.

## Claude Code (this repo's primary runtime)

**Native, via symlink.** `.claude/agents` → `../docs/agents` and
`.agents/agents` → `../docs/agents` are already live in this repo (verified:
`ls -la .claude/agents`). Every `kwf-*`, `wf-*`, `orch-*`, and guardian file
under `docs/agents/` resolves as a Claude subagent type with no extra wiring.
A session started before an agent file was added will not resolve it — start
a fresh session after installing/editing the cast.

- **Dispatch:** the `Agent`/`Task` tool with `subagent_type: kwf-<name>` (or
  `wf-<name>`, `orch-<name>`, `astro-drf-aws-<guardian>`). Forest/camp nodes
  fan out in parallel in one message when the plan allows it.
- **Two coexisting renderings of issue delivery** ([[adr-04-issue-delivery]]):
  - `docs/skills/kdx-wf-triage-and-fix` — the deterministic Claude `Workflow`
    script driving the pre-existing `wf-*` cast (12 agents). This is the
    **Claude-runtime rendering**: schema-enforced structured output, a real
    Workflow runtime.
  - `docs/skills/triage-and-fix` (this vendoring) — the canonical,
    runtime-agnostic `kwf-*` cast (18 agents) + playbook. On Claude Code it
    runs the same way any host without a native `Workflow` primitive would:
    the main agent reads `SKILL.md` and executes it phase by phase via
    `Agent`/`Task` dispatch, branching on the YAML contract each node returns.
  Both are valid; neither supersedes the other. A session chooses one cast
  for a given issue and does not mix nodes from the two across a single run.
- **Tools:** grant `WebFetch` where the canonical `kwf-*` files (upstream,
  Kimi-authored) say `FetchURL` — this repo's `kwf-owl.md` and `kwf-cat.md`
  already carry `tools: [WebSearch, WebFetch]`, adapted at vendoring time.
  `Agent` is this runtime's spawn tool (Kimi's is also named `Agent` but
  resolves to a different registry).
- **Model tiers** — Claude Code has no `k3-256k`/`kimi-for-coding` strings;
  map tier *intent* (see `references/cast.md`) to Claude model classes:

  | Tier intent | Claude model class |
  |---|---|
  | cheap / low | Haiku-class (`orch-low` precedent) |
  | mid | Sonnet-class |
  | high | Sonnet-class (camp builders, bard) |
  | heavy | Sonnet or Opus (mage, inquisitor, elf-mage, paladin) |

  No `model_preference: secondary` fallback exists on this runtime (that
  field is Kimi's `[secondary_model]` config lever) — a `kwf-*` file that
  still carries `model_preference: secondary` is inert here, harmlessly; the
  dispatcher just picks the heavy Claude class directly.

## Kimi Code CLI

**Native**, and the runtime this cast was authored against. `docs/agents/`
resolves when it is on `extra_agent_dirs` in `~/.kimi-code/config.toml`
(pointed at this project's clone path, never a sibling repo). The skill
resolves via a symlink `docs/skills/triage-and-fix` → `~/.kimi-code/skills/triage-and-fix`.

- **Dispatch:** `Agent` with `subagent_type: kwf-<name>`, forest/camp fanned
  out in parallel in one message.
- **Model pins** (explicit at the dispatch call):

  | Tier | Model pin |
  |---|---|
  | cheap / low | `kimi-code/kimi-for-coding` |
  | mid | `kimi-code/kimi-for-coding-highspeed` |
  | heavy | `kimi-code/k3-256k` |
  | high | inherit caller (or highspeed when upgrading) |

- **Fallback:** mage / elf-mage / paladin's `model_preference: secondary`
  binds to `kimi-code/k3-256k` when the `Agent` call omits `model` — this is
  the one field in the vendored `kwf-*` files that is genuinely Kimi-specific
  and has no Claude Code equivalent; it stays as-is and is simply inert on
  other runtimes.
- **Tools:** `FetchURL` (not `WebFetch`), `WebSearch`. If this repo is ever
  driven from Kimi Code, `kwf-owl.md`/`kwf-cat.md`'s `tools:` line must be
  read back to `[WebSearch, FetchURL]` for that session — the vendored copy
  here is pinned to Claude's `WebFetch` because Claude Code is this
  template's primary runtime ([[adr-02-harness]]).

## Cursor / Grok

**No native `kwf-*`/`wf-*` registry.** Cursor's `Task` subagent types are a
fixed enum; there is no per-project agent directory to point at. The main
agent still *is the script*: for each node, `Read` the corresponding
`docs/agents/kwf-<name>.md` (or `wf-<name>.md`), then dispatch `Task` with a
mapped built-in worker and a prompt that **inlines that file's full content**
plus the phase handoff, requiring the same YAML output contract as the final
message.

| Tier intent | Cursor `subagent_type` |
|---|---|
| cheap / low | `orch-low` (read-only scouts/familiars/priest/shadow) |
| mid | `orch-medium` |
| high | `orch-medium` or `generalPurpose` (builders that write) |
| heavy | `orch-high` or `generalPurpose` (mage, inquisitor, elf-mage, paladin) |

- A builder that must edit files uses a write-capable worker
  (`orch-medium`/`generalPurpose`) — never `orch-low`.
- `priest` and `shadow` stay tool-free in the prompt even when the mapped
  worker technically has tools available: instruct explicitly "tools: none;
  judge only" so the zero-tool contract these two nodes are built on is
  honored even without a frontmatter `tools: []` the host can enforce.
- Parallelism: fan out forest (hunter+falcon+hound) and camp slices as
  parallel `Task` calls in one turn where the host supports it.
- Doctrine loop: `resume` the same planner `Task` when the host supports
  session resume; otherwise re-dispatch a fresh `Task` with the full prior
  plan + inquisitor findings inlined (worse fidelity, but legal per
  `cast.md`'s shared invariants).
- Grok on this same host follows the identical Cursor adapter above. Prefer
  the heaviest available class for mage/inquisitor when the host exposes one.

This is the one runtime where the answer is genuinely partial, stated
honestly rather than oversold: without a native per-project agent registry,
every dispatch pays an inlining cost and loses whatever native
structured-output enforcement Claude's `Workflow` or Kimi's frontmatter
parsing gives for free. The playbook and contracts are unchanged; only the
ceremony around each dispatch grows.

## Souls (voice, not law)

Every `kwf-*` (and guardian) agent may declare `soul: docs/agents/souls/<name>.md`
([[adr-02-harness]]). On a host that loads agent frontmatter natively (Claude
Code, Kimi Code CLI), the `soul:` field is read the same way any other
frontmatter field is. On a host with no native frontmatter parsing
(Cursor/Grok, per the adapter above), **prepend the soul file's content** to
the node's inlined prompt by hand. Either way the soul is voice only — the
YAML contract and the law links (`## Law (read before acting)`) in the agent
file itself always win over anything the soul's prose might suggest.

## Shared invariants (all runtimes)

1. YAML final-message contracts travel between phases — never a prose
   handoff.
2. A dead node or a broken/garbage contract aborts that phase
   (`hunter-failed`, `plan-failed`, `build-failed`, `gate-failed`,
   `review-failed`, `doctrine-failed`, `publish-failed`).
3. Builders create their own git worktree as their first act, on their own
   branch; the bard merges path-disjoint slices.
4. Post-bard, on every runtime: `python3 docs/hooks/guardian-dispatch --bundle <baseRef>`
   (bundle pasted into each owed guardian's prompt, cheap tier, parallel
   dispatch) + `docs/skills/assertion-review/SKILL.md` whenever the combined
   diff touches `docs/assertions/**`.
5. `bin/kwf-deps` always runs from repo root as
   `docs/skills/triage-and-fix/bin/kwf-deps` — a `python3` stdlib CLI, no
   per-runtime variant.

## Guardians (all runtimes)

| Intent | Pin |
|---|---|
| cheap (default) | Kimi `kimi-for-coding` · Claude Haiku-class · Cursor `orch-low` or native `astro-drf-aws-*` guardian with the cheapest model available |
| escalate | mid/high only when triage cannot return the one-line pass ([[adr-03-guardians]] rule 8) |

The owner process always runs `python3 docs/hooks/guardian-dispatch --bundle …`
and inlines that stdout into the guardian prompt before spawn on every
runtime — never let a guardian rediscover the batch itself.

## Related

- [[adr-02-harness]] — tooling under law; the vendoring discipline this doc
  extends to a cross-runtime concern.
- [[adr-04-issue-delivery]] — the cast+playbook as canonical, this file as
  its runtime-dispatch complement, the Workflow script as the Claude
  rendering.
- `docs/skills/triage-and-fix/references/cast.md` — node contracts, phases,
  tiers (the thing this file dispatches).
- `docs/skills/triage-and-fix/references/deps.md` — the `requires:<N>` /
  `deferred` REQUIREMENT system, runtime-agnostic.
- `docs/constitution/HARNESS.md` — the vendored-skill inventory this
  addition needs a follow-up row in (out of scope here; reported to the
  owner process).
