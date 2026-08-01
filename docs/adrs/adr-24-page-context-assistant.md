---
title: adr-24-page-context-assistant
type: adr
status: active
created: 2026-08-01
tags: [adr, chatbot, assistant, ai, security]
---

# ADR-24 — the page-context assistant

Rules only; the channel, its v1 bounds, the context priority and the honest limit live in
[[CHATBOT]] ([[adr-00-adr-doctrine]] rule 1). This ADR adds to [[adr-15-chatbot-two-tier]]:
it lifts that ADR's rule-9 stop ("the template ships the choosing tier and stops") for
exactly one surface — the page-context assistant, which enters through
[[adr-07-development-flow]] as that rule prescribes; it supersedes nothing and narrows none
of that ADR's rules 1–8.

1. The page-context assistant is the sanctioned first surface of the generating tier, and it
   exists only in the shape [[CHATBOT]] records: a **direct user → generating-tier channel**
   that does not pass through the choosing tier. It is **read-only, forever** — it holds no
   actuator rights, emits no `confirm`, performs no write, and reaches no mutating endpoint.
   [[adr-15-chatbot-two-tier]] rules 1–8 bind unchanged; an action the assistant wants
   re-enters through the choosing tier under rule 4, never from this surface.

2. **View-first context.** The content of the user's current view is the first-priority
   context tier for any AI answer, and for any retrieval layered on top of it later. This is
   a priority ordering and nothing more: it commits this project to no retrieval mechanism,
   no store, no embedding strategy and no vendor. RAG stays facilitated, not designed
   ([[CHATBOT]] — the bounds are that document's).

3. Context is assembled **server-side** from the page identity — a member of the closed nav
   registry — and is built under the caller's Django Groups. Client-shipped page content is
   prohibited: the request carries an identity, never page text. The assistant MUST NEVER
   surface data its caller's groups could not `GET` directly ([[adr-10-auth]] rules 1–2 —
   the decision is Django's, never a model's, never a Cognito claim).

4. Links the generating tier emits are **structured and validated server-side** against the
   closed nav registry; a target outside the registry is dropped. Prose never mints a link:
   no anchor is ever parsed out of generated text, and the rendered answer interprets no
   markup.

5. Boilerplate. The endpoint enters [[API]] before its code ([[adr-03-api-and-backend]]
   rules 1–2); every name — surface, endpoint segment, component, model, env stem — enters
   [[GLOSSARY]] before first use ([[adr-01-glossary-and-localization]] rule 1); every
   variable a setting reads enters [[VARIABLES]] before code reads it
   ([[adr-03-api-and-backend]] rule 7); the answer reaches the screen and is therefore
   rendered copy — localizable through the i18n layer, while code, keys and everything else
   stay English ([[LOCALIZATION]], [[adr-01-glossary-and-localization]]). Any change to
   rules 1–4 is semantic and MUST supersede this ADR ([[adr-00-adr-doctrine]] rule 4).
