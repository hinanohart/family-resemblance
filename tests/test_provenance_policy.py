"""Automatic enforcement of the PI fair-use quotation policy.

PROVENANCE.md commits to two limits when quoting *Philosophical Investigations*:
* per `§N` reference: ≤ 50 words,
* across the whole repository: ≤ 250 words total.

This test scans repo-level Markdown and Python sources for `§N "…"` patterns
and fails the build if either limit is breached. The corpus directory
``data/`` is excluded because Tractatus is public-domain and not subject to
the policy.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PER_SECTION_LIMIT = 50
REPO_TOTAL_LIMIT = 250

# Match `§N` (optionally with a sub-range like `§65-67`) followed within ~80
# characters by a quoted passage. The quote may use ASCII or curly quotes.
_SECTION_QUOTE_RE = re.compile(
    r'§\s*(\d+(?:[-–]\d+)?)[^\n"“]{0,80}["“]([^"”\n]{1,500})["”]'
)


def _files_to_scan() -> list[Path]:
    paths: list[Path] = []
    for top_level in ("README.md", "CHANGELOG.md", "CONTRIBUTING.md"):
        p = REPO / top_level
        if p.exists():
            paths.append(p)
    docs = REPO / "docs"
    if docs.exists():
        paths.extend(docs.rglob("*.md"))
    if (REPO / "src").exists():
        paths.extend((REPO / "src").rglob("*.py"))
    if (REPO / "tests").exists():
        paths.extend((REPO / "tests").rglob("*.py"))
    # PROVENANCE.md states the policy itself and the data/ corpus is PD;
    # neither should count toward the budget.
    return [p for p in paths if "PROVENANCE.md" not in str(p)]


def test_per_section_quotation_word_limit():
    over_limit: list[tuple[str, str, int]] = []
    for p in _files_to_scan():
        text = p.read_text(encoding="utf-8", errors="replace")
        for sec, quote in _SECTION_QUOTE_RE.findall(text):
            wc = len(quote.split())
            if wc > PER_SECTION_LIMIT:
                over_limit.append((str(p.relative_to(REPO)), sec, wc))
    assert not over_limit, (
        f"Per-section quotation exceeded {PER_SECTION_LIMIT} words: {over_limit}"
    )


def test_repo_total_quotation_word_limit():
    total = 0
    for p in _files_to_scan():
        text = p.read_text(encoding="utf-8", errors="replace")
        for _, quote in _SECTION_QUOTE_RE.findall(text):
            total += len(quote.split())
    assert total <= REPO_TOTAL_LIMIT, (
        f"Repo-wide PI quotation total {total} > {REPO_TOTAL_LIMIT}"
    )
