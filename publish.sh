#!/usr/bin/env bash
# publish.sh — family-resemblance v0.1.0 ONE-shot release script (Phase 7).
#
# This is the only manual step in the release pipeline. Build artefacts in
# dist/, the v0.1.0 git tag, and 74 green tests are produced automatically
# by Phases 1-6. This script wires them up to GitHub + PyPI.
#
# Usage:
#   ./publish.sh              # publish under the gh owner named in pyproject.toml
#   ./publish.sh --check      # dry-run; pre-flight only, no push, no upload
#
# Prerequisites:
#   * `gh` is logged in. The script auto-switches the active account if the
#     intended owner is already stored. Otherwise it tells you the exact
#     single command to log in as that owner.
#   * `~/.pypirc` is configured with a `__token__` entry, OR
#     `TWINE_USERNAME` / `TWINE_PASSWORD` env vars are set. The script never
#     reads or echoes those tokens; twine reads them directly.
#
# Idempotent: rerunning after a partial failure is safe (gh repo / release /
# twine all use existence-checks or --skip-existing).

set -euo pipefail
cd "$(dirname "$0")"

DRY_RUN=0
case "${1:-}" in
    --check)  DRY_RUN=1 ;;
    "")       ;;
    *)        echo "Usage: $0 [--check]"; exit 2 ;;
esac

PKG_NAME="family-resemblance"
PKG_UNDER="${PKG_NAME//-/_}"

# Parse owner + version from pyproject.toml so the script never disagrees
# with the package metadata.
HOMEPAGE_OWNER=$(
    awk -F'/' '/Homepage = "https:\/\/github\.com\//{print $4; exit}' pyproject.toml
)
PKG_VER=$(awk -F'"' '/^version = "/{print $2; exit}' pyproject.toml)
TAG="v$PKG_VER"

echo "==> Pre-flight"

[ -n "$HOMEPAGE_OWNER" ] \
    || { echo "ERROR: could not parse Homepage owner from pyproject.toml"; exit 1; }
[ -n "$PKG_VER" ] \
    || { echo "ERROR: could not parse version from pyproject.toml"; exit 1; }

git diff --quiet --exit-code \
    || { echo "ERROR: working tree dirty — commit or stash first"; exit 1; }
git diff --staged --quiet --exit-code \
    || { echo "ERROR: staged changes present"; exit 1; }
git rev-parse "$TAG" >/dev/null 2>&1 \
    || { echo "ERROR: tag $TAG not found — recreate before publishing"; exit 1; }

ls "dist/${PKG_UNDER}-${PKG_VER}.tar.gz" \
   "dist/${PKG_UNDER}-${PKG_VER}-py3-none-any.whl" >/dev/null 2>&1 \
    || { echo "ERROR: dist/ has no artefacts for version $PKG_VER (run: python -m build)"; exit 1; }
twine check dist/* >/dev/null \
    || { echo "ERROR: twine check failed"; exit 1; }

if [ -x .venv/bin/pytest ]; then
    .venv/bin/pytest -q >/dev/null \
        || { echo "ERROR: pytest not green (.venv)"; exit 1; }
elif command -v pytest >/dev/null 2>&1; then
    pytest -q >/dev/null \
        || { echo "ERROR: pytest not green (system)"; exit 1; }
else
    echo "ERROR: neither .venv/bin/pytest nor system pytest available"; exit 1
fi

# gh auth: try to auto-align active account with HOMEPAGE_OWNER.
CURRENT_GH=$(gh api user --jq .login 2>/dev/null || echo "")
if [ -z "$CURRENT_GH" ]; then
    cat <<EOF
ERROR: gh is not authenticated. Run once:
    gh auth login -u $HOMEPAGE_OWNER
then re-run: ./publish.sh
EOF
    exit 1
fi

if [ "$CURRENT_GH" != "$HOMEPAGE_OWNER" ]; then
    # Discover all stored gh accounts (regardless of which is active).
    STORED=$(gh auth status 2>&1 \
        | grep -oE 'account [A-Za-z0-9_-]+' \
        | awk '{print $2}' | sort -u | tr '\n' ' ')
    if echo " $STORED " | grep -q " $HOMEPAGE_OWNER "; then
        echo "==> Switching gh active account: $CURRENT_GH → $HOMEPAGE_OWNER"
        gh auth switch -u "$HOMEPAGE_OWNER" >/dev/null
        CURRENT_GH=$(gh api user --jq .login 2>/dev/null || echo "")
    fi
fi

if [ "$CURRENT_GH" != "$HOMEPAGE_OWNER" ]; then
    cat <<EOF
ERROR: gh active user mismatch and the intended owner is not stored locally.
  pyproject.toml Homepage owner: $HOMEPAGE_OWNER
  gh active user:                $CURRENT_GH
  stored accounts:               ${STORED:-(none)}

To finish publishing, pick ONE of:

  (a) Log in once as $HOMEPAGE_OWNER (recommended; keeps attribution):
        gh auth login -u $HOMEPAGE_OWNER
        ./publish.sh

  (b) Publish under $CURRENT_GH instead (changes attribution everywhere):
        sed -i "s|github.com/$HOMEPAGE_OWNER|github.com/$CURRENT_GH|g" \\
            pyproject.toml CHANGELOG.md README.md
        git commit -am "chore: switch attribution to $CURRENT_GH"
        python -m build && git tag -f $TAG && ./publish.sh
EOF
    exit 1
fi

echo "==> Pre-flight PASS (owner=$HOMEPAGE_OWNER, tag=$TAG, dist=$PKG_VER)"

if [ "$DRY_RUN" -eq 1 ]; then
    echo "==> --check mode: stopping before push/upload."
    exit 0
fi

echo "==> 1/4 ensure GitHub repo exists (idempotent)"
if ! gh repo view "$HOMEPAGE_OWNER/$PKG_NAME" >/dev/null 2>&1; then
    gh repo create "$HOMEPAGE_OWNER/$PKG_NAME" --public --source=. --remote=origin --push
else
    echo "  repo $HOMEPAGE_OWNER/$PKG_NAME exists, skipping create"
    if ! git remote get-url origin >/dev/null 2>&1; then
        git remote add origin "https://github.com/$HOMEPAGE_OWNER/$PKG_NAME.git"
    fi
fi

echo "==> 2/4 push main + tag"
git push origin main
git push origin "$TAG"

echo "==> 3/4 create GitHub release (notes auto-extracted from CHANGELOG)"
if gh release view "$TAG" >/dev/null 2>&1; then
    echo "  release $TAG already exists, skipping"
else
    NOTES=$(mktemp)
    awk -v v="${TAG#v}" '
        $0 ~ "^## \\[" v "\\]" {flag=1; next}
        flag && /^## \[/        {exit}
        flag                    {print}
    ' CHANGELOG.md > "$NOTES"
    [ -s "$NOTES" ] || { echo "ERROR: empty release notes for $TAG"; rm -f "$NOTES"; exit 1; }
    gh release create "$TAG" --notes-file "$NOTES" --verify-tag
    rm -f "$NOTES"
fi

echo "==> 4/4 PyPI upload (idempotent via --skip-existing)"
twine upload --skip-existing dist/*

echo
echo "==> Done."
echo "  https://github.com/$HOMEPAGE_OWNER/$PKG_NAME"
echo "  https://pypi.org/project/$PKG_NAME/"
