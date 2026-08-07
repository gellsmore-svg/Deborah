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
