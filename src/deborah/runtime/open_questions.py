"""Open-questions store — residual uncertainty as a first-class record.

File-backed by default (JSONL under a path you choose). Optional Tirzah Mongo
collection when a db is injected. Deborah stays dependency-free: Mongo is never
imported unless the caller passes a db handle.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OpenQuestion:
    """One unresolved question / residual from a framed run."""

    question: str
    reason: str
    plan_id: str | None = None
    run_terminal: str | None = None
    open_question_id: str = field(default_factory=lambda: f"oq_{uuid4().hex[:12]}")
    created_at: str = field(default_factory=_utcnow)
    source: str = "deborah"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OpenQuestion":
        from dataclasses import fields

        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


class OpenQuestionStore:
    """Append-only open-question log (JSONL)."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, question: OpenQuestion) -> OpenQuestion:
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(question.to_dict(), default=str) + "\n")
        return question

    def list(self, *, plan_id: str | None = None, limit: int = 100) -> list[OpenQuestion]:
        if not self.path.exists():
            return []
        rows: list[OpenQuestion] = []
        with self.path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if plan_id and data.get("plan_id") != plan_id:
                    continue
                rows.append(OpenQuestion.from_dict(data))
        return rows[-limit:]


def record_open_question_mongo(
    db: Any,
    question: OpenQuestion,
    *,
    collection: str = "deborah_open_questions",
) -> OpenQuestion:
    """Best-effort insert into a Mongo-like db (Tirzah estate). Never raises."""
    try:
        db[collection].insert_one(question.to_dict())
    except Exception:
        pass
    return question


def open_question_from_run(
    plan: dict[str, Any],
    run: Any,
    *,
    reasons: list[str] | None = None,
    claim: str | None = None,
) -> OpenQuestion:
    """Build an OpenQuestion from a plan + RunResult (or duck-typed run)."""
    terminal = getattr(run, "terminal", None) or (
        run.get("terminal") if isinstance(run, dict) else None
    )
    plan_id = str(plan.get("plan_id") or getattr(run, "plan_id", "") or "unknown")
    q = (
        claim
        or plan.get("request")
        or plan.get("intent")
        or "Unresolved plan residual"
    )
    reason_parts = list(reasons or [])
    unresolved = getattr(run, "unresolved", None)
    if unresolved:
        reason_parts.extend(str(u) for u in unresolved)
    if not reason_parts:
        reason_parts.append(f"terminal={terminal}")
    return OpenQuestion(
        question=str(q).strip(),
        reason="; ".join(reason_parts),
        plan_id=plan_id,
        run_terminal=str(terminal) if terminal else None,
        metadata={
            "on_uncertainty": plan.get("on_uncertainty"),
            "intent": plan.get("intent"),
        },
    )
