"""Schema induction over UseTraces (genson-backed).

Requires the ``[mcp]`` extra. PI §43 motivates "schema from use", and PI §201
motivates emitting a confidence rather than a final, definite schema.
"""

from __future__ import annotations

from typing import Any, Iterable

try:
    from genson import SchemaBuilder  # type: ignore

    _IMPORT_ERROR: ImportError | None = None
except ImportError as _imp_err:  # pragma: no cover - extras not installed
    SchemaBuilder = None  # type: ignore[assignment]
    _IMPORT_ERROR = _imp_err


def _require_genson() -> None:
    if SchemaBuilder is None:
        raise ImportError(
            "family-resemblance[mcp] extra is required for schema induction; "
            "install via `pip install family-resemblance[mcp]`."
        ) from _IMPORT_ERROR


def induce_schema(samples: Iterable[Any]) -> dict:
    """Induce a JSON Schema from observed samples."""
    _require_genson()
    builder = SchemaBuilder()  # type: ignore[operator]
    for s in samples:
        builder.add_object(s)
    return builder.to_schema()


def induce_with_confidence(
    samples: Iterable[Any],
    min_support: int = 3,
    hide_below_support: bool = True,
) -> tuple[dict | None, float]:
    """Return (schema, confidence) where confidence ∈ [0, 1].

    Confidence = min(1, support / min_support); below `min_support` the
    schema is treated as provisional (PI §201, family-resemblance limit
    on rule-following).

    When ``hide_below_support`` is True (the default) and the number of
    observed samples is below ``min_support``, this function returns
    ``(None, conf)`` rather than emitting a schema. This realises the
    private-language argument (PI §243-315): a "rule" induced from a
    single use is not yet a rule. Pass ``hide_below_support=False`` to
    bypass the gate (useful for tests and debugging).

    Note: this is a *hide* gate, not a contradiction-driven *discard*.
    Contradiction-driven discard (PI §139 picture-and-application replay
    loop) is roadmapped for v0.2 via ``SchemaCandidate.contradictions``.
    """
    if min_support <= 0:
        raise ValueError(f"min_support must be > 0; got {min_support}")
    samples_list = list(samples)
    n = len(samples_list)
    conf = min(1.0, float(n) / float(min_support))
    if hide_below_support and n < min_support:
        return None, conf
    schema = induce_schema(samples_list)
    return schema, conf


__all__ = ["induce_schema", "induce_with_confidence"]
