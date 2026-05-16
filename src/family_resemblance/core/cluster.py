"""WFRCluster: sklearn-compatible family-resemblance clusterer.

Uses DBSCAN with a precomputed WFR distance matrix. No prototype is ever
selected (PI §65–67: families have no centre); density connectivity is used
to grow families, mirroring "overlapping similarities".
"""

from __future__ import annotations

from typing import Optional, Union

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin
from sklearn.cluster import DBSCAN

from .wfr import wfr_distance

ArrayLike = Union[np.ndarray, list, tuple]


class WFRCluster(BaseEstimator, ClusterMixin):
    """Weighted Family Resemblance clustering — prototype-free.

    Parameters
    ----------
    eps : float, default=0.5
        DBSCAN ε in WFR distance space (1 − similarity).
    min_samples : int, default=2
        DBSCAN `min_samples`; the smallest family size.
    feature_weights : array-like of shape (n_features,), optional
        Per-feature weights. ``None`` → uniform. Renormalised internally.
    kernel : {"rbf", "linear", "match"}, default="rbf"
        Per-feature similarity kernel passed to `wfr_distance`.
    scale : float, default=1.0
        RBF bandwidth (ignored for non-rbf kernels).

    Attributes
    ----------
    labels_ : ndarray of shape (n_samples,)
        Cluster labels. ``-1`` marks noise / unassigned points (PI §201).
    distance_matrix_ : ndarray of shape (n_samples, n_samples)
        The pairwise WFR distance matrix used for clustering.
    n_features_in_ : int
        Number of features seen during ``fit``.

    Examples
    --------
    >>> import numpy as np
    >>> from family_resemblance import WFRCluster
    >>> X = np.array([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 4.9]])
    >>> labels = WFRCluster(eps=0.4, min_samples=2).fit_predict(X)
    >>> set(labels.tolist()) <= {-1, 0, 1}
    True
    """

    def __init__(
        self,
        eps: float = 0.5,
        min_samples: int = 2,
        feature_weights: Optional[ArrayLike] = None,
        kernel: str = "rbf",
        scale: float = 1.0,
    ) -> None:
        self.eps = eps
        self.min_samples = min_samples
        self.feature_weights = feature_weights
        self.kernel = kernel
        self.scale = scale

    def _validate_params(self) -> None:
        if not (0.0 <= float(self.eps) <= 1.0):
            raise ValueError(f"eps must lie in [0, 1]; got {self.eps}")
        if int(self.min_samples) < 1:
            raise ValueError(f"min_samples must be >= 1; got {self.min_samples}")

    def fit(self, X: ArrayLike, y=None) -> "WFRCluster":
        self._validate_params()
        X = np.asarray(X, dtype=float)
        if X.ndim != 2:
            raise ValueError(
                f"X must be 2-d (n_samples, n_features); got ndim={X.ndim}"
            )
        self.n_features_in_ = X.shape[1]
        if X.shape[0] == 0:
            # Empty in, empty out — bypass DBSCAN, which rejects empty matrices.
            self.distance_matrix_ = np.zeros((0, 0), dtype=float)
            self.labels_ = np.zeros((0,), dtype=int)
            return self
        weights = (
            None
            if self.feature_weights is None
            else np.asarray(self.feature_weights, dtype=float)
        )
        D = wfr_distance(X, weights=weights, kernel=self.kernel, scale=self.scale)
        self.distance_matrix_ = D
        db = DBSCAN(
            eps=float(self.eps), min_samples=int(self.min_samples), metric="precomputed"
        )
        self.labels_ = db.fit_predict(D)
        return self

    def fit_predict(self, X: ArrayLike, y=None) -> np.ndarray:
        return self.fit(X).labels_

    def family_membership(self) -> np.ndarray:
        """Per-sample confidence ∈ [0, 1]: mean similarity to family co-members.

        Returns 0 for noise points (label = -1) and for singleton families.
        """
        if not hasattr(self, "distance_matrix_") or not hasattr(self, "labels_"):
            raise RuntimeError("fit() must be called before family_membership()")
        labels = self.labels_
        n = len(labels)
        conf = np.zeros(n, dtype=float)
        if n == 0:
            return conf
        idx = np.arange(n)
        for i in range(n):
            li = labels[i]
            if li == -1:
                continue
            mask = (labels == li) & (idx != i)
            if not mask.any():
                continue
            sim = 1.0 - self.distance_matrix_[i, mask]
            conf[i] = float(np.clip(sim.mean(), 0.0, 1.0))
        return conf


__all__ = ["WFRCluster"]
