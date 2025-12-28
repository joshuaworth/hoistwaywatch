#!/usr/bin/env bash
set -euo pipefail

echo "CI: repo hygiene checks"

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Basic expectations
test -f README.md || fail "README.md missing"
test -f LICENSE || fail "LICENSE missing"

# Ensure docs exist (scaffold contract)
test -d docs || fail "docs/ missing"
test -f docs/safety.md || fail "docs/safety.md missing"

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
    echo "CI: Python config detected; running basic import/lint hooks if configured"
    # Keep this intentionally minimal until a runtime is chosen.
    python3 -V
  else
    fail "Python config present but python3 not available"
  fi
fi

echo "CI: OK"

