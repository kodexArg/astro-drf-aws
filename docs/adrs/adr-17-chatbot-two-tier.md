---
title: adr-17-chatbot-two-tier
type: adr
category: backend
use_case: adding any chatbot or router capability, wiring a model call, deciding whether an output is a choice or free text, touching the CHATBOT surface
created: 2026-07-10
modified: 2026-08-04
tags: [adr, chatbot, two-tier, ai]
---

# ADR-17 — the two-tier chatbot

## CONTEXT

> The tier that chooses holds actuator rights and never emits free text; the
> tier that generates free text is read-only forever. No component holds
> both.

Rules only; content lives in [[CHATBOT]], [[API]], [[VARIABLES]].

## ASSERTIONS

1. Capabilities are disjoint, permanently. The tier that chooses holds
   actuator rights and MUST NEVER emit free text. The tier that generates
   free text is read-only, forever and MUST NEVER flip a switch. No
   component may hold both. This is a standing boundary, not a transitional
   arrangement, and no future feature may blur it ([[CHATBOT]] — the
   permanent invariant).
2. The choosing tier's only valid output is one member of a closed enum,
   built server-side in Django and filtered by the requesting user's
   permissions ([[adr-14-auth]]) before the model is invoked. A model output
   outside that menu is a hard reject: logged as a fault, never repaired,
   never defaulted, never retried into a nearest match.
3. The model never makes an authorization decision and can never widen
   privilege. Authorization is decided once, in Django, before inference;
   the router only narrows within an already-authorized set. A permission
   decision read from a model's output is a defect, exactly as a permission
   decision read from a Cognito claim is ([[adr-14-auth]] rule 2).
4. When the generating tier wants an action, it re-enters through the
   choosing tier with a closed menu, subject to the same filtering, the same
   enum, the same hard reject, and the same audit row as a human utterance.
   There is no path from generated text to an actuator that bypasses rule 2.
5. The choosing tier NEVER forwards user-supplied text to the generating
   tier. What it forwards is a structured reinterpretation: a hand-authored
   template selected from a closed set, filled with typed, validated slots.
   A free-prose restatement is prohibited — emitting one would make the
   choosing tier a generator, violating rule 1, and would reopen the channel
   this design exists to close. Mechanism and its limits: [[CHATBOT]].
6. A free-text slot is a residual channel and requires an explicit, recorded
   decision in [[CHATBOT]] before it ships. No document, comment, or commit
   message may state the containment as a closed channel or a proof; it is
   bounded as [[CHATBOT]] bounds it. Overstating the security property is a
   defect.
7. Inference is deterministic and structurally constrained: temperature 0,
   and constrained decoding where the provider supports it, with code-side
   enum validation enforcing the same closure regardless.
8. This is a capability layer, not a doctrine change ([[adr-16-m365-graph]]
   precedent). Cognito remains the sole authentication provider
   ([[adr-14-auth]]); [[CACHE]] gains no cache server ([[adr-10-cache]]);
   every endpoint enters through [[API]] before code
   ([[adr-07-api-and-backend]]); every variable a setting reads enters
   [[VARIABLES]] first; the app, its endpoint segments, and its env stem get
   their [[GLOSSARY]] rows before first use.
9. The base template ships the choosing tier and stops there by default; the
   generating tier and any RAG on top of it are additions that enter through
   [[adr-11-development-flow]]. The page-context assistant
   ([[adr-25-page-context-assistant]]) is the one sanctioned first surface of
   the generating tier and is bounded there — it does not reopen this
   rule for any other surface.

## RELATED

### related files

- [[adr-14-auth]] — RBAC and authorization decisions the model never makes
- [[adr-16-m365-graph]] — the capability-layer precedent
- [[adr-25-page-context-assistant]] — the bounded generating-tier exception
- [[adr-11-development-flow]] — how a future generating-tier feature enters
- [[CHATBOT]] — the router shape, closed enum, and residual-channel bounds
- [[API]] — endpoint declaration for router routes
- [[VARIABLES]] — env stems this capability reads
