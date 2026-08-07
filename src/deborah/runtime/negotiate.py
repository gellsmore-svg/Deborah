"""Bounded pre-execution negotiation (substrate slice).

This is a **control pattern**, not a COGNITION product. It may emit a step
result shaped for ``COGNITION: negotiate`` when crystallised, but the loop
itself is runtime-enforced ``max_rounds`` — models do not decrement the bound.

Negotiators:
- ``default_accept_negotiator`` — one-shot accept (crystallised skip of content)
- ``critique_content_negotiator`` — rule-based milcah.critique gate (clarify /
  refuse / accept) without calling an LLM

Inject a custom ``Negotiator`` for live model-backed negotiation later.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


@dataclass
class NegotiationMessage:
    type: str  # invocation_proposal | clarification_request | acceptance | refusal | exhaustion
    role: str  # caller | capability
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "role": self.role, "payload": dict(self.payload)}


@dataclass
class NegotiationResult:
    status: str  # agreed | partial | unresolved | refused
    rounds_used: int
    max_rounds: int
    messages: list[NegotiationMessage] = field(default_factory=list)
    tradeoffs: list[str] = field(default_factory=list)
    reason: str | None = None

    @property
    def ok(self) -> bool:
        return self.status in {"agreed", "partial"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "rounds_used": self.rounds_used,
            "max_rounds": self.max_rounds,
            "messages": [m.to_dict() for m in self.messages],
            "tradeoffs": list(self.tradeoffs),
            "reason": self.reason,
            # COGNITION negotiate product-shaped fields (for contracts if recorded)
            "agreement": self.status == "agreed",
            "selected": self.status if self.status in {"agreed", "partial"} else None,
        }

    def as_cognition_result(self) -> dict[str, Any]:
        """Shape suitable for validate_cognition_result('negotiate', …)."""
        return {
            "status": self.status if self.status in {"agreed", "partial", "unresolved"} else "unresolved",
            "tradeoffs": list(self.tradeoffs) or None,
            "agreement": self.status == "agreed" or None,
            "selected": "proceed" if self.ok else None,
            "force_agreement": False,
        }


class Negotiator(Protocol):
    """One capability-side turn: given proposal + history, reply with a message type."""

    def __call__(
        self,
        proposal: dict[str, Any],
        history: list[NegotiationMessage],
        round_index: int,
    ) -> NegotiationMessage:
        ...


CallerResponder = Callable[
    [dict[str, Any], list[NegotiationMessage], NegotiationMessage],
    NegotiationMessage,
]


def default_accept_negotiator(
    proposal: dict[str, Any],
    history: list[NegotiationMessage],
    round_index: int,
) -> NegotiationMessage:
    """One-shot accept — no clarification (crystallised path)."""
    return NegotiationMessage(
        type="acceptance",
        role="capability",
        payload={"assumes": proposal.get("assumes"), "note": "one-shot accept"},
    )


# --- Content-aware milcah.critique negotiator ---------------------------------

_CLAIM_MARKERS = re.compile(
    r"\b(is|are|was|were|can|could|should|must|whether|claim|holds?|true|false|"
    r"supported|coherent|consistent|implies?|because|therefore)\b",
    re.I,
)
_OUT_OF_SCOPE = re.compile(
    r"^\s*(hi|hello|hey|thanks|thank you|ok|okay|run tests?|npm |git |"
    r"please (write|fix|debug|refactor)|what('s| is) the weather)\b",
    re.I,
)
_CODE_ONLY = re.compile(r"^[\s\W\d]*$|^(def |class |import |from |function |const )", re.I)


def _claim_text(proposal: dict[str, Any]) -> str:
    parts = [
        str(proposal.get("claim") or "").strip(),
        str(proposal.get("context") or "").strip(),
        str(proposal.get("intent") or "").strip(),
    ]
    # Prefer claim; fall back to intent only if claim empty
    if parts[0]:
        return parts[0] if not parts[1] else f"{parts[0]} {parts[1]}".strip()
    return (parts[2] or "").strip()


def _history_has(history: list[NegotiationMessage], msg_type: str) -> bool:
    return any(str(m.type).lower() == msg_type for m in history)


def critique_content_negotiator(
    proposal: dict[str, Any],
    history: list[NegotiationMessage],
    round_index: int,
) -> NegotiationMessage:
    """Rule-based capability-side gate for ``milcah.critique`` / coherence_check.

    Deterministic (no LLM): inspect claim/context and either clarify, refuse, or
    accept. After one clarification cycle, empty claims refuse rather than loop.

    Failure modes (Keturah Stage 0):
    - ``underspecified-claim`` → clarification_request (once), then refusal
    - ``domain-out-of-scope`` → refusal
    """
    text = _claim_text(proposal)
    clarified = _history_has(history, "constraint_declaration")
    assumes = proposal.get("assumes") or []

    if not text or len(text) < 8:
        if clarified:
            return NegotiationMessage(
                type="refusal",
                role="capability",
                payload={
                    "reason": "underspecified-claim: no claim after clarification",
                    "failure_mode": "underspecified-claim",
                    "assumes": assumes,
                },
            )
        return NegotiationMessage(
            type="clarification_request",
            role="capability",
            payload={
                "need": "a single assertion or claim to pressure-test",
                "failure_mode": "underspecified-claim",
                "hint": "Provide claim=… or a full REQUEST sentence with is/are/whether.",
            },
        )

    if _OUT_OF_SCOPE.search(text) or (_CODE_ONLY.match(text) and not _CLAIM_MARKERS.search(text)):
        return NegotiationMessage(
            type="refusal",
            role="capability",
            payload={
                "reason": "domain-out-of-scope: not a coherence claim",
                "failure_mode": "domain-out-of-scope",
                "assumes": assumes,
            },
        )

    if not _CLAIM_MARKERS.search(text):
        if clarified:
            # Still no claim shape after re-state → partial (run may open)
            return NegotiationMessage(
                type="partial",
                role="capability",
                payload={
                    "note": "claim shape still weak; proceed with residual risk",
                    "failure_mode": "underspecified-claim",
                    "assumes": assumes,
                },
            )
        return NegotiationMessage(
            type="clarification_request",
            role="capability",
            payload={
                "need": "frame as a single evaluable assertion "
                "(e.g. 'X is Y', 'whether Z holds')",
                "failure_mode": "underspecified-claim",
                "received": text[:200],
            },
        )

    return NegotiationMessage(
        type="acceptance",
        role="capability",
        payload={
            "assumes": assumes,
            "note": "critique_content_negotiator: claim shape ok",
            "claim_preview": text[:160],
        },
    )


def default_caller_responder(
    proposal: dict[str, Any],
    history: list[NegotiationMessage],
    clarification: NegotiationMessage,
) -> NegotiationMessage:
    """Caller response to clarification: re-state intent/claim + constraints."""
    need = (clarification.payload or {}).get("need") or (clarification.payload or {}).get(
        "reason"
    )
    return NegotiationMessage(
        type="constraint_declaration",
        role="caller",
        payload={
            "note": "caller re-states crystallised intent after clarification",
            "intent": proposal.get("intent"),
            "claim": proposal.get("claim") or proposal.get("intent"),
            "context": proposal.get("context"),
            "need_echo": need,
            "constraints": [
                "do not invent sources",
                "empty evidence set is allowed and must be explicit",
                "do not force agreement",
            ],
        },
    )


def resolve_negotiator(
    name: str | None,
    *,
    assumes: list[str] | None = None,
) -> Negotiator:
    """Pick a negotiator by name or from plan ASSUMES (``auto``)."""
    key = (name or "auto").strip().lower()
    if key in {"accept", "default", "oneshot", "one-shot"}:
        return default_accept_negotiator
    if key in {"critique", "milcah", "milcah.critique", "content"}:
        return critique_content_negotiator
    if key == "auto":
        stems = " ".join(str(a).lower() for a in (assumes or []))
        if "critique" in stems or "coherence" in stems or "milcah" in stems:
            return critique_content_negotiator
        return default_accept_negotiator
    return default_accept_negotiator


def run_negotiation(
    *,
    intent: str,
    assumes: list[str] | None = None,
    claim: str | None = None,
    context: str | None = None,
    max_rounds: int = 4,
    negotiator: Negotiator | None = None,
    caller_responder: CallerResponder | None = None,
) -> NegotiationResult:
    """Run a bounded caller↔capability negotiation.

    Exhaustion at ``max_rounds`` without acceptance → status ``unresolved``
    (not an exception). Refusal is first-class.
    """
    max_rounds = max(0, int(max_rounds))
    negotiator = negotiator or default_accept_negotiator
    responder = caller_responder or default_caller_responder
    proposal: dict[str, Any] = {
        "intent": intent,
        "assumes": list(assumes or []),
        "claim": claim or intent,
        "context": context or "",
    }
    messages: list[NegotiationMessage] = [
        NegotiationMessage(type="invocation_proposal", role="caller", payload=dict(proposal))
    ]
    tradeoffs: list[str] = []

    if max_rounds == 0:
        # Explicit no-negotiation: treat as agreed for crystallised plans.
        messages.append(
            NegotiationMessage(
                type="acceptance",
                role="capability",
                payload={"note": "max_rounds=0; crystallised skip"},
            )
        )
        return NegotiationResult(
            status="agreed",
            rounds_used=0,
            max_rounds=0,
            messages=messages,
            tradeoffs=tradeoffs,
        )

    for r in range(max_rounds):
        reply = negotiator(proposal, messages, r)
        if not isinstance(reply, NegotiationMessage):
            reply = NegotiationMessage(
                type="refusal",
                role="capability",
                payload={"reason": "invalid negotiator reply"},
            )
        messages.append(reply)
        rtype = str(reply.type).lower()
        if rtype in {"acceptance", "accept", "agreed"}:
            return NegotiationResult(
                status="agreed",
                rounds_used=r + 1,
                max_rounds=max_rounds,
                messages=messages,
                tradeoffs=tradeoffs,
            )
        if rtype in {"refusal", "refuse", "rejected"}:
            return NegotiationResult(
                status="refused",
                rounds_used=r + 1,
                max_rounds=max_rounds,
                messages=messages,
                tradeoffs=tradeoffs,
                reason=str((reply.payload or {}).get("reason") or "capability refused"),
            )
        if rtype in {"clarification_request", "clarification"}:
            response = responder(proposal, messages, reply)
            if not isinstance(response, NegotiationMessage):
                response = default_caller_responder(proposal, messages, reply)
            messages.append(response)
            # Enrich proposal from caller constraint declaration for next turn.
            payload = response.payload or {}
            if payload.get("claim"):
                proposal["claim"] = payload["claim"]
            if payload.get("context"):
                proposal["context"] = payload["context"]
            if payload.get("intent"):
                proposal["intent"] = payload["intent"]
            tradeoffs.append(f"round {r + 1}: clarification requested")
            continue
        if rtype in {"partial", "partial_acceptance"}:
            return NegotiationResult(
                status="partial",
                rounds_used=r + 1,
                max_rounds=max_rounds,
                messages=messages,
                tradeoffs=tradeoffs + ["partial acceptance"],
            )
        # Unknown type counts as unresolved pressure for that round
        tradeoffs.append(f"round {r + 1}: unrecognised reply {rtype!r}")

    return NegotiationResult(
        status="unresolved",
        rounds_used=max_rounds,
        max_rounds=max_rounds,
        messages=messages,
        tradeoffs=tradeoffs,
        reason="max_rounds exhausted without agreement",
    )
