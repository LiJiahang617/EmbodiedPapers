#!/usr/bin/env bash
# One-command sync for a fresh clone or a second machine.
#
# The Git sync policy keeps only text in the repo: paper notes, bilingual reading
# drafts, the paper map, and setting/. PDFs (papers/pdfs/) and figures
# (papers/images/) stay local, so a fresh clone renders every image embed as a
# broken link until they are re-fetched. This script does the whole round trip.
#
#   pull  ->  rehydrate PDFs  ->  rehydrate images  ->  validate map + sync policy
#
# Usage
#   setting/scripts/sync.sh              # pull, then fetch whatever is missing
#   setting/scripts/sync.sh --check      # verify only: no pull, no downloads, exit 1 if incomplete
#   setting/scripts/sync.sh --no-pull    # fetch missing assets without touching git
#   setting/scripts/sync.sh --force      # re-fetch every PDF and image, even if present
#
# PYTHON=/path/to/python setting/scripts/sync.sh   # pin an interpreter for this run
#
# Exit code is 0 only when every step succeeded, so it works as a pre-push gate.

set -uo pipefail

DO_PULL=1
CHECK_ONLY=0
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --check)   CHECK_ONLY=1; DO_PULL=0 ;;
    --no-pull) DO_PULL=0 ;;
    --force)   FORCE=1 ;;
    -h|--help) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "sync.sh: unknown option '$arg' (try --help)" >&2; exit 64 ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "sync.sh: not inside a git repository" >&2
  exit 1
}
cd "$ROOT" || exit 1

# Interpreter: never hardcoded. Honour $PYTHON, else the first one that has the deps.
pick_python() {
  local candidate
  for candidate in "${PYTHON:-}" python3 python; do
    [ -n "$candidate" ] || continue
    command -v "$candidate" >/dev/null 2>&1 || continue
    if "$candidate" -c 'import fitz, requests' >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

PY="$(pick_python)" || {
  echo "sync.sh: no Python with PyMuPDF + requests found." >&2
  echo "         pip install -r setting/scripts/requirements.txt" >&2
  echo "         (without PyMuPDF the extraction scripts produce nothing and do not error)" >&2
  exit 1
}
echo "python: $PY ($("$PY" --version 2>&1))"
echo

FAILED=()

run_step() {
  local label="$1"; shift
  echo "── $label ─────────────────────────────────────────"
  if "$@"; then
    echo "   ok"
  else
    local code=$?
    echo "   FAILED (exit $code)"
    FAILED+=("$label")
  fi
  echo
}

if [ "$DO_PULL" -eq 1 ]; then
  run_step "git pull --ff-only" git pull --ff-only
fi

pdf_args=()
img_args=()
if [ "$CHECK_ONLY" -eq 1 ]; then
  pdf_args+=(--check)
  img_args+=(--check)
elif [ "$FORCE" -eq 1 ]; then
  pdf_args+=(--force)
  img_args+=(--force)
fi

run_step "rehydrate PDFs"   "$PY" setting/scripts/rehydrate_pdfs.py   "${pdf_args[@]}"
run_step "rehydrate images" "$PY" setting/scripts/rehydrate_images.py "${img_args[@]}"
run_step "paper map"        "$PY" setting/scripts/check_paper_map.py
run_step "git sync policy"  "$PY" setting/scripts/check_git_sync_policy.py

if [ "${#FAILED[@]}" -eq 0 ]; then
  echo "sync.sh: all steps passed."
  exit 0
fi

echo "sync.sh: ${#FAILED[@]} step(s) need attention: ${FAILED[*]}"
echo
echo "Common causes:"
echo "  - a paper note with no 'arxiv:' field cannot be rehydrated; copy its PDF/images by hand"
echo "  - arXiv throttling; rerun, or raise the gap with --delay (rehydrate_images.py)"
echo "  - hand-made figures that were never in the arXiv source package"
exit 1
