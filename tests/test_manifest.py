from importlib.metadata import PackageNotFoundError

import deborah.manifest as manifest_module
from deborah.conformance import PLAN_CONSTRUCTS
from deborah.manifest import build_manifest


def test_manifest_conforms_and_lists_grammar():
    m = build_manifest()
    assert m.product == "deborah"
    vp = next(c for c in m.capabilities if c.name == "validate_plan")
    # constructs are listed from the contract, not duplicated
    for construct in PLAN_CONSTRUCTS:
        assert construct in vp.description
    tool_names = [t["name"] for t in m.to_mcp()["tools"]]
    assert "validate_plan" in tool_names
    assert "parse_document" in tool_names
    assert "validate_document" in tool_names
    assert "render_plan" in tool_names


def test_manifest_advertises_only_the_language():
    """The analysis capabilities moved to Huldah — Deborah must not claim them.

    A manifest is a promise about what the package can execute; advertising
    tools that live in another distribution is how MCP consumers get a tool
    that raises ImportError.
    """
    tool_names = {t["name"] for t in build_manifest().to_mcp()["tools"]}
    moved_to_huldah = {
        "analyze_human_factors",
        "analyze_ui_simulation_report",
        "analyze_functional_layout",
        "recommend_interface_changes",
        "build_analysis_report",
        "build_agent_harness_plan",
    }
    assert tool_names.isdisjoint(moved_to_huldah)


def test_manifest_version_prefers_distribution_name(monkeypatch):
    calls = []

    def fake_version(distribution: str) -> str:
        calls.append(distribution)
        if distribution == "deborah":
            return "9.9.9"
        raise PackageNotFoundError

    monkeypatch.setattr(manifest_module, "_pkg_version", fake_version)

    assert manifest_module._version() == "9.9.9"
    assert calls == ["deborah"]


def test_manifest_version_falls_back_to_the_cairn_distribution(monkeypatch):
    """An environment still holding the pre-split `cairn-lang` wheel resolves."""
    calls = []

    def fake_version(distribution: str) -> str:
        calls.append(distribution)
        if distribution == "cairn-lang":
            return "0.8.2"
        raise PackageNotFoundError

    monkeypatch.setattr(manifest_module, "_pkg_version", fake_version)

    assert manifest_module._version() == "0.8.2"
    assert calls == ["deborah", "cairn-lang"]
