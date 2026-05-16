"""Tests for [mcp] extra modules — trace, inducer, adapter, server."""

from __future__ import annotations

import json

import pytest

from family_resemblance._ext.mcp.adapter import is_available
from family_resemblance._ext.mcp.inducer import induce_schema, induce_with_confidence
from family_resemblance._ext.mcp.server import build_server, summarise_traces
from family_resemblance._ext.mcp.trace import UseTrace


def test_usetrace_dataclass_basics():
    t = UseTrace(name="translate", args={"x": 1}, ret="ok")
    assert t.name == "translate"
    assert t.ret == "ok"
    assert t.ts > 0
    assert t.repair_of is None


def test_usetrace_json_roundtrip():
    t = UseTrace(name="x", args=[1, 2], ret={"ok": True})
    s = t.to_json()
    d = json.loads(s)
    assert d["name"] == "x"
    assert d["args"] == [1, 2]
    assert d["ret"] == {"ok": True}
    t2 = UseTrace.from_json(s)
    assert t2.name == "x"
    assert t2.args == [1, 2]


def test_usetrace_repair_of_set():
    t = UseTrace(name="x", args={}, ret=None, repair_of=5)
    assert t.repair_of == 5


def test_induce_with_confidence_hide_below_support():
    schema, conf = induce_with_confidence([{"a": 1}], min_support=3)
    assert schema is None
    assert conf == pytest.approx(1 / 3)


def test_induce_with_confidence_emits_when_met():
    schema, conf = induce_with_confidence([{"a": 1}, {"a": 2}, {"a": 3}], min_support=3)
    assert schema is not None
    assert conf == 1.0
    assert "properties" in schema


def test_induce_with_confidence_bypass_gate():
    schema, conf = induce_with_confidence(
        [{"a": 1}], min_support=3, hide_below_support=False
    )
    assert schema is not None
    assert conf == pytest.approx(1 / 3)


def test_induce_with_confidence_caps_at_one():
    schema, conf = induce_with_confidence([{"a": 1}] * 10, min_support=3)
    assert schema is not None
    assert conf == 1.0


def test_induce_with_confidence_rejects_non_positive_min_support():
    with pytest.raises(ValueError, match="min_support must be > 0"):
        induce_with_confidence([{"a": 1}], min_support=0)


def test_induce_schema_basic():
    schema = induce_schema([{"a": 1}, {"a": 2}])
    assert "properties" in schema
    assert "a" in schema["properties"]


def test_adapter_is_available_bool():
    assert is_available() in (True, False)


def test_build_server_returns_description():
    if not is_available():
        pytest.skip("mcp SDK not installed")
    desc = build_server(name="x", min_support=5)
    assert desc["name"] == "x"
    assert desc["ready"] is True
    assert desc["induce_then_replay"]["min_support"] == 5


def test_summarise_traces_groups_and_gates():
    traces = [
        UseTrace(name="t1", args={"a": 1}, ret=None),
        UseTrace(name="t1", args={"a": 2}, ret=None),
        UseTrace(name="t1", args={"a": 3}, ret=None),
        UseTrace(name="t2", args={"b": 1}, ret=None),
    ]
    out = summarise_traces(traces, min_support=3)
    assert set(out.keys()) == {"t1", "t2"}
    assert out["t1"]["schema"] is not None
    assert out["t1"]["confidence"] == 1.0
    # t2 has 1 sample < min_support=3 -> hidden
    assert out["t2"]["schema"] is None
    assert out["t2"]["confidence"] == pytest.approx(1 / 3, abs=1e-4)
