---
title: CHATBOT
type: reference
status: active
created: 2026-07-14
tags: [harness, chatbot, router, assistant, ai, security]
---

# CHATBOT

The template's conversational surface and the architecture behind it. Ruled by [[adr-17-chatbot-two-tier]] and, for the assistant surface, [[adr-25-page-context-assistant]]. This file **owns the content**; the ADRs state only the rules and link here.

> [!note] Naming — settled
> `chatui`, `router`, the endpoint segment `route` (`/api/router/route/`), the models `Intent` and `IntentQuery`, the reserved outcomes `NO_MATCH`/`ESCALATE`, the action field `kind`, and the env stem `ROUTER_*` are all registered in [[GLOSSARY]] ([[adr-05-glossary-and-localisation]]).

## The one-line split

> [!important]
> **The tier that chooses never generates. The tier that generates never chooses.**
> Choosing carries actuator rights and emits nothing but a member of a closed enum. Generating emits free text and is read-only, forever. The two capabilities are disjoint, permanently — this is the architecture, not a phase.

## What ships in this template — the router (the choosing tier)

A chat-like UI — `chatui` — where the user types free text into a box and gets a result. **It feels like a chatbot. It is not one.** There is no conversation, no memory, no prose coming back from a model. What sits behind the box is a **router**.

The router:

1. Takes the utterance.
2. Builds the menu **server-side in Django**, filtered by the requesting user's permissions (Django Groups + DRF permission classes, [[adr-14-auth]]) — before the model sees anything.
3. Calls **Amazon Nova Micro on Bedrock** (us-east-1) with a **JSON-Schema-constrained** request whose only free variable is an `enum` field, at **temperature 0**.
4. Gets back exactly one member of that enum. Nothing else is a valid response.
5. Maps that member to a preconfigured link, site action, or `GET` view and executes it.

**Zero free-text generation happens anywhere in the choosing tier.** The router never writes a sentence a user reads.

The shipped menu is a **closed, permission-filtered menu** built from a growable registry the owner authors — it is not a fixed, hardcoded list, and no specific option count is part of the design. Two reserved members are always present regardless of registry size: `NO_MATCH` (understood, but nothing on the menu answers it) and `ESCALATE` (below); every other member maps 1:1 to a link/action or an already-declared `GET` endpoint ([[API]]). Menus stay small on purpose, because a small closed menu is what makes the security argument below hold cheaply.

**A response outside the enum is a hard reject** — logged as a fault, never repaired, never defaulted to a nearest match, never retried into one. Silent repair would reintroduce exactly the ambiguity the enum exists to delete. Every decision, including rejects and escalations, persists an audit row (see Retention below).

**The router's build stops here.** The router-mediated generating path below is *made possible* by this design; it is not built, not designed in detail, and not scheduled. A **direct** user → generating-tier channel is a separate, recorded decision — the page-context assistant, further down ([[adr-25-page-context-assistant]]) — and it changes no line of the router's contract.

### Local development calls Bedrock directly

A developer runs the router **from their own machine against Bedrock**, with their own IAM credentials, region us-east-1. That is the local path: no emulator, no local model server, no offline stand-in required to exercise the real pipeline.

> [!note] The VPC interface endpoint is a *cloud* requirement, not a local blocker
> The `com.amazonaws.us-east-1.bedrock-runtime` interface endpoint exists because **Fargate runs in a private subnet with no NAT gateway** ([[INFRASTRUCTURE]]) and therefore cannot otherwise reach Bedrock. That is a deployment concern and belongs to the cloud phase alone. A laptop reaches Bedrock over the public internet like any other AWS API call. Any document or plan that presents the interface endpoint as a prerequisite for building or testing the router is wrong.

### AccessDenied from Bedrock has TWO root causes — triage before touching IAM

An `AccessDeniedException` on the router's Bedrock call reads identically for two unrelated problems:

1. **IAM** — the caller (task role in cloud, your credentials locally) lacks `bedrock:InvokeModel` on the model **and** its inference profile. The grant shape lives in [[INFRASTRUCTURE]] (Bedrock inference grant).
2. **Model access** — the account/region toggle for the model was never enabled in the Bedrock console. No IAM policy fixes this.

Distinguish in one command: `aws bedrock get-foundation-model-availability --model-id amazon.nova-micro-v1:0` — `authorizationStatus: AUTHORIZED` + `entitlementAvailability: AVAILABLE` means model access is fine and the problem is IAM; anything else means enable model access first (Bedrock console → Model access). Also remember the model id is the **inference profile** form `us.amazon.nova-micro-v1:0` ([[VARIABLES]] `ROUTER_BEDROCK_MODEL_ID`) — the bare `amazon.nova-micro-v1:0` id is not on-demand invokable and fails with a `ValidationException`, a third error that is neither of the above.

