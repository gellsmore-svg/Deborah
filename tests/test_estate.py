"""Phase E: optional estate integration (Keturah-shaped index + demo dispatch)."""

from __future__ import annotations

from pathlib import Path

import pytest

from deborah import (
    DictCapabilityIndex,
    document_to_plan,
    interpret_with_estate,
    parse_document,
    resolve_assumes,
)
from deborah.runtime.cli import main as run_main
from deborah.runtime.estate import (
    demo_capability_index,
    record_run_on_tracer,
    try_make_tracer,
)

GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "cross-llm-critique.cairn.md"


def _plan() -> dict:
    return document_to_plan(parse_document(GOLDEN.read_text(encoding="utf-8")))


def test_resolve_assumes_without_index_accepts_stems() -> None:
    res = resolve_assumes(["milcah.critique@1", "tirzah.retrieve"], None)
    assert res.ok
    assert "milcah.critique" in res.resolved
    assert res.resolved["milcah.critique"].get("unverified") is True


def test_resolve_assumes_with_index_reports_missing() -> None:
    idx = DictCapabilityIndex()
    idx.add("tirzah.retrieve")
    res = resolve_assumes(["tirzah.retrieve@1", "milcah.critique@1"], idx)
    assert not res.ok
    assert res.missing == ["milcah.critique@1"]
    assert "tirzah.retrieve" in res.resolved


def test_estate_demo_run_completes_or_opens() -> None:
    run = interpret_with_estate(
        _plan(),
        demo=True,
        check_contracts=True,
        contract_mode="soft",
        validate_profile="full",
    )
    assert run.terminal in {"complete", "open"}
    assert len(run.steps) >= 3
    # CALL steps should have been dispatched (evaluate product on critique)
    call_steps = [s for s in run.steps if s.construct == "CALL"]
    assert call_steps
    assert call_steps[0].status == "completed"
    assert call_steps[0].result is not None
    assert "criteria" in call_steps[0].result


def test_estate_blocks_unresolved_assumes() -> None:
    idx = demo_capability_index()
    # drop critique from index
    idx.capabilities.pop("milcah.critique", None)
    run = interpret_with_estate(
        _plan(),
        index=idx,
        dispatch={},
        require_assumes=True,
        demo=False,
    )
    assert run.terminal == "blocked"
    assert any("unresolved assumes" in e for e in run.errors)


def test_cli_estate_demo(capsys) -> None:
    code = run_main([str(GOLDEN), "--estate-demo", "--check-contracts"])
    assert code == 0
    out = capsys.readouterr().out
    assert "terminal:" in out


def test_galeed_tracer_optional() -> None:
    """record_run_on_tracer is a no-op without galeed; with galeed, emits events."""
    run = interpret_with_estate(_plan(), demo=True, validate_profile="full")
    # always safe
    assert record_run_on_tracer(run, None) == []

    tracer = try_make_tracer(source="deborah-test")
    if tracer is None:
        pytest.skip("galeed not installed")
    recorded = record_run_on_tracer(run, tracer)
    assert recorded
    assert hasattr(tracer, "events")
    assert len(tracer.events) >= 1


def test_estate_live_with_injected_adapters() -> None:
    """live=True with explicit dispatch (no Mongo/Hoglah) completes under contracts."""
    from deborah.runtime.estate import DictCapabilityIndex

    def retrieve(step, context):
        return {
            "status": "completed",
            "result": {
                "evidence": [
                    {
                        "statement": "Injected memory hit about the claim.",
                        "source": "tirzah.retrieve:test",
                        "trace_ref": "t1",
                    }
                ]
            },
        }

    def critique(step, context):
        return {
            "status": "completed",
            "result": {
                "criteria": ["groundedness", "internal_consistency", "adversarial_resilience"],
                "scores": {
                    "groundedness": "medium",
                    "internal_consistency": "medium",
                    "adversarial_resilience": "low",
                },
                "ranking": ["open", "revise", "accept"],
                "objections": ["Evidence is thin."],
                "confidence": {
                    "evidence": "medium",
                    "inference": "low",
                    "execution": "high",
                    "basis": "injected",
                },
            },
        }

    idx = DictCapabilityIndex()
    idx.add("tirzah.retrieve", product="tirzah")
    idx.add("milcah.critique", product="milcah")
    run = interpret_with_estate(
        _plan(),
        index=idx,
        dispatch={
            "tirzah.retrieve": retrieve,
            "retrieve": retrieve,
            "milcah.critique": critique,
            "critique": critique,
        },
        live=False,
        demo=False,
        check_contracts=True,
        contract_mode="soft",
        validate_profile="full",
    )
    assert run.terminal in {"complete", "open"}
    observe = [s for s in run.steps if s.cognition == "observe"]
    assert observe and observe[0].status == "completed"
    assert observe[0].result and observe[0].result.get("evidence")
    call_steps = [s for s in run.steps if s.construct == "CALL"]
    assert call_steps and call_steps[0].result and "criteria" in call_steps[0].result


def test_cognition_routing_observe_without_call() -> None:
    from deborah.runtime.estate import EstateHandler
    from deborah.runtime.interpreter import StubHandler

    seen: list[str] = []

    def retrieve(step, context):
        seen.append("retrieve")
        return {
            "status": "completed",
            "result": {"evidence": [{"statement": "x", "source": "t", "trace_ref": "1"}]},
        }

    h = EstateHandler(
        dispatch={"tirzah.retrieve": retrieve},
        fallback=StubHandler(),
        route_cognition=True,
    )
    out = h({"construct": "STEP", "cognition": "observe", "id": "1"}, {})
    assert out["status"] == "completed"
    assert seen == ["retrieve"]


def test_try_load_live_failsoft() -> None:
    from deborah.runtime.estate import live_estate_available, try_load_live_dispatch

    # Must not raise whether or not packages are installed.
    avail = live_estate_available()
    assert {"tirzah", "milcah", "mahalath"} <= set(avail)
    dispatch = try_load_live_dispatch()
    assert isinstance(dispatch, dict)


def test_keturah_registry_optional() -> None:
    try:
        from keturah import Registry, capability, manifest
    except ImportError:
        pytest.skip("keturah not installed")

    from deborah.runtime.estate import registry_as_index

    m = manifest(
        "milcah",
        version="0.0.0-test",
        description="test",
        capabilities=[
            capability("critique", "Pressure-test a claim."),
        ],
    )
    reg = Registry([m])
    idx = registry_as_index(reg)
    assert idx.find("milcah.critique") is not None
    assert idx.find("critique") is not None or idx.find("milcah.critique") is not None


def test_interpret_with_estate_forwards_decisions() -> None:
    """GATED decide accepts injected verdict via interpret_with_estate."""
    from deborah import document_to_plan, parse_document
    from deborah.runtime.estate import interpret_with_estate
    from pathlib import Path

    plan = document_to_plan(
        parse_document(
            (Path(__file__).resolve().parents[1] / "examples" / "answer-substrate-question.cairn.md")
            .read_text(encoding="utf-8")
        )
    )
    run = interpret_with_estate(
        plan,
        demo=True,
        check_contracts=True,
        decisions={"default": "open"},
    )
    decide_steps = [
        s
        for s in run.steps
        if str(s.cognition or "").lower() == "decide"
        or str(s.construct or "").upper() == "DECISION"
    ]
    assert decide_steps, "expected a decide step"
    result = decide_steps[-1].result or {}
    assert str(result.get("selected") or "").lower() == "open"
