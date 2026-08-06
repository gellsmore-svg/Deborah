"""Named transformation-view templates: persisted render recipes.

A *template* is a saved render recipe — a profile plus its options and the
target language/format. That is exactly a Cairn **stylesheet** (see
``render/styles/default.yaml``) with a name and a description. Templates are
stored as JSON, one file per template, so a saved template is **directly
usable** as a stylesheet::

    deborah-render --stylesheet ~/.cairn/templates/<name>.json input.cairn.md

The store is dependency-free (stdlib ``json`` only); the interactive composer
in ``deborah.web`` is a thin UI over it.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from deborah.render.profiles import registered_profiles

# The keys that make up the render recipe itself (a flat stylesheet). Anything
# else in a template file (name, description, saved_at) is metadata that the
# render pipeline harmlessly ignores.
STYLESHEET_KEYS: tuple[str, ...] = (
    "profile",
    "language",
    "output_format",
    "boxed",
    "include_tags",
    "include_sub_blocks",
    "include_footnotes",
    "max_depth",
    "sections",
)
_BOOL_KEYS = ("boxed", "include_tags", "include_sub_blocks", "include_footnotes")

OUTPUT_FORMATS: tuple[str, ...] = ("markdown", "text", "json", "mermaid")
SECTIONS: tuple[str, ...] = ("context", "requirements", "outcomes", "plan", "process")

DEFAULT_TEMPLATE_DIR = Path.home() / ".cairn" / "templates"

_SLUG_RE = re.compile(r"[^a-z0-9._-]+")


def slugify(name: str) -> str:
    """A safe, stable filename stem for a template name."""
    slug = _SLUG_RE.sub("-", name.strip().lower()).strip("-.")
    return slug or "untitled"


def normalize_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    """Validate and coerce a raw recipe into a clean stylesheet dict.

    Raises ``ValueError`` on an unknown profile / format / section so the UI can
    surface a clear message instead of failing at render time.
    """
    out: dict[str, Any] = {}

    profile = str(recipe.get("profile") or "narrative_steps")
    if profile not in registered_profiles():
        raise ValueError(f"unknown profile {profile!r}; known: {registered_profiles()}")
    out["profile"] = profile

    out["language"] = str(recipe.get("language") or "en")

    fmt = str(recipe.get("output_format") or "markdown")
    if fmt not in OUTPUT_FORMATS:
        raise ValueError(f"unknown output_format {fmt!r}; known: {list(OUTPUT_FORMATS)}")
    out["output_format"] = fmt

    for key in _BOOL_KEYS:
        if key in recipe and recipe[key] is not None:
            out[key] = bool(recipe[key])

    if recipe.get("max_depth") not in (None, "", 0):
        try:
            depth = int(recipe["max_depth"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"max_depth must be an integer, got {recipe['max_depth']!r}") from exc
        if depth > 0:
            out["max_depth"] = depth

    sections = recipe.get("sections")
    if sections:
        if isinstance(sections, str):
            sections = [s.strip() for s in sections.split(",") if s.strip()]
        unknown = [s for s in sections if s not in SECTIONS]
        if unknown:
            raise ValueError(f"unknown section(s) {unknown}; known: {list(SECTIONS)}")
        out["sections"] = list(sections)

    return out


def stylesheet_of(template: dict[str, Any]) -> dict[str, Any]:
    """Extract just the render recipe from a stored template (drop metadata)."""
    return {k: template[k] for k in STYLESHEET_KEYS if k in template}


class TemplateStore:
    """A directory of named render templates, one ``<slug>.json`` per template."""

    def __init__(self, directory: str | Path = DEFAULT_TEMPLATE_DIR) -> None:
        self.directory = Path(directory)

    def _path(self, name: str) -> Path:
        return self.directory / f"{slugify(name)}.json"

    def list_templates(self) -> list[dict[str, Any]]:
        """All templates, newest-saved first (missing timestamps sort last)."""
        if not self.directory.exists():
            return []
        items: list[dict[str, Any]] = []
        for path in self.directory.glob("*.json"):
            try:
                items.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
        items.sort(key=lambda t: t.get("saved_at") or "", reverse=True)
        return items

    def get_template(self, name: str) -> dict[str, Any] | None:
        path = self._path(name)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def save_template(
        self, name: str, recipe: dict[str, Any], description: str = ""
    ) -> dict[str, Any]:
        """Persist a recipe under ``name``.

        Overwrites an existing template only when the stored ``name`` matches
        exactly. Different display names that slug to the same filename (e.g.
        ``\"Exec Brief\"`` vs ``\"exec brief\"``) are rejected so one save cannot
        silently clobber another (Deborah #4).
        """
        name = name.strip()
        if not name:
            raise ValueError("template name is required")
        path = self._path(name)
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = None
            if (
                isinstance(existing, dict)
                and existing.get("name")
                and existing["name"] != name
            ):
                slug = slugify(name)
                raise ValueError(
                    f"template slug {slug!r} is already used by "
                    f"{existing['name']!r}; choose a different name or delete "
                    "the existing template first"
                )
        record: dict[str, Any] = {
            "name": name,
            "description": description.strip(),
            "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            **normalize_recipe(recipe),
        }
        self.directory.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record

    def delete_template(self, name: str) -> bool:
        path = self._path(name)
        if path.exists():
            path.unlink()
            return True
        return False
