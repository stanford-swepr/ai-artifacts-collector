#!/usr/bin/env bash
# Monthly snapshot collection for repos_msrc.txt.
#
# Runs the existing batch pipeline once per snapshot date. For each snapshot:
#   1. Generate a temp config with temporal.start_date / end_date set to the
#      backward-looking one-month window [prev_month_first, snapshot_date).
#   2. Invoke scripts/artifacts_collection.py --repos-file --config <temp>.
#      The pipeline writes flat outputs to output/msrc/{repo}/{repo}_*.csv etc.
#   3. Move each repo's flat-level outputs into output/msrc/{repo}/{snapshot}/.
#   4. Touch a .done_{snapshot} marker so interrupted reruns can resume.
#
# No Python code changes. Base config.yaml is not modified on disk.
#
# Usage:
#     ./collect_monthly.sh                                  # full 23-month run
#     ./collect_monthly.sh 2024-01-01 2024-02-01            # run only these dates
#     TOKEN=ghp_xxx ./collect_monthly.sh                    # GitHub token for private repos
#     REPOS_FILE=/path/to/other.txt ./collect_monthly.sh    # override repos file
#     CONFIG_BASE=/path/to/other.yaml ./collect_monthly.sh  # override base config

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make the project venv's `python` available on PATH without sourcing
# `.venv/bin/activate`. That script hardcodes VIRTUAL_ENV to the path the
# venv had at creation time, and breaks if the project was later moved.
# The venv's python binary itself self-discovers its prefix just fine, so
# simply prepending the real bin dir to PATH is enough.
if [[ -x "${SCRIPT_DIR}/.venv/bin/python" ]]; then
  export VIRTUAL_ENV="${SCRIPT_DIR}/.venv"
  export PATH="${VIRTUAL_ENV}/bin:${PATH}"
fi

REPOS_FILE="${REPOS_FILE:-${SCRIPT_DIR}/repos_msrc.txt}"
CONFIG_BASE="${CONFIG_BASE:-${SCRIPT_DIR}/config.yaml}"
# OUT_PATH_SLUG controls the subdirectory under output/ and ../analyzed_repos/.
# Default "msrc" preserves the original behaviour; per-connection runs can set
# e.g. OUT_PATH_SLUG=magic-caterpillar to keep outputs and clones segregated.
OUT_PATH_SLUG="${OUT_PATH_SLUG:-msrc}"
# Per-slug temp config so concurrent sweeps (e.g. partitioned by org range)
# don't overwrite each other's snapshot window between phases.
CONFIG_SNAP="${SCRIPT_DIR}/.config_monthly_snap.${OUT_PATH_SLUG}.yaml"
OUTPUT_DIR="${SCRIPT_DIR}/output/${OUT_PATH_SLUG}"
CLONE_DIR="${SCRIPT_DIR}/../analyzed_repos/${OUT_PATH_SLUG}"
LOG_DIR="${OUTPUT_DIR}/logs"
TOKEN_ARG=()
if [[ -n "${TOKEN:-}" ]]; then
  TOKEN_ARG=( --token "${TOKEN}" )
fi
# DELETE_CLONE=1 tells the pipeline to rm each repo's clone dir after
# processing it, capping disk usage during large per-connection sweeps.
DELETE_CLONE_ARG=()
if [[ "${DELETE_CLONE:-0}" == "1" ]]; then
  DELETE_CLONE_ARG=( --delete-clone )
fi

mkdir -p "${LOG_DIR}" "${OUTPUT_DIR}"

if [[ ! -f "${REPOS_FILE}" ]]; then
  echo "Error: repos file not found: ${REPOS_FILE}" >&2
  exit 1
fi
if [[ ! -f "${CONFIG_BASE}" ]]; then
  echo "Error: base config not found: ${CONFIG_BASE}" >&2
  exit 1
fi

