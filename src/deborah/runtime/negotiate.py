"""Bounded pre-execution negotiation (substrate slice).

This is a **control pattern**, not a COGNITION product. It may emit a step
result shaped for ``COGNITION: negotiate`` when crystallised, but the loop
itself is runtime-enforced ``max_rounds`` — models do not decrement the bound.

Default: one-shot *accept* (0 clarification rounds) so crystallised plans run
without live negotiation. Inject a ``Negotiator`` to exercise clarification /
refusal / exhaustion paths in tests and harnesses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


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


def run_negotiation(
    *,
    intent: str,
    assumes: list[str] | None = None,
    claim: str | None = None,
    max_rounds: int = 4,
    negotiator: Negotiator | None = None,
) -> NegotiationResult:
    """Run a bounded caller↔capability negotiation.

    Exhaustion at ``max_rounds`` without acceptance → status ``unresolved``
    (not an exception). Refusal is first-class.
    """
    max_rounds = max(0, int(max_rounds))
    negotiator = negotiator or default_accept_negotiator
    proposal = {
        "intent": intent,
        "assumes": list(assumes or []),
        "claim": claim or intent,
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
            # Caller supplies a fixed constraint echo for the next round (no LLM).
            messages.append(
                NegotiationMessage(
                    type="constraint_declaration",
                    role="caller",
                    payload={
                        "note": "caller re-states crystallised intent",
                        "intent": intent,
                    },
                )
            )
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
