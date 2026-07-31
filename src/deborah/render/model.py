"""Internal model for simplified view generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepNode:
    number: str
    text: str
    construct: str | None = None
    tags: list[str] = field(default_factory=list)
    sub_blocks: dict[str, str] = field(default_factory=dict)
    children: list[StepNode] = field(default_factory=list)
    owner: str | None = None
    purpose: str | None = None
    assisted_by: str | None = None
    outputs: list[str] = field(default_factory=list)
    iterate_until: str | None = None
    next_phase: str | None = None
    parsed_modifiers: dict[str, str] = field(default_factory=dict)  # for domain constructs like REGULATION [STRATEGY]


@dataclass
class ProcessDocument:
    title: str = ""
    mode: str = "formal"
    context: dict[str, str] = field(default_factory=dict)
    requirements: list[str] = field(default_factory=list)
    outcomes: list[str] = field(default_factory=list)
    steps: list[StepNode] = field(default_factory=list)
    plan: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    # Alternate backbones from multi-profile Cairn docs (formal / operator / narrative).
    operator_steps: list[StepNode] = field(default_factory=list)
    narrative_steps: list[StepNode] = field(default_factory=list)


@dataclass
class RenderResult:
    profile: str
    language: str
    format: str
    body: str
    footnotes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "language": self.language,
            "format": self.format,
            "body": self.body,
            "footnotes": self.footnotes,
            "metadata": self.metadata,
        }