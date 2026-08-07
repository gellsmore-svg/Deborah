"""CLI for Cairn grammar validation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.conformance import VALIDATE_PROFILES, validate_plan
from deborah.contracts import CONTRACT_MODES, validate_step_results
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
    parser.add_argument(
        "--results",
        metavar="PATH",
        help=(
            "JSON file: either a plan dict with step results, or a list/object of "
            "per-step results merged onto the exported plan for contract checks"
        ),
    )
    parser.add_argument(
        "--results-mode",
        choices=sorted(CONTRACT_MODES),
        default="soft",
        help="Cognitive result contract mode: soft (default) or strict",
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
    result_errors: list[str] = []
    plan_dict = None
    if not doc.parse_errors:
        try:
            plan_dict = document_to_plan(doc)
            plan_errors = validate_plan(plan_dict, profile=plan_profile)
        except ValueError as exc:
            plan_errors = [f"plan export: {exc}"]

    if args.results and plan_dict is not None and not plan_errors:
        raw = json.loads(Path(args.results).read_text(encoding="utf-8"))
        merged = _merge_results(plan_dict, raw)
        result_errors = validate_step_results(merged, mode=args.results_mode)

    all_errors = (
        errors
        + [f"plan/{plan_profile}: {e}" for e in plan_errors]
        + [f"results/{args.results_mode}: {e}" for e in result_errors]
    )
    report = {
        "parse_errors": doc.parse_errors,
        "well_formedness_errors": [e for e in errors if e not in doc.parse_errors],
        "plan_profile": plan_profile,
        "plan_errors": plan_errors,
        "results_mode": args.results_mode if args.results else None,
        "result_errors": result_errors,
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


def _merge_results(plan: dict, raw: object) -> dict:
    """Attach results to plan steps from a results payload."""
    import copy

    merged = copy.deepcopy(plan)
    steps = merged.get("steps")
    if not isinstance(steps, list):
        return merged
    if isinstance(raw, dict) and isinstance(raw.get("steps"), list):
        # Full plan-shaped payload
        for i, step in enumerate(raw["steps"]):
            if i < len(steps) and isinstance(step, dict) and "result" in step:
                steps[i]["result"] = step["result"]
                if step.get("cognition"):
                    steps[i]["cognition"] = step["cognition"]
        return merged
    if isinstance(raw, dict) and "results" in raw and isinstance(raw["results"], list):
        raw = raw["results"]
    if isinstance(raw, list):
        for i, item in enumerate(raw):
            if i >= len(steps):
                break
            if isinstance(item, dict) and "result" in item:
                steps[i]["result"] = item["result"]
                if item.get("cognition"):
                    steps[i]["cognition"] = item["cognition"]
            else:
                steps[i]["result"] = item
        return merged
    if isinstance(raw, dict):
        # Map by step id, or by cognition key (observe/infer/evaluate/decide).
        by_id = raw
        for step in steps:
            sid = step.get("id")
            cog = step.get("cognition")
            if sid in by_id:
                step["result"] = by_id[sid]
            elif cog and cog in by_id:
                step["result"] = by_id[cog]
        return merged
    return merged


if __name__ == "__main__":
    raise SystemExit(main())
