---
title: Mermaid Lint Test Fixture - Bad Braces
description: Known-bad test fixture for verifying brace collision detection in mermaid diagrams
version: v0.1.0
updated: 2026-08-18
---
# fixture: KNOWN-BAD — placeholder braces collide with mermaid node syntax

```mermaid
%%{init: {'theme':'base','fontFamily':"'Nunito',sans-serif"}}%%
flowchart TD
  A([{{INPUT}}]) --> B{{{DECISION_POINT}}}
  B -->|sí| C[{{PATH_A}}]
```