## The generating tier reached *through* the router — a security filter (not built)

This design only **makes it possible**. Nothing of this router-mediated path is designed, planned, or shipped by this repo. The one generating-tier surface this template has decided on is the **direct** channel recorded below, which does not travel through the router at all — and therefore inherits none of the containment this section describes.

When it arrives, a **second, smarter model — deliberately unnamed, TBD** — is added behind the router to do the generating the router refuses to do. The router does not step aside for it. The router becomes the **filter it must pass through**.

**The router never forwards the user's raw text.** It forwards a **reinterpreted prompt**: its own restatement of what the user meant. The smart model never sees attacker-controlled bytes verbatim. This is the whole point of the arrangement, and it only works because of the next section.

### The crux — the reinterpretation is structured, never free prose

The router's restatement is **not** a sentence the router writes. It is a **slot-filled template**:

- The **template** is chosen from a **closed, hand-authored set**, one per enum member. The prose is ours, held in code, written by us, reviewed by us. The model picks *which*, never *what*.
- The **slots** are a fixed, declared list per template. Each slot has a **type and a validator**: an enum, an integer, a date, a primary key that must resolve to a row this user is already allowed to read. A slot that fails validation fails the request; it is not coerced.
- What reaches the smart model is therefore **a sentence we wrote, parameterized by values that passed our validators**.

**Why free prose would break it, mechanically.** If the router were allowed to emit a free-text restatement, then:

1. **The router would be *generating*** — and the invariant above (the choosing tier never generates) is violated at the very first extension. The design would have eaten itself.
2. **The channel reopens.** Containment here comes from **channel capacity**, not from a model's good behaviour. An enum of *n* members plus *k* typed slots carries a bounded, enumerable, auditable number of bits — you can list every prompt the smart model can ever receive. A free-prose restatement carries as many bits as the attacker cares to spend. A model told to "restate faithfully" will faithfully carry a payload; faithfulness is precisely the property the attacker is counting on.

The security property is **the re-encoding through a narrow, typed bottleneck**. An injection payload is instructions expressed in bytes; it does not survive being reduced to *"member 3 of 5, with `date=2026-07-14`"* and then re-expanded from a template we authored. Nothing of the attacker's phrasing is left to survive.

This is a claim about the *mechanism*, and it is the only form in which the claim is true. "The router sanitizes the prompt" is not the property; **"the router re-encodes intent through a bottleneck too narrow to carry an instruction"** is.

### The honest limit — this is containment, not a proof

> [!warning] Bound the claim; do not oversell it
> This is a **strong containment**, not a proof of impossibility.

- **Any slot that carries user-derived free text is a residual channel**, in exact proportion to its width. A `search_query` slot typed as an arbitrary string hands the attacker a pipe to the smart model, and calling it a "parameter" changes nothing about that.
- Therefore: **no free-text slot ships without being an explicit, recorded decision in this file.** Where one is genuinely unavoidable, it is length-bounded, character-class-restricted, interpolated strictly as *data* (delimited, and named as data in the downstream instructions), and never placed where the downstream model would read it as instruction.
- Those are **mitigations**. They shrink the channel; they do not close it. A doc that promises a closed channel while shipping a free-text slot is worse than no doc at all.
- The routing model itself is still a model: it can be *confused* into picking the wrong menu member. What it **cannot** do is pick something that is not on the menu, and the menu was already filtered to what this user could have done by hand. **The worst outcome of a successful injection against the router is that the user gets an action they were already authorized to perform.** That is a bounded blast radius, and it is bounded by Django's authorization, not by the model's judgment.

## The permanent invariant

This is the spine of [[adr-17-chatbot-two-tier]] and the reason the enum-constrained tier is built first:

| Tier | Emits | Rights |
|---|---|---|
| **Choosing** (the router) | Exactly one member of a closed, permission-filtered enum. Never text. | **Actuator rights** — its output can flip a switch, navigate, trigger an action. |
| **Generating** (the assistant today; any router-mediated path TBD) | Free-form natural language. | **Read-only, forever.** Never flips a switch. |

If the generating tier wants an action, it does not take one. It **re-enters through the router** with a closed menu and is subject to the same filtering, the same enum, the same hard reject, and the same audit row as a human utterance. There is no privileged back door for the model that talks.

**Disjoint capabilities, permanently.** Not a transitional arrangement, not a stage-1 shortcut to be relaxed once the smart model proves trustworthy. A component that generates text must never hold actuator rights; a component that holds actuator rights must never emit unconstrained text. Every future extension is measured against this line.

### The four outcomes — Action, Answer, Escalate, NO_MATCH

