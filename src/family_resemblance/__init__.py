"""family-resemblance: weighted family-resemblance clustering (Wittgenstein PI §65-67)."""

from family_resemblance.core.cluster import WFRCluster
from family_resemblance.core.therapeutic import (
    DEFAULT_THRESHOLD,
    TherapeuticResponse,
    describe,
)
from family_resemblance.core.wfr import (
    VALID_KERNELS,
    feature_similarity,
    wfr_distance,
    wfr_similarity,
)

__version__ = "0.1.0.post1"

__all__ = [
    "__version__",
    "WFRCluster",
    "TherapeuticResponse",
    "describe",
    "DEFAULT_THRESHOLD",
    "wfr_similarity",
    "wfr_distance",
    "feature_similarity",
    "VALID_KERNELS",
]
