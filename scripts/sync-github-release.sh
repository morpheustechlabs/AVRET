#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
SOURCE_DMG="$DIST_ROOT/dist1.1.6_b26081203/AVRET-1.1.6-b26081203.dmg"

VERSION="1.1.6"
BUILD="26081203"
TAG="v$VERSION"
TITLE="AVRET $VERSION — macOS Universal"
GITHUB_REPO="morpheustechlabs/AVRET"
EXPECTED_SHA="711660764310b8c3bc530fbe7ac556005ca5d14cd11e48ee56fa58745bbb95fc"
RELEASE_DIR="$REPO_ROOT/release"
NOTES_FILE="$RELEASE_DIR/RELEASE-NOTES-v$VERSION.md"
STAGED_DMG="$RELEASE_DIR/AVRET-1.1.6-b26081203.dmg"
SHA_FILE="$RELEASE_DIR/AVRET-1.1.6-b26081203.dmg.sha256"

if [[ ! -f "$SOURCE_DMG" ]]; then
  echo "ERROR: Production DMG not found:"
  echo "  $SOURCE_DMG"
  exit 1
fi

ACTUAL_SHA="$(shasum -a 256 "$SOURCE_DMG" | awk '{print $1}')"
if [[ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]]; then
  echo "ERROR: SHA-256 mismatch"
  echo "Expected: $EXPECTED_SHA"
  echo "Actual:   $ACTUAL_SHA"
  exit 2
fi

echo "SHA-256 verified."

if command -v xcrun >/dev/null 2>&1; then
  echo "Checking notarization ticket..."
  xcrun stapler validate "$SOURCE_DMG"
fi

mkdir -p "$RELEASE_DIR"
rm -f "$STAGED_DMG"
ln -s "$SOURCE_DMG" "$STAGED_DMG"
printf '%s  %s\n' "$ACTUAL_SHA" "AVRET-1.1.6-b26081203.dmg" > "$SHA_FILE"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI not installed."
  echo "Install with: brew install gh"
  echo "Then run: gh auth login"
  exit 3
fi

cd "$REPO_ROOT"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Initializing Git repository..."
  git init -b main
fi

if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "https://github.com/morpheustechlabs/AVRET.git"
else
  git remote add origin "https://github.com/morpheustechlabs/AVRET.git"
fi

git add README.md SECURITY.md NOTICE.md .gitignore assets/welcomeAvret.png "release/RELEASE-NOTES-v$VERSION.md" scripts/sync-github-release.sh

if ! git diff --cached --quiet; then
  git commit -m "AVRET $VERSION public distribution"
fi

git branch -M main
git push -u origin main

if gh release view "$TAG" --repo "$GITHUB_REPO" >/dev/null 2>&1; then
  gh release upload "$TAG" "$STAGED_DMG#AVRET-1.1.6-b26081203.dmg" "$SHA_FILE" --clobber --repo "$GITHUB_REPO"
  gh release edit "$TAG" --title "$TITLE" --notes-file "$NOTES_FILE" --repo "$GITHUB_REPO"
else
  gh release create "$TAG"     "$STAGED_DMG#AVRET-1.1.6-b26081203.dmg"     "$SHA_FILE"     --title "$TITLE"     --notes-file "$NOTES_FILE"     --latest     --repo "$GITHUB_REPO"
fi

echo
echo "DONE."
echo "Repository: https://github.com/morpheustechlabs/AVRET"
echo "Release: $TAG"
