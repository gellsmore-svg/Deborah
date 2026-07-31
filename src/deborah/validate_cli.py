"""CLI for Cairn grammar validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.grammar import document_to_dict, document_to_plan, parse_document, validate_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deborah-validate",
        description="Validate a Cairn description against GRAMMAR.md and SPEC §12 well-formedness.",
    )
    parser.add_argument("input", nargs="?", help="Path to .cairn.md or raw Cairn text (stdin with '-')")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--export-plan", action="store_true", help="Print document_to_plan JSON on success")
    parser.add_argument("--export-ast", action="store_true", help="Print document_to_dict JSON AST")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any well-formedness warning")

    args = parser.parse_args(argv)
    if args.input in (None, "-"):
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    doc = parse_document(text)
    errors = validate_document(doc)
    report = {
        "parse_errors": doc.parse_errors,
        "well_formedness_errors": [e for e in errors if e not in doc.parse_errors],
        "errors": errors,
        "process_count": len(doc.processes),
        "plan_count": len(doc.plans),
        "source_kind": doc.source_kind,
        "ok": not errors,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if errors:
            for err in errors:
                print(err, file=sys.stderr)
        else:
            print(
                f"ok: {report['process_count']} process(es), "
                f"{report['plan_count']} plan(s), source={report['source_kind']}"
            )

    if args.export_ast:
        print(json.dumps(document_to_dict(doc), indent=2))
    elif args.export_plan and not errors:
        print(json.dumps(document_to_plan(doc), indent=2))

    if errors or (args.strict and report["well_formedness_errors"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())