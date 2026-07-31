"""Cairn structural grammar parser (GRAMMAR.md EBNF + SPEC §12 well-formedness)."""

from deborah.grammar.ast import CairnDocument
from deborah.grammar.extract import extract_cairn_source
from deborah.grammar.parser import parse_document
from deborah.grammar.plan_export import document_to_plan
from deborah.grammar.serialize import document_to_dict
from deborah.grammar.validate import validate_document

__all__ = [
    "CairnDocument",
    "document_to_dict",
    "document_to_plan",
    "extract_cairn_source",
    "parse_document",
    "validate_document",
]