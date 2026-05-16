"""Tests for therapeutic.describe and TherapeuticResponse — PI §133 / §201."""

from __future__ import annotations

import dataclasses

import pytest

from family_resemblance import DEFAULT_THRESHOLD, TherapeuticResponse, describe


def test_describe_high_confidence_no_boundary():
    r = describe(0, 0.9)
    assert isinstance(r, TherapeuticResponse)
    assert r.boundary is False
    assert r.label == 0
    assert r.confidence == pytest.approx(0.9)
    assert "Confident" in r.description


def test_describe_low_confidence_marks_boundary():
    r = describe(0, 0.3, threshold=0.5)
    assert r.boundary is True
    assert "PI §65-67" in r.description
    assert r.confidence == pytest.approx(0.3)


def test_describe_noise_label_cites_section_201():
    r = describe(-1, 0.9)  # confidence ignored when label == -1
    assert r.label == -1
    assert r.confidence == 0.0
    assert r.boundary is True
    assert "PI §201" in r.description


def test_describe_clips_above_one():
    r = describe(0, 1.5)
    assert r.confidence == pytest.approx(1.0)
    assert r.boundary is False


def test_describe_clips_below_zero():
    r = describe(0, -0.5, threshold=0.0)
    assert r.confidence == pytest.approx(0.0)


def test_describe_rejects_nan():
    with pytest.raises(ValueError, match="confidence must be finite"):
        describe(0, float("nan"))


def test_describe_rejects_pos_inf():
    with pytest.raises(ValueError, match="confidence must be finite"):
        describe(0, float("inf"))


def test_describe_rejects_neg_inf():
    with pytest.raises(ValueError, match="confidence must be finite"):
        describe(0, float("-inf"))


def test_describe_rejects_threshold_above_unit():
    with pytest.raises(ValueError, match="threshold must lie in"):
        describe(0, 0.5, threshold=1.5)


def test_describe_rejects_threshold_below_zero():
    with pytest.raises(ValueError, match="threshold must lie in"):
        describe(0, 0.5, threshold=-0.1)


def test_therapeutic_response_is_frozen():
    r = describe(0, 0.9)
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.label = 1  # type: ignore[misc]


def test_default_threshold_value():
    assert DEFAULT_THRESHOLD == 0.5


def test_describe_threshold_boundary_is_exclusive():
    # confidence == threshold -> not below -> not boundary
    r = describe(0, 0.5, threshold=0.5)
    assert r.boundary is False
