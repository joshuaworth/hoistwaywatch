#!/usr/bin/env bash
set -euo pipefail

echo "CI: repo hygiene checks"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Basic git integrity checks (no dependencies)
echo "CI: git diff whitespace check"
git diff --check --cached || true
git diff --check || true

# Basic expectations
test -f README.md || fail "README.md missing"
test -f LICENSE || fail "LICENSE missing"

# Ensure docs exist (scaffold contract)
test -d docs || fail "docs/ missing"
test -f docs/safety.md || fail "docs/safety.md missing"
test -f docs/privacy.md || fail "docs/privacy.md missing"

echo "CI: ensure text files end with newline"
while IFS= read -r -d '' f; do
  # Skip known binary extensions
  case "$f" in
    *.png|*.jpg|*.jpeg|*.gif|*.webp|*.mp4|*.mov|*.avi|*.zip|*.gz|*.tgz|*.7z) continue ;;
  esac
  # If file is empty, allow it (but we avoid empty files in scaffold anyway)
  if test ! -s "$f"; then
    continue
  fi
  # Check last byte is newline (10). Avoid command-substitution stripping newlines.
  last_byte="$(tail -c 1 "$f" | od -An -t u1 | tr -d ' \n' || true)"
  if test "$last_byte" != "10"; then
    fail "missing final newline: $f"
  fi
done < <(git ls-files -z)

# If Node exists, run common checks (optional)
if test -f package.json; then
  if command -v npm >/dev/null 2>&1; then
    echo "CI: package.json detected; running npm checks"
    npm ci
    npm test --if-present
  else
    fail "package.json present but npm not available"
  fi
fi

# If Python tooling exists, run common checks (optional)
if test -f pyproject.toml || test -f requirements.txt; then
  if command -v python3 >/dev/null 2>&1; then
    echo "CI: Python config detected; running lint/tests"
    python3 -m pip install -U pip
    python3 -m pip install -e ".[dev]"
    python3 -m ruff check .
    python3 -m pytest
  else
    fail "Python config present but python3 not available"
  fi
fi

echo "CI: OK"

