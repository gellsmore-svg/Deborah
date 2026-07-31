"""Construct rephrasing and multilingual glossaries."""

from __future__ import annotations

import re

CONSTRUCT_PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "STEP": "",
        "CALL": "Invoke",
        "ITERATE": "Repeat the following",
        "DECISION": "Decide",
        "RECURSE": "Recurse",
        "QUEUE": "Queue",
        "PARALLEL": "Run in parallel",
        "MERGE": "Merge",
        "SERVICE": "Run service",
        "RETRY": "Retry",
        "AWAIT": "Wait for",
        "BREAK": "Stop when",
        "CONTINUE": "Continue to",
        "MILESTONE": "Milestone",
        "REGULATION": "Regulate",
        "APPRAISAL": "Appraise",
        "DUAL_PROCESS": "Dual-process",
        "METACOGNITION": "Metacognize",
        "ALIGN": "Align",
        "COALITION": "Build coalition",
        "RESISTANCE": "Address resistance",
        "REINFORCEMENT": "Reinforce",
        "CASCADE": "Cascade",
        "VISION": "Form vision",
        "SOCIALIZE": "Socialize",
        "INSTITUTIONALIZE": "Institutionalize",
        "SYMBOLIC_INTERACTION": "Symbolic interact",
        "CONFLICT": "Conflict",
        "ACCOMMODATE": "Accommodate",
        "ASSIMILATE": "Assimilate",
        "ROLE": "Role",
        "FEEDBACK": "Feedback",
        "MACRO": "Macro",
    },
    "fr": {
        "STEP": "",
        "CALL": "Appeler",
        "ITERATE": "Répéter ce qui suit",
        "DECISION": "Décider",
        "RECURSE": "Récursion",
        "QUEUE": "Mettre en file",
        "FEEDBACK": "Rétroaction",
        "REGULATION": "Réguler",
        "APPRAISAL": "Évaluer",
        "COALITION": "Construire coalition",
        "VISION": "Former vision",
        "SOCIALIZE": "Socialiser",
        "SYMBOLIC_INTERACTION": "Interaction symbolique",
        "MACRO": "Macro",
        "PARALLEL": "Exécuter en parallèle",
        "MERGE": "Fusionner",
        "SERVICE": "Exécuter le service",
        "RETRY": "Réessayer",
        "AWAIT": "Attendre",
        "BREAK": "Arrêter quand",
        "CONTINUE": "Continuer vers",
        "MILESTONE": "Jalon",
    },
    "es": {
        "STEP": "",
        "CALL": "Invocar",
        "ITERATE": "Repetir lo siguiente",
        "DECISION": "Decidir",
        "RECURSE": "Recursar",
        "QUEUE": "Encolar",
        "PARALLEL": "Ejecutar en paralelo",
        "MERGE": "Combinar",
        "SERVICE": "Ejecutar servicio",
        "RETRY": "Reintentar",
        "AWAIT": "Esperar",
        "BREAK": "Detener cuando",
        "CONTINUE": "Continuar a",
        "MILESTONE": "Hito",
        "FEEDBACK": "Retroalimentación",
        "MACRO": "Macro",
    },
}

SUB_BLOCK_LABELS: dict[str, dict[str, str]] = {
    "en": {
        "CONSTRAINTS": "Constraints",
        "OUTPUT": "Output",
        "PURPOSE": "Purpose",
        "RISKS": "Risks",
        "CONTEXT": "Context",
        "BOUNDARIES": "Boundaries",
        "HUMAN_DEMAND": "Human demand",
        "HUMAN_SIMULATION": "Human simulation",
        "HUMAN_LOAD": "Human load",
        "HUMAN_FACTORS": "Human factors",
        "HUMAN_RISK": "Human risk",
        "TRUST": "Trust",
        "SUPPORT": "Support",
        "FAILURE_MODE": "Failure mode",
        "SIMULATION_FINDINGS": "Simulation findings",
        "IMPROVEMENT": "Improvement",
        "CHANGE_IMPACT": "Change impact",
    },
    "fr": {
        "CONSTRAINTS": "Contraintes",
        "OUTPUT": "Sortie",
        "PURPOSE": "Objectif",
        "RISKS": "Risques",
        "CONTEXT": "Contexte",
        "BOUNDARIES": "Limites",
    },
    "es": {
        "CONSTRAINTS": "Restricciones",
        "OUTPUT": "Salida",
        "PURPOSE": "Propósito",
        "RISKS": "Riesgos",
        "CONTEXT": "Contexto",
        "BOUNDARIES": "Límites",
    },
}

_TAG_RE = re.compile(r"\[([^\]]+)\]")


def extract_tags(text: str) -> tuple[str, list[str]]:
    tags = _TAG_RE.findall(text)
    cleaned = _TAG_RE.sub("", text).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned, tags


# QUEUE parameters live in the step's bracket annotation, e.g.
# ``[ORDER: ROUND_ROBIN; ONE_AT_A_TIME; ROUNDS: 5; UNTIL: consensus]``. These
# patterns lift them back out so the turn-based / round-robin meaning can be
# phrased, instead of the view showing a bare "Queue:".
_Q_ORDER = re.compile(r"ORDER\s*:\s*([A-Za-z_]+)", re.I)
_Q_ROUNDS = re.compile(r"(?:ROUNDS|MAX)\s*:\s*(\d+)", re.I)
_Q_UNTIL = re.compile(r"UNTIL\s*:\s*([^;\]]+)", re.I)
_Q_SERIAL = re.compile(r"ONE[ _]AT[ _]A[ _]TIME|SERIAL", re.I)

