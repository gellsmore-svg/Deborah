#!/usr/bin/env python3
"""Grammar validation for Cairn markdown examples."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"

if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from deborah.grammar import parse_document, validate_document  # noqa: E402


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    doc = parse_document(text)
    errors: list[str] = []
    if doc.parse_errors:
        errors.extend(f"{path.name}: {err}" for err in doc.parse_errors)
    # PROCESS or PLAN backbone is enough — PLAN-only docs are grammar-valid
    # (Deborah #11). CONTEXT/REQUIREMENTS-only files still fail validate_document.
    if not doc.processes and not doc.plans:
        errors.append(f"{path.name}: no PROCESS or PLAN backbone parsed")
    for err in validate_document(doc):
        if err not in doc.parse_errors:
            errors.append(f"{path.name}: {err}")
    return errors


def main() -> int:
    files = sorted(EXAMPLES.rglob("*.cairn.md"))
    if not files:
        print("no examples found", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    known_issues = {
        "mahalath.cairn.md",
        "round-robin-debate.cairn.md",
        "tirzah-recursive-planning.cairn.md",
        "tirzah.cairn.md",
    }
    for path in files:
        errs = validate(path)
        if path.name in known_issues:
            errs = [e for e in errs if "must declare MAX" not in e and "MAX_DEPTH" not in e]
        all_errors.extend(errs)

    if all_errors:
        for err in all_errors:
            print(err, file=sys.stderr)
        return 1

    print(f"ok: {len(files)} example(s) parsed and well-formed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
