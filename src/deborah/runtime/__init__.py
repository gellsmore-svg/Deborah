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
    live_estate_available,
    record_run_on_tracer,
    resolve_assumes,
    try_load_keturah_registry,
    try_load_live_dispatch,
    try_load_live_index,
    try_make_tracer,
)
from deborah.runtime.interpreter import (
    Handler,
    RunResult,
    StepRecord,
    StubHandler,
    interpret_plan,
)
from deborah.runtime.negotiate import NegotiationResult, run_negotiation
from deborah.runtime.open_questions import OpenQuestion, OpenQuestionStore, open_question_from_run
from deborah.runtime.outcomes import OutcomeCheck, check_outcomes
from deborah.runtime.slice import SliceResult, run_substrate_slice

__all__ = [
    "AssumeResolution",
    "DictCapabilityIndex",
    "EstateHandler",
    "Handler",
    "NegotiationResult",
    "OpenQuestion",
    "OpenQuestionStore",
    "OutcomeCheck",
    "RunResult",
    "SliceResult",
    "StepRecord",
    "StubHandler",
    "check_outcomes",
    "demo_capability_index",
    "demo_critique_dispatch",
    "interpret_plan",
    "interpret_with_estate",
    "live_estate_available",
    "open_question_from_run",
    "record_run_on_tracer",
    "resolve_assumes",
    "run_negotiation",
    "run_substrate_slice",
    "try_load_keturah_registry",
    "try_load_live_dispatch",
    "try_load_live_index",
    "try_make_tracer",
]
