"""Therapeutic response — PI §133 honest description for low-confidence cases.

When WFR clustering yields a low-confidence family assignment we do not
invent a missing rule (PI §201). The therapeutic reading reports the limit
explicitly: a family-boundary point sits between overlapping similarities,
and no single rule decides its membership.
"""

from __future__ import annotations

import dataclasses as _dc
import math

DEFAULT_THRESHOLD: float = 0.5


@_dc.dataclass(frozen=True)
class TherapeuticResponse:
    """A boundary-aware label/confidence/description triple.

    Attributes
    ----------
    label : int
        Family label; -1 for noise.
    confidence : float
        Per-sample family confidence in [0, 1].
    description : str
        Human-readable status; high-confidence answers are short, boundary
        answers cite PI sections to make the limit explicit.
    boundary : bool
        True iff ``confidence < threshold`` or ``label == -1``.
    """

    label: int
    confidence: float
    description: str
    boundary: bool


def describe(
    label: int,
    confidence: float,
    threshold: float = DEFAULT_THRESHOLD,
) -> TherapeuticResponse:
    """Build a `TherapeuticResponse` from a label / confidence pair."""
    if not (0.0 <= float(threshold) <= 1.0):
        raise ValueError(f"threshold must lie in [0, 1]; got {threshold}")
    conf_in = float(confidence)
    if not math.isfinite(conf_in):
        raise ValueError(f"confidence must be finite; got {confidence!r}")
    conf = max(0.0, min(1.0, conf_in))
    if int(label) == -1:
        return TherapeuticResponse(
            label=-1,
            confidence=0.0,
            description=(
                "No family found for this point (DBSCAN noise label). "
                "Following PI §201, no single rule decides its membership."
            ),
            boundary=True,
        )
    if conf < float(threshold):
        return TherapeuticResponse(
            label=int(label),
            confidence=conf,
            description=(
                f"Point assigned to family {int(label)} with confidence {conf:.2f} "
                f"(< threshold {float(threshold):.2f}). The boundary is genuinely fuzzy "
                "(PI §65-67) and no centre defines the family."
            ),
            boundary=True,
        )
    return TherapeuticResponse(
        label=int(label),
        confidence=conf,
        description=f"Confident assignment to family {int(label)} (conf={conf:.2f}).",
        boundary=False,
    )


__all__ = ["TherapeuticResponse", "describe", "DEFAULT_THRESHOLD"]
