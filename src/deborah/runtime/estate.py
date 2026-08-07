"""Optional estate integration: Keturah capability resolution + Galeed tracing.

Phase E — all imports of ``keturah`` / ``galeed`` are optional. Tests and the
core interpreter run without them. When installed, Deborah can:

1. Resolve plan ``ASSUMES`` against a Keturah :class:`~keturah.registry.Registry`
   (or any object with ``find(name) -> … | None``).
2. Record interpretation events on a Galeed :class:`~galeed.recorder.Tracer`.
3. Dispatch CALL steps through registered capability handlers
   (e.g. mock or real ``milcah.critique`` / ``tirzah.retrieve``).

This does **not** pull Tirzah/Milcah into Deborah's hard dependencies — handlers
are injected by the harness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from deborah.runtime.interpreter import Handler, RunResult, StubHandler, interpret_plan

# --- Capability index (Keturah-shaped, no hard dependency) -------------------


class CapabilityIndex(Protocol):
    """Minimal surface for resolving ``name`` or ``product.tool`` assumes."""

    def find(self, name: str) -> Any | None:
        """Return a truthy capability record if known, else None."""
        ...


@dataclass
class DictCapabilityIndex:
    """In-memory index: maps capability stems to metadata dicts.

    Keys may be bare (``critique``) or namespaced (``milcah.critique``).
    """

    capabilities: dict[str, dict[str, Any]] = field(default_factory=dict)

    def find(self, name: str) -> dict[str, Any] | None:
        stem = name.strip().split("@", 1)[0].strip()
        if stem in self.capabilities:
            return self.capabilities[stem]
        # bare name match against suffix
        bare = stem.split(".")[-1]
        for key, cap in self.capabilities.items():
            if key == bare or key.endswith("." + bare):
                return cap
        return None

    def add(self, name: str, **meta: Any) -> None:
        self.capabilities[name.split("@", 1)[0]] = {"name": name, **meta}


def registry_as_index(registry: Any) -> CapabilityIndex:
    """Adapt a Keturah :class:`Registry` (or similar) to :class:`CapabilityIndex`."""

    class _Adapter:
        def find(self, name: str) -> Any | None:
            found = registry.find(name)
            if found is None and "." not in name:
                # try product.name for each product
                for product in getattr(registry, "products", lambda: [])():
                    found = registry.find(name, product=product)
                    if found is not None:
                        break
            if found is None:
                return None
            product, cap = found
            return {
                "product": product,
                "name": getattr(cap, "name", name),
                "description": getattr(cap, "description", ""),
                "capability": cap,
            }

    return _Adapter()


def try_load_keturah_registry(manifests: list[Any] | None = None) -> CapabilityIndex | None:
    """Build a Registry from manifests if ``keturah`` is installed."""
    try:
        from keturah import Registry  # type: ignore[import-not-found]
    except ImportError:
        return None
    reg = Registry(manifests or [])
    return registry_as_index(reg)


@dataclass
class AssumeResolution:
    """Result of resolving plan ASSUMES against a capability index."""

    resolved: dict[str, Any] = field(default_factory=dict)  # stem → record
    missing: list[str] = field(default_factory=list)
    stems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing


def resolve_assumes(
    assumes: list[str] | None,
    index: CapabilityIndex | None,
) -> AssumeResolution:
    """Resolve each assume ref. Without an index, refs are accepted as stems only."""
    out = AssumeResolution()
    if not assumes:
        return out
    for ref in assumes:
        if not isinstance(ref, str) or not ref.strip():
            continue
        stem = ref.strip().split("@", 1)[0].strip()
        out.stems.append(stem)
        if index is None:
            out.resolved[stem] = {"name": stem, "unverified": True}
            continue
        found = index.find(stem)
        if found is None:
            out.missing.append(ref)
        else:
            out.resolved[stem] = found
    return out


# --- Handler that enforces registry + dispatches CALL tools -------------------

CapabilityDispatch = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]


class EstateHandler:
    """Handler: resolve CALL tools via index + optional per-tool dispatch.

    * ``dispatch`` maps capability stem → callable(step, context) -> outcome
    * Unknown CALL tools → blocked (if index present) or delegated to ``fallback``
    * Non-CALL steps always use ``fallback`` (default :class:`StubHandler`)
    """

    def __init__(
        self,
        *,
        index: CapabilityIndex | None = None,
        dispatch: dict[str, CapabilityDispatch] | None = None,
        fallback: Handler | None = None,
        require_resolved_assumes: bool = True,
    ) -> None:
        self.index = index
        self.dispatch = {k.split("@", 1)[0].lower(): v for k, v in (dispatch or {}).items()}
        self.fallback: Handler = fallback or StubHandler()
        self.require_resolved_assumes = require_resolved_assumes

    def __call__(self, step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        construct = (step.get("construct") or "STEP").upper()
        if construct != "CALL":
            return self.fallback(step, context)

        tools = _call_tools(step)
        if not tools:
            return {"status": "blocked", "reason": "CALL step has no tool name"}

        tool = tools[0]
        stem = tool.split("@", 1)[0].lower()

        if self.index is not None:
            found = self.index.find(stem) or self.index.find(tool)
            if found is None:
                return {
                    "status": "blocked",
                    "reason": f"capability {tool!r} not in registry",
                }

        if stem in self.dispatch:
            return self.dispatch[stem](step, context)
        # Also try product.tool full key
        for key, fn in self.dispatch.items():
            if stem.endswith("." + key) or key.endswith("." + stem.split(".")[-1]):
                return fn(step, context)

        return self.fallback(step, context)


def _call_tools(step: dict[str, Any]) -> list[str]:
    tools: list[str] = []
    allowed = step.get("allowed_tools")
    if isinstance(allowed, list):
        tools.extend(str(t).strip() for t in allowed if str(t).strip())
    if not tools:
        action = str(step.get("action") or "")
        head = action.split("[", 1)[0].strip()
        head = head.split("—", 1)[0].split("–", 1)[0].strip()
        parts = head.split()
        if parts:
            tools.append(parts[0])
    return tools


# --- Demo dispatch for the cross-LLM critique slice ---------------------------


def demo_retrieve_handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Stub tirzah.retrieve → observe product."""
    claim = context.get("claim") or context.get("request") or "the claim"
    return {
        "status": "completed",
        "result": {
            "evidence": [
                {
                    "statement": f"Retrieved context snippets bearing on: {claim}",
                    "source": "tirzah.retrieve.demo",
                    "trace_ref": "demo_obs_1",
                }
            ]
        },
    }


def demo_critique_handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    """Stub milcah.critique → evaluate product (adversarial-ish)."""
    artifacts = context.get("artifacts") or {}
    prior = list(artifacts.values())
    return {
        "status": "completed",
        "result": {
            "criteria": ["groundedness", "internal_consistency", "adversarial_resilience"],
            "scores": {
                "groundedness": "medium",
                "internal_consistency": "medium",
                "adversarial_resilience": "low",
            },
            "ranking": ["open", "revise", "accept"],
            "objections": ["Supporting evidence is thin for a firm accept."],
            "prior_artifact_count": len(prior),
            "confidence": {
                "evidence": "medium",
                "inference": "low",
                "execution": "high",
                "basis": "demo critique handler",
            },
        },
    }


def demo_critique_dispatch() -> dict[str, CapabilityDispatch]:
    """Map both bare and namespaced stems used in the golden example."""
    retrieve = demo_retrieve_handler
    critique = demo_critique_handler
    return {
        "tirzah.retrieve": retrieve,
        "retrieve": retrieve,
        "milcah.critique": critique,
        "critique": critique,
    }


def demo_capability_index() -> DictCapabilityIndex:
    idx = DictCapabilityIndex()
    idx.add("tirzah.retrieve", product="tirzah", kind="tool")
    idx.add("milcah.critique", product="milcah", kind="tool", tags=["critique", "evaluate"])
    return idx


# --- Galeed tracing (optional) ------------------------------------------------


def try_make_tracer(
    *,
    source: str = "deborah",
    session_id: str | None = None,
    request_id: str | None = None,
    db: Any = None,
) -> Any | None:
    """Return a Galeed Tracer if galeed is installed, else None."""
    try:
        from galeed import Tracer  # type: ignore[import-not-found]
    except ImportError:
        return None
    return Tracer(
        source=source,
        session_id=session_id or "deborah-session",
        request_id=request_id,
        db=db,
    )


