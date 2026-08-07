"""Live estate bootstrap for the substrate slice (optional Tirzah Mongo).

Deborah stays dependency-free: all imports of ``tirzah`` / ``pymongo`` are
lazy and fail-soft. Use when ``--estate-live`` / ``live=True`` and a real
memory store should back retrieve + open-question persistence.
"""

from __future__ import annotations

from typing import Any


def try_tirzah_db() -> Any | None:
    """Return Tirzah's configured Mongo database, or None."""
    try:
        from tirzah.deborah import try_live_db  # type: ignore[import-not-found]

        return try_live_db()
    except Exception:
        pass
    try:
        from pymongo import MongoClient  # type: ignore[import-not-found]

        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return client["mnemosyne_dev"]
    except Exception:
        return None


def try_open_questions_db() -> Any | None:
    """Mongo handle for open-question persistence (same family DB when possible)."""
    return try_tirzah_db()


def prepare_live_slice(
    *,
    db: Any = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Assemble live dispatch + open-questions db for :func:`run_substrate_slice`.

    Returns a dict suitable for unpacking:
    ``dispatch``, ``open_questions_db``, ``live_ok``, ``db``, ``error``.
    """
    store = db
    dispatch: dict[str, Any] = {}
    error: str | None = None

    try:
        from tirzah.deborah import prepare_live_estate  # type: ignore[import-not-found]

        estate = prepare_live_estate(db=store, limit=limit)
        if estate.get("ok"):
            store = estate["db"]
            dispatch = dict(estate.get("dispatch") or {})
        else:
            error = str(estate.get("error") or "tirzah estate unavailable")
    except Exception as exc:
        error = f"tirzah.deborah unavailable: {type(exc).__name__}: {exc}"
        store = store or try_tirzah_db()

    # Merge Milcah live critique when importable (rule path offline-safe).
    try:
        from milcah.deborah import deborah_dispatch as milcah_dispatch  # type: ignore[import-not-found]

        dispatch = {**dispatch, **milcah_dispatch()}
    except Exception:
        pass

    if store is None and not dispatch:
        return {
            "live_ok": False,
            "db": None,
            "dispatch": {},
            "open_questions_db": None,
            "error": error or "no live adapters",
        }

    return {
        "live_ok": store is not None or bool(dispatch),
        "db": store,
        "dispatch": dispatch,
        "open_questions_db": store,
        "error": error,
    }
