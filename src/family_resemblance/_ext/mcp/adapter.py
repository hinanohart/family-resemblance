"""Thin MCP SDK wrapper.

Isolates ``mcp`` SDK churn from the rest of the codebase. Requires the
``[mcp]`` extra.
"""

from __future__ import annotations

from typing import Any

try:
    import mcp  # type: ignore  # noqa: F401

    _IMPORT_ERROR: ImportError | None = None
except ImportError as _imp_err:  # pragma: no cover
    mcp = None  # type: ignore[assignment]
    _IMPORT_ERROR = _imp_err


def require_mcp() -> Any:
    """Return the imported ``mcp`` module or raise a helpful ImportError."""
    if mcp is None:
        raise ImportError(
            "family-resemblance[mcp] extra is required; "
            "install via `pip install family-resemblance[mcp]`."
        ) from _IMPORT_ERROR
    return mcp


def is_available() -> bool:
    """``True`` if the ``mcp`` SDK is importable in this environment."""
    return mcp is not None


__all__ = ["require_mcp", "is_available"]
