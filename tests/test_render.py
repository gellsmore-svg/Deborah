from pathlib import Path

import deborah
from deborah import CANONICAL_PLAN, render_plan, registered_profiles


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_registered_profiles_include_required_views():
    names = registered_profiles()
    for profile in ("narrative_steps", "simple_prose", "operator", "executive", "human_demand", "human_factors"):
        assert profile in names


def test_render_plan_from_canonical_dict_narrative():
    text = render_plan(CANONICAL_PLAN, profile="narrative_steps")
    assert "Retrieve relevant context" in text
    assert "Invoke" in text or "Synthesise" in text


def test_render_plan_spanish_prose():
    text = render_plan(CANONICAL_PLAN, profile="simple_prose", language="es")
    assert "El flujo consiste en" in text


def test_render_plan_executive_includes_objective():
    text = render_plan(CANONICAL_PLAN, profile="executive")
    assert "grounded answer" in text.lower() or "Objective" in text


def test_render_plan_json_output():
    payload = render_plan(CANONICAL_PLAN, profile="narrative_steps", output_format="json")
    assert payload["profile"] == "narrative_steps"
    assert "body" in payload


def test_render_plan_mermaid():
    diagram = render_plan(CANONICAL_PLAN, output_format="mermaid")
    assert diagram.startswith("flowchart TD")
    assert "s1" in diagram


def test_render_plan_from_keturah_example_markdown():
    md = (EXAMPLES / "keturah.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="narrative_steps")
    assert "Load seam contracts" in text or "BuildCapabilitiesFromSeams" in text


def test_render_plan_operator_profile_from_example():
    md = (EXAMPLES / "tirzah-plan-interpreter.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="operator", options={"boxed": True})
    assert "Purpose" in text or "WALK the plan" in text or "Execute each planned step" in text


def test_render_plan_warns_on_nonconformant_plan():
    payload = render_plan({"plan_id": "x", "steps": []}, output_format="json")
    assert payload["metadata"]["warnings"]


def test_render_plan_boxed_narrative():
    text = render_plan(CANONICAL_PLAN, profile="narrative_steps", options={"boxed": True})
    assert "> ### Step" in text


def test_public_api_exports_render_plan():
    assert hasattr(deborah, "render_plan")


def test_audit_profile_lists_tags():
    plan = dict(CANONICAL_PLAN)
    plan["steps"][0]["action"] = "Retrieve context. [CODE] [SATISFIES: R1]"
    text = render_plan(plan, profile="audit")
    assert "Audit record" in text
    assert "SATISFIES" in text or "CODE" in text


def test_french_simple_prose():
    text = render_plan(CANONICAL_PLAN, profile="simple_prose", language="fr")
    assert "Le flux procède ainsi" in text


def test_max_depth_filter():
    md = (EXAMPLES / "tirzah-plan-interpreter.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="narrative_steps", options={"max_depth": 1})
    assert "2.1" not in text or "2.3" not in text


def test_sections_filter_process_only():
    md = (EXAMPLES / "keturah.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="narrative_steps", options={"sections": ["process"]})
    assert "R1." not in text


def test_export_view_requires_registered_exporter():
    from deborah.render import export_view
    from deborah.render.model import RenderResult
    import pytest

    result = RenderResult(profile="x", language="en", format="markdown", body="hi")
    with pytest.raises(NotImplementedError, match="No exporter registered"):
        export_view(result, "unknown_format")

    # html is built-in
    html = export_view(result, "html")
    assert b"<!DOCTYPE html>" in html

    # docx/pdf require extra, raise ImportError when called
    with pytest.raises(ImportError, match="python-docx is required"):
        export_view(result, "docx")
    with pytest.raises(ImportError, match="fpdf2 is required"):
        export_view(result, "pdf")


def test_manifest_lists_render_plan():
    from deborah.manifest import build_manifest

    m = build_manifest()
    names = [c.name for c in m.capabilities]
    assert "render_plan" in names


def test_human_demand_profile_from_accounts_payable_example():
    md = (EXAMPLES / "accounts-payable-exception.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="human_demand")
    assert "Human Demand View" in text
    assert "ORIENT: understand the AI claim" in text
    assert "Simulation findings" in text
    assert "context switches" in text or "context_switches" in text


def test_human_factors_profile_from_accounts_payable_example():
    md = (EXAMPLES / "accounts-payable-exception.cairn.md").read_text(encoding="utf-8")
    text = render_plan(md, profile="human_factors")
    assert "Human Factors Review" in text
    assert "automation bias" in text
    assert "score: critical" in text
    assert "Conversation starter" in text