Every routed utterance resolves to exactly one of four outcome kinds — **`NO_MATCH` is a distinct fourth outcome, never collapsed into `ESCALATE` or treated as an edge case of the others**:

1. **Action** — a concrete site action or navigation target is triggered.
2. **Answer** — the utterance is really a question an already-declared `GET` endpoint answers.
3. **Escalate** — the utterance needs real reasoning the closed menu cannot serve; the reserved `ESCALATE` member is selected.
4. **NO_MATCH** — the utterance was understood, but no registry entry answers it; the reserved `NO_MATCH` member is selected. This is a real, distinct answer ("nothing exists for that"), not a failure mode of `ESCALATE` ("this needs reasoning we don't have yet").

### The escalation seam

`ESCALATE` is the **single, stable handoff point** between the tiers, and it ships with the router — not later. `NO_MATCH` is a sibling reserved member with a different meaning (above) and is never used as a stand-in for it.

- **Today:** selecting `ESCALATE` returns a fixed "not supported yet" response. Nothing generative runs behind it.
- **When the router-mediated generating tier arrives:** it plugs in **exactly here**, receiving the structured reinterpretation described above. The choosing tier's contract does not change to accommodate it.

Shipping the seam dead, from day one, is what keeps the generating tier from ever becoming a rewrite.

## The page-context assistant — the direct channel

> [!important] The decision
> A **direct user → generating-tier channel** is authorized: the page-context assistant. It bypasses the router entirely. Its force is [[adr-25-page-context-assistant]], which lifts [[adr-17-chatbot-two-tier]]'s rule-9 stop for exactly this surface, adds to that ADR, and supersedes none of its rules.

Until this decision, this document described the generating tier as reachable **only** through the router's structured reinterpretation. It is now reachable two ways, and they are different objects: the router-mediated path above is still unbuilt and undesigned, while this one is decided, bounded, and entered through [[API]] as `POST /api/assistant/ask/`.

**This is a second free-text channel, and it is stated as one.** The bottleneck argument above — an enum plus typed slots too narrow to carry an instruction — does **not** apply here: the user's utterance reaches the generating model as text. What bounds this surface is not channel capacity; it is that the tier receiving the text can do nothing but write words back, under an authorization decided in Django before it runs (`CanUseAssistant`, [[API]]). Anyone reading this section as "the assistant is contained the way the router is contained" has read it wrong, and the honest limit below is the whole of the claim.

### The v1 bounds

- **Read-only, forever.** No actuator rights, no `confirm`, no write, no mutating endpoint — [[adr-17-chatbot-two-tier]] rule 1 unchanged. An action the assistant wants re-enters through the router (rule 4); v1 emits no action at all.
- **Server-assembled, group-filtered context.** The request carries a **page identity** — a member of the closed nav registry — plus the params the page itself used; never page text, never DOM scrape, never client-shipped content. The backend recomputes that page's data through the same layer the page's declared `GET` endpoints use, under the caller's Django Groups. A page whose backing endpoint the caller may not read yields **no context**, not an error, and never a figure the caller could not have fetched by hand ([[adr-14-auth]], [[adr-25-page-context-assistant]] rule 3).
- **Structured, registry-validated links.** Link suggestions travel in their own constrained field and each `target` is validated server-side against the nav registry; anything outside it is dropped. The prose may name a view; only the validated array renders as an anchor. The frontend renders the answer as text nodes — no HTML, no Markdown interpretation, no link minted from prose ([[adr-25-page-context-assistant]] rule 4).
- **Kill switch.** `ASSISTANT_ENABLED=false` short-circuits to a fixed `disabled` outcome with zero inference calls, exactly as `ROUTER_ENABLED` does for the router ([[VARIABLES]]).
- **Abuse guard, reused.** The router's per-user cooldown and its silent rate block are reused rather than reimplemented; both return `429`, indistinguishable to the caller.
- **Bounded audit retention, mirroring the router's.** Every ask persists an `AssistantQuery` audit row under a bounded-window policy of the same shape as `IntentQuery`'s (Retention, below): `ASSISTANT_AUDIT_RETENTION_DAYS` bounds the window, `purge_assistant_audit` deletes past it ([[VARIABLES]]). No conversation memory exists beyond those rows.
- **Rendered copy, localizable.** The answer reaches the screen, so it is rendered output localizable through the i18n layer like any user-facing string; prompt scaffolding identifiers, keys, and every other non-rendered string stay English ([[LOCALISATION]], [[adr-25-page-context-assistant]] rule 5).

### View-first context — the agnostic principle

