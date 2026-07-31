"""Output formatters: markdown, plain text, JSON, Mermaid."""

from __future__ import annotations

import json
from typing import Any

from deborah.render.model import ProcessDocument, RenderResult, StepNode


def to_text(result: RenderResult) -> str:
    parts = [result.body]
    if result.footnotes:
        parts.append("")
        parts.append("---")
        parts.append("Notes:")
        parts.extend(f"- {n}" for n in result.footnotes)
    return "\n".join(parts)


def to_json(result: RenderResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def _mermaid_id(number: str) -> str:
    return "s" + number.replace(".", "_")


def to_mermaid(doc: ProcessDocument, language: str = "en") -> str:
    from deborah.render.phrasing import phrase_construct

    lines = ["flowchart TD"]
    seen: set[str] = set()

    def walk(nodes: list[StepNode], parent: str | None = None) -> None:
        for node in nodes:
            nid = _mermaid_id(node.number)
            if nid in seen:
                continue
            seen.add(nid)
            label = phrase_construct(
                node.construct,
                node.text,
                language,
                node.tags,
                node.parsed_modifiers,
            ).replace('"', "'")[:80]
            lines.append(f'  {nid}["{node.number}. {label}"]')
            if parent:
                lines.append(f"  {parent} --> {nid}")
            child_parent = nid
            if node.children:
                walk(node.children, child_parent)

    walk(doc.steps)
    return "\n".join(lines)


def apply_format(result: RenderResult, doc: ProcessDocument, fmt: str) -> str | dict[str, Any]:
    if fmt == "json":
        return result.to_dict()
    if fmt == "text":
        return to_text(result)
    if fmt == "mermaid":
        return to_mermaid(doc, result.language)
    if fmt == "markdown":
        body = result.body
        if result.footnotes:
            body += "\n\n---\n\n### Notes\n\n" + "\n".join(f"- {n}" for n in result.footnotes)
        return body
    raise ValueError(f"Unknown output format: {fmt!r}")
