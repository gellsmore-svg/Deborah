"""Simplified human-readable view generation for Cairn process descriptions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from deborah.render.export import export_view, register_exporter, registered_exporters
from deborah.render.filters import apply_filters
from deborah.render.formats import apply_format
from deborah.render.parse import normalize_input
from deborah.render.profiles import get_profile, registered_profiles

DEFAULT_OPTIONS: dict[str, Any] = {
    "boxed": False,
    "include_tags": False,
    "include_sub_blocks": True,
    "include_footnotes": True,
}


def _load_stylesheet(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        import json

        data = json.loads(text)
    else:
        try:
            import yaml
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required for YAML stylesheets: pip install 'deborah[render]'"
            ) from exc
        data = yaml.safe_load(text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Stylesheet must be a mapping: {path}")
    return data


def render_plan(
    input_cairn: str | dict[str, Any],
    profile: str = "narrative_steps",
    language: str = "en",
    output_format: str = "markdown",
    options: dict[str, Any] | None = None,
    *,
    stylesheet: str | Path | None = None,
) -> str | dict[str, Any] | bytes:
    """Transform a Cairn process description into a simplified human-readable view.

    Parameters
    ----------
    input_cairn:
        Raw Cairn markdown/text or a parsed PLAN dict (``validate_plan``-compatible).
    profile:
        ``narrative_steps``, ``simple_prose``, ``operator``, ``executive``, or
        ``narrative`` (alias).
    language:
        ``en``, ``es``, or ``fr`` (phrasing tables; more codes fall back to English).
    output_format:
        ``markdown``, ``text``, ``json``, ``mermaid``, ``html``, ``docx``, or ``pdf``
        (docx/pdf require 'deborah[export]').
    options:
        Per-render overrides: ``boxed``, ``include_tags``, ``include_sub_blocks``,
        ``include_footnotes``, ``max_depth``, ``sections``, ``lenient``.
    stylesheet:
        Optional YAML/JSON path defining profile rules (XSLT-inspired).

    Returns
    -------
    str or dict or bytes
        Rendered view (dict for json; bytes for export formats like html).
    """
    opts: dict[str, Any] = dict(DEFAULT_OPTIONS)
    if stylesheet is not None:
        opts.update(_load_stylesheet(stylesheet))
    opts.update(options or {})
    opts["output_format"] = output_format

    profile_name = opts.pop("profile", profile)
    language = opts.pop("language", language)
    # Opt-in legacy fallback when the grammar raises (Deborah #3).
    lenient = bool(opts.pop("lenient", False))

    doc = apply_filters(normalize_input(input_cairn, lenient=lenient), opts)
    renderer = get_profile(profile_name)
    result = renderer.render(doc, language, opts)

    # Binary export formats go through the exporter (returns bytes)
    if output_format in ("html",) or output_format in registered_exporters():
        return export_view(result, output_format, opts)

    if output_format == "json":
        return apply_format(result, doc, "json")
    if output_format == "text":
        return apply_format(result, doc, "text")
    if output_format == "mermaid":
        return apply_format(result, doc, "mermaid")
    return apply_format(result, doc, "markdown")


__all__ = [
    "apply_filters",
    "export_view",
    "normalize_input",
    "register_exporter",
    "registered_exporters",
    "registered_profiles",
    "render_plan",
]