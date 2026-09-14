---
title: adr-10-cache
type: adr
category: backend
use_case: considering a cache server or a caching mechanism, writing a response header, caching authenticated or personalized data
created: 2026-07-10
modified: 2026-08-04
tags: [adr, cache]
---

# ADR-10 — cache

## CONTEXT

> No cache server, ever. The four defined layers are the whole strategy.

Rules only; content lives in [[CACHE]].

## ASSERTIONS

1. No cache server, ever. Redis and ElastiCache are prohibited; the stack
   must never grow one. Do not add them, do not depend on packages that
   require them.
2. The four layers defined in [[CACHE]] — HTTP, Django shared cache,
   per-process, Astro — are the whole strategy. No caching mechanism exists
   outside them.
3. Every response the containers emit carries an explicit `Cache-Control`
   header; an absent header is a bug, not a default.
4. Authenticated responses are `no-store` by default; caching personalized
   data is an opt-in, row-level decision in [[API]] — never a blanket
   policy.

## RELATED

### related files

- [[adr-06-initial-stack]] — the stack-level cache-server prohibition
- [[CACHE]] — the four-layer strategy
- [[API]] — row-level opt-in for personalized caching
