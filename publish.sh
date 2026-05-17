#!/usr/bin/env bash
# publish.sh — family-resemblance v0.1.0 ONE-script release.
#
# Usage:
#   ./publish.sh              # interactive: handles gh-auth mismatch in-script
#   ./publish.sh --check      # dry-run; pre-flight only, no push, no upload
#   ./publish.sh --yes        # non-interactive; auto-switch if possible, else fail
#
# What this script automates (everything except identity):
#   * pre-flight (clean tree / tag / dist match version / twine check / pytest)
#   * gh active-account alignment (auto-switch if intended owner is stored)
#   * interactive `gh auth login` launch when the owner is NOT stored locally
#   * `gh repo create` (idempotent) + push main + push tag
#   * GitHub release creation with notes auto-extracted from CHANGELOG
#   * `twine upload --skip-existing dist/*` (reads ~/.pypirc itself; no token
#     ever passes through this script)
#
# What remains manual (physical R11 boundary):
#   * If gh is not yet logged in as the pyproject Homepage owner, you will
#     complete ONE OAuth web flow (the script launches `gh auth login` for
#     you). After that, the script continues automatically.

set -euo pipefail
cd "$(dirname "$0")"

MODE="interactive"
case "${1:-}" in
    --check)  MODE="check" ;;
    --yes)    MODE="yes" ;;
    "")       ;;
    *)        echo "Usage: $0 [--check | --yes]"; exit 2 ;;
esac

PKG_NAME="family-resemblance"
PKG_UNDER="${PKG_NAME//-/_}"

HOMEPAGE_OWNER=$(
    awk -F'/' '/Homepage = "https:\/\/github\.com\//{print $4; exit}' pyproject.toml
)
PKG_VER=$(awk -F'"' '/^version = "/{print $2; exit}' pyproject.toml)
TAG="v$PKG_VER"

# ---------- 1/5 Pre-flight ----------
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
    || { echo "ERROR: dist/ has no artefacts for v$PKG_VER (run: python -m build)"; exit 1; }
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

# ---------- 2/5 gh auth alignment ----------
CURRENT_GH=$(gh api user --jq .login 2>/dev/null || echo "")
STORED=$(gh auth status 2>&1 \
    | grep -oE 'account [A-Za-z0-9_-]+' \
    | awk '{print $2}' | sort -u | tr '\n' ' ')

if [ -n "$CURRENT_GH" ] && [ "$CURRENT_GH" != "$HOMEPAGE_OWNER" ]; then
    if echo " $STORED " | grep -q " $HOMEPAGE_OWNER "; then
        echo "==> Switching gh active account: $CURRENT_GH → $HOMEPAGE_OWNER"
        gh auth switch -u "$HOMEPAGE_OWNER" >/dev/null
        CURRENT_GH=$(gh api user --jq .login 2>/dev/null || echo "")
    fi
fi

if [ -z "$CURRENT_GH" ] || [ "$CURRENT_GH" != "$HOMEPAGE_OWNER" ]; then
    cat <<EOF

──────────────────────────────────────────────────────────────────────
 gh identity is not aligned with pyproject.toml.
   pyproject Homepage owner: $HOMEPAGE_OWNER
   gh active account:        ${CURRENT_GH:-(none)}
   gh stored accounts:       ${STORED:-(none)}
──────────────────────────────────────────────────────────────────────
EOF
    if [ "$MODE" = "yes" ] || [ "$MODE" = "check" ] || [ ! -t 0 ]; then
        cat <<EOF
Non-interactive mode; cannot launch the OAuth web flow.
Choose ONE manually, then re-run ./publish.sh:

  (a) Log in once as $HOMEPAGE_OWNER (recommended; keeps attribution):
        gh auth login --hostname github.com --git-protocol https --web
        # log in as $HOMEPAGE_OWNER in the browser, then:
        ./publish.sh

  (b) Publish under ${CURRENT_GH:-<current>} instead (changes attribution):
        sed -i "s|github.com/$HOMEPAGE_OWNER|github.com/${CURRENT_GH:-NEW}|g" \\
            pyproject.toml CHANGELOG.md README.md
        git commit -am "chore: switch attribution"
        python -m build && git tag -f $TAG && ./publish.sh
