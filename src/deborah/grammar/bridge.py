"""Bridge grammar AST to render ProcessDocument."""

from __future__ import annotations

from deborah.grammar.ast import Annotation, CairnDocument, Process, Step
from deborah.render.model import ProcessDocument, StepNode


def _annotation_map(annotations: list[Annotation]) -> dict[str, str]:
    out: dict[str, str] = {}
    for ann in annotations:
        key = ann.keyword
        if key in out:
            out[key] = f"{out[key]}; {ann.text}"
        else:
            out[key] = ann.text
    return out


def _step_to_node(step: Step) -> StepNode:
    return StepNode(
        number=step.step_id,
        text=step.text,
        construct=step.construct,
        tags=list(step.tags),
        sub_blocks=_annotation_map(step.annotations),
        children=[_step_to_node(child) for child in step.children],
        parsed_modifiers=getattr(step, "parsed_modifiers", {}) or {},
    )


def _process_mode(proc: Process) -> str:
    if proc.signature:
        return "formal"
    if proc.description:
        return "narrative"
    return "formal"


def document_to_render_model(doc: CairnDocument) -> ProcessDocument:
    """Project a parsed CairnDocument into the render layer's ProcessDocument."""
    render_doc = ProcessDocument()
    render_doc.warnings = list(doc.parse_errors)

    for block in doc.context_blocks:
        for line in block.lines:
            if " — " in line:
                key, value = line.split(" — ", 1)
                render_doc.context[key.strip()] = value.strip()
            elif " - " in line:
                key, value = line.split(" - ", 1)
                render_doc.context[key.strip()] = value.strip()

    for block in doc.requirements_blocks:
        for req in block.requirements:
            line = f"{req.req_id}. {req.text}"
            if req.priority:
                line += f" [{req.priority}]"
            render_doc.requirements.append(line)
            if req.acceptance:
                render_doc.requirements.append(f"    ACCEPTANCE: {req.acceptance}")

    for block in doc.outcomes_blocks:
        render_doc.outcomes.extend(block.lines)
        for emergent in block.emergent_blocks:
            render_doc.outcomes.append(emergent.satisfies)
            render_doc.outcomes.extend(emergent.lines)

    formal: list[StepNode] = []
    operator: list[StepNode] = []
    narrative: list[StepNode] = []

    profile = doc.directives[-1].profile if doc.directives else None
    processes = list(doc.processes)
    # PLAN-only documents nest PROCESS under PLAN — project those steps too.
    for plan in doc.plans:
        if plan.process and plan.process not in processes:
            processes.append(plan.process)

    for proc in processes:
        nodes = [_step_to_node(step) for step in proc.steps]
        mode = _process_mode(proc)
        render_doc.process_sections.append((proc.name or "Process", nodes))
        if profile == "operator" or mode == "operator":
            operator.extend(nodes)
        elif mode == "narrative":
            narrative.extend(nodes)
        else:
            formal.extend(nodes)
        if not render_doc.title:
            render_doc.title = proc.name

    render_doc.steps = formal or narrative or operator
    render_doc.operator_steps = operator
    render_doc.narrative_steps = narrative
    if formal:
        render_doc.mode = "formal"
    elif operator:
        render_doc.mode = "operator"
    elif narrative:
        render_doc.mode = "narrative"

    if doc.plans:
        from deborah.grammar.plan_export import document_to_plan

        try:
            render_doc.plan = document_to_plan(doc)
            # PLAN-level OUTCOMES fill doc.outcomes when document-level OUTCOMES empty.
            if not render_doc.outcomes and render_doc.plan.get("outcomes"):
                render_doc.outcomes = list(render_doc.plan["outcomes"])
            if not render_doc.title and render_doc.plan.get("intent"):
                render_doc.title = str(render_doc.plan["intent"])[:80]
        except ValueError as exc:
            # Keep the render usable, but surface the loss of PLAN envelope
            # metadata so callers are not left with a silent gap (Deborah #10).
            render_doc.warnings.append(f"plan export failed: {exc}")

    render_doc.metadata["grammar"] = {
        "process_count": len(doc.processes),
        "plan_count": len(doc.plans),
        "source_kind": doc.source_kind,
    }
    return render_doc