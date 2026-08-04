---
title: adr-05-glossary-and-localisation
type: adr
category: harness
use_case: naming anything — a model, endpoint segment, env var stem, service, UI label, doc name; writing non-English rendered copy
created: 2026-07-10
modified: 2026-08-04
tags: [adr, glossary, localization]
---

# ADR-05 — glossary and localization

## CONTEXT

> A name is decided once, in one place, before its first use. This ADR binds
> naming and language.

Rules only; content lives in [[GLOSSARY]] and [[LOCALISATION]].

## ASSERTIONS

1. A name is decided in [[GLOSSARY]] before its first use. Every
   identifier-worthy term — model names, endpoint segments, env var stems,
   service names, UI labels, doc names — uses the canonical form registered
   there. A new term gets its row first; the ABC gate ([[AGENTS]]) applies to
   naming like to everything else.
2. Forbidden forms listed in [[GLOSSARY]] are banned everywhere: code, docs,
   prose, commit messages.
3. Everything that is code is English — always, no exceptions: identifiers,
   comments, docstrings, commit messages, API paths, env var names, test
   names, log messages. Rationale and mechanics live in [[LOCALISATION]].
4. Non-English text exists ONLY in the frontend's rendered output, through
   the i18n layer defined in [[LOCALISATION]]. Keys, message IDs, and
   variables stay English even there.
5. Naming questions resolve in [[GLOSSARY]]; language and locale questions
   resolve in [[LOCALISATION]]. Neither rule is restated elsewhere — link,
   don't repeat.

## RELATED

### related files

- [[adr-01-constitution]] — authority order this ADR sits beneath
- [[GLOSSARY]] — naming authority
- [[LOCALISATION]] — language and i18n mechanics
- [[AGENTS]] — the ABC gate naming answers to
