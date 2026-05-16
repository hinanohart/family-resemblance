"""scikit-learn-contrib compatibility surface.

scikit-learn-contrib packages typically expose their estimators at the
top-level. `family_resemblance.WFRCluster` already does that via the
package `__init__`. This module exists as a stable re-export so future
adapters (e.g. `check_estimator` smoke tests) have a single import path
without depending on the internal `core.cluster` location.
"""

from family_resemblance.core.cluster import WFRCluster

__all__ = ["WFRCluster"]
