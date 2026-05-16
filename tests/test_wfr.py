"""Tests for core/wfr.py — feature_similarity, wfr_similarity, wfr_distance."""

from __future__ import annotations

import numpy as np
import pytest

from family_resemblance.core.wfr import (
    VALID_KERNELS,
    feature_similarity,
    wfr_distance,
    wfr_similarity,
)


def test_feature_similarity_match_kernel():
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([1.0, 9.0, 3.0])
    fs = feature_similarity(x, y, kernel="match")
    assert fs.tolist() == [1.0, 0.0, 1.0]


def test_feature_similarity_rbf_value():
    fs = feature_similarity(
        np.array([0.0, 0.0]), np.array([1.0, 0.0]), kernel="rbf", scale=1.0
    )
    assert fs[0] == pytest.approx(np.exp(-0.5))
    assert fs[1] == pytest.approx(1.0)


def test_feature_similarity_linear_value():
    fs = feature_similarity(np.array([0.0]), np.array([1.0]), kernel="linear")
    assert fs[0] == pytest.approx(0.5)


def test_feature_similarity_unknown_kernel():
    with pytest.raises(ValueError, match="unknown kernel"):
        feature_similarity(np.array([0.0]), np.array([1.0]), kernel="quartz")


def test_feature_similarity_rbf_negative_scale_rejected():
    with pytest.raises(ValueError, match="scale must be > 0"):
        feature_similarity(np.array([0.0]), np.array([1.0]), kernel="rbf", scale=-1.0)


def test_wfr_similarity_unit_diagonal_and_symmetry():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(8, 4))
    S = wfr_similarity(X)
    assert S.shape == (8, 8)
    np.testing.assert_allclose(np.diag(S), 1.0)
    np.testing.assert_allclose(S, S.T)


def test_wfr_similarity_identical_points():
    X = np.zeros((3, 4))
    S = wfr_similarity(X)
    np.testing.assert_allclose(S, 1.0)


def test_wfr_similarity_explicit_weights_concentrate():
    X = np.array([[0.0, 0.0], [10.0, 0.0]])
    S = wfr_similarity(X, weights=[0.0, 1.0])
    assert S[0, 1] == pytest.approx(1.0)


def test_wfr_similarity_weights_renormalised():
    X = np.array([[0.0, 0.0], [1.0, 1.0]])
    S_norm = wfr_similarity(X, weights=[1.0, 1.0])
    S_unnorm = wfr_similarity(X, weights=[2.0, 2.0])
    np.testing.assert_allclose(S_norm, S_unnorm)


def test_wfr_similarity_weights_wrong_shape():
    X = np.array([[0.0, 0.0], [1.0, 1.0]])
    with pytest.raises(ValueError, match="feature_weights shape"):
        wfr_similarity(X, weights=[1.0])


def test_wfr_similarity_negative_weights_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        wfr_similarity(np.array([[0.0], [1.0]]), weights=[-1.0])


def test_wfr_similarity_zero_sum_weights_rejected():
    with pytest.raises(ValueError, match="positive sum"):
        wfr_similarity(np.array([[0.0, 0.0], [1.0, 1.0]]), weights=[0.0, 0.0])


def test_wfr_similarity_handles_empty_input():
    S = wfr_similarity(np.zeros((0, 3)))
    assert S.shape == (0, 0)


def test_wfr_similarity_rejects_1d_input():
    with pytest.raises(ValueError, match="must be 2-d"):
        wfr_similarity(np.array([1.0, 2.0, 3.0]))


def test_wfr_similarity_rejects_zero_scale_rbf():
    with pytest.raises(ValueError, match="scale must be > 0"):
        wfr_similarity(np.array([[0.0], [1.0]]), kernel="rbf", scale=0.0)


def test_wfr_similarity_unknown_kernel_at_pairwise():
    with pytest.raises(ValueError, match="unknown kernel"):
        wfr_similarity(np.array([[0.0], [1.0]]), kernel="quartz")


def test_wfr_similarity_linear_kernel_returns_values_in_unit_interval():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(6, 3))
    S = wfr_similarity(X, kernel="linear")
    assert (S >= 0.0).all() and (S <= 1.0).all()


def test_wfr_similarity_match_kernel_binary():
    X = np.array([[0, 0, 0], [0, 1, 0], [1, 1, 0]], dtype=float)
    S = wfr_similarity(X, kernel="match")
    assert S[0, 1] == pytest.approx(2 / 3)
    assert S[1, 2] == pytest.approx(2 / 3)
    assert S[0, 2] == pytest.approx(1 / 3)


def test_wfr_distance_complement_of_similarity():
    X = np.array([[0.0, 0.0], [0.5, 0.5], [1.0, 1.0]])
    S = wfr_similarity(X)
    D = wfr_distance(X)
    np.testing.assert_allclose(D, 1.0 - S)


def test_wfr_distance_clipped_to_unit_interval():
    rng = np.random.default_rng(7)
    X = rng.normal(size=(10, 3))
    D = wfr_distance(X)
    assert (D >= 0.0).all() and (D <= 1.0).all()


def test_valid_kernels_constant_exposed():
    assert set(VALID_KERNELS) >= {"rbf", "linear", "match"}
