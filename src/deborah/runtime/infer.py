"""Infer capability — provisional reading from claim + retrieved evidence.

Default path is **rule-based** (deterministic, no model). Optional Ollama HTTP
generation when ``use_llm=True`` and a host is reachable.

Product shape matches COGNITION **infer** (claim, evidence_refs, assumptions,
residual_gaps, confidence bands).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any, Callable

CapabilityDispatch = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


def _collect_evidence(context: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    artifacts = context.get("artifacts") or {}
    for val in artifacts.values():
        if not isinstance(val, dict):
            continue
        ev = val.get("evidence")
        if isinstance(ev, list):
            for item in ev:
                if isinstance(item, dict):
                    evidence.append(item)
                elif isinstance(item, str) and item.strip():
                    evidence.append({"statement": item, "source": "artifact", "trace_ref": None})
    return evidence


def rule_based_infer(
    claim: str,
    evidence: list[dict[str, Any]],
    *,
    novel_terms: list[str] | None = None,
) -> dict[str, Any]:
    """Deterministic infer product from claim + evidence items."""
    claim = (claim or "").strip() or "unspecified claim"
    refs: list[str] = []
    statements: list[str] = []
    for i, e in enumerate(evidence):
        ref = str(e.get("trace_ref") or e.get("source") or f"ev_{i + 1}")
        refs.append(ref)
        st = str(e.get("statement") or e.get("text") or "").strip()
        if st:
            statements.append(st[:240])

    gaps: list[str] = []
    assumptions: list[str] = []
    if not evidence:
        gaps.append("no retrieved evidence")
        assumptions.append("reading may rest on prior knowledge only")
        band_e, band_i = "low", "low"
        restatement = f"Without corpus evidence, the claim remains provisional: {claim}"
    else:
        band_e = "medium" if len(evidence) >= 2 else "low"
        band_i = "medium"
        snippet = statements[0] if statements else "(evidence present)"
        restatement = (
            f"Given {len(evidence)} evidence item(s), a provisional reading of "
            f"{claim!r} is supported in part by: {snippet}"
        )
        if len(evidence) == 1:
            gaps.append("single evidence source — triangulation weak")
        assumptions.append("retrieved snippets are relevant to the claim")

    if novel_terms:
        gaps.append(f"novel/unmodelled terms: {', '.join(novel_terms[:8])}")
        band_i = "low"
        assumptions.append("unmodelled terms may shift meaning under ontology review")

    return {
        "claim": restatement,
        "claim_original": claim,
        "evidence_refs": refs,
        "assumptions": assumptions,
        "residual_gaps": gaps,
        "confidence": {
            "evidence": band_e,
            "inference": band_i,
            "execution": "high",
            "basis": "rule_based_infer",
        },
    }


def _ollama_generate(
    prompt: str,
    *,
    host: str = "http://localhost:11434",
    model: str = "gemma2:2b",
    timeout: float = 30.0,
) -> str | None:
    """Best-effort Ollama generate; returns None if unavailable."""
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        f"{host.rstrip('/')}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
        return str(data.get("response") or "").strip() or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
        return None


def make_infer_handler(
    *,
    use_llm: bool = False,
    ollama_host: str = "http://localhost:11434",
    model: str = "gemma2:2b",
) -> CapabilityDispatch:
    """Build EstateHandler dispatch for infer / deborah.infer."""

    def handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        claim = str(
            context.get("claim")
            or context.get("request")
            or context.get("query")
            or step.get("purpose")
            or ""
        ).strip()
        evidence = _collect_evidence(context)
        novel = context.get("novel_terms")
        if isinstance(novel, list):
            novel_terms = [str(t) for t in novel]
        else:
            novel_terms = None
            # Also pull from prior mahalath step artifacts
            for val in (context.get("artifacts") or {}).values():
                if isinstance(val, dict) and val.get("novel"):
                    novel_terms = [str(t) for t in val["novel"]]
                    break

        product = rule_based_infer(claim, evidence, novel_terms=novel_terms)

        if use_llm and evidence:
            prompt = (
                "Restate the claim as a provisional reading grounded only in the evidence.\n"
                f"Claim: {claim}\n"
                f"Evidence: {json.dumps(evidence[:8], default=str)[:2000]}\n"
                "Reply with one paragraph."
            )
            text = _ollama_generate(prompt, host=ollama_host, model=model)
            if text:
                product["claim"] = text[:800]
                product["confidence"]["basis"] = f"ollama:{model}"
                product["confidence"]["inference"] = "medium"

        return {"status": "completed", "result": product}

    return handler


def infer_handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Default rule-based infer (no LLM)."""
    return make_infer_handler(use_llm=False)(step, context)


def deborah_infer_dispatch(*, use_llm: bool = False) -> dict[str, CapabilityDispatch]:
    h = make_infer_handler(use_llm=use_llm)
    return {
        "deborah.infer": h,
        "infer": h,
    }
