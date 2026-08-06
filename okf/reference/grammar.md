---
type: Reference
title: Grammar (GRAMMAR.md)
description: The formal (EBNF) grammar of Cairn's formal style — processes, steps, constructs, tags, STATE, PLAN framing fields, and sub-blocks.
resource: https://github.com/gellsmore-svg/Deborah/blob/main/GRAMMAR.md
tags: [deborah, cairn, grammar, ebnf, syntax]
timestamp: 2026-08-06T00:00:00Z
---

# Grammar — `GRAMMAR.md` (v0.10)

The formal (EBNF) grammar for Cairn's **formal style** — the precise, machine-
checkable syntax behind the prose-first [specification](spec.md). It pins down how
[constructs](../concepts/constructs.md), [tags](../concepts/tags.md),
[STATE](../concepts/state.md), PLAN framing fields (`INTENT`, `OUTCOMES`,
`ASSUMES`, `ON_UNCERTAINTY`, `REEVALUATE_WHEN`), and sub-blocks are written.

The grammar covers the **`ai`/formal** projection; narrative and other
[render profiles](../concepts/backbone-and-render-profiles.md) are lossy
projections of the same backbone. Validity is the **structural conformance** of
[SPEC §12](spec.md).

## Executable parser

The **`deborah`** package implements this grammar in Python
(`deborah.parse_document`, `deborah.validate_document`, `deborah.document_to_plan`).
See [docs/GRAMMAR-PARSER.md](../../docs/GRAMMAR-PARSER.md).