**The content of the user's current view is the first context any AI answer draws on**, and the first tier of any retrieval layered on later. That is a *priority ordering* and deliberately nothing else: it names no store, no embedding strategy, no chunking, no vendor, and no retrieval contract ([[adr-25-page-context-assistant]] rule 2). It sits beside the RAG paragraph below rather than replacing it — the page's already-computed variables are hot context precisely because they were computed once, server-side, for the screen, so chat and screen can never disagree.

### The escalation seam is unchanged

`ESCALATE` still means what it meant, still ships dead, and is still the single stable handoff point *from the choosing tier*. The assistant is a **sibling direct surface**, not a replacement for it and not an implementation of it: nothing about the router's contract, its four outcomes, or its reserved members moves. When the router-mediated generating path is eventually built, it plugs into the seam exactly as described above.

## Retention — the audit row is bounded, not forever (closes #65)

The raw utterance persists in `IntentQuery`, but under a bounded retention policy, not indefinitely:

- **Window** — `ROUTER_AUDIT_RETENTION_DAYS` ([[VARIABLES]], default `30`) bounds a row's lifetime, measured from `created_at`.
- **Purge** — the `purge_router_audit` management command deletes rows past the window; idempotent, `--dry-run` reports without deleting.
- **On-delete** — `IntentQuery.chosen_intent` is `SET_NULL`, not `PROTECT`: deleting an `Intent` registry row never cascade-deletes, and is never blocked by, its audit history (resolves the #105 collision).
- **Admin visibility** — `utterance` / `raw_model_output` are visible in Django admin only to the "Router Auditors" group; every other admin user's views exclude both fields.
- **Assistant mirror** — `AssistantQuery` audit rows live under the same policy shape: `ASSISTANT_AUDIT_RETENTION_DAYS` ([[VARIABLES]], default `30`) bounds the window, `purge_assistant_audit` deletes rows past it (idempotent, `--dry-run`), and raw text carries the same admin-visibility restriction.

## The action descriptor — the backend chooses, the frontend acts

The choosing tier's response is a **typed action descriptor**, never a performed side effect. The router selects; it does not navigate, redirect, or execute on the caller's behalf. This narrows [[adr-17-chatbot-two-tier]] rule 1's "actuator rights" to *emitting a descriptor*, not *performing an action* — content, not a rule change, so it lives here rather than in a new ADR ([[adr-00-adr-doctrine]] rule 1).

The descriptor carries typed, validated slots:

- **`kind`** — `navigate` or `confirm`. Reversibility decides which: `navigate` fires immediately and MUST be safe and idempotent (`GET` only); `confirm` returns a proposal the browser must present to the user before executing it as a separate, CSRF-protected request against `target`, subject to that endpoint's own authorization. Every irreversible or state-changing action is `confirm` — logout included.
- **`target`** — the URL or endpoint the frontend acts on.
- **`label`** — the hand-authored, human-facing text for the choice ([[LOCALISATION]] — registry content, not code).

The response body carries **no prose beyond the registry-authored `label`**: the reserved outcomes (`NO_MATCH`, `ESCALATE`, the kill switch's `disabled`) return their outcome key only, and the frontend owns the corresponding user-facing copy. A router response that mutates state, redirects, or free-text-explains itself is a defect — it would make the choosing tier a generator, eroding the invariant above.

## RAG — facilitated, not designed

The chatbot is the intended **future entry point for a RAG**. The template only *facilitates* it: a free-text surface and a generating tier that is read-only by construction are the two things a retrieval-augmented answer path needs.

**No RAG is designed, planned, or built here** — no store, no embedding strategy, no chunking, no retrieval contract. This paragraph is the entire extent of the commitment.

**pgvector and embeddings are deliberately deferred, not omitted by oversight.** The enum-constrained model call already performs the semantic matching a small, hand-authored registry needs; a vector index next to it would be a second matching mechanism with its own threshold, tie-break rule, and drift, for a menu that fits in a prompt with room to spare. **The trigger to revisit:** the registry grows past what fits comfortably in a single prompt (dozens to low hundreds of entries) or per-call token cost stops being negligible. At that point the fix is a **retrieval pre-filter** in front of the enum — embed the utterance, shortlist the nearest registry entries, hand only those to the enum-constrained call — never a replacement of the enum itself; the security argument above is unaffected because the shortlist is still a subset of an already permission-filtered menu.

## Relationship to the sibling documents

- [[API]] — every endpoint this feature needs enters there first, in its own guarded act, before any code ([[adr-07-api-and-backend]]).
- [[AUTH]] / [[adr-14-auth]] — unchanged. Cognito authenticates; Django authorizes. The router authorizes nothing; it narrows a menu Django already authorized.
- [[adr-25-page-context-assistant]] — the rules of the direct channel; this file owns the content those rules point to.
