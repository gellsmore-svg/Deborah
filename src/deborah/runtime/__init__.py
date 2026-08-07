"""Thin PLAN interpreter — framed execution, not free-form agent loops.

Phase D: walk a crystallised plan dict under allow-lists and bounds, produce
terminal statuses (complete|open|refused|blocked), optionally check cognitive
result contracts. Re-entry on low confidence is **off** (see contracts module
docs).

Handlers are injectable so estate products (Tirzah, Milcah, …) can supply real
capability dispatch later without owning the control frame.
"""

from deborah.runtime.estate import (
    AssumeResolution,
    DictCapabilityIndex,
    EstateHandler,
    demo_capability_index,
    demo_critique_dispatch,
    interpret_with_estate,
    record_run_on_tracer,
    resolve_assumes,
    try_load_keturah_registry,
    try_make_tracer,
)
from deborah.runtime.interpreter import (
    Handler,
    RunResult,
    StepRecord,
    StubHandler,
    interpret_plan,
)

__all__ = [
    "AssumeResolution",
    "DictCapabilityIndex",
    "EstateHandler",
    "Handler",
    "RunResult",
    "StepRecord",
    "StubHandler",
    "demo_capability_index",
    "demo_critique_dispatch",
    "interpret_plan",
    "interpret_with_estate",
    "record_run_on_tracer",
    "resolve_assumes",
    "try_load_keturah_registry",
    "try_make_tracer",
]
