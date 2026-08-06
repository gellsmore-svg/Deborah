"""Lightweight Cairn text / PLAN-dict normalisation (not full grammar validation)."""

from __future__ import annotations

import re
from typing import Any

from deborah.conformance import validate_plan
from deborah.render.model import ProcessDocument, StepNode
from deborah.render.phrasing import extract_tags

_STEP_LINE = re.compile(r"^(\s*)(\d+(?:\.\d+)*)\.\s+(.+)$")
_SUB_BLOCK = re.compile(
    r"^(CONSTRAINTS|OUTPUT|PURPOSE|RISKS|CONTEXT|BOUNDARIES|STATE UPDATE|"
    r"HUMAN_DEMAND|HUMAN SIMULATION|HUMAN_SIMULATION|HUMAN_LOAD|TRUST|SUPPORT|"
    r"HUMAN_FACTORS|HUMAN_RISK|FAILURE_MODE|SIMULATION_FINDINGS|IMPROVEMENT|"
    r"CHANGE_IMPACT):\s*(.*)$",
    re.I,
)
_CONSTRUCT_PREFIX = re.compile(
    r"^(ITERATE|DECISION|DECIDE|CALL|RECURSE|QUEUE|PARALLEL|MERGE|SERVICE|RETRY|AWAIT|BREAK|CONTINUE|MILESTONE)\b",
    re.I,
)
_OPERATOR_FIELD = re.compile(r"^(Purpose|Owner|Assisted by|Outputs|Iterate-until|Next):\s*(.+)$", re.I)
_SECTION = re.compile(r"^##\s+(.+)$", re.M)
_FENCE = re.compile(r"^```(?:\w*)?\s*$")


def _detect_construct(text: str) -> tuple[str | None, str]:
    upper = text.strip()
    match = _CONSTRUCT_PREFIX.match(upper)
    if not match:
        return None, text
    construct = match.group(1).upper()
    if construct == "DECIDE":
        construct = "DECISION"
    remainder = upper[match.end() :].lstrip(" :→")
    return construct, remainder or text


def _parse_step_lines(lines: list[str]) -> list[StepNode]:
    roots: list[StepNode] = []
    stack: list[tuple[int, StepNode]] = []

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or line.strip().startswith("#"):
            continue

        sub = _SUB_BLOCK.match(line.strip())
        if sub and stack:
            key = sub.group(1).upper().replace(" ", "_")
            stack[-1][1].sub_blocks[key] = sub.group(2).strip()
            continue

        op = _OPERATOR_FIELD.match(line.strip())
        if op and stack:
            field = op.group(1).lower().replace(" ", "_").replace("-", "_")
            value = op.group(2).strip()
            node = stack[-1][1]
            if field == "purpose":
                node.purpose = value
            elif field == "owner":
                node.owner = value
            elif field == "assisted_by":
                node.assisted_by = value
            elif field == "outputs":
                node.outputs = [value]
            elif field == "iterate_until":
                node.iterate_until = value
            elif field == "next":
                node.next_phase = value
            continue

        match = _STEP_LINE.match(line)
        if not match:
            stripped = line.strip()
            if (
                stripped
                and not line[:1].isspace()
                and not stripped.lower().startswith("render-profile:")
                and not stripped.upper().startswith("PROCESS")
                and not _SUB_BLOCK.match(stripped)
                and not _OPERATOR_FIELD.match(stripped)
            ):
                auto = StepNode(number=str(len(roots) + 1), text=stripped)
                roots.append(auto)
                stack = [(0, auto)]
            continue

        indent = len(match.group(1).replace("\t", "    "))
        number = match.group(2)
        body = match.group(3).strip()
        construct, cleaned = _detect_construct(body)
        cleaned, tags = extract_tags(cleaned)

        node = StepNode(number=number, text=cleaned, construct=construct, tags=tags)

        depth = indent // 2 + number.count(".")
        while stack and stack[-1][0] >= depth:
            stack.pop()

        if stack:
            stack[-1][1].children.append(node)
        else:
            roots.append(node)
        stack.append((depth, node))

    return roots


