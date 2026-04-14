#!/usr/bin/env bash
# Lightweight documentation sync check for coarse.
# Reports (but does not fix) gaps between source and docs. Run from /pre-pr.
#
# Checks:
#   1. Every .py in src/coarse/ is listed in CLAUDE.md's package-structure tree
#   2. CHANGELOG.md has an "## Unreleased" section
#   3. pyproject.toml version matches src/coarse/__init__.py
#   4. No model-ID literals added to the diff outside src/coarse/models.py
#
# Exit codes:
#   0 = in sync
#   2 = at least one check failed

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

FAIL=0

note() { printf "  %s\n" "$1"; }
fail() { printf "FAIL: %s\n" "$1" >&2; FAIL=1; }

echo "== doc-sync =="

# 1) Modules listed in the canonical package-structure docs.
#
# We accept EITHER ``CLAUDE.md`` OR ``CONTRIBUTING.md`` as the source of
# truth so the project-structure tree can live in whichever file makes
# sense for the current contributor-facing docs layout. The rule is:
# every ``src/coarse/*.py`` file must be mentioned by name in at least
# one of the two files. If a module is missing from both, the check
# fails and the file names are printed so the developer can add them.
#
# (Earlier versions of this script hardcoded CLAUDE.md as the only
# allowed home for the tree. The restructure that moved CLAUDE.md to
# a deploy-workflow brief left the tree in CONTRIBUTING.md — both
# conventions are fine, this just makes the check flexible to either.)
missing_modules=()
doc_sources=()
[ -f CLAUDE.md ] && doc_sources+=(CLAUDE.md)
[ -f CONTRIBUTING.md ] && doc_sources+=(CONTRIBUTING.md)
while IFS= read -r -d '' file; do
    name=$(basename "$file")
    case "$name" in
        __init__.py|__main__.py) continue ;;
    esac
    found=0
    for doc in "${doc_sources[@]}"; do
        if grep -qF "$name" "$doc"; then
            found=1
            break
        fi
    done
    if [ "$found" -eq 0 ]; then
        missing_modules+=("$file")
    fi
done < <(find src/coarse -name '*.py' -print0)

if [ "${#missing_modules[@]}" -eq 0 ]; then
    note "[OK] every src/coarse/*.py referenced in CLAUDE.md or CONTRIBUTING.md"
else
    fail "modules missing from package-structure docs (CLAUDE.md or CONTRIBUTING.md):"
    printf "       %s\n" "${missing_modules[@]}" >&2
fi

# 2) CHANGELOG has an Unreleased section
if grep -qE '^## \[?Unreleased\]?' CHANGELOG.md 2>/dev/null; then
    note "[OK] CHANGELOG.md has an Unreleased section"
else
    fail "CHANGELOG.md is missing a '## Unreleased' section"
fi

# 3) Version consistency
py_version=$(grep -E '^version *= *' pyproject.toml | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
init_version=$(grep -E '__version__ *= *' src/coarse/__init__.py | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
if [ -z "$py_version" ] || [ -z "$init_version" ]; then
    fail "could not parse version from pyproject.toml or src/coarse/__init__.py"
elif [ "$py_version" != "$init_version" ]; then
    fail "version mismatch: pyproject.toml=$py_version  __init__.py=$init_version"
else
    note "[OK] version $py_version consistent"
fi

# 4) No new model-ID literals in the diff outside src/coarse/models.py
base="${DOC_SYNC_BASE:-dev}"
if git rev-parse --verify "$base" >/dev/null 2>&1; then
    diff_files=()
    while IFS= read -r file; do
        [ -n "$file" ] || continue
        diff_files+=("$file")
    done <<EOF
$(git diff --name-only "${base}...HEAD" 2>/dev/null \
    | grep -E '^src/coarse/.*\.py$' \
    | grep -v '^src/coarse/models\.py$' || true)
EOF
    if [ "${#diff_files[@]}" -gt 0 ]; then
        offenders=$(git diff "${base}...HEAD" -- "${diff_files[@]}" \
            | grep -E '^\+' \
            | grep -v '^+++' \
            | grep -Ev '^\+ *#|^\+ *"""|^\+ *\x27\x27\x27' \
            | grep -Eo '"(openai|anthropic|google|gemini|perplexity|mistral|qwen|openrouter|deepseek)/[^"]+"' \
            | grep -v '/auto"$' \
            | sort -u || true)
        if [ -n "$offenders" ]; then
            fail "model-ID literal added to src/coarse/ outside models.py:"
            echo "$offenders" | sed 's/^/       /' >&2
        else
            note "[OK] no new model-ID literals in diff"
        fi
    else
        note "[OK] no src/coarse/ changes in diff"
    fi
else
    note "[WARN] base branch '$base' not found; skipping diff checks"
fi

# 5) Current architecture docs must match runtime shape
doc_hits=$(rg -n \
    -e '3-judge overview panel' \
    -e 'overview panel +3-judge' \
    -e 'crossref \+ critique.*primary path' \
    -e 'ships the per-stage model routing feature' \
    -e 'crossref agent.*Deduplicate, validate quotes, consistency' \
    -e 'critique agent.*Self-critique quality gate' \
    CLAUDE.md README.md CONTRIBUTING.md 2>/dev/null || true)
changelog_hits=""
if git rev-parse --verify "$base" >/dev/null 2>&1; then
    changelog_hits=$(git diff "${base}...HEAD" -- CHANGELOG.md 2>/dev/null \
        | grep -E '^\+' \
        | grep -v '^+++' \
        | rg -n \
            -e '3-judge overview panel' \
            -e 'overview panel +3-judge' \
            -e 'crossref \+ critique.*primary path' \
            -e 'ships the per-stage model routing feature' \
            -e 'crossref agent.*Deduplicate, validate quotes, consistency' \
            -e 'critique agent.*Self-critique quality gate' \
            || true)
fi
stale_hits=$(printf '%s\n%s\n' "$doc_hits" "$changelog_hits" | sed '/^$/d')
if [ -n "$stale_hits" ]; then
    fail "stale architecture wording found in canonical docs:"
    echo "$stale_hits" | sed 's/^/       /' >&2
else
    note "[OK] canonical docs match current runtime architecture"
fi

echo ""
if [ "$FAIL" -eq 0 ]; then
    echo "doc-sync: OK"
    exit 0
fi
echo "doc-sync: FAILED"
exit 2
