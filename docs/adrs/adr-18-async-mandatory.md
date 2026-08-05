---
title: adr-18-async-mandatory
type: adr
category: backend
use_case: writing a streaming or long-running view, calling Bedrock, considering WebSockets, touching ASGI configuration
created: 2026-07-10
modified: 2026-08-04
tags: [adr, async, asgi, sse]
---

# ADR-18 — async is a capability the project MUST carry, not a per-view default

## CONTEXT

> The project stays async-capable at all times; a normal sync view is the
> unchanged default and needs no justification.

Rules only; content lives in [[BACKEND]].

## ASSERTIONS

1. The project MUST stay async-capable at all times: ASGI server, config,
   and dependencies never block a view from being `async def`. This is a
   standing capacity requirement, not a per-view mandate — a normal sync
   `def` view is the unchanged default and needs no justification.
2. When a feature needs async — streaming, non-blocking I/O, long-running
   inference — it is written `async def`. Server-Sent Events (an async view
   returning `StreamingHttpResponse` over an async generator) is the
   sanctioned mechanism, riding the existing ASGI server ([[BACKEND]]); no
   Django Channels, no channel layer, no new infrastructure.
3. WebSockets are a reserved escalation at the `/ws/` prefix, only for a
   need SSE genuinely cannot meet (bidirectional push), and only in a shape
   needing no cross-process channel layer — Redis is prohibited
   ([[adr-10-cache]]), so a design requiring fan-out across Fargate tasks is
   not buildable in this stack.
4. Bedrock inference calls use `boto3` wrapped in `asgiref.sync_to_async`,
   never `aiobotocore` ([[BACKEND]], [[REQUIREMENTS]]) — the one concrete
   requirement async-capability imposes today. Revisit only on measured
   latency evidence that the thread-pool wrap is a real bottleneck.

## RELATED

### related files

- [[adr-10-cache]] — the Redis prohibition WebSockets cannot route around
- [[BACKEND]] — the ASGI server and SSE mechanics
- [[REQUIREMENTS]] — the boto3/asgiref pin
