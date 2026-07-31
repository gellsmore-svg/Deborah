"""Serialize CairnDocument AST to JSON-friendly dicts."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from deborah.grammar.ast import CairnDocument


def document_to_dict(doc: CairnDocument) -> dict[str, Any]:
    """Export a parsed document as a plain dict (JSON-serializable)."""
    return asdict(doc)