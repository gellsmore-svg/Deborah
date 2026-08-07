"""Pluggable render profiles for simplified Cairn views."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from deborah.render.model import ProcessDocument, RenderResult, StepNode
from deborah.render.phrasing import SUB_BLOCK_LABELS, describe_queue, phrase_construct


def _steps_for_profile(doc: ProcessDocument, profile: str) -> list[StepNode]:
    if profile == "operator" and doc.operator_steps:
        return doc.operator_steps
    if profile in {"narrative_steps", "narrative"} and doc.narrative_steps and not doc.steps:
        return doc.narrative_steps
    return doc.steps


class RenderProfile(ABC):
    name: str

    @abstractmethod
    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        ...


def _indent(depth: int) -> str:
    return "  " * depth


def _render_step_line(node: StepNode, language: str, depth: int, options: dict[str, Any]) -> list[str]:
    include_tags = options.get("include_tags", False)
    text = phrase_construct(node.construct, node.text, language, node.tags, getattr(node, "parsed_modifiers", {}))
    line = f"{_indent(depth)}{node.number}. {text}"
    lines = [line]
    if include_tags and node.tags:
        lines.append(f"{_indent(depth)}   _(tags: {', '.join(node.tags)})_")
    return lines


def _plan_header(doc: ProcessDocument, language: str) -> list[str]:
    """Render PLAN envelope including framing fields (SPEC v0.10/v0.11)."""
    if not doc.plan:
        return []
    plan = doc.plan
    lines: list[str] = []
    if language == "fr":
        lines.append(f"**Plan:** {plan.get('plan_id', '')} (révision {plan.get('revision', '?')})")
        lines.append(f"**Statut:** {plan.get('status', '')}")
        intent_l, assumes_l, unc_l, out_l = "Intention", "Suppose", "Incertitude", "Résultats"
        req_l = "Demande"
    elif language == "es":
        lines.append(f"**Plan:** {plan.get('plan_id', '')} (revisión {plan.get('revision', '?')})")
        lines.append(f"**Estado:** {plan.get('status', '')}")
        intent_l, assumes_l, unc_l, out_l = "Intención", "Asume", "Incertidumbre", "Resultados"
        req_l = "Solicitud"
    else:
        lines.append(f"**Plan:** {plan.get('plan_id', '')} (revision {plan.get('revision', '?')})")
        lines.append(f"**Status:** {plan.get('status', '')}")
        intent_l, assumes_l, unc_l, out_l = "Intent", "Assumes", "On uncertainty", "Outcomes"
        req_l = "Request"
    if plan.get("request"):
        lines.append(f"**{req_l}:** {plan['request']}")
    intent = plan.get("intent") or plan.get("objective")
    if intent:
        lines.append(f"**{intent_l}:** {intent}")
    assumes = plan.get("assumes") or []
    if assumes:
        lines.append(f"**{assumes_l}:** {', '.join(str(a) for a in assumes)}")
    if plan.get("on_uncertainty"):
        lines.append(f"**{unc_l}:** {plan['on_uncertainty']}")
    outcomes = plan.get("outcomes") or plan.get("stopping_conditions") or []
    if outcomes:
        lines.append(f"**{out_l}:**")
        for item in outcomes:
            lines.append(f"- {item}")
    lines.append("")
    return lines


def _walk_steps(nodes: list[StepNode], language: str, depth: int, options: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    footnotes: list[str] = []
    include_sub = options.get("include_sub_blocks", True)

    for node in nodes:
        lines.extend(_render_step_line(node, language, depth, options))
        if include_sub and node.sub_blocks:
            labels = SUB_BLOCK_LABELS.get(language, SUB_BLOCK_LABELS["en"])
            for key, value in node.sub_blocks.items():
                label = labels.get(key, key.replace("_", " ").title())
                lines.append(f"{_indent(depth + 1)}**{label}:** {value}")
                footnotes.append(f"{node.number} {label}: {value}")
        lines.extend(_walk_steps(node.children, language, depth + 1, options))

    return lines


def _boxed(title: str, body_lines: list[str]) -> list[str]:
    out = [f"> ### {title}", ">"]
    for line in body_lines:
        out.append(f"> {line}" if line else ">")
    out.append(">")
    return out


class NarrativeStepsProfile(RenderProfile):
    name = "narrative_steps"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"## {doc.title}")
            lines.append("")
        lines.extend(_plan_header(doc, language))

        steps = _steps_for_profile(doc, self.name)
        step_lines = _walk_steps(steps, language, 0, options)
        if options.get("boxed"):
            for node in steps:
                block = _render_step_line(node, language, 0, options)
                block.extend(_walk_steps(node.children, language, 1, options))
                lines.extend(_boxed(f"Step {node.number}", block))
                lines.append("")
        else:
            lines.extend(step_lines)

        footnotes = []
        if options.get("include_footnotes") and doc.requirements:
            footnotes.extend(f"Requirement: {r}" for r in doc.requirements[:10])

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            footnotes=footnotes,
            metadata={"warnings": doc.warnings},
        )


class SimpleProseProfile(RenderProfile):
    name = "simple_prose"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        parts: list[str] = []
        if doc.title:
            parts.append(doc.title)
        elif doc.plan:
            parts.append(doc.plan.get("objective", "This process"))

        actions = []
        for node in _steps_for_profile(doc, self.name):
            actions.append(phrase_construct(node.construct, node.text, language, node.tags, getattr(node, "parsed_modifiers", {})).rstrip("."))

        if actions:
            if language == "es":
                parts.append("El flujo consiste en: " + "; luego, ".join(actions) + ".")
            elif language == "fr":
                parts.append("Le flux procède ainsi : " + " ; puis, ".join(actions) + ".")
            else:
                parts.append("The flow proceeds by: " + "; then, ".join(actions) + ".")

        if doc.outcomes:
            label = "Resultados esperados" if language == "es" else "Expected outcomes"
            parts.append(f"{label}: {', '.join(doc.outcomes)}.")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n\n".join(parts),
            metadata={"warnings": doc.warnings},
        )


def _step_cognition(node: StepNode) -> str | None:
    """COGNITION product type from sub_blocks when present."""
    raw = (node.sub_blocks or {}).get("COGNITION") or (node.sub_blocks or {}).get("cognition")
    if not raw:
        return None
    return str(raw).strip().split()[0].lower() or None


class OperatorProfile(RenderProfile):
    name = "operator"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"# {doc.title}")
            lines.append("")
        lines.extend(_plan_header(doc, language))

        for node in _steps_for_profile(doc, self.name):
            body_text = node.text
            if not body_text.strip() and node.construct == "QUEUE":
                body_text = describe_queue(node.tags, language, node.parsed_modifiers)
            title = body_text.split(".")[0][:60] if body_text else f"Step {node.number}"
            block: list[str] = []
            purpose = node.purpose or (node.sub_blocks or {}).get("PURPOSE") or body_text
            cognition = _step_cognition(node)
            if language == "fr":
                block.append(f"**Objectif :** {purpose}")
                if cognition:
                    block.append(f"**Cognition :** {cognition}")
                if node.owner:
                    block.append(f"**Responsable :** {node.owner}")
                if node.assisted_by:
                    block.append(f"**Assisté par :** {node.assisted_by}")
                if node.outputs:
                    block.append(f"**Sorties :** {', '.join(node.outputs)}")
                if node.iterate_until:
                    block.append(f"**Répéter jusqu'à :** {node.iterate_until}")
                if node.next_phase:
                    block.append(f"**Suivant :** {node.next_phase}")
            elif language == "es":
                block.append(f"**Propósito:** {purpose}")
                if cognition:
                    block.append(f"**Cognición:** {cognition}")
                if node.owner:
                    block.append(f"**Responsable:** {node.owner}")
                if node.assisted_by:
                    block.append(f"**Asistido por:** {node.assisted_by}")
                if node.outputs:
                    block.append(f"**Salidas:** {', '.join(node.outputs)}")
                if node.iterate_until:
                    block.append(f"**Repetir hasta:** {node.iterate_until}")
                if node.next_phase:
                    block.append(f"**Siguiente:** {node.next_phase}")
            else:
                block.append(f"**Purpose:** {purpose}")
                if cognition:
                    block.append(f"**Cognition:** {cognition}")
                if node.owner:
                    block.append(f"**Owner:** {node.owner}")
                if node.assisted_by:
                    block.append(f"**Assisted by:** {node.assisted_by}")
                if node.outputs:
                    block.append(f"**Outputs:** {', '.join(node.outputs)}")
                if node.iterate_until:
                    block.append(f"**Iterate until:** {node.iterate_until}")
                if node.next_phase:
                    block.append(f"**Next:** {node.next_phase}")

                if getattr(node, "parsed_modifiers", {}):
                    mods = ", ".join(f"{k}:{v}" for k,v in node.parsed_modifiers.items())
                    block.append(f"**Modifiers:** {mods}")

            if options.get("boxed", True):
                lines.extend(_boxed(title, block))
            else:
                lines.extend(block)
            lines.append("")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


class ExecutiveProfile(RenderProfile):
    name = "executive"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        heading = (
            "Aperçu exécutif"
            if language == "fr"
            else "Resumen ejecutivo"
            if language == "es"
            else "Executive overview"
        )
        lines.append(f"## {heading}")
        lines.append("")
        lines.extend(_plan_header(doc, language))

        objective = (doc.plan or {}).get("intent") or (doc.plan or {}).get("objective") if doc.plan else doc.title
        if objective and not doc.plan:
            label = "Objectif" if language == "fr" else "Objetivo" if language == "es" else "Objective"
            lines.append(f"**{label}:** {objective}")
            lines.append("")

        milestone_label = "Jalons" if language == "fr" else "Hitos" if language == "es" else "Milestones"
        lines.append(f"### {milestone_label}")
        for node in _steps_for_profile(doc, self.name):
            if node.construct == "MILESTONE" or not node.children:
                summary = node.purpose or phrase_construct(node.construct, node.text, language, node.tags, getattr(node, "parsed_modifiers", {}))
                owner = f" ({node.owner})" if node.owner else ""
                lines.append(f"- **{node.number}** {summary}{owner}")

        if doc.outcomes:
            label = "Résultats" if language == "fr" else "Resultados" if language == "es" else "Outcomes"
            lines.append("")
            lines.append(f"### {label}")
            for outcome in doc.outcomes:
                lines.append(f"- {outcome}")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


class AuditProfile(RenderProfile):
    name = "audit"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        title = "Registre d'audit" if language == "fr" else "Registro de auditoría" if language == "es" else "Audit record"
        lines.append(f"## {title}")
        lines.append("")
        lines.extend(_plan_header(doc, language))

        if doc.requirements:
            req = "Exigences" if language == "fr" else "Requisitos" if language == "es" else "Requirements"
            lines.append(f"### {req}")
            for req_line in doc.requirements:
                lines.append(f"- {req_line}")
            lines.append("")

        def walk(nodes: list[StepNode], depth: int) -> None:
            for node in nodes:
                construct = f" [{node.construct}]" if node.construct else ""
                tag_str = f" tags={node.tags}" if node.tags else ""
                mod_str = ""
                if node.parsed_modifiers:
                    mods = ", ".join(f"{key}:{value}" for key, value in node.parsed_modifiers.items())
                    mod_str = f" modifiers={mods}"
                lines.append(f"{'  ' * depth}- **{node.number}**{construct}{tag_str}{mod_str} {node.text}")
                for key, value in node.sub_blocks.items():
                    lines.append(f"{'  ' * (depth + 1)}- {key}: {value}")
                walk(node.children, depth + 1)

        walk(doc.steps, 0)
        footnotes = [f"Requirement: {r}" for r in doc.requirements[:20]] if doc.requirements else []

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            footnotes=footnotes,
            metadata={"warnings": doc.warnings},
        )


class TherapeuticProfile(RenderProfile):
    name = "therapeutic"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        res = OperatorProfile().render(doc, language, options)
        body = res.body
        if language == "en":
            body = body.replace("# ", "# Therapeutic View: ", 1) if body.startswith("# ") else "# Therapeutic View\n\n" + body
            if "Modifiers:" in body:
                body += "\n\n_Note: Focus on regulation, appraisal, and feedback loops for emotional/psychological work._"
        res.body = body
        res.profile = self.name
        return res


class ChangeLeaderProfile(RenderProfile):
    name = "change_leader"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        res = OperatorProfile().render(doc, language, options)
        body = res.body
        if language == "en":
            body = body.replace("# ", "# Change Leadership View: ", 1) if body.startswith("# ") else "# Change Leadership View\n\n" + body
            if "Modifiers:" in body:
                body += "\n\n_Note: Emphasize coalition, resistance, reinforcement, and alignment for organisational change._"
        res.body = body
        res.profile = self.name
        return res


_HUMAN_DEMAND_KEYS = (
    "HUMAN_DEMAND",
    "HUMAN_LOAD",
    "HUMAN_FACTORS",
    "HUMAN_RISK",
    "HUMAN_SIMULATION",
    "TRUST",
    "SUPPORT",
    "FAILURE_MODE",
    "SIMULATION_FINDINGS",
    "IMPROVEMENT",
    "CHANGE_IMPACT",
)

_HUMAN_FACTORS_KEYS = (
    "HUMAN_FACTORS",
    "HUMAN_RISK",
    "SIMULATION_FINDINGS",
    "IMPROVEMENT",
    "SUPPORT",
    "TRUST",
    "CHANGE_IMPACT",
)


class HumanDemandProfile(RenderProfile):
    name = "human_demand"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"# Human Demand View: {doc.title}")
            lines.append("")

        labels = SUB_BLOCK_LABELS.get(language, SUB_BLOCK_LABELS["en"])

        def emit(nodes: list[StepNode], depth: int = 0) -> None:
            for node in nodes:
                demand_blocks = {key: node.sub_blocks[key] for key in _HUMAN_DEMAND_KEYS if key in node.sub_blocks}
                human_touch = any(tag.upper().startswith("HUMAN") or "ASSISTED-BY" in tag.upper() for tag in node.tags)
                if demand_blocks or human_touch:
                    summary = phrase_construct(
                        node.construct,
                        node.text,
                        language,
                        node.tags,
                        getattr(node, "parsed_modifiers", {}),
                    )
                    lines.append(f"{_indent(depth)}## {node.number}. {summary}")
                    if node.tags:
                        lines.append(f"{_indent(depth)}_Tags: {', '.join(node.tags)}_")
                    purpose = node.sub_blocks.get("PURPOSE")
                    if purpose:
                        lines.append(f"{_indent(depth)}**Purpose:** {purpose}")
                    for key, value in demand_blocks.items():
                        label = labels.get(key, key.replace("_", " ").title())
                        lines.append(f"{_indent(depth)}**{label}:**")
                        for subline in value.splitlines() or [""]:
                            lines.append(f"{_indent(depth)}  {subline}")
                    lines.append("")
                emit(node.children, depth + 1)

        emit(_steps_for_profile(doc, self.name))
        if not lines:
            lines.append("# Human Demand View")
            lines.append("")
            lines.append("No human demand annotations were found.")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


class HumanFactorsProfile(RenderProfile):
    name = "human_factors"

    def render(self, doc: ProcessDocument, language: str, options: dict[str, Any]) -> RenderResult:
        lines: list[str] = []
        if doc.title:
            lines.append(f"# Human Factors Review: {doc.title}")
            lines.append("")

        labels = SUB_BLOCK_LABELS.get(language, SUB_BLOCK_LABELS["en"])

        def emit(nodes: list[StepNode], depth: int = 0) -> None:
            for node in nodes:
                factor_blocks = {key: node.sub_blocks[key] for key in _HUMAN_FACTORS_KEYS if key in node.sub_blocks}
                if factor_blocks:
                    summary = phrase_construct(
                        node.construct,
                        node.text,
                        language,
                        node.tags,
                        getattr(node, "parsed_modifiers", {}),
                    )
                    lines.append(f"{_indent(depth)}## {node.number}. {summary}")
                    purpose = node.sub_blocks.get("PURPOSE")
                    if purpose:
                        lines.append(f"{_indent(depth)}**Purpose:** {purpose}")
                    for key, value in factor_blocks.items():
                        label = labels.get(key, key.replace("_", " ").title())
                        lines.append(f"{_indent(depth)}**{label}:**")
                        for subline in value.splitlines() or [""]:
                            lines.append(f"{_indent(depth)}  {subline}")
                    lines.append(f"{_indent(depth)}**Conversation starter:** What human-system forces are plausibly present here, and which should be redesigned first?")
                    lines.append("")
                emit(node.children, depth + 1)

        emit(_steps_for_profile(doc, self.name))
        if not lines:
            lines.append("# Human Factors Review")
            lines.append("")
            lines.append("No human factors annotations were found.")

        return RenderResult(
            profile=self.name,
            language=language,
            format=options.get("output_format", "markdown"),
            body="\n".join(lines).strip(),
            metadata={"warnings": doc.warnings},
        )


_PROFILES: dict[str, RenderProfile] = {
    "narrative_steps": NarrativeStepsProfile(),
    "simple_prose": SimpleProseProfile(),
    "operator": OperatorProfile(),
    "executive": ExecutiveProfile(),
    "audit": AuditProfile(),
    "therapeutic": TherapeuticProfile(),
    "change_leader": ChangeLeaderProfile(),
    "human_demand": HumanDemandProfile(),
    "human_factors": HumanFactorsProfile(),
    # SPEC v0.9 aliases
    "narrative": NarrativeStepsProfile(),
}


def get_profile(name: str) -> RenderProfile:
    if name not in _PROFILES:
        raise ValueError(f"Unknown render profile: {name!r}. Known: {sorted(_PROFILES)}")
    return _PROFILES[name]


def registered_profiles() -> list[str]:
    return sorted(_PROFILES)
