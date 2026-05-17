# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0.post1] - 2026-05-17

### Fixed

- README relative links (`LICENSE`, `data/PROVENANCE.md`,
  `src/family_resemblance/core/wfr.py`, `tests/test_provenance_policy.py`,
  `CHANGELOG.md`) rewritten to absolute `github.com/hinanohart/...` URLs.
  PyPI renders the README as-is and treats relative links as relative to
  the PyPI page URL, where they 404. No source-code change.
- README header gains a PyPI version badge.

## [0.1.0] - 2026-05-17

### Added

- `WFRCluster`: scikit-learn-compatible weighted family-resemblance
  clusterer (`BaseEstimator + ClusterMixin`). Internally DBSCAN with
  `metric="precomputed"` over a pairwise WFR distance matrix. No prototype,
  centroid, or cluster-centre attribute is ever exposed (PI §65–67).
- `TherapeuticResponse` + `describe()`: PI §133 honest description when a
  point lies on a family boundary (low confidence) or on the noise label
  (PI §201). NaN / ±∞ confidences are rejected explicitly.
- `wfr_similarity`, `wfr_distance`, `feature_similarity`: standalone WFR
  primitives with three kernels (`rbf`, `linear`, `match`) and explicit
  per-feature weights.
- `fr` CLI (typer): `fr version`, `fr cluster <csv>`, `fr inspect <csv>`.
- `[mcp]` optional extra:
  - `UseTrace` dataclass (PI §43, meaning = use), with JSON roundtrip.
  - `induce_with_confidence(samples, min_support, hide_below_support)`:
    JSON-Schema induction over observed traces, with a PI §243–315 hide
    gate — schemas are not emitted until a tool has been seen
    `min_support` times.
  - FastMCP `build_server` skeleton + `summarise_traces` (Phase 3 stage;
    the full induce-then-replay loop ships in v0.2).
- `[viz]` optional extra (matplotlib + seaborn; plotting helpers are
  roadmapped for v0.2).
- Project Gutenberg eBook #5740 (bilingual *Tractatus*: Ogden 1922 +
  German original) shipped under `data/` as a reference corpus, US PD.
- `tests/test_provenance_policy.py`: automatic enforcement of the PI
  fair-use quotation budget (≤ 50 words per §, ≤ 250 words across the
  whole repo).

### Tested

- 74 tests, statement coverage 98% (`pytest --cov=family_resemblance`);
  `core/wfr.py`, `core/cluster.py`, `core/therapeutic.py` reach 100%.
- CLI smoke via `typer.testing.CliRunner`.
- `get_type_hints()` resolves all `[mcp]` annotations (autodoc-safe).

### Known limits

- WFR distance is **not** metric — the triangle inequality is violated by
  design. Do not pair `WFRCluster` with Ward / complete-link Agglomerative
  clustering. DBSCAN and HDBSCAN tolerate this; the default backend is
  DBSCAN.
- Memory: `wfr_similarity` materialises an `(n, n, n_features)` float64
  intermediate. For `n = 10 000, d = 10` this is ≈ 8 GiB. Chunk or
  pre-aggregate for large inputs.
- The `[mcp]` server is a skeleton; runtime use is not yet wired into
  FastMCP transport. See `_ext/mcp/server.py` for the v0.2 roadmap.

### Roadmap (v0.2)

- SQLite-backed `UseTrace` persistence (Layer L3 in the architecture).
- Bootstrap confidence intervals / p-values for `family_membership()`.
- `SchemaCandidate.contradictions` counter wired into induce-then-replay
  (PI §139 picture-and-application loop).
- `Game(participants, rules, boundary_conf)` dataclass for PI §7 / §23
  language-game framing of multi-tool boundaries (currently informal).
- `feature_weights` learning from labelled / unlabelled data.
- scikit-learn-contrib admission (templates + `check_estimator` pass).
- `examples/mcp_translate_demo.py` runnable demo for the `[mcp]` extra.
- `[viz]` plotting helpers for resemblance heatmaps.

[Unreleased]: https://github.com/hinanohart/family-resemblance/compare/v0.1.0.post1...HEAD
[0.1.0.post1]: https://github.com/hinanohart/family-resemblance/releases/tag/v0.1.0.post1
[0.1.0]: https://github.com/hinanohart/family-resemblance/releases/tag/v0.1.0
