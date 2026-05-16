"""Tests for the typer-based `fr` CLI (version / cluster / inspect)."""

from __future__ import annotations

import json

import numpy as np
import pytest
from typer.testing import CliRunner

from family_resemblance.cli import app


@pytest.fixture
def csv_path(tmp_path):
    p = tmp_path / "X.csv"
    X = np.array([[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 4.9]])
    np.savetxt(p, X, delimiter=",")
    return str(p)


def test_version_command():
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "0.1.0.dev0"


def test_cluster_command(csv_path):
    result = CliRunner().invoke(
        app, ["cluster", csv_path, "--eps", "0.4", "--min-samples", "2"]
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert "labels" in data
    assert len(data["labels"]) == 4


def test_cluster_command_default_args(csv_path):
    result = CliRunner().invoke(app, ["cluster", csv_path])
    assert result.exit_code == 0, result.stdout


def test_inspect_command(csv_path):
    result = CliRunner().invoke(
        app, ["inspect", csv_path, "--eps", "0.4", "--min-samples", "2"]
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) == 4
    for row in data:
        assert "i" in row
        assert "label" in row
        assert "confidence" in row
        assert "boundary" in row
        assert "description" in row


def test_help_top_level():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "family-resemblance" in result.stdout
    assert "version" in result.stdout
    assert "cluster" in result.stdout
    assert "inspect" in result.stdout


def test_cluster_help():
    result = CliRunner().invoke(app, ["cluster", "--help"])
    assert result.exit_code == 0
    assert "eps" in result.stdout
