"""Deborah's Keturah manifest — its LLM-consumable interfaces.

Built from deborah.conformance so the advertised grammar matches the enforced one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from typing import Any

try:
    from keturah import Manifest, capability, manifest
except ImportError:

    @dataclass
    class _Capability:
        name: str
        description: str
        input_schema: dict[str, Any] | None = None
        output_schema: dict[str, Any] | None = None
        tags: list[str] = field(default_factory=list)
        kind: str = "tool"

    @dataclass
    class Manifest:
        product: str
        version: str
        description: str
        capabilities: list[_Capability]

        def to_mcp(self) -> dict[str, Any]:
            tools = []
            for item in self.capabilities:
                if item.kind == "resource":
                    continue
                tools.append(
                    {
                        "name": item.name,
                        "description": item.description,
                        "inputSchema": item.input_schema or {"type": "object"},
                    }
                )
            return {"tools": tools}

    def capability(
        name: str,
        description: str,
        *,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        kind: str = "tool",
    ) -> _Capability:
        return _Capability(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            tags=tags or [],
            kind=kind,
        )

    def manifest(product: str, *, version: str, description: str, capabilities: list[_Capability]) -> Manifest:
        return Manifest(product=product, version=version, description=description, capabilities=capabilities)

from deborah.conformance import PLAN_CONSTRUCTS, PLAN_STATUSES, REQUIRED_PLAN_FIELDS


def _version() -> str:
    for distribution in ("deborah", "cairn-lang", "cairn"):
        try:
            return _pkg_version(distribution)
        except PackageNotFoundError:
            continue
    return "0.0.0+source"


def build_manifest() -> Manifest:
    return manifest(
        "deborah",
        version=_version(),
        description=(
            "Process meta-language: plan/template grammar and a machine-readable "
            "conformance surface. Library capabilities map to the console tools: "
            "validate_document/parse_document ≈ deborah-validate; render_plan ≈ "
            "deborah-render. The interactive composer (deborah-serve) and its "
            "template store are operator-only CLIs — not MCP tools."
        ),
        capabilities=[
            capability(
                "validate_plan",
                "Validate a runtime PLAN dict against the conformance contract; returns a list of "
                "errors (empty = conformant). Allowed step constructs: "
                + ", ".join(sorted(PLAN_CONSTRUCTS))
                + ". (CLI: deborah-validate on exported plan JSON.)",
                input_schema={"type": "object", "properties": {"plan": {"type": "object"}}, "required": ["plan"]},
                output_schema={
                    "type": "object",
                    "properties": {"errors": {"type": "array", "items": {"type": "string"}}},
                },
                tags=["validation", "plan", "cli:deborah-validate"],
            ),
            capability(
                "render_plan",
                "Render a Cairn process description or PLAN dict into a simplified human-readable "
                "view (narrative_steps, simple_prose, operator, executive, audit). "
                "CLI: deborah-render [--profile …] [--language en|es|fr] [--stylesheet path] "
                "[--lenient] [--format markdown|text|json|mermaid].",
                input_schema={
                    "type": "object",
                    "properties": {
                        "input_cairn": {"description": "Markdown text or PLAN object"},
                        "profile": {
                            "type": "string",
                            "enum": [
                                "narrative_steps",
                                "simple_prose",
                                "operator",
                                "executive",
                                "audit",
                                "narrative",
                            ],
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "es", "fr"],
                            "description": "Phrasing language (en, es, fr)",
                        },
                        "output_format": {
                            "type": "string",
                            "enum": ["markdown", "text", "json", "mermaid"],
                        },
                        "stylesheet": {
                            "type": "string",
                            "description": "Optional path to a YAML/JSON stylesheet (saved template)",
                        },
                        "options": {
                            "type": "object",
                            "description": "boxed, include_tags, max_depth, sections, lenient, …",
                        },
                    },
                    "required": ["input_cairn"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "body": {"type": "string"},
                        "profile": {"type": "string"},
                        "language": {"type": "string"},
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "warnings": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                },
                tags=["render", "plan", "cli:deborah-render"],
            ),
            capability(
                "parse_document",
                "Parse a Cairn markdown or skeleton text file into a structural AST (GRAMMAR.md EBNF). "
                "CLI: deborah-validate --export-ast.",
                input_schema={
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "Cairn markdown or skeleton text"}},
                    "required": ["text"],
                },
                output_schema={"type": "object", "properties": {"process_count": {"type": "integer"}}},
                tags=["grammar", "parse", "cli:deborah-validate"],
            ),
            capability(
                "validate_document",
                "Validate a Cairn description for GRAMMAR.md structure and SPEC §12 well-formedness; "
                "returns errors (empty = well-formed). CLI: deborah-validate.",
                input_schema={
                    "type": "object",
                    "properties": {"text": {"type": "string"}},
                    "required": ["text"],
                },
                output_schema={
                    "type": "object",
                    "properties": {"errors": {"type": "array", "items": {"type": "string"}}},
                },
                tags=["grammar", "validation", "cli:deborah-validate"],
            ),
            capability(
                "plan_schema",
                "The Cairn plan contract: required fields ("
                + ", ".join(REQUIRED_PLAN_FIELDS)
                + "), allowed constructs, and statuses ("
                + ", ".join(sorted(PLAN_STATUSES))
                + ").",
                kind="resource",
                tags=["schema"],
            ),
        ],
    )