def record_run_on_tracer(run: RunResult, tracer: Any) -> list[dict[str, Any]]:
    """Best-effort emit interpret events onto a Galeed Tracer. Never raises."""
    recorded: list[dict[str, Any]] = []
    if tracer is None:
        return recorded
    try:
        for ev in run.events:
            etype = str(ev.get("type") or "process.step")
            summary = etype
            if ev.get("id"):
                summary = f"{etype} {ev.get('id')}"
            if ev.get("terminal"):
                summary = f"{etype} → {ev.get('terminal')}"
            meta = {k: v for k, v in ev.items() if k != "type"}
            meta["plan_id"] = run.plan_id
            status = "ok"
            if "failed" in etype or ev.get("status") == "blocked":
                status = "error"
            elif ev.get("status") == "refused":
                status = "error"
            tracer.emit(etype, summary=summary, status=status, metadata=meta)
            recorded.append({"type": etype, "summary": summary})
        # terminal marker
        tracer.emit(
            "process.completed" if run.terminal == "complete" else "process.step",
            summary=f"deborah.interpret terminal={run.terminal}",
            status="ok" if run.terminal in {"complete", "open"} else "error",
            metadata={
                "plan_id": run.plan_id,
                "terminal": run.terminal,
                "unresolved": list(run.unresolved),
            },
        )
    except Exception:
        pass
    return recorded


# --- Convenience entry point --------------------------------------------------


def interpret_with_estate(
    plan: dict[str, Any],
    *,
    index: CapabilityIndex | None = None,
    dispatch: dict[str, CapabilityDispatch] | None = None,
    require_assumes: bool = True,
    tracer: Any | None = None,
    demo: bool = False,
    check_contracts: bool = False,
    contract_mode: str = "soft",
    validate_profile: str | None = "full",
    max_steps: int | None = None,
    fallback_results_by_cognition: dict[str, dict[str, Any]] | None = None,
) -> RunResult:
    """Interpret a plan with optional registry resolution and Galeed tracing.

    If ``demo=True``, installs the demo retrieve/critique dispatch and index
    (for the cross-llm-critique slice without live Tirzah/Milcah).
    """
    if demo:
        index = index or demo_capability_index()
        dispatch = {**demo_critique_dispatch(), **(dispatch or {})}

    resolution = resolve_assumes(plan.get("assumes"), index)
    if require_assumes and index is not None and resolution.missing:
        return RunResult(
            plan_id=str(plan.get("plan_id") or "unknown"),
            terminal="blocked",
            steps=[],
            events=[
                {
                    "type": "plan.assumes.unresolved",
                    "missing": list(resolution.missing),
                }
            ],
            on_uncertainty=str(plan.get("on_uncertainty") or "record"),
            errors=[f"unresolved assumes: {resolution.missing}"],
        )

    allow = set(resolution.stems) if resolution.stems else None
    if index is not None and resolution.resolved:
        allow = set(resolution.resolved.keys())

    from deborah.contracts import EXAMPLE_RESULTS

    fallback = StubHandler(
        results_by_cognition=fallback_results_by_cognition or (EXAMPLE_RESULTS if demo else {})
    )
    handler: Handler = EstateHandler(
        index=index,
        dispatch=dispatch,
        fallback=fallback,
        require_resolved_assumes=require_assumes,
    )

    # Stash request text for demo handlers
    context_claim = plan.get("request") or plan.get("intent") or plan.get("objective")

    # Wrap handler to inject claim into context
    inner = handler

    def _handler(step: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        context = dict(context)
        context.setdefault("request", context_claim)
        context.setdefault("claim", context_claim)
        return inner(step, context)

    run = interpret_plan(
        plan,
        handler=_handler,
        allow_list=allow,
        validate_profile=validate_profile,
        check_contracts=check_contracts,
        contract_mode=contract_mode,
        max_steps=max_steps,
    )
    if tracer is not None:
        record_run_on_tracer(run, tracer)
        # expose galeed events count on a copy-friendly field via events
        run.events.append({"type": "galeed.recorded", "ok": True})
    return run
