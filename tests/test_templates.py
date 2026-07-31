"""Named transformation-view template store (persisted render recipes)."""

from __future__ import annotations


import pytest

from deborah.render import render_plan
from deborah.render.templates import (
    TemplateStore,
    normalize_recipe,
    slugify,
    stylesheet_of,
)

_SAMPLE = """# Sample
## CONTEXT
one context line.

## OUTCOMES
A result.

## PROCESS — Formal

```
PROCESS Demo (INPUT: x; OUTPUT: y)
  1. STEP — do the first thing. [CODE, DETERMINISTIC]
  2. STEP — do the second thing. [CODE, DETERMINISTIC]
```
"""


def test_slugify_makes_safe_stems() -> None:
    assert slugify("Executive Brief!") == "executive-brief"
    assert slugify("  ") == "untitled"
    assert slugify("a/b\\c") == "a-b-c"


def test_normalize_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="unknown profile"):
        normalize_recipe({"profile": "nope"})


def test_normalize_rejects_unknown_format_and_section() -> None:
    with pytest.raises(ValueError, match="output_format"):
        normalize_recipe({"profile": "operator", "output_format": "pdf"})
    with pytest.raises(ValueError, match="section"):
        normalize_recipe({"profile": "operator", "sections": ["context", "bogus"]})


def test_normalize_coerces_types() -> None:
    recipe = normalize_recipe(
        {
            "profile": "operator",
            "boxed": "yes",  # truthy → True
            "max_depth": "2",
            "sections": "process, outcomes",
        }
    )
    assert recipe["boxed"] is True
    assert recipe["max_depth"] == 2
    assert recipe["sections"] == ["process", "outcomes"]
    # zero/None depth is dropped rather than stored.
    assert "max_depth" not in normalize_recipe({"profile": "operator", "max_depth": 0})


def test_save_list_get_delete_roundtrip(tmp_path) -> None:
    store = TemplateStore(tmp_path)
    assert store.list_templates() == []

    saved = store.save_template(
        "Exec Brief", {"profile": "executive", "boxed": True}, description="One-pager"
    )
    assert saved["name"] == "Exec Brief"
    assert saved["profile"] == "executive"
    assert saved["description"] == "One-pager"
    assert "saved_at" in saved

    listed = store.list_templates()
    assert len(listed) == 1 and listed[0]["name"] == "Exec Brief"

    got = store.get_template("Exec Brief")
    assert got is not None and got["boxed"] is True
    # slug-insensitive lookup.
    assert store.get_template("exec brief") is not None

    assert store.delete_template("Exec Brief") is True
    assert store.get_template("Exec Brief") is None
    assert store.delete_template("Exec Brief") is False


def test_saved_template_is_a_usable_stylesheet(tmp_path) -> None:
    """A stored template file works directly as `--stylesheet` for render_plan."""
    store = TemplateStore(tmp_path)
    store.save_template("audit-view", {"profile": "audit", "output_format": "markdown"})
    path = tmp_path / "audit-view.json"
    assert path.exists()

    out = render_plan(_SAMPLE, stylesheet=str(path))
    assert isinstance(out, str)
    assert "Audit record" in out  # the audit profile's heading


def test_stylesheet_of_drops_metadata(tmp_path) -> None:
    store = TemplateStore(tmp_path)
    record = store.save_template("v", {"profile": "operator", "boxed": True})
    sheet = stylesheet_of(record)
    assert "name" not in sheet and "saved_at" not in sheet
    assert sheet["profile"] == "operator" and sheet["boxed"] is True


def test_corrupt_file_is_skipped(tmp_path) -> None:
    (tmp_path).mkdir(exist_ok=True)
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    store = TemplateStore(tmp_path)
    assert store.list_templates() == []
    assert store.get_template("broken") is None
