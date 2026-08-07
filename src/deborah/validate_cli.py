"""CLI for Cairn grammar validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.conformance import VALIDATE_PROFILES, validate_plan
from deborah.grammar import document_to_dict, document_to_plan, parse_document, validate_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deborah-validate",
        description=(
            "Validate a Cairn description against GRAMMAR.md and SPEC well-formedness; "
            "optionally validate the exported plan under a conformance profile."
        ),
    )
    parser.add_argument("input", nargs="?", help="Path to .cairn.md or raw Cairn text (stdin with '-')")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--export-plan", action="store_true", help="Print document_to_plan JSON on success")
    parser.add_argument("--export-ast", action="store_true", help="Print document_to_dict JSON AST")
    parser.add_argument(
        "--profile",
        choices=sorted(VALIDATE_PROFILES),
        default="full",
        help=(
            "Plan conformance profile: full (default), core (CORE constructs only), "
            "strict (COGNITION needs output; CALL tools ⊆ assumes when set)"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on well-formedness errors (always) and set plan profile to strict",
    )

    args = parser.parse_args(argv)
    if args.input in (None, "-"):
        text = sys.stdin.read()
    else:
        text = Path(args.input).read_text(encoding="utf-8")

    plan_profile = "strict" if args.strict and args.profile == "full" else args.profile

    doc = parse_document(text)
    errors = list(validate_document(doc))
    plan_errors: list[str] = []
    plan_dict = None
    if not doc.parse_errors:
        try:
            plan_dict = document_to_plan(doc)
            plan_errors = validate_plan(plan_dict, profile=plan_profile)
        except ValueError as exc:
            plan_errors = [f"plan export: {exc}"]

    all_errors = errors + [f"plan/{plan_profile}: {e}" for e in plan_errors]
    report = {
        "parse_errors": doc.parse_errors,
        "well_formedness_errors": [e for e in errors if e not in doc.parse_errors],
        "plan_profile": plan_profile,
        "plan_errors": plan_errors,
        "errors": all_errors,
        "process_count": len(doc.processes),
        "plan_count": len(doc.plans),
        "source_kind": doc.source_kind,
        "ok": not all_errors,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if all_errors:
            for err in all_errors:
                print(err, file=sys.stderr)
        else:
            print(
                f"ok: {report['process_count']} process(es), "
                f"{report['plan_count']} plan(s), source={report['source_kind']}, "
                f"plan_profile={plan_profile}"
            )

    if args.export_ast:
        print(json.dumps(document_to_dict(doc), indent=2))
    elif args.export_plan and not all_errors and plan_dict is not None:
        print(json.dumps(plan_dict, indent=2))

    if all_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
