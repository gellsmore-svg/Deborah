"""Deborah — Cairn process language: framing, grammar, conformance, and views.

Maintains the **Cairn** document format for framing cross-LLM caller↔capability
work (SPEC.md / GRAMMAR.md). This package exposes parse/validate, plan
conformance, and simplified view generation.

*Deborah was a judge* — judgment, governance, conformance. Human-systems
analysis lives in **Huldah**; capability manifests in **Keturah**; traces in
**Galeed**.

Dependency-free by default: nothing here imports anything outside the standard
library. The document format keeps the Cairn name — ``.cairn.md`` sources and
```cairn fences are unchanged.
"""

from importlib.metadata import PackageNotFoundError, version as _pkg_version

from deborah.conformance import (
    CANONICAL_PLAN,
    COGNITION_MVP,
    COGNITION_RESERVED,
    COGNITION_VALUES,
    CONFORMANCE_VERSION,
    CORE_CONSTRUCTS,
    EXTENSION_CONSTRUCTS,
    ON_UNCERTAINTY_POLICIES,
    OPTIONAL_PLAN_FIELDS,
    PLAN_CONSTRUCTS,
    PLAN_STATUSES,
    REQUIRED_PLAN_FIELDS,
    REQUIRED_STEP_FIELDS,
    REVISION_DECISIONS,
    STEP_STATUSES,
    VALIDATE_PROFILES,
    is_conformant,
    is_core_construct,
    validate_plan,
)
from deborah.contracts import (
    CONFIDENCE_BANDS,
    CONFIDENCE_DIMENSIONS,
    CONTRACT_VERSION,
    EXAMPLE_RESULTS,
    validate_cognition_result,
    validate_confidence,
    validate_step_results,
)
from deborah.runtime import RunResult, StubHandler, interpret_plan
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
    "COGNITION_MVP",
    "COGNITION_RESERVED",
    "COGNITION_VALUES",
    "CONFIDENCE_BANDS",
    "CONFIDENCE_DIMENSIONS",
    "CONFORMANCE_VERSION",
    "CONTRACT_VERSION",
    "CORE_CONSTRUCTS",
    "CairnDocument",
    "EXAMPLE_RESULTS",
    "EXTENSION_CONSTRUCTS",
    "ON_UNCERTAINTY_POLICIES",
    "OPTIONAL_PLAN_FIELDS",
    "PLAN_CONSTRUCTS",
    "PLAN_STATUSES",
    "REQUIRED_PLAN_FIELDS",
    "REQUIRED_STEP_FIELDS",
    "REVISION_DECISIONS",
    "STEP_STATUSES",
    "VALIDATE_PROFILES",
    "document_to_dict",
    "document_to_plan",
    "RunResult",
    "StubHandler",
    "export_view",
    "extract_cairn_source",
    "interpret_plan",
    "is_conformant",
    "is_core_construct",
    "parse_document",
    "register_exporter",
    "registered_exporters",
    "registered_profiles",
    "render_plan",
    "validate_cognition_result",
    "validate_confidence",
    "validate_document",
    "validate_plan",
    "validate_step_results",
]
