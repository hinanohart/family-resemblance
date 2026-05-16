#!/usr/bin/env bash
# publish.sh — family-resemblance v0.1.0 release script (Phase 7).
#
# This is the only manual step in the release pipeline. Build artefacts in
# dist/, the v0.1.0 git tag, and 72 green tests are produced automatically
# by Phase 1-6. This script wires them up to GitHub + PyPI.
#
# Prerequisites:
#   * `gh` is logged in as the owner that pyproject.toml's Homepage names
#     (run: gh auth login   — or: gh auth switch -u <owner>).
#   * `~/.pypirc` is configured, or TWINE_USERNAME / TWINE_PASSWORD env
#     vars are set. Tokens are never read by this script directly.
#   * The repo is clean and v0.1.0 already exists locally.
#
# The script is idempotent — rerunning after a partial failure is safe.
# It never executes `set -x` and never echoes credentials.

set -euo pipefail

cd "$(dirname "$0")"

PKG_NAME="family-resemblance"
TAG="v0.1.0"

# Extract the GitHub owner from pyproject.toml's Homepage URL.
HOMEPAGE_OWNER=$(
    awk -F'/' '/Homepage = "https:\/\/github\.com\//{print $4; exit}' pyproject.toml
)

echo "==> Pre-flight"

git diff --quiet --exit-code \
    || { echo "ERROR: working tree dirty — commit or stash first"; exit 1; }
git diff --staged --quiet --exit-code \
    || { echo "ERROR: staged changes present"; exit 1; }
git rev-parse "$TAG" >/dev/null 2>&1 \
    || { echo "ERROR: tag $TAG not found — recreate before publishing"; exit 1; }
[ -d dist ] && ls dist/*.whl >/dev/null 2>&1 \
    || { echo "ERROR: dist/ missing wheel — run: python -m build"; exit 1; }
twine check dist/* >/dev/null \
    || { echo "ERROR: twine check failed"; exit 1; }

PKG_VER=$(awk -F'"' '/^version = "/{print $2; exit}' pyproject.toml)
[ -n "$PKG_VER" ] \
    || { echo "ERROR: could not parse version from pyproject.toml"; exit 1; }
[ "$TAG" = "v$PKG_VER" ] \
    || { echo "ERROR: TAG=$TAG does not match pyproject version v$PKG_VER"; exit 1; }
ls "dist/${PKG_NAME//-/_}-${PKG_VER}.tar.gz" \
   "dist/${PKG_NAME//-/_}-${PKG_VER}-py3-none-any.whl" >/dev/null 2>&1 \
    || { echo "ERROR: dist/ has no artefacts for version $PKG_VER"; exit 1; }

if [ -x .venv/bin/pytest ]; then
    .venv/bin/pytest -q >/dev/null \
        || { echo "ERROR: pytest not green (.venv)"; exit 1; }
elif command -v pytest >/dev/null 2>&1; then
    pytest -q >/dev/null \
        || { echo "ERROR: pytest not green (system)"; exit 1; }
else
    echo "ERROR: neither .venv/bin/pytest nor system pytest available"; exit 1
fi

CURRENT_GH_USER=$(gh api user --jq .login 2>/dev/null || echo "")
if [ -z "$CURRENT_GH_USER" ]; then
    echo "ERROR: gh is not authenticated. Run: gh auth login"; exit 1
fi
if [ -z "$HOMEPAGE_OWNER" ]; then
    echo "ERROR: could not parse Homepage owner from pyproject.toml"; exit 1
fi
if [ "$CURRENT_GH_USER" != "$HOMEPAGE_OWNER" ]; then
    cat <<EOF
ERROR: gh active user mismatch.
  pyproject.toml Homepage owner: $HOMEPAGE_OWNER
  gh active user:                $CURRENT_GH_USER

Pick one:
  (a) Switch gh:   gh auth switch -u $HOMEPAGE_OWNER
  (b) Edit pyproject.toml Homepage/Issues/Documentation to point at
      $CURRENT_GH_USER, commit, then rerun: python -m build && ./publish.sh
EOF
    exit 1
fi

echo "==> Pre-flight PASS (owner=$HOMEPAGE_OWNER, tag=$TAG)"

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

echo "==> 3/4 create GitHub release"
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
