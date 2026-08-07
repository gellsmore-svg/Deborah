"""CLI: interpret a crystallised Cairn PLAN (thin runtime)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.contracts import EXAMPLE_RESULTS
from deborah.grammar import document_to_plan, parse_document, validate_document
from deborah.runtime.interpreter import StubHandler, interpret_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deborah-run",
        description=(
            "Interpret a crystallised Cairn PLAN under allow-lists and bounds "
            "(thin runtime — no free-form re-planning)."
        ),
    )
    parser.add_argument("input", nargs="?", help=".cairn.md or plan JSON (stdin with '-')")
    parser.add_argument("--json", action="store_true", help="Emit full RunResult JSON")
    parser.add_argument(
        "--profile",
        choices=["full", "core", "strict"],
        default="full",
        help="validate_plan profile before run (default full)",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip pre-run validate_plan",
    )
    parser.add_argument(
        "--check-contracts",
        action="store_true",
        help="Validate step results against COGNITION contracts when present",
    )
    parser.add_argument(
        "--contract-mode",
        choices=["soft", "strict"],
        default="soft",
        help="Contract check mode (default soft)",
    )
    parser.add_argument(
        "--demo-results",
        action="store_true",
        help="Use built-in EXAMPLE_RESULTS by cognition (demo / contract tests)",
    )
    parser.add_argument(
        "--results",
        metavar="PATH",
        help="JSON map of step results (by id or by cognition key)",
    )
    parser.add_argument("--max-steps", type=int, default=None, help="Hard step cap")
    args = parser.parse_args(argv)

    if args.input in (None, "-"):
        raw = sys.stdin.read()
        source_path = None
    else:
        source_path = Path(args.input)
        raw = source_path.read_text(encoding="utf-8")

    plan: dict
    if source_path and source_path.suffix.lower() == ".json":
        plan = json.loads(raw)
    elif raw.lstrip().startswith("{"):
        plan = json.loads(raw)
    else:
        doc = parse_document(raw)
        doc_errors = validate_document(doc)
        if doc_errors:
            for e in doc_errors:
                print(e, file=sys.stderr)
            return 1
        try:
            plan = document_to_plan(doc)
        except ValueError as exc:
            print(f"plan export: {exc}", file=sys.stderr)
            return 1

    results_by_id: dict = {}
    results_by_cog: dict = {}
    if args.demo_results:
        results_by_cog = dict(EXAMPLE_RESULTS)
    if args.results:
        payload = json.loads(Path(args.results).read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            for key, val in payload.items():
                if key in EXAMPLE_RESULTS or key in {
                    "observe",
                    "infer",
                    "evaluate",
                    "decide",
                }:
                    results_by_cog[key] = val
                else:
                    results_by_id[key] = val

    handler = StubHandler(results_by_id=results_by_id, results_by_cognition=results_by_cog)
    run = interpret_plan(
        plan,
        handler=handler,
        validate_profile=None if args.no_validate else args.profile,
        check_contracts=args.check_contracts,
        contract_mode=args.contract_mode,
        max_steps=args.max_steps,
    )

    if args.json:
        print(json.dumps(run.to_dict(), indent=2))
    else:
        print(f"terminal: {run.terminal}  plan_id={run.plan_id}")
        for step in run.steps:
            extra = f" ({step.reason})" if step.reason else ""
            cog = f" [{step.cognition}]" if step.cognition else ""
            print(f"  {step.id}: {step.status}{cog}{extra}")
        if run.unresolved:
            print("unresolved:")
            for u in run.unresolved:
                print(f"  - {u}")
        if run.errors:
            for e in run.errors:
                print(e, file=sys.stderr)

    return 0 if run.terminal in {"complete", "open"} and not run.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
