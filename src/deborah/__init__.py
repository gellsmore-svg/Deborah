"""Deborah — process meta-language: spec, grammar, and conformance surface.

The repo is primarily a specification (SPEC.md / GRAMMAR.md). This package exposes
the machine-readable conformance surface and simplified view generation for plans
and process descriptions.

*Deborah was a judge* — judgment, governance, conformance. The human-systems
analysis that used to ship in the same package now lives in Huldah.

Dependency-free by default: nothing here imports anything outside the standard
library, so any runtime can adopt the conformance surface. The document format
keeps the Cairn name — `.cairn.md` sources and ```cairn fences are unchanged.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

from deborah.conformance import (
    CANONICAL_PLAN,
    CONFORMANCE_VERSION,
    PLAN_CONSTRUCTS,
    PLAN_STATUSES,
    REQUIRED_PLAN_FIELDS,
    REQUIRED_STEP_FIELDS,
    REVISION_DECISIONS,
    STEP_STATUSES,
    is_conformant,
    validate_plan,
)
from deborah.grammar import (
    CairnDocument,
    document_to_dict,
    document_to_plan,
    extract_cairn_source,
    parse_document,
    validate_document,
)
from deborah.render import (
    export_view,
    register_exporter,
    registered_exporters,
    registered_profiles,
    render_plan,
)

try:
    # Single source of truth: read the installed distribution rather than
    # restating the version here, so it cannot drift from pyproject.
    __version__ = _pkg_version("deborah")
except PackageNotFoundError:  # running straight from a source checkout
    __version__ = "0.0.0+source"

__all__ = [
    "CANONICAL_PLAN",
    "CONFORMANCE_VERSION",
    "CairnDocument",
    "PLAN_CONSTRUCTS",
    "PLAN_STATUSES",
    "REQUIRED_PLAN_FIELDS",
    "REQUIRED_STEP_FIELDS",
    "REVISION_DECISIONS",
    "STEP_STATUSES",
    "document_to_dict",
    "document_to_plan",
    "export_view",
    "extract_cairn_source",
    "is_conformant",
    "parse_document",
    "register_exporter",
    "registered_exporters",
    "registered_profiles",
    "render_plan",
    "validate_document",
    "validate_plan",
]
