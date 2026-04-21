#!/usr/bin/env bash
# Monthly snapshot collection for a repos-file.
#
# Thin wrapper around scripts/artifacts_collection.py: generates a snapshots
# TSV (one "start<TAB>end<TAB>label" row per window) and hands it to Python
# via --snapshots-file. The pipeline loads the embedding model ONCE and
# iterates the windows internally, writing outputs to
# ``output/<slug>/<repo>/<label>/`` and a ``output/<slug>/.done_<label>``
# marker per completed snapshot. Interrupted runs resume by skipping
# snapshots whose marker is already present.
#
# Usage:
#     ./collect_monthly.sh                                  # full 23-month run
#     ./collect_monthly.sh 2024-01-01 2024-02-01            # restrict to these snap dates
#     TOKEN=ghp_xxx ./collect_monthly.sh                    # GitHub token for private repos
#     DELETE_CLONE=1 ./collect_monthly.sh                   # rm each clone after processing
#     REPOS_FILE=/path/to/other.txt ./collect_monthly.sh    # override repos file
#     CONFIG_BASE=/path/to/other.yaml ./collect_monthly.sh  # override base config
#     OUT_PATH_SLUG=my-org ./collect_monthly.sh             # segregated output/clone paths

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
# Per-slug temp config + snapshots TSV so concurrent sweeps (e.g. partitioned
# by org range) don't stomp each other.
CONFIG_SNAP="${SCRIPT_DIR}/.config_monthly_snap.${OUT_PATH_SLUG}.yaml"
SNAPS_TSV="${SCRIPT_DIR}/.snapshots.${OUT_PATH_SLUG}.tsv"
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

# PARALLEL_REPOS=N runs N repos concurrently inside a snapshot. Default 1
# (serial). Recommended 4-6 on a 12-core machine; git I/O and embedding both
# release the GIL, so threads give real parallelism. Higher values risk
# saturating your network or git-provider rate limits.
PARALLEL_REPOS="${PARALLEL_REPOS:-1}"

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

# Generate the per-slug config once: clone the base config, override paths so
# outputs and clones land under the slug-scoped directories. Temporal dates
# don't matter here — they're supplied per-row in the snapshots TSV.
OUT_PATH="output/${OUT_PATH_SLUG}" CLONE_PATH="../analyzed_repos/${OUT_PATH_SLUG}" \
CONFIG_BASE="${CONFIG_BASE}" python3 - <<'PY' > "${CONFIG_SNAP}"
import os, sys, yaml
with open(os.environ["CONFIG_BASE"]) as f:
    cfg = yaml.safe_load(f) or {}
cfg.setdefault("paths", {})
cfg["paths"]["output_dir"] = os.environ["OUT_PATH"]
cfg["paths"]["clone_dir"]  = os.environ["CLONE_PATH"]
yaml.safe_dump(cfg, sys.stdout, sort_keys=False)
PY

# Build the snapshots TSV. Row format: start_date<TAB>end_date<TAB>label
# The first snapshot gets a cumulative window back to 2020-01-01 to capture
# the full historical baseline; subsequent rows are one-month slices.
: > "${SNAPS_TSV}"
FIRST_SNAP="${SNAPS_TSV}.first"
printf '%s\n' "${SNAPS_TSV}" > /dev/null  # keep shellcheck quiet
python3 - "${SNAPS_TSV}" "${SNAPSHOTS[@]}" <<'PY'
import sys
from datetime import date, timedelta

out_path = sys.argv[1]
snaps = sys.argv[2:]
rows = []
for i, s in enumerate(snaps):
    end = date.fromisoformat(s)
    if i == 0:
        start = date(2020, 1, 1)
    else:
        start = (end.replace(day=1) - timedelta(days=1)).replace(day=1)
    rows.append(f"{start.isoformat()}\t{end.isoformat()}\t{end.isoformat()}")
with open(out_path, "w") as f:
    f.write("\n".join(rows) + "\n")
PY

# Bash 3.2 (macOS default) can't do "${array[-1]}", so compute the last index.
LAST_IDX=$(( ${#SNAPSHOTS[@]} - 1 ))
echo "================================================================"
echo " Monthly snapshot run (slug=${OUT_PATH_SLUG})"
echo "   snapshots:   ${#SNAPSHOTS[@]}  (${SNAPSHOTS[0]} … ${SNAPSHOTS[${LAST_IDX}]})"
echo "   repos-file:  ${REPOS_FILE}"
echo "   output_dir:  ${OUTPUT_DIR}"
echo "   clone_dir:   ${CLONE_DIR}"
echo "   started_at:  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"

run_start=$(date '+%s')

# One Python process handles all snapshots — model loaded once, clones reused,
# .done_<label> markers written after each snapshot completes, and outputs go
# straight to output/<slug>/<repo>/<label>/ (no mv step).
python "${SCRIPT_DIR}/scripts/artifacts_collection.py" \
    --repos-file "${REPOS_FILE}" \
    --config "${CONFIG_SNAP}" \
    --snapshots-file "${SNAPS_TSV}" \
    --parallel-repos "${PARALLEL_REPOS}" \
    ${TOKEN_ARG[@]+"${TOKEN_ARG[@]}"} \
    ${DELETE_CLONE_ARG[@]+"${DELETE_CLONE_ARG[@]}"} \
    2>&1 | tee "${LOG_DIR}/collect_$(date '+%Y%m%d_%H%M%S').log"

rc=${PIPESTATUS[0]}

rm -f "${CONFIG_SNAP}" "${SNAPS_TSV}"

run_elapsed=$(( $(date '+%s') - run_start ))
hours=$(( run_elapsed / 3600 ))
minutes=$(( (run_elapsed % 3600) / 60 ))
seconds=$(( run_elapsed % 60 ))

echo ""
echo "================================================================"
echo " Monthly snapshot run finished (slug=${OUT_PATH_SLUG})"
echo "   snapshots:   ${#SNAPSHOTS[@]}"
echo "   exit code:   ${rc}"
echo "   elapsed:     ${hours}h ${minutes}m ${seconds}s"
echo "   finished:    $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"

exit "${rc}"
