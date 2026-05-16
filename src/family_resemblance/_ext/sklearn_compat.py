"""scikit-learn-contrib compatibility surface.

scikit-learn-contrib packages typically expose their estimators at the
top-level. `family_resemblance.WFRCluster` already does that via the
package `__init__`. This module exists as a stable re-export so future
adapters (e.g. `check_estimator` smoke tests) have a single import path
without depending on the internal `core.cluster` location.
"""

from family_resemblance.core.cluster import WFRCluster

__all__ = ["WFRCluster"]

# v0.2 roadmap: wire `sklearn.utils.estimator_checks.check_estimator(WFRCluster())`
# under `tests/test_sklearn_contrib.py` and document any waivers (notably the
# non-metric distance, which DBSCAN tolerates but check_estimator does not assert).
