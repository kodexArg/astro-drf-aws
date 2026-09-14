---
title: adr-25-page-context-assistant
type: adr
category: backend
use_case: building the page-context assistant surface, assembling view context for an AI answer, adding a link the assistant may emit
created: 2026-07-10
modified: 2026-08-04
tags: [adr, chatbot, assistant, rag]
---

# ADR-25 — the page-context assistant

## CONTEXT

> The one sanctioned, read-only-forever, direct user → generating-tier
> channel, bounded by view-first server-assembled context.

Rules only; the channel, its v1 bounds, the context priority and the honest
limit live in [[CHATBOT]]. This ADR adds to [[adr-17-chatbot-two-tier]]: it
lifts that ADR's rule-9 default ("the base template ships the choosing tier
and stops") for exactly one surface — the page-context assistant, which
enters through [[adr-11-development-flow]] as that rule prescribes; it
supersedes nothing and narrows none of that ADR's rules 1–8.

## ASSERTIONS

1. The page-context assistant is the sanctioned first surface of the
   generating tier, and it exists only in the shape [[CHATBOT]] records: a
   **direct user → generating-tier channel** that does not pass through the
   choosing tier. It is **read-only, forever** — it holds no actuator
   rights, emits no `confirm`, performs no write, and reaches no mutating
   endpoint. [[adr-17-chatbot-two-tier]] rules 1–8 bind unchanged; an action
   the assistant wants re-enters through the choosing tier under rule 4,
   never from this surface.
2. **View-first context.** The content of the user's current view is the
   first-priority context tier for any AI answer, and for any retrieval
   layered on top of it later. This is a priority ordering and nothing
   more: it commits this project to no retrieval mechanism, no store, no
   embedding strategy and no vendor. RAG stays facilitated, not designed
   ([[CHATBOT]] — the bounds are that document's).
3. Context is assembled **server-side** from the page identity — a member
   of the closed nav registry — and is built under the caller's Django
   Groups. Client-shipped page content is prohibited: the request carries
   an identity, never page text. The assistant MUST NEVER surface data its
   caller's groups could not `GET` directly ([[adr-14-auth]] rules 1–2 —
   the decision is Django's, never a model's, never a Cognito claim).
4. Links the generating tier emits are **structured and validated
   server-side** against the closed nav registry; a target outside the
   registry is dropped. Prose never mints a link: no anchor is ever parsed
   out of generated text, and the rendered answer interprets no markup.
5. Boilerplate. The endpoint enters [[API]] before its code
   ([[adr-07-api-and-backend]] rules 1–2); every name — surface, endpoint
   segment, component, model, env stem — enters [[GLOSSARY]] before first
   use ([[adr-05-glossary-and-localisation]] rule 1); every variable a
   setting reads enters [[VARIABLES]] before code reads it
   ([[adr-07-api-and-backend]] rule 7); the answer reaches the screen and is
   therefore rendered copy — localizable through the i18n layer, while
   code, keys and everything else stay English ([[LOCALISATION]],
   [[adr-05-glossary-and-localisation]]).

## RELATED

### related files

- [[adr-17-chatbot-two-tier]] — the two-tier boundary this ADR bounds an
  exception into (rules 1–8)
- [[adr-11-development-flow]] — the entry gate this surface used
- [[adr-14-auth]] — the group-scoped context rule
- [[adr-07-api-and-backend]] — endpoint and variable declaration order
- [[adr-05-glossary-and-localisation]] — naming and rendered-copy language
- [[CHATBOT]] — channel shape, v1 bounds, context priority, honest limit
- [[API]] — the endpoint row
- [[GLOSSARY]], [[VARIABLES]], [[LOCALISATION]] — boilerplate detail