EOF
        exit 1
    fi

    echo "Pick how to proceed:"
    echo "  1) Launch  gh auth login --web  now (log in as $HOMEPAGE_OWNER in the browser; recommended)"
    echo "  2) Switch attribution to ${CURRENT_GH:-<current>} (rewrites repo metadata, commits, retags)"
    echo "  3) Abort"
    read -r -p "Choice [1/2/3]: " choice
    case "$choice" in
        1)
            echo
            echo "==> Launching gh auth login."
            echo "    When the browser opens, log in as: $HOMEPAGE_OWNER"
            echo "    (gh auth login has no -u flag; the active account becomes whoever you log in as.)"
            echo
            gh auth login --hostname github.com --git-protocol https --web \
                || { echo "ERROR: gh auth login failed or was cancelled"; exit 1; }
            # Force the new login to be the active account (gh defaults to it, but be defensive).
            if gh auth status 2>&1 | grep -oE 'account [A-Za-z0-9_-]+' | awk '{print $2}' | grep -qx "$HOMEPAGE_OWNER"; then
                gh auth switch -u "$HOMEPAGE_OWNER" >/dev/null 2>&1 || true
            fi
            CURRENT_GH=$(gh api user --jq .login 2>/dev/null || echo "")
            if [ "$CURRENT_GH" != "$HOMEPAGE_OWNER" ]; then
                echo "ERROR: still not $HOMEPAGE_OWNER after login (active = ${CURRENT_GH:-none})."
                echo "       Did you log in as a different user? Rerun ./publish.sh after:"
                echo "         gh auth switch -u $HOMEPAGE_OWNER   # if $HOMEPAGE_OWNER is now stored"
                exit 1
            fi
            ;;
        2)
            [ -n "$CURRENT_GH" ] || { echo "ERROR: no active gh account to switch to"; exit 1; }
            echo "==> Rewriting attribution: $HOMEPAGE_OWNER → $CURRENT_GH"
            sed -i "s|github.com/$HOMEPAGE_OWNER|github.com/$CURRENT_GH|g" \
                pyproject.toml CHANGELOG.md README.md
            git commit -am "chore: switch attribution to $CURRENT_GH" >/dev/null
            python -m build >/dev/null
            git tag -f "$TAG" >/dev/null
            HOMEPAGE_OWNER="$CURRENT_GH"
            ;;
        *)
            echo "Aborted."; exit 1
            ;;
    esac
fi

echo "==> Pre-flight PASS (owner=$HOMEPAGE_OWNER, tag=$TAG, dist=v$PKG_VER)"

if [ "$MODE" = "check" ]; then
    echo "==> --check mode: stopping before push/upload."
    exit 0
fi

# ---------- 3/5 GitHub repo (idempotent) ----------
echo "==> 3/5 ensure GitHub repo exists"
if ! gh repo view "$HOMEPAGE_OWNER/$PKG_NAME" >/dev/null 2>&1; then
    gh repo create "$HOMEPAGE_OWNER/$PKG_NAME" --public --source=. --remote=origin --push
else
    echo "  repo $HOMEPAGE_OWNER/$PKG_NAME exists, skipping create"
    if ! git remote get-url origin >/dev/null 2>&1; then
        git remote add origin "https://github.com/$HOMEPAGE_OWNER/$PKG_NAME.git"
    fi
fi

# ---------- 4/5 push main + tag ----------
echo "==> 4/5 push main + tag"
git push origin main
git push origin "$TAG"

# ---------- 5/5 GitHub release + PyPI upload ----------
echo "==> 5/5 GitHub release + PyPI upload"
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

twine upload --skip-existing dist/*

echo
echo "==> Done."
echo "  https://github.com/$HOMEPAGE_OWNER/$PKG_NAME"
echo "  https://pypi.org/project/$PKG_NAME/"
