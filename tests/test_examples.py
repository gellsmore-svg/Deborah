import subprocess
import sys
from pathlib import Path

from deborah.grammar import parse_document


def test_cairn_examples_pass_skeleton_validation() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "validate_examples.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_validate_examples_accepts_plan_only_backbone(tmp_path: Path) -> None:
    """Deborah #11: PLAN-only docs are grammar-valid examples."""
    # Import the script's validate() with the same path setup it uses.
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))
    sys.path.insert(0, str(root / "scripts"))
    import validate_examples as ve  # type: ignore[import-not-found]

    plan_only = tmp_path / "plan-only.cairn.md"
    plan_only.write_text(
        """\
PLAN plan_solo REVISION 1 [STATUS: draft]
  PARENT: none
  REQUEST: Ship the release
  TRIGGER: initial_request
  PROCESS Ship (INPUT: crate; OUTPUT: tag)
    1. Tag release. [CODE]
""",
        encoding="utf-8",
    )
    doc = parse_document(plan_only.read_text(encoding="utf-8"))
    assert doc.plans and not any(
        # ensure the path under test is the backbone check, not parse failure
        e
        for e in doc.parse_errors
    )
    # Script treats PLAN as sufficient backbone.
    errs = ve.validate(plan_only)
    assert not any("no PROCESS or PLAN" in e or "no PROCESS backbone" in e for e in errs)