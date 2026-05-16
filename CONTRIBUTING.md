# Contributing

Thanks for your interest in `family-resemblance`. Issues, bug reports, and
pull requests are all welcome.

## Dev setup

```bash
git clone https://github.com/runza/family-resemblance
cd family-resemblance
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[mcp,viz,dev]"
pytest -q --cov=family_resemblance --cov-report=term-missing
```

The full suite takes a few seconds and currently sits at 72 tests / 99%
statement coverage.

## Run tests

```bash
pytest -q                                        # full suite
pytest --cov=family_resemblance                  # with coverage
pytest tests/test_provenance_policy.py           # fair-use guardrail only
pytest tests/test_cli.py -v                      # CLI smoke
```

## Repository layout

```
src/family_resemblance/
├─ core/
│  ├─ wfr.py             # pairwise WFR similarity / distance
│  ├─ cluster.py         # WFRCluster: sklearn-compatible estimator
│  └─ therapeutic.py     # PI §133 honest description
├─ cli.py                # typer-based `fr` CLI
├─ _ext/
│  ├─ sklearn_compat.py  # re-export surface for scikit-learn-contrib
│  └─ mcp/               # [mcp] optional extra
│     ├─ trace.py        # UseTrace dataclass
│     ├─ inducer.py      # induce_with_confidence (PI §201, §243)
│     ├─ adapter.py      # mcp SDK lazy import
│     └─ server.py       # FastMCP skeleton (v0.2 full loop)
data/                    # Tractatus PD corpus + PROVENANCE.md
tests/                   # 72 tests, coverage 99%
examples/                # runnable demos
```

## Design constraints (read before changing core)

1. **No prototype, ever.** PI §65–67 forbids representing a family by a
   single centre. Do not add `cluster_centers_`, `centroid_`, `prototype_`,
   or any other attribute that promotes a single representative. The
   `test_wfrcluster_no_prototype_attributes` test enforces this.
2. **WFR distance is not metric.** Don't pair `WFRCluster` with Ward,
   complete-link, or any clusterer that assumes the triangle inequality.
   DBSCAN / HDBSCAN tolerate non-metric distances. The docstring on
   `wfr_distance` is the authoritative reference.
3. **`[mcp]` is optional.** The package must always install and import
   without `mcp` or `genson` present. Use the lazy `_require_genson()` /
   `require_mcp()` helpers, never an unconditional `import mcp` at module
   top.
4. **Philosophical Investigations is under copyright.** See
   `data/PROVENANCE.md` for the per-section (≤ 50 words) and per-repo
   (≤ 250 words) quotation budget. `tests/test_provenance_policy.py`
   enforces this automatically — adding too much PI text to a README,
   docstring, or comment fails CI.
5. **Confidence has to be finite.** `describe()` rejects NaN / ±∞ rather
   than silently flowing into the high-confidence branch.

## Pull-request checklist

- [ ] `pytest -q` passes locally.
- [ ] Statement coverage stays ≥ 95%.
- [ ] `fr version` still resolves after `pip install -e .`.
- [ ] No new top-level `centroid_` / `prototype_` / `cluster_centers_`
      attribute on any estimator class.
- [ ] PI quotations within the budget (`tests/test_provenance_policy.py`).
- [ ] CHANGELOG entry under `[Unreleased]` for user-facing changes.

## Commit and tag conventions

- Commit subjects follow `phase-<n>: <short summary>` while the project is
  pre-1.0. Post-1.0 we switch to conventional commits (`feat:`, `fix:`,
  `docs:`, etc.).
- Version tags follow SemVer: `v0.1.0`, `v0.2.0-rc1`, …

## Reporting security issues

Please use GitHub's **Security → Report a vulnerability** feature on the
repository for confidential disclosure rather than filing a public issue
or emailing maintainers directly. The maintainer responds via the same
private thread.
