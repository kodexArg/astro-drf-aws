---
title: adr-20-markdown-vault-mcp
type: adr
category: harness
use_case: searching or reading docs/ content, traversing wikilink backlinks or outlinks, reindexing the vault after a docs change
created: 2026-07-10
modified: 2026-08-04
tags: [adr, mcp, vault, docs]
---

# ADR-20 — the vendored markdown-vault MCP

## CONTEXT

> The markdown-vault MCP is the mandatory first source of truth for
> reaching `docs/` content — before Grep or Read.

Rules only; the server, its config, the tool cheat-sheet, and the code↔doc
live-doc convention live in [[markdown-vault-mcp]]. Force over its use is
here.

## ASSERTIONS

1. The markdown-vault MCP (`markdown-vault-docs`) is the mandatory first
   source of truth for reaching `docs/` content — searching, reading, and
   traversing the vault graph (backlinks, outlinks, similarity). An agent
   consults it before Grep/Read for anything that is `docs/` prose or its
   wikilink structure ([[adr-00-adr-doctrine]] rule 9, [[AGENTS]]). Grep/Read
   stay free for code, configs, and non-`docs/` files.
2. It is vendored and transported with the repo, not registered
   machine-globally. The template ships a project-scoped `.mcp.json`, a
   self-bootstrapping launcher `scripts/mvmcp.py`, and a git-ignored
   `.mvmcp/` (project-local venv + index + embeddings). A fresh clone
   exposes the server with no external links — the same self-contained
   discipline [[adr-02-harness]] imposes on skills. The inventory row lives
   in [[HARNESS]]; the version pin in [[REQUIREMENTS]].
3. Its name and env stem are registered in [[GLOSSARY]] before use. The
   server name is `markdown-vault-docs`; the env stem is
   `MARKDOWN_VAULT_MCP_`. The launcher's env is harness-dev tooling, never
   app runtime and never a secret, so it does not enter [[VARIABLES]] —
   which governs only variables backend or frontend code reads
   ([[adr-07-api-and-backend]] rule 7).
4. It complements, and never replaces, the codebase-memory graph. The
   markdown-vault MCP owns the `docs/` prose + wikilink graph;
   `codebase-memory-mcp` owns the code graph ([[AGENTS]] Code Discovery
   Protocol). Neither is folded into the other's category; a code-structure
   question still goes to codebase-memory first.
5. The vault index must be kept fresh. After `docs/` changes it is rebuilt
   or reindexed before its answers are trusted; the `mvmcp_freshness.py`
   SessionStart hook is the safety net, not the trigger
   ([[markdown-vault-mcp]]). Writes carry the known link-index degradation
   caveat recorded in [[markdown-vault-mcp]]; Obsidian syntax is still
   authored through the `obsidian-markdown` skill ([[HARNESS]]).

## RELATED

### related files

- [[adr-00-adr-doctrine]] — the vault-first read path (rule 9)
- [[adr-02-harness]] — the vendoring discipline this MCP follows
- [[adr-07-api-and-backend]] — why the launcher's env stays out of VARIABLES
- [[markdown-vault-mcp]] — server, config, tool cheat-sheet, live-doc
  convention
- [[HARNESS]] — inventory row and version pin
- [[GLOSSARY]] — server name and env stem