def _extract_fenced_blocks(text: str) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    lines = text.splitlines()
    section = ""
    in_fence = False
    buf: list[str] = []

    for line in lines:
        sec = _SECTION.match(line)
        if sec:
            section = sec.group(1).strip()
        if _FENCE.match(line.strip()):
            if in_fence:
                blocks.append((section, buf))
                buf = []
                in_fence = False
            else:
                in_fence = True
            continue
        if in_fence:
            buf.append(line)

    if buf:
        blocks.append((section, buf))
    return blocks


def parse_markdown(text: str) -> ProcessDocument:
    doc = ProcessDocument()
    doc.warnings = []

    for section, lines in _extract_fenced_blocks(text):
        lower = section.lower()
        if lower.startswith("context"):
            for line in lines:
                m = re.match(r"^-\s+\*\*(.+?)\*\*\s+—\s+(.+)$", line.strip())
                if m:
                    doc.context[m.group(1)] = m.group(2)
        elif lower.startswith("requirements"):
            doc.requirements.extend(line.strip() for line in lines if line.strip() and not line.strip().startswith("```"))
        elif lower.startswith("outcomes"):
            doc.outcomes.extend(line.strip() for line in lines if line.strip())
        elif "process" in lower:
            if "operator" in lower or "render-profile: operator" in "\n".join(lines):
                doc.mode = "operator"
            elif "narrative" in lower:
                doc.mode = "narrative"
            else:
                doc.mode = "formal"
            if not doc.title:
                doc.title = section.replace("PROCESS —", "").replace("PROCESS -", "").strip()
            steps = _parse_step_lines(lines)
            if not steps:
                continue
            if "operator" in lower or "render-profile: operator" in "\n".join(lines):
                doc.operator_steps = steps
            elif "narrative" in lower:
                doc.narrative_steps = steps
            else:
                doc.steps = steps
                doc.mode = "formal"

    if not doc.steps:
        doc.steps = _parse_step_lines(text.splitlines())
        if doc.steps:
            doc.warnings.append("parsed steps from raw text without fenced PROCESS block")

    return doc


def parse_plan_dict(plan: dict[str, Any]) -> ProcessDocument:
    doc = ProcessDocument(title=plan.get("objective", "") or plan.get("plan_id", "PLAN"))
    doc.plan = plan
    doc.warnings = list(validate_plan(plan))

    for index, step in enumerate(plan.get("steps", []), start=1):
        action = str(step.get("action", ""))
        cleaned, tags = extract_tags(action)
        doc.steps.append(
            StepNode(
                number=str(index),
                text=cleaned,
                construct=step.get("construct"),
                tags=tags,
                sub_blocks={
                    k: str(v)
                    for k, v in step.items()
                    if k in {"success_criteria", "allowed_tools"} and v
                },
            )
        )

    if plan.get("stopping_conditions"):
        doc.outcomes.extend(str(x) for x in plan["stopping_conditions"])
    return doc


def parse_with_grammar(text: str) -> ProcessDocument:
    """Parse via the structural grammar and project into ProcessDocument."""
    from deborah.grammar import parse_document, validate_document
    from deborah.grammar.bridge import document_to_render_model

    doc = parse_document(text)
    render_doc = document_to_render_model(doc)
    render_doc.warnings.extend(validate_document(doc))
    return render_doc


def normalize_input(
    input_cairn: str | dict[str, Any],
    *,
    use_grammar: bool = True,
    lenient: bool = False,
) -> ProcessDocument:
    """Normalise Cairn text or a PLAN dict into a :class:`ProcessDocument`.

    By default the structural grammar is used. Unexpected grammar failures are
    **not** swallowed: they propagate so a render that failed validation cannot
    silently become a plausible legacy view (see Deborah #3).

    Pass ``lenient=True`` to fall back to the heuristic markdown parser on
    grammar exceptions; the fallback always records an explicit warning so the
    path is visible in render metadata.
    """
    if isinstance(input_cairn, dict):
        return parse_plan_dict(input_cairn)
    if use_grammar:
        try:
            return parse_with_grammar(input_cairn)
        except Exception as exc:
            if not lenient:
                raise
            doc = parse_markdown(input_cairn)
            msg = (
                f"grammar parse failed ({type(exc).__name__}: {exc}); "
                "used legacy parser"
            )
            doc.warnings = [msg, *list(doc.warnings or [])]
            return doc
    return parse_markdown(input_cairn)
