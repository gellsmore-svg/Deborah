"""Phase C: cognitive result contracts and confidence bands."""

from __future__ import annotations

import json
from pathlib import Path

from deborah import (
    EXAMPLE_RESULTS,
    document_to_plan,
    parse_document,
    validate_cognition_result,
    validate_confidence,
    validate_step_results,
)
# EXAMPLE_RESULTS includes Phase F cognitions
from deborah.contracts import CONFIDENCE_BANDS, CONTRACT_VERSION
from deborah.validate_cli import main as validate_main

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cognition_results.json"
GOLDEN = Path(__file__).resolve().parents[1] / "examples" / "cross-llm-critique.cairn.md"


def test_contract_version() -> None:
    assert CONTRACT_VERSION == "1.1"
    assert "high" in CONFIDENCE_BANDS


def test_example_results_pass_strict() -> None:
    for cognition, result in EXAMPLE_RESULTS.items():
        assert validate_cognition_result(cognition, result, mode="strict") == [], cognition


def test_fixture_file_matches_examples() -> None:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    for cognition, result in data.items():
        assert validate_cognition_result(cognition, result, mode="strict") == []


def test_soft_allows_missing_required_keys() -> None:
    # Soft: incomplete infer is ok if types that exist are fine
    assert validate_cognition_result("infer", {"claim": "x"}, mode="soft") == []
    # Strict: missing evidence_refs
    errors = validate_cognition_result("infer", {"claim": "x"}, mode="strict")
    assert any("evidence_refs" in e for e in errors)


def test_observe_rejects_bad_evidence_type() -> None:
    errors = validate_cognition_result("observe", {"evidence": "not a list"}, mode="soft")
    assert any("must be a list" in e for e in errors)


def test_confidence_rejects_single_float() -> None:
    errors = validate_confidence({"value": 0.91})
    assert any("band dimensions" in e or "single float" in e for e in errors)


def test_confidence_accepts_bands() -> None:
    assert (
        validate_confidence(
            {"evidence": "high", "inference": "low", "execution": "high", "basis": "n=1"}
        )
        == []
    )


def test_unknown_cognition() -> None:
    assert any("unknown cognition" in e for e in validate_cognition_result("teleport", {}))


def test_extended_cognition_learn_gate() -> None:
    # soft empty ok; strict needs change/scope/reversible
    assert validate_cognition_result("learn", {}, mode="soft") == []
    errors = validate_cognition_result("learn", {"change": "x"}, mode="strict")
    assert any("scope" in e for e in errors)
    # auto_apply without approval is always a gate error
    bad = {
        "change": "prefer hybrid retrieval",
        "scope": "session",
        "reversible": True,
        "auto_apply": True,
    }
    assert any("auto_apply" in e for e in validate_cognition_result("learn", bad, mode="soft"))
    good = {**bad, "auto_apply": False}
    assert validate_cognition_result("learn", good, mode="strict") == []


def test_negotiate_and_optimize_examples() -> None:
    assert validate_cognition_result("negotiate", EXAMPLE_RESULTS["negotiate"], mode="strict") == []
    assert validate_cognition_result("optimize", EXAMPLE_RESULTS["optimize"], mode="strict") == []


def test_validate_step_results_on_plan() -> None:
    plan = document_to_plan(parse_document(GOLDEN.read_text(encoding="utf-8")))
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    for step, cog in zip(plan["steps"], ["observe", "infer", "evaluate", "decide"], strict=True):
        step["cognition"] = cog
        step["result"] = fixtures[cog]
    assert validate_step_results(plan, mode="strict") == []

    # Break infer
    plan["steps"][1]["result"] = {"claim": "only"}
    errors = validate_step_results(plan, mode="strict")
    assert any("evidence_refs" in e for e in errors)


def test_strict_mode_requires_result_when_cognition_set() -> None:
    plan = {
        "steps": [
            {"id": "s1", "cognition": "observe", "action": "x", "construct": "STEP", "status": "pending"}
        ]
    }
    assert any("requires result" in e for e in validate_step_results(plan, mode="strict"))
    assert validate_step_results(plan, mode="soft") == []


def test_cli_results_check(tmp_path, capsys) -> None:
    # Cognition-keyed fixture file (same shape as tests/fixtures/cognition_results.json)
    code = validate_main(
        [
            str(GOLDEN),
            "--profile",
            "strict",
            "--results",
            str(FIXTURES),
            "--results-mode",
            "strict",
        ]
    )
    assert code == 0, capsys.readouterr()
