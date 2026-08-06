"""CLI for Cairn view generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from deborah.render import registered_profiles, render_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="deborah-render",
        description="Render a Cairn process description (tech/psych/org/socio) into a simplified human-readable view. Supports domain constructs like REGULATION, FEEDBACK, COALITION, MACRO.",
    )
    parser.add_argument("input", nargs="?", help="Path to .cairn.md file (or stdin with '-')")
    parser.add_argument(
        "-p",
        "--profile",
        default="narrative_steps",
        choices=registered_profiles(),
        help="Render profile",
    )
    parser.add_argument("-l", "--language", default="en", help="Language code (en, es, fr)")
    available_formats = ["markdown", "text", "json", "mermaid", "html", "docx", "pdf"]
    parser.add_argument(
        "-f",
        "--format",
        default="markdown",
        choices=available_formats,
        dest="output_format",
        help="Output format (docx/pdf require deborah[export])",
    )
    parser.add_argument("-o", "--output", help="Write to file instead of stdout")
    parser.add_argument("--boxed", action="store_true", help="Use boxed/card layout")
    parser.add_argument("--include-tags", action="store_true")
    parser.add_argument("--max-depth", type=int, help="Limit step hierarchy depth")
    parser.add_argument(
        "--sections",
        help="Comma-separated sections to include: context,requirements,outcomes,plan,process",
    )
    parser.add_argument("--stylesheet", help="YAML/JSON stylesheet path")
    parser.add_argument(
        "--lenient",
        action="store_true",
        help=(
            "On grammar parse failure, fall back to the legacy heuristic parser "
            "with an explicit warning instead of aborting"
        ),
    )

    args = parser.parse_args(argv)
    if args.input in (None, "-"):
        text = sys.stdin.read()
        source: str | dict = text
    else:
        path = Path(args.input)
        if path.suffix == ".json":
            source = json.loads(path.read_text(encoding="utf-8"))
        else:
            source = path.read_text(encoding="utf-8")

    options: dict = {}
    if args.boxed:
        options["boxed"] = True
    if args.include_tags:
        options["include_tags"] = True
    if args.max_depth is not None:
        options["max_depth"] = args.max_depth
    if args.sections:
        options["sections"] = [s.strip() for s in args.sections.split(",") if s.strip()]
    if args.lenient:
        options["lenient"] = True

    try:
        result = render_plan(
            source,
            profile=args.profile,
            language=args.language,
            output_format=args.output_format,
            options=options,
            stylesheet=args.stylesheet,
        )
    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if isinstance(result, (bytes, bytearray)):
        if args.output:
            Path(args.output).write_bytes(result)
        else:
            sys.stdout.buffer.write(result)
        return 0

    if args.output_format == "json":
        out = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
    else:
        out = str(result)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())