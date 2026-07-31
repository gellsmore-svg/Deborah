#!/usr/bin/env python3
"""Example command provider for ``huldah-human-factors --llm-command``.

This is not an LLM. It documents the adapter contract by reading the JSON payload
from stdin and returning JSON with a ``text`` field. Replace the body with a call
to llama.cpp, Ollama, Claude/Codex wrappers, or a queue submitter.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    payload = json.load(sys.stdin)
    report = payload.get("context", {}).get("offline_report", {})
    steps = report.get("steps", [])
    highest = next(
        (
            step
            for step in steps
            if (step.get("risk") or {}).get("score") in {"critical", "significant"}
        ),
        steps[0] if steps else {},
    )
    text = "\n".join(
        [
            "## Highest-risk steps",
            "",
            f"- Step {highest.get('step', '?')}: {highest.get('text', 'no step text')}",
            "",
            "## Questions for the developer or process owner",
            "",
            "- Does the human have enough context, authority, and recovery path at this point?",
            "- Which interface actions are overhead rather than business work?",
        ]
    )
    print(json.dumps({"text": text}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
