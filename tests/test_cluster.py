"""Tests for WFRCluster — fit / fit_predict / family_membership / validation."""

from __future__ import annotations

import numpy as np
import pytest

from family_resemblance import WFRCluster


@pytest.fixture
def two_groups():
    return np.array([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 4.9]])


def test_wfrcluster_separates_two_groups(two_groups):
    labels = WFRCluster(eps=0.4, min_samples=2).fit_predict(two_groups)
    assert set(labels.tolist()) == {0, 1}
    assert labels[0] == labels[1]
    assert labels[2] == labels[3]
    assert labels[0] != labels[2]


def test_wfrcluster_no_prototype_attributes(two_groups):
    wfr = WFRCluster().fit(two_groups)
    # Family-resemblance has no centre; assert library never grows one.
    assert not hasattr(wfr, "cluster_centers_")
    assert not hasattr(wfr, "prototype_")
    assert not hasattr(wfr, "centroid_")


def test_wfrcluster_labels_and_n_features(two_groups):
    wfr = WFRCluster().fit(two_groups)
    assert wfr.n_features_in_ == 2
    assert wfr.labels_.shape == (4,)


def test_wfrcluster_distance_matrix_stored():
    X = np.array([[0.0, 0.0], [1.0, 1.0]])
    wfr = WFRCluster(eps=0.5).fit(X)
    D = wfr.distance_matrix_
    assert D.shape == (2, 2)
    assert D[0, 0] == pytest.approx(0.0)
    assert D[1, 1] == pytest.approx(0.0)
    assert D[0, 1] == pytest.approx(D[1, 0])


def test_wfrcluster_family_membership_noise_zero():
    X = np.array([[0.0, 0.0]])
    wfr = WFRCluster(eps=0.4, min_samples=2).fit(X)
    conf = wfr.family_membership()
    assert conf.tolist() == [0.0]


def test_wfrcluster_family_membership_full_confidence(two_groups):
    wfr = WFRCluster(eps=0.4, min_samples=2).fit(two_groups)
    conf = wfr.family_membership()
    assert (conf > 0.9).all()


def test_wfrcluster_family_membership_before_fit_raises():
    with pytest.raises(RuntimeError, match=r"fit\(\)"):
        WFRCluster().family_membership()


def test_wfrcluster_validates_eps_range():
    with pytest.raises(ValueError, match="eps must lie in"):
        WFRCluster(eps=2.0).fit(np.array([[0.0]]))


def test_wfrcluster_validates_min_samples():
    with pytest.raises(ValueError, match="min_samples must be"):
        WFRCluster(min_samples=0).fit(np.array([[0.0]]))


def test_wfrcluster_rejects_1d_input():
    with pytest.raises(ValueError, match="must be 2-d"):
        WFRCluster().fit(np.array([1.0, 2.0, 3.0]))


def test_wfrcluster_feature_weights_used():
    # Zero-weight the second feature: clusters by first feature only.
    X = np.array([[0.0, 0.0], [0.0, 5.0], [5.0, 0.0], [5.0, 5.0]])
    wfr = WFRCluster(eps=0.3, min_samples=2, feature_weights=[1.0, 0.0]).fit(X)
    assert wfr.labels_[0] == wfr.labels_[1]
    assert wfr.labels_[2] == wfr.labels_[3]
    assert wfr.labels_[0] != wfr.labels_[2]


def test_wfrcluster_fit_predict_returns_labels(two_groups):
    labels = WFRCluster(eps=0.4, min_samples=2).fit_predict(two_groups)
    assert labels.shape == (4,)


def test_wfrcluster_sklearn_compat_reexport_is_same_class():
    from family_resemblance import WFRCluster as W1
    from family_resemblance._ext.sklearn_compat import WFRCluster as W2

    assert W1 is W2


def test_wfrcluster_default_params_settable():
    wfr = WFRCluster(kernel="linear", scale=2.0)
    assert wfr.kernel == "linear"
    assert wfr.scale == 2.0
