"""Compatibility shim. The implementation is the versioned cairn_core package."""

import cairn_core.conformance as _impl

globals().update({key: value for key, value in vars(_impl).items() if not key.startswith("__")})
