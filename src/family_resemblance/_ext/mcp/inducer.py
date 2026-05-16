"""Schema induction over UseTraces (genson-backed).

Requires the ``[mcp]`` extra. PI §43 motivates "schema from use", and PI §201
motivates emitting a confidence rather than a final, definite schema.
"""

from __future__ import annotations

from typing import Any, Iterable, Tuple

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
    samples: Iterable[Any], min_support: int = 3
) -> Tuple[dict, float]:
    """Return (schema, confidence) where confidence ∈ [0, 1].

    Confidence = min(1, support / min_support); below `min_support` the
    schema is treated as provisional (PI §201, family-resemblance limit
    on rule-following).
    """
    samples_list = list(samples)
    schema = induce_schema(samples_list)
    if min_support <= 0:
        raise ValueError(f"min_support must be > 0; got {min_support}")
    conf = min(1.0, float(len(samples_list)) / float(min_support))
    return schema, conf


__all__ = ["induce_schema", "induce_with_confidence"]
