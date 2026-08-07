"""Phase B: validate_plan profiles and framing render."""

from __future__ import annotations

from pathlib import Path

from deborah import (
    CANONICAL_PLAN,
    document_to_plan,
    parse_document,
    render_plan,
    validate_plan,
)
from deborah.validate_cli import main as validate_main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
GOLDEN = EXAMPLES / "cross-llm-critique.cairn.md"


def test_full_profile_accepts_canonical() -> None:
    assert validate_plan(CANONICAL_PLAN, profile="full") == []


def test_core_profile_rejects_extension_construct() -> None:
    plan = dict(CANONICAL_PLAN)
    plan["steps"] = [dict(plan["steps"][0], construct="SYMBOLIC_INTERACTION")]
    errors = validate_plan(plan, profile="core")
    assert any("not in the core profile" in e for e in errors)
    assert validate_plan(plan, profile="full") == []


def test_strict_requires_output_for_cognition() -> None:
    plan = dict(CANONICAL_PLAN)
    plan["steps"] = [dict(plan["steps"][0], cognition="observe")]
    # no success_criteria / output
    plan["steps"][0] = {
        k: v for k, v in plan["steps"][0].items() if k not in {"success_criteria", "output"}
    }
    plan["steps"][0]["cognition"] = "observe"
    errors = validate_plan(plan, profile="strict")
    assert any("requires success_criteria or output" in e for e in errors)


def test_strict_assumes_vs_call_tools() -> None:
    plan = dict(CANONICAL_PLAN)
    plan["assumes"] = ["milcah.critique@1"]
    plan["steps"] = [
        {
            "id": "s1",
            "action": "other.tool — do stuff",
            "construct": "CALL",
            "status": "pending",
            "allowed_tools": ["other.tool"],
            "cognition": "evaluate",
            "success_criteria": ["scores"],
            "output": "scores",
        }
    ]
    errors = validate_plan(plan, profile="strict")
    assert any("not in assumes" in e for e in errors)

    plan["steps"][0]["action"] = "milcah.critique — pressure test"
    plan["steps"][0]["allowed_tools"] = ["milcah.critique"]
    assert validate_plan(plan, profile="strict") == []


def test_golden_exports_and_passes_strict() -> None:
    doc = parse_document(GOLDEN.read_text(encoding="utf-8"))
    plan = document_to_plan(doc)
    assert validate_plan(plan, profile="full") == []
    assert validate_plan(plan, profile="core") == []
    assert validate_plan(plan, profile="strict") == [], validate_plan(plan, profile="strict")
    cognitions = [s.get("cognition") for s in plan["steps"]]
    assert cognitions == ["observe", "infer", "evaluate", "decide"]


def test_render_shows_framing_and_cognition() -> None:
    text = GOLDEN.read_text(encoding="utf-8")
    body = render_plan(text, profile="narrative_steps")
    assert isinstance(body, str)
    assert "Assumes:" in body or "assumes" in body.lower()
    assert "milcah.critique" in body
    assert "Intent:" in body or "intent" in body.lower() or "Objective:" in body
    # COGNITION surfaces via sub-blocks
    assert "Cognition" in body or "observe" in body

    op = render_plan(text, profile="operator")
    assert isinstance(op, str)
    assert "Cognition:" in op or "cognition" in op.lower()
    assert "observe" in op

    audit = render_plan(text, profile="audit")
    assert isinstance(audit, str)
    assert "COGNITION" in audit or "Cognition" in audit or "observe" in audit


def test_validate_cli_profile(tmp_path, capsys) -> None:
    code = validate_main([str(GOLDEN), "--profile", "strict"])
    assert code == 0
    out = capsys.readouterr()
    assert "ok:" in out.out
    assert "plan_profile=strict" in out.out
