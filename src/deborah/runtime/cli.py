"""CLI: interpret a crystallised Cairn PLAN (thin runtime)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.contracts import EXAMPLE_RESULTS
from deborah.grammar import document_to_plan, parse_document, validate_document
from deborah.runtime.estate import interpret_with_estate
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
        "--estate-demo",
        action="store_true",
        help=(
            "Phase E demo: resolve ASSUMES via in-process capability index and "
            "dispatch tirzah.retrieve / milcah.critique stubs"
        ),
    )
    parser.add_argument(
        "--estate-live",
        action="store_true",
        help=(
            "Use real Tirzah/Milcah Deborah adapters when installed "
            "(tirzah.deborah / milcah.deborah); falls back to demo stubs if "
            "neither package is importable"
        ),
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Record run on Galeed Tracer if galeed is installed (no-op otherwise)",
    )
    parser.add_argument(
        "--results",
        metavar="PATH",
        help="JSON map of step results (by id or by cognition key)",
    )
    parser.add_argument("--max-steps", type=int, default=None, help="Hard step cap")
    parser.add_argument(
        "--allow-reentry",
        action="store_true",
        help="Phase F: allow one re-dispatch of low-confidence infer/evaluate when exploration_budget > 0",
    )
    parser.add_argument(
        "--reflective-pass",
        action="store_true",
        help="Phase F: flag residual when infer/evaluate inference confidence is low/unassessed",
    )
    parser.add_argument(
        "--slice",
        action="store_true",
        help=(
            "Substrate slice: bounded negotiation → estate interpret → outcome "
            "check → open-question record when residual"
        ),
    )
    parser.add_argument(
        "--question",
        metavar="TEXT",
        help="Override plan REQUEST / claim for this run (slice or estate)",
    )
    parser.add_argument(
        "--open-questions",
        metavar="PATH",
        help="JSONL path for open-question records (used with --slice)",
    )
    parser.add_argument(
        "--confidence-floor",
        choices=["high", "medium", "low"],
        default="low",
        help="Minimum inference band for slice outcome check (default low)",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=4,
        help="Negotiation max rounds for --slice (default 4; 0 = skip loop, treat as agreed)",
    )
    parser.add_argument(
        "--no-negotiate",
        action="store_true",
        help="Skip pre-execution negotiation in --slice",
    )
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

    tracer = None
    if args.trace:
        from deborah.runtime.estate import try_make_tracer

        tracer = try_make_tracer(source="deborah-run")

    if args.question:
        plan = dict(plan)
        plan["request"] = args.question

    if args.slice:
        from deborah.runtime.slice import run_substrate_slice

        # Default estate demo for the slice unless live was requested.
        demo = not args.estate_live
        if args.estate_demo:
            demo = True
        slice_result = run_substrate_slice(
            plan,
            question=args.question,
            demo=demo,
            live=bool(args.estate_live),
            negotiate=not args.no_negotiate,
            max_rounds=args.max_rounds,
            confidence_floor=args.confidence_floor,
            open_questions_path=args.open_questions,
            check_contracts=args.check_contracts or True,
            contract_mode=args.contract_mode,
            tracer=tracer,
        )
        if args.json:
            print(json.dumps(slice_result.to_dict(), indent=2))
        else:
            print(
                f"terminal: {slice_result.terminal}  plan_id={slice_result.plan_id}  "
                f"outcomes_ok={slice_result.outcomes.ok}"
            )
            if slice_result.negotiation:
                print(
                    f"negotiation: {slice_result.negotiation.status} "
                    f"rounds={slice_result.negotiation.rounds_used}/"
                    f"{slice_result.negotiation.max_rounds}"
                )
            for step in slice_result.run.steps:
                extra = f" ({step.reason})" if step.reason else ""
                cog = f" [{step.cognition}]" if step.cognition else ""
                print(f"  {step.id}: {step.status}{cog}{extra}")
            if slice_result.outcomes.open_reasons:
                print("open_reasons:")
                for r in slice_result.outcomes.open_reasons:
                    print(f"  - {r}")
            if slice_result.open_question:
                print(
                    f"open_question: {slice_result.open_question.open_question_id} "
                    f"— {slice_result.open_question.reason}"
                )
            if slice_result.run.errors:
                for e in slice_result.run.errors:
                    print(e, file=sys.stderr)
        ok = slice_result.terminal in {"complete", "open"} and not slice_result.run.errors
        return 0 if ok else 1

    if args.estate_demo or args.estate_live:
        run = interpret_with_estate(
            plan,
            demo=bool(args.estate_demo) and not args.estate_live,
            live=bool(args.estate_live),
            tracer=tracer,
            check_contracts=args.check_contracts,
            contract_mode=args.contract_mode,
            validate_profile=None if args.no_validate else args.profile,
            max_steps=args.max_steps,
            fallback_results_by_cognition=results_by_cog or EXAMPLE_RESULTS,
            allow_reentry=args.allow_reentry,
            reflective_pass=True if args.reflective_pass else None,
        )
    else:
        handler = StubHandler(results_by_id=results_by_id, results_by_cognition=results_by_cog)
        run = interpret_plan(
            plan,
            handler=handler,
            validate_profile=None if args.no_validate else args.profile,
            check_contracts=args.check_contracts,
            contract_mode=args.contract_mode,
            max_steps=args.max_steps,
            allow_reentry=args.allow_reentry,
            reflective_pass=True if args.reflective_pass else None,
        )
        if tracer is not None:
            from deborah.runtime.estate import record_run_on_tracer

            record_run_on_tracer(run, tracer)
            run.events.append({"type": "galeed.recorded", "ok": True})

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
