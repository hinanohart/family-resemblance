"""FastMCP server skeleton — PI §43 + §201 + §133.

This module builds (but does not run) a minimal MCP server. It depends on
the ``[mcp]`` extra. The full induce-then-replay loop is roadmapped for
v0.2; the Phase 3 skeleton here is sufficient for `family-resemblance[mcp]`
to be import-tested.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .adapter import require_mcp
from .inducer import induce_with_confidence
from .trace import UseTrace


def build_server(
    name: str = "family-resemblance-mcp",
    *,
    min_support: int = 3,
) -> Dict[str, Any]:
    """Construct (but do not start) a minimal MCP server description.

    Returns a description dict so callers can compose a real `FastMCP`
    instance themselves without this module pinning the SDK class layout.
    """
    require_mcp()  # validates the [mcp] extra is installed
    return {
        "name": name,
        "ready": True,
        "induce_then_replay": {"min_support": min_support},
        "note": "Phase 3 skeleton; the full induce_then_replay loop ships in v0.2.",
    }


def summarise_traces(traces: List[UseTrace], min_support: int = 3) -> Dict[str, Any]:
    """For each tool name in `traces`, induce a schema and report confidence."""
    grouped: Dict[str, List[Any]] = {}
    for t in traces:
        grouped.setdefault(t.name, []).append(t.args)
    out: Dict[str, Any] = {}
    for name, args in grouped.items():
        schema, conf = induce_with_confidence(args, min_support=min_support)
        out[name] = {"schema": schema, "confidence": round(float(conf), 4)}
    return out


__all__ = ["build_server", "summarise_traces"]
