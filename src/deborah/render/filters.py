"""Section and depth filters for view generation."""

from __future__ import annotations

import copy
from typing import Any

from deborah.render.model import ProcessDocument, StepNode


def _truncate_steps(nodes: list[StepNode], max_depth: int, depth: int = 0) -> list[StepNode]:
    out: list[StepNode] = []
    for node in nodes:
        cloned = StepNode(
            number=node.number,
            text=node.text,
            construct=node.construct,
            tags=list(node.tags),
            sub_blocks=dict(node.sub_blocks),
            owner=node.owner,
            purpose=node.purpose,
            assisted_by=node.assisted_by,
            outputs=list(node.outputs),
            iterate_until=node.iterate_until,
            next_phase=node.next_phase,
        )
        if depth + 1 < max_depth:
            cloned.children = _truncate_steps(node.children, max_depth, depth + 1)
        out.append(cloned)
    return out


def apply_filters(doc: ProcessDocument, options: dict[str, Any]) -> ProcessDocument:
    filtered = copy.deepcopy(doc)
    sections = options.get("sections")
    if sections is not None:
        allowed = {s.lower() for s in sections}
        if "context" not in allowed:
            filtered.context = {}
        if "requirements" not in allowed:
            filtered.requirements = []
        if "outcomes" not in allowed:
            filtered.outcomes = []
        if "plan" not in allowed:
            filtered.plan = None

    max_depth = options.get("max_depth")
    if isinstance(max_depth, int) and max_depth > 0:
        filtered.steps = _truncate_steps(filtered.steps, max_depth)
        filtered.operator_steps = _truncate_steps(filtered.operator_steps, max_depth)
        filtered.narrative_steps = _truncate_steps(filtered.narrative_steps, max_depth)

    return filtered