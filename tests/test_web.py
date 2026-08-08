"""Composer web app: render preview + template CRUD over the store."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from deborah.render.templates import TemplateStore  # noqa: E402
from deborah.web import _render_preview, create_app  # noqa: E402

_SAMPLE = """## CONTEXT
a line.

## OUTCOMES
done.

## PROCESS — Formal

```
PROCESS P (INPUT: a; OUTPUT: b)
  1. STEP — first. [CODE, DETERMINISTIC]
  2. STEP — second. [CODE, DETERMINISTIC]
```
"""


def _client(tmp_path) -> TestClient:
    return TestClient(create_app(TemplateStore(tmp_path)))


def test_render_preview_ok_and_bad_recipe() -> None:
    good = _render_preview(_SAMPLE, {"profile": "operator"})
    assert good["ok"] is True
    assert good["format"] == "markdown"
    assert good["line_count"] >= 1
    assert "warnings" in good

    bad = _render_preview(_SAMPLE, {"profile": "does-not-exist"})
    assert bad["ok"] is False and "unknown profile" in bad["error"]


def test_render_preview_is_single_pass(monkeypatch) -> None:
    """Deborah #7: preview must not re-render solely to harvest warnings."""
    from deborah.render import parse as parse_mod

    calls = {"n": 0}
    real = parse_mod.normalize_input

    def counting_normalize(*args, **kwargs):
        calls["n"] += 1
        return real(*args, **kwargs)

    monkeypatch.setattr(parse_mod, "normalize_input", counting_normalize)
    out = _render_preview(_SAMPLE, {"profile": "narrative_steps", "output_format": "markdown"})
    assert out["ok"] is True
    assert calls["n"] == 1


def test_render_preview_empty_source() -> None:
    out = _render_preview("   ", {"profile": "audit"})
    # Empty source is not a successful render (review F6/M7).
    assert out["ok"] is False and out["output"] == ""
    assert "empty" in (out.get("error") or "").lower()


def test_index_and_meta(tmp_path) -> None:
    c = _client(tmp_path)
    page = c.get("/")
    assert page.status_code == 200 and "transformation-view composer" in page.text
    meta = c.get("/api/meta").json()
    assert "operator" in meta["profiles"]
    assert meta["output_formats"] == ["markdown", "text", "json", "mermaid"]
    assert meta["sample"]


def test_render_endpoint(tmp_path) -> None:
    c = _client(tmp_path)
    r = c.post("/api/render", json={"source": _SAMPLE, "recipe": {"profile": "executive"}})
    data = r.json()
    assert data["ok"] is True
    assert "Executive overview" in data["output"]


def test_template_crud_via_api(tmp_path) -> None:
    c = _client(tmp_path)
    assert c.get("/api/templates").json() == []

    saved = c.post("/api/templates", json={
        "name": "Ops view", "description": "for operators",
        "recipe": {"profile": "operator", "boxed": True},
    }).json()
    assert saved["ok"] is True
    assert saved["stylesheet"]["profile"] == "operator"

    listed = c.get("/api/templates").json()
    assert len(listed) == 1 and listed[0]["name"] == "Ops view"

    got = c.get("/api/templates/Ops view").json()
    assert got["boxed"] is True

    assert c.get("/api/templates/nope").status_code == 404

    assert c.delete("/api/templates/Ops view").json() == {"ok": True}
    assert c.get("/api/templates").json() == []


def test_save_rejects_unknown_profile(tmp_path) -> None:
    c = _client(tmp_path)
    r = c.post("/api/templates", json={"name": "x", "recipe": {"profile": "bogus"}})
    assert r.status_code == 400
    assert r.json()["ok"] is False


def test_save_requires_name(tmp_path) -> None:
    c = _client(tmp_path)
    r = c.post("/api/templates", json={"name": "  ", "recipe": {"profile": "operator"}})
    assert r.status_code == 400
