# Usage

This document walks through the main user-facing paths. For a quick
overview see [README.md](../README.md); for design constraints see
[CONTRIBUTING.md](../CONTRIBUTING.md).

## Python API

### Basic clustering

```python
import numpy as np
from family_resemblance import WFRCluster

X = np.array(
    [[0.0, 0.0], [0.1, 0.1], [5.0, 5.0], [5.1, 4.9]]
)
wfr = WFRCluster(eps=0.4, min_samples=2).fit(X)
print(wfr.labels_)               # [0 0 1 1]
print(wfr.family_membership())   # per-point confidence in [0, 1]
```

### Feature weights

If you know some features carry more information than others, pass
`feature_weights`. They are renormalised internally to sum to 1.

```python
# Cluster by the first feature only:
wfr = WFRCluster(feature_weights=[1.0, 0.0]).fit(X)

# Weight the second feature three times as much as the first:
wfr = WFRCluster(feature_weights=[1.0, 3.0]).fit(X)
```

### Similarity kernels

```python
WFRCluster(kernel="rbf",    scale=1.0).fit(X)   # default (Gaussian)
WFRCluster(kernel="linear").fit(X)              # 1 / (1 + |diff|)
WFRCluster(kernel="match").fit(X)               # categorical / exact-match
```

`scale` controls the RBF bandwidth and is ignored for the other kernels.

### Therapeutic mode (PI §133)

`describe()` turns a `(label, confidence)` pair into a boundary-aware
response. NaN and ±∞ confidences are rejected explicitly.

```python
from family_resemblance import describe

conf = wfr.family_membership()
for i, label in enumerate(wfr.labels_):
    r = describe(int(label), float(conf[i]), threshold=0.5)
    print(r.description)
    if r.boundary:
        # The model is being honest about being unsure — surface this!
        ...
```

### Standalone primitives

If you do not need the full `WFRCluster` estimator, the underlying
primitives are exposed directly:

```python
from family_resemblance import wfr_similarity, wfr_distance, feature_similarity

S = wfr_similarity(X, kernel="rbf", scale=1.0)   # (n, n), symmetric, 1 on the diagonal
D = wfr_distance(X)                              # 1 - S, suitable for metric="precomputed"
fs = feature_similarity(X[0], X[1], kernel="match")
```

## CLI

The `fr` console script is installed automatically.

```bash
fr version                                       # 0.1.0.dev0
fr cluster path/to/X.csv --eps 0.4 --min-samples 2
fr inspect path/to/X.csv --threshold 0.5
fr --help
fr cluster --help
```

`fr cluster` writes a JSON object: `{"labels": [0, 0, 1, 1]}`.

`fr inspect` writes a JSON list with one record per row:

```json
[
  {
    "i": 0, "label": 0, "confidence": 0.995,
    "boundary": false,
    "description": "Confident assignment to family 0 (conf=0.99)."
  }
]
```

The CSV must have one sample per row and one feature per column, with no
header.

## `[mcp]` optional extra

Install with `pip install "family-resemblance[mcp]"`. The package itself
still imports without these extras — only the `_ext/mcp/...` submodules
require them.

```python
from family_resemblance._ext.mcp.inducer import induce_with_confidence
from family_resemblance._ext.mcp.trace import UseTrace

# Below min_support -> (None, conf): PI §243-315 refuses to call one use a rule.
schema, conf = induce_with_confidence([{"a": 1}], min_support=3)
assert schema is None and conf == 1/3

# At or above min_support -> a real schema is emitted.
schema, conf = induce_with_confidence(
    [{"a": 1}, {"a": 2}, {"a": 3}], min_support=3
)
```

`UseTrace` is a JSON-serialisable dataclass:

```python
t = UseTrace(name="translate", args={"text": "hi", "to": "fr"}, ret="salut")
json_str = t.to_json()
back = UseTrace.from_json(json_str)
```

## Limits and pitfalls

- **Memory.** `wfr_similarity` materialises an `(n, n, n_features)` float64
  intermediate. For `n = 10 000, n_features = 10` this is ≈ 8 GiB.
  Chunk or pre-aggregate features for large `n`.
- **Non-metric distance.** Do not pair `WFRCluster` with hierarchical
  clusterers that assume the triangle inequality (Ward, complete-link).
  DBSCAN / HDBSCAN are safe.
- **`fr` requires `typer`.** `typer` is a hard dependency (not an extra),
  so a plain `pip install family-resemblance` is enough to use the CLI.
- **`[mcp]` server is a skeleton.** `build_server()` returns a description
  dict; full FastMCP transport, SQLite persistence, and induce-then-replay
  contradiction tracking are roadmapped for v0.2.