if (( $# > 0 )); then
  # Positional args override the default 23-date list (e.g. for test runs).
  SNAPSHOTS=( "$@" )
else
  # Snapshot windows are half-open [prev_month_first, snap). For the study
  # range "Jan 2024 through Nov 2025" to cover commits IN both endpoint
  # months, the list must include 2025-12-01 (which captures Nov 2025 commits).
  SNAPSHOTS=(
    "2024-01-01" "2024-02-01" "2024-03-01" "2024-04-01" "2024-05-01" "2024-06-01"
    "2024-07-01" "2024-08-01" "2024-09-01" "2024-10-01" "2024-11-01" "2024-12-01"
    "2025-01-01" "2025-02-01" "2025-03-01" "2025-04-01" "2025-05-01" "2025-06-01"
    "2025-07-01" "2025-08-01" "2025-09-01" "2025-10-01" "2025-11-01" "2025-12-01"
  )
fi

# prev_month_first "2024-03-01" -> "2024-02-01"
prev_month_first() {
  SNAP_DATE="$1" python3 - <<'PY'
import os
from datetime import date, timedelta
d = date.fromisoformat(os.environ["SNAP_DATE"])
first_of_prev = (d.replace(day=1) - timedelta(days=1)).replace(day=1)
print(first_of_prev.isoformat())
PY
}

# Generate .config_monthly_snap.yaml by cloning the base config and overriding:
#   temporal.start_date, temporal.end_date
#   paths.output_dir   = "output/<OUT_PATH_SLUG>"        (replaces any {organisation})
#   paths.clone_dir    = "../analyzed_repos/<OUT_PATH_SLUG>"
write_snapshot_config() {
  # $1 = prev_month_first (ISO date), $2 = snapshot_date (ISO date)
  CONFIG_BASE="${CONFIG_BASE}" START_DATE="$1" END_DATE="$2" \
  OUT_PATH="output/${OUT_PATH_SLUG}" CLONE_PATH="../analyzed_repos/${OUT_PATH_SLUG}" \
  python3 - <<'PY' > "${CONFIG_SNAP}"
import os, sys, yaml
with open(os.environ["CONFIG_BASE"]) as f:
    cfg = yaml.safe_load(f) or {}
cfg.setdefault("temporal", {})
cfg["temporal"]["start_date"] = os.environ["START_DATE"]
cfg["temporal"]["end_date"]   = os.environ["END_DATE"]
cfg.setdefault("paths", {})
cfg["paths"]["output_dir"] = os.environ["OUT_PATH"]
cfg["paths"]["clone_dir"]  = os.environ["CLONE_PATH"]
yaml.safe_dump(cfg, sys.stdout, sort_keys=False)
PY
}

run_start=$(date '+%s')
completed=0
skipped=0

for SNAP in "${SNAPSHOTS[@]}"; do
  MARKER="${OUTPUT_DIR}/.done_${SNAP}"
  if [[ -f "${MARKER}" ]]; then
    echo "[skip] ${SNAP}: marker present (.done_${SNAP})"
    skipped=$(( skipped + 1 ))
    continue
  fi

  # First snapshot gets a cumulative window back to 2020-01-01 to capture
  # the full historical baseline. All subsequent snapshots use a one-month slice.
  if [[ "${SNAP}" == "${SNAPSHOTS[0]}" ]]; then
    PREV="2020-01-01"
  else
    PREV="$(prev_month_first "${SNAP}")"
  fi
  echo ""
  echo "================================================================"
  echo " Snapshot: ${SNAP}   temporal window: [${PREV}, ${SNAP})"
  echo " Started:  $(date '+%Y-%m-%d %H:%M:%S')"
  echo "================================================================"

  write_snapshot_config "${PREV}" "${SNAP}"

  # Restore any previously-reset clones to their origin branch tip so the
  # pipeline's pull_latest sees "Already up to date" instead of triggering
  # a slow fast-forward checkout that can exceed the idle-timeout watcher.
  # This is a no-op before the first snapshot (no clones yet).
  if [[ -d "${CLONE_DIR}" ]]; then
    shopt -s nullglob
    for _repo in "${CLONE_DIR}"/*/; do
      _branch="$(cd "${_repo}" && git rev-parse --abbrev-ref HEAD 2>/dev/null)" || continue
      (cd "${_repo}" && git reset --hard "origin/${_branch}" --quiet 2>/dev/null) || true
    done
    shopt -u nullglob
  fi

  # Run the existing batch pipeline for this snapshot.
  # ${TOKEN_ARG[@]+"${TOKEN_ARG[@]}"} is the bash-3.2-safe idiom for
  # "expand the array if it has any elements, otherwise nothing" under set -u.
  python "${SCRIPT_DIR}/scripts/artifacts_collection.py" \
      --repos-file "${REPOS_FILE}" \
      --config "${CONFIG_SNAP}" \
      ${TOKEN_ARG[@]+"${TOKEN_ARG[@]}"} \
      ${DELETE_CLONE_ARG[@]+"${DELETE_CLONE_ARG[@]}"} \
      2>&1 | tee "${LOG_DIR}/collect_${SNAP}.log"

  # Move each repo's freshly-written flat-level outputs into the snapshot subdir.
  # Skip the bundled Artifacts/ dir. Skip any repo dir that has no fresh flat
  # output (e.g. a repo whose first commit is after ${SNAP} — the pipeline
  # raised ValueError and wrote nothing for that repo on this run).
  shopt -s nullglob
  for repo_dir in "${OUTPUT_DIR}"/*/; do
    repo_name="$(basename "${repo_dir}")"
    if [[ "${repo_name}" == "Artifacts" ]]; then
      continue
    fi
    files=( "${repo_dir}"*.csv "${repo_dir}"*.pkl "${repo_dir}"*.json )
    if (( ${#files[@]} == 0 )); then
      continue
    fi
    mkdir -p "${repo_dir}${SNAP}"
    mv "${files[@]}" "${repo_dir}${SNAP}/"
  done
  shopt -u nullglob

  # Extract failed repos from the "Failed repositories:" block at the end
  # of the pipeline log. Format in log:  "    URL: error_reason"
  # Produces two files:
  #   failed_YYYY-MM-01.tsv  — URL<tab>error  (human-readable report)
  #   failed_YYYY-MM-01.urls — one URL per line (pass as REPOS_FILE to retry)
  #
  # Retry example:
  #   rm output/msrc/.done_2024-03-01
  #   REPOS_FILE=logs_monthly/failed_2024-03-01.urls ./collect_monthly.sh 2024-03-01
  FAIL_TSV="${LOG_DIR}/failed_${SNAP}.tsv"
  sed -n '/Failed repositories:/,/Finished at:/p' "${LOG_DIR}/collect_${SNAP}.log" \
    | grep '^\s\+http' \
    | sed -E 's/^[[:space:]]+(https?:[^:]+):[[:space:]]+(.*)/\1\t\2/' \
    > "${FAIL_TSV}" 2>/dev/null || true

  n_failed="$(wc -l < "${FAIL_TSV}" | tr -d ' ')"
  if (( n_failed > 0 )); then
    echo "[warn] ${SNAP}: ${n_failed} repos failed — see ${FAIL_TSV}"
    echo "       Retry: rm ${MARKER} && REPOS_FILE=<(cut -f1 ${FAIL_TSV}) ./collect_monthly.sh ${SNAP}"
  fi
  [[ -s "${FAIL_TSV}" ]] || rm -f "${FAIL_TSV}"

  touch "${MARKER}"
  completed=$(( completed + 1 ))
  echo "[done] ${SNAP}: outputs moved into per-repo ${SNAP}/"
done

rm -f "${CONFIG_SNAP}"

run_elapsed=$(( $(date '+%s') - run_start ))
hours=$(( run_elapsed / 3600 ))
minutes=$(( (run_elapsed % 3600) / 60 ))
seconds=$(( run_elapsed % 60 ))

echo ""
echo "================================================================"
echo " Monthly snapshot run summary"
echo "================================================================"
echo "   Snapshots total:     ${#SNAPSHOTS[@]}"
echo "   Newly completed:     ${completed}"
echo "   Skipped (markers):   ${skipped}"
echo "   Total elapsed:       ${hours}h ${minutes}m ${seconds}s"
echo "   Finished:            $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"