# Localised fragments for composing the QUEUE description.
_QUEUE_PHRASING: dict[str, dict[str, str]] = {
    "en": {
        "subject": "Queue the participants",
        "ROUND_ROBIN": "round-robin", "PRIORITY": "by priority",
        "FIFO": "in turn", "_default": "in turn",
        "serial": ", one at a time",
        "rounds_1": ", for up to {n} round", "rounds_n": ", for up to {n} rounds",
        "until": ", until {u}",
    },
    "fr": {
        "subject": "Mettre les participants en file",
        "ROUND_ROBIN": "à tour de rôle", "PRIORITY": "par priorité",
        "FIFO": "dans l'ordre", "_default": "dans l'ordre",
        "serial": ", un à la fois",
        "rounds_1": ", pour un maximum de {n} tour", "rounds_n": ", pour un maximum de {n} tours",
        "until": ", jusqu'à {u}",
    },
    "es": {
        "subject": "Encolar a los participantes",
        "ROUND_ROBIN": "por turnos rotativos", "PRIORITY": "por prioridad",
        "FIFO": "en orden", "_default": "en orden",
        "serial": ", uno a la vez",
        "rounds_1": ", hasta {n} ronda", "rounds_n": ", hasta {n} rondas",
        "until": ", hasta {u}",
    },
}


def parse_queue_params(
    tags: list[str] | None,
    parsed_modifiers: dict[str, str] | None = None,
) -> dict[str, str | bool]:
    """Pull ORDER / ROUNDS / UNTIL / one-at-a-time out of a QUEUE step's tags."""
    blob = "; ".join(tags or [])
    params: dict[str, str | bool] = {}
    if (m := _Q_ORDER.search(blob)):
        params["order"] = m.group(1).upper()
    if (m := _Q_ROUNDS.search(blob)):
        params["rounds"] = m.group(1)
    if (m := _Q_UNTIL.search(blob)):
        params["until"] = m.group(1).strip()
    if _Q_SERIAL.search(blob):
        params["serial"] = True
    if parsed_modifiers:
        if order := parsed_modifiers.get("ORDER"):
            params["order"] = order.upper()
        if rounds := (parsed_modifiers.get("ROUNDS") or parsed_modifiers.get("MAX")):
            params["rounds"] = rounds
        if until := parsed_modifiers.get("UNTIL"):
            params["until"] = until
        if "ONE_AT_A_TIME" in parsed_modifiers or "SERIAL" in parsed_modifiers:
            params["serial"] = True
    return params


def describe_queue(
    tags: list[str] | None,
    language: str = "en",
    parsed_modifiers: dict[str, str] | None = None,
) -> str:
    """A readable, localised description of a QUEUE step from its parameters."""
    words = _QUEUE_PHRASING.get(language, _QUEUE_PHRASING["en"])
    params = parse_queue_params(tags, parsed_modifiers)
    order = str(params.get("order", "")) or "_default"
    parts = [words["subject"], " ", words.get(order, words["_default"])]
    if params.get("serial"):
        parts.append(words["serial"])
    if params.get("rounds"):
        n = str(params["rounds"])
        key = "rounds_1" if n == "1" else "rounds_n"
        parts.append(words[key].format(n=n))
    if params.get("until"):
        parts.append(words["until"].format(u=params["until"]))
    return "".join(parts)


def phrase_construct(
    construct: str | None, text: str, language: str = "en", tags: list[str] | None = None,
    parsed_modifiers: dict = None
) -> str:
    if not construct or construct == "STEP":
        return text
    if construct == "QUEUE":
        desc = describe_queue(tags, language, parsed_modifiers)
        return f"{desc} — {text}" if text.strip() else desc
    glossary = CONSTRUCT_PHRASES.get(language, CONSTRUCT_PHRASES["en"])
    prefix = glossary.get(construct, construct)
    if construct == "ITERATE":
        return f"{prefix}: {text}"
    if construct == "DECISION":
        return f"{prefix} {text}"
    if construct == "CALL":
        return f"{prefix} {text}"
    if construct == "REGULATION" and parsed_modifiers:
        strat = parsed_modifiers.get("STRATEGY", "")
        target = parsed_modifiers.get("TARGET", "")
        extra = f" {strat}" if strat else ""
        if target:
            extra += f" on {target}"
        return f"{prefix}{extra}: {text}" if extra else f"{prefix}: {text}"
    if construct == "FEEDBACK" and parsed_modifiers:
        frm = parsed_modifiers.get("FROM", "")
        via = parsed_modifiers.get("VIA", "")
        extra = f" from {frm}" if frm else ""
        if via:
            extra += f" via {via}"
        return f"{prefix}{extra}: {text}" if extra else f"{prefix}: {text}"
    if construct == "APPRAISAL" and parsed_modifiers:
        typ = parsed_modifiers.get("TYPE", "")
        return f"{prefix} ({typ}): {text}" if typ else f"{prefix}: {text}"
    if construct == "COALITION" and parsed_modifiers:
        action = parsed_modifiers.get("BUILD", "build")
        return f"{prefix} {action}: {text}"
    if construct == "ALIGN" and parsed_modifiers:
        elems = parsed_modifiers.get("ELEMENTS", "")
        return f"{prefix} ({elems}): {text}" if elems else f"{prefix}: {text}"
    if construct == "SOCIALIZE" and parsed_modifiers:
        typ = parsed_modifiers.get("TYPE", "")
        return f"{prefix} ({typ}): {text}" if typ else f"{prefix}: {text}"
    if construct == "MACRO":
        return f"Macro: {text}"
    return f"{prefix}: {text}" if prefix else text
