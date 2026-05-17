"""Phase 1 smoke test — gives pytest --collect-only a node to find, exit 0."""

import family_resemblance


def test_version_string() -> None:
    assert family_resemblance.__version__ == "0.1.0.post1"
