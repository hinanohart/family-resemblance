"""CLI entry `fr` — cluster / inspect / version commands."""

from __future__ import annotations

import json

import numpy as np
import typer

from family_resemblance import __version__
from family_resemblance.core.cluster import WFRCluster
from family_resemblance.core.therapeutic import describe

app = typer.Typer(
    add_completion=False,
    help="family-resemblance: weighted family-resemblance clustering (PI §65-67).",
)


def _load_csv(path: str) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", dtype=float, ndmin=2)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def cluster(
    path: str = typer.Argument(..., help="CSV with rows = samples, cols = features."),
    eps: float = typer.Option(0.5, help="DBSCAN epsilon in WFR distance."),
    min_samples: int = typer.Option(2, help="DBSCAN min_samples."),
    kernel: str = typer.Option("rbf", help="Per-feature similarity kernel."),
) -> None:
    """Cluster samples in PATH and emit family labels as JSON."""
    X = _load_csv(path)
    labels = WFRCluster(eps=eps, min_samples=min_samples, kernel=kernel).fit_predict(X)
    typer.echo(json.dumps({"labels": labels.tolist()}, indent=2))


@app.command()
def inspect(
    path: str = typer.Argument(..., help="CSV with rows = samples, cols = features."),
    eps: float = typer.Option(0.5),
    min_samples: int = typer.Option(2),
    threshold: float = typer.Option(0.5, help="Confidence threshold (PI §133)."),
) -> None:
    """Cluster PATH and emit per-sample therapeutic descriptions."""
    X = _load_csv(path)
    wfr = WFRCluster(eps=eps, min_samples=min_samples).fit(X)
    conf = wfr.family_membership()
    out = []
    for i, (lab, c) in enumerate(zip(wfr.labels_.tolist(), conf.tolist())):
        r = describe(int(lab), float(c), threshold=threshold)
        out.append(
            {
                "i": i,
                "label": r.label,
                "confidence": round(r.confidence, 4),
                "boundary": r.boundary,
                "description": r.description,
            }
        )
    typer.echo(json.dumps(out, indent=2))


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
