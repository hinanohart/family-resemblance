"""Weighted Family Resemblance (WFR) distance — PI §65-67.

family members share *overlapping* features rather than a single defining
feature shared by all. This module computes pairwise resemblance as a
weighted aggregation of feature-wise similarities, deliberately avoiding
any centroid or prototype representation (contrast: Prototypical Networks).

Algorithmic inspiration: arXiv:2601.01127 (Weighted Family Resemblance
Clustering). The implementation here is a faithful port of the pairwise
similarity formulation, simplified to remain under 200 LoC and to expose
only what `WFRCluster` needs.
"""

from __future__ import annotations

from typing import Optional, Union

import numpy as np

ArrayLike = Union[np.ndarray, list, tuple]

VALID_KERNELS = ("rbf", "linear", "match")


def feature_similarity(
    x: np.ndarray, y: np.ndarray, kernel: str = "rbf", scale: float = 1.0
) -> np.ndarray:
    """Per-feature similarity between two samples of equal length.

    Returns an array of shape (n_features,) with values in [0, 1] for `rbf`
    and `match`, and in (0, 1] for `linear`. No reduction is performed —
    aggregation is the caller's responsibility (see `wfr_similarity`).
    """
    if kernel not in VALID_KERNELS:
        raise ValueError(f"unknown kernel {kernel!r}; valid: {VALID_KERNELS}")
    diff = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    if kernel == "rbf":
        if scale <= 0:
            raise ValueError(f"scale must be > 0 for rbf; got {scale}")
        return np.exp(-(diff**2) / (2.0 * scale * scale))
    if kernel == "linear":
        return 1.0 / (1.0 + np.abs(diff))
    return (diff == 0).astype(float)


def _check_weights(weights: Optional[ArrayLike], n_features: int) -> np.ndarray:
    if weights is None:
        return np.ones(n_features, dtype=float) / n_features
    w = np.asarray(weights, dtype=float).ravel()
    if w.shape != (n_features,):
        raise ValueError(
            f"feature_weights shape {w.shape} != (n_features,) = ({n_features},)"
        )
    if not np.all(np.isfinite(w)) or np.any(w < 0):
        raise ValueError("feature_weights must be finite and non-negative")
    total = float(w.sum())
    if total <= 0:
        raise ValueError("feature_weights must have positive sum")
    return w / total


def wfr_similarity(
    X: ArrayLike,
    weights: Optional[ArrayLike] = None,
    kernel: str = "rbf",
    scale: float = 1.0,
) -> np.ndarray:
    """Pairwise WFR similarity matrix in [0, 1].

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
    weights : array-like of shape (n_features,), optional
        Per-feature weights. None = uniform. Renormalised to sum to 1.
    kernel : {"rbf", "linear", "match"}
    scale : float, default=1.0
        RBF bandwidth; ignored for `linear` / `match`.

    Notes
    -----
    The matrix is symmetric with unit diagonal (a thing resembles itself
    perfectly). It is **not** necessarily transitive — a hallmark of
    family-resemblance (PI §66).

    Memory: a vectorised intermediate of shape ``(n, n, n_features)`` is
    materialised, so peak memory grows as ``O(n^2 * n_features * 8 bytes)``.
    For ``n = 10000, n_features = 10`` this is ~8 GiB; chunk your input or
    pre-aggregate features for large ``n``.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError(f"X must be 2-d (n_samples, n_features); got ndim={X.ndim}")
    n, d = X.shape
    if n == 0:
        return np.zeros((0, 0), dtype=float)
    w = _check_weights(weights, d)

    # Vectorised pairwise feature diff: shape (n, n, d)
    diff = X[:, None, :] - X[None, :, :]
    if kernel == "rbf":
        if scale <= 0:
            raise ValueError(f"scale must be > 0 for rbf; got {scale}")
        per_feature = np.exp(-(diff**2) / (2.0 * scale * scale))
    elif kernel == "linear":
        per_feature = 1.0 / (1.0 + np.abs(diff))
    elif kernel == "match":
        per_feature = (diff == 0).astype(float)
    else:
        raise ValueError(f"unknown kernel {kernel!r}; valid: {VALID_KERNELS}")

    # Weighted aggregation across features → (n, n)
    S = per_feature @ w
    # Numerical safety: clamp to [0, 1] and re-symmetrise
    S = np.clip(S, 0.0, 1.0)
    S = 0.5 * (S + S.T)
    np.fill_diagonal(S, 1.0)
    return S


def wfr_distance(
    X: ArrayLike,
    weights: Optional[ArrayLike] = None,
    kernel: str = "rbf",
    scale: float = 1.0,
) -> np.ndarray:
    """Pairwise WFR distance matrix in [0, 1] = 1 − similarity.

    Suitable for `metric="precomputed"` clustering. The metric is symmetric
    and zero on the diagonal but does **not** satisfy the triangle
    inequality in general — DBSCAN/HDBSCAN tolerate this, Ward/Agglomerative
    with single-link generally do; avoid algorithms that assume a true metric.
    """
    return 1.0 - wfr_similarity(X, weights=weights, kernel=kernel, scale=scale)


__all__ = [
    "feature_similarity",
    "wfr_similarity",
    "wfr_distance",
    "VALID_KERNELS",
]
