"""Convert parsed Cairn PLAN/PROCESS backbones to runtime PLAN dicts."""

from __future__ import annotations

from typing import Any

from deborah.grammar.ast import CairnDocument, Plan, Step
from deborah.grammar.tags import split_tag_list


def document_to_plan(doc: CairnDocument) -> dict[str, Any]:
    """Export the first PLAN envelope, or synthesise a plan from the first PROCESS."""
    if doc.plans:
        return _plan_to_dict(doc.plans[0])
    if doc.processes:
        proc = doc.processes[0]
        return {
            "plan_id": f"process_{_slug(proc.name)}",
            "revision": 1,
            "parent_revision": None,
            "request": proc.description or proc.name,
            "objective": proc.description or proc.name,
            "status": "draft",
            "steps": _steps_to_dict(proc.steps),
            "stopping_conditions": _outcomes(doc),
            "unresolved_questions": [],
            "revision_decision": "revise",
            "revision_reason": "",
        }
    raise ValueError("document has no PLAN or PROCESS to export")


def _plan_to_dict(plan: Plan) -> dict[str, Any]:
    proc = plan.process
    steps: list[dict[str, Any]] = []
    objective = plan.intent or plan.request
    if proc:
        steps = _steps_to_dict(proc.steps)
        if not plan.intent and proc.description:
            objective = proc.description
    out: dict[str, Any] = {
        "plan_id": plan.plan_id,
        "revision": plan.revision,
        "parent_revision": None if plan.parent in (None, "none") else _maybe_int(plan.parent),
        "request": plan.request,
        "intent": plan.intent or objective,
        "objective": objective,
        "status": plan.status,
        "steps": steps,
        "stopping_conditions": list(plan.outcomes),
        "outcomes": list(plan.outcomes),
        "assumes": list(plan.assumes),
        "on_uncertainty": plan.on_uncertainty or "record",
        "reevaluate_when": list(plan.reevaluate_when),
        "unresolved_questions": [],
        "revision_decision": "revise",
        "revision_reason": plan.trigger,
    }
    # Capability refs on CALL steps (name@version or bare name) become allowed_tools
    # hints when the step text starts with CALL — runtime still owns enforcement.
    return out


def _steps_to_dict(steps: list[Step], *, prefix: str = "s") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    counter = 1

    def walk(nodes: list[Step], parent_id: str | None = None) -> None:
        nonlocal counter
        for node in nodes:
            step_id = f"{prefix}{counter}"
            counter += 1
            action = node.text
            if node.tags:
                action = f"{action} [{' , '.join(node.tags)}]".strip()
            entry: dict[str, Any] = {
                "id": step_id,
                "action": action,
                "construct": node.construct or "STEP",
                "status": "pending",
                "depends_on": [parent_id] if parent_id else [],
            }
            criteria = [a.text for a in node.annotations if a.keyword == "OUTPUT"]
            if criteria:
                entry["success_criteria"] = criteria
                entry["output"] = criteria[0]
            purpose = next((a.text for a in node.annotations if a.keyword == "PURPOSE"), None)
            if purpose:
                entry["purpose"] = purpose
            cognition = next((a.text for a in node.annotations if a.keyword == "COGNITION"), None)
            if cognition:
                # First token is the product type; remainder is optional prose.
                token = cognition.strip().split()[0].lower() if cognition.strip() else ""
                if token:
                    entry["cognition"] = token
            # CALL target → allowed_tools hint for strict assumes checks.
            if (node.construct or "").upper() == "CALL" or (
                node.text and node.text.upper().startswith("CALL ")
            ):
                head = node.text
                if head.upper().startswith("CALL "):
                    head = head[5:]
                target = head.split("—", 1)[0].split("–", 1)[0].strip()
                target = target.split()[0] if target.split() else ""
                if target:
                    entry.setdefault("allowed_tools", [])
                    if target not in entry["allowed_tools"]:
                        entry["allowed_tools"] = list(entry.get("allowed_tools") or []) + [target]
            # Determinism tag → execution axis (HOW), when present.
            # Tags may arrive as one bracket group ("CODE, DETERMINISTIC").
            for raw in node.tags:
                for tag in split_tag_list(raw):
                    root = tag.split(":", 1)[0].split("[", 1)[0].strip().upper()
                    if root in {"DETERMINISTIC", "STOCHASTIC"}:
                        entry["execution"] = root.lower()
                        break
                if "execution" in entry:
                    break
            out.append(entry)
            if node.children:
                walk(node.children, step_id)

    walk(steps)
    return out


def _outcomes(doc: CairnDocument) -> list[str]:
    lines: list[str] = []
    for block in doc.outcomes_blocks:
        lines.extend(block.lines)
    return lines


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_") or "unnamed"


def _maybe_int(value: str | None) -> int | str | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value