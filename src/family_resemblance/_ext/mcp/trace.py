"""UseTrace — a single MCP tool call record (PI §43, meaning = use)."""

from __future__ import annotations

import dataclasses as _dc
import json
import time
from typing import Any, Optional


@_dc.dataclass
class UseTrace:
    """One observation of a tool call.

    Attributes
    ----------
    name : str
        Tool name as observed (no schema required).
    args : Any
        Argument payload; JSON-serialisable structures only.
    ret : Any
        Return payload; JSON-serialisable structures only.
    ts : float
        Unix timestamp of the call (seconds since epoch).
    repair_of : Optional[int]
        If this call is a repair attempt of an earlier failed trace, the
        index of the earlier trace within a trace store. ``None`` otherwise.
    """

    name: str
    args: Any
    ret: Any
    ts: float = _dc.field(default_factory=time.time)
    repair_of: Optional[int] = None

    def to_dict(self) -> dict:
        return _dc.asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, s: str) -> "UseTrace":
        return cls(**json.loads(s))


__all__ = ["UseTrace"]
