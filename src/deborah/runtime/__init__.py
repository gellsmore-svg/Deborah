"""Thin PLAN interpreter — framed execution, not free-form agent loops.

Phase D: walk a crystallised plan dict under allow-lists and bounds, produce
terminal statuses (complete|open|refused|blocked), optionally check cognitive
result contracts. Re-entry on low confidence is **off** (see contracts module
docs).

Handlers are injectable so estate products (Tirzah, Milcah, …) can supply real
capability dispatch later without owning the control frame.
"""

from deborah.runtime.interpreter import (
    Handler,
    RunResult,
    StepRecord,
    StubHandler,
    interpret_plan,
)

__all__ = [
    "Handler",
    "RunResult",
    "StepRecord",
    "StubHandler",
    "interpret_plan",
]
