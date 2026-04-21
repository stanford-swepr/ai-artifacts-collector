"""Sequential collection sweep across orgs from prod_orgs_to_process.csv.

For each organisation (in the CSV's order), runs every one of its non-AI
connections through the full 23-snapshot `collect_monthly.sh` pipeline.
Connection metadata — slug, bundle stem, repo count, token — is read from
`orgs/index.csv` (produced by scripts/fetch_org_config.py).

Per connection:
  1. Set OUT_PATH_SLUG=<slug>, REPOS_FILE=orgs/<stem>.txt, TOKEN=<orgs/<stem>.token>
  2. Invoke ./collect_monthly.sh (no args → full 23-snapshot default).
  3. After the pipeline finishes, rm -rf ../analyzed_repos/<slug>/ to free disk.
     Clones are retained during the 23-snapshot run (git reset between snapshots
     is cheap, re-cloning 23× is not).

Connections with repo_count=0 are skipped. Any non-zero exit from collect_monthly.sh
is logged but does NOT stop the sweep — we continue to the next connection.

A summary is written to `output/_sweep/sweep.log`. Per-connection stderr (if any)
lands in `output/_sweep/<slug>.err`.

Usage:
    python scripts/run_sweep.py                        # first 10 orgs from CSV
    python scripts/run_sweep.py --orgs-limit 5         # first 5 orgs
    python scripts/run_sweep.py --orgs-limit 0         # all orgs
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORGS_CSV = ROOT / "prod_orgs_to_process.csv"
DEFAULT_INDEX_CSV = ROOT / "orgs" / "index.csv"
DEFAULT_SWEEP_DIR = ROOT / "output" / "_sweep"


def load_org_order(csv_path: Path) -> list[tuple[int, str]]:
    """Return [(id_organisation, name), ...] preserving the CSV's row order."""
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    out: list[tuple[int, str]] = []
    for r in rows:
        try:
            out.append((int(r["id_organisation"]), r["name"]))
        except (KeyError, ValueError):
            continue
    return out


def load_index_by_org(index_csv: Path) -> dict[int, list[dict]]:
    """Group connections from index.csv by id_organisation."""
    grouped: dict[int, list[dict]] = defaultdict(list)
    with index_csv.open() as f:
        for row in csv.DictReader(f):
            try:
                oid = int(row["id_organisation"])
            except (KeyError, ValueError):
                continue
            grouped[oid].append(row)
    return grouped


def run_connection(
    conn: dict, orgs_dir: Path, sweep_dir: Path, log
) -> tuple[str, int, float]:
    """Run collect_monthly.sh for one connection. Returns (status, rc, elapsed_sec)."""
    slug = conn["slug"]
    stem = conn["bundle_stem"]
    repos_file = orgs_dir / f"{stem}.txt"
    token_file = orgs_dir / f"{stem}.token"

    env = os.environ.copy()
    env["OUT_PATH_SLUG"] = slug
    env["REPOS_FILE"] = str(repos_file)
    if token_file.exists():
        token = token_file.read_text().strip()
        if token:
            env["TOKEN"] = token

    script = ROOT / "collect_monthly.sh"
    err_log = sweep_dir / f"{slug}.err"
    started = time.time()

    # Stream collect_monthly.sh's stdout straight to the sweep's stdout so
    # progress is visible in real time. Capture stderr separately so we can
    # persist it to <slug>.err for post-mortem without cluttering the sweep log.
    try:
        with err_log.open("wb") as errf:
            proc = subprocess.run(
                [str(script)],
                env=env,
                cwd=str(ROOT),
                stdout=None,        # inherit → appears in sweep's stdout
                stderr=errf,
                check=False,
            )
        rc = proc.returncode
    except Exception as e:
        elapsed = time.time() - started
        log(f"    EXCEPTION: {e}")
        return ("exception", -1, elapsed)

    elapsed = time.time() - started
    if rc == 0:
        err_log.unlink(missing_ok=True)
        return ("ok", 0, elapsed)
    return ("fail", rc, elapsed)


def cleanup_clones(slug: str, log) -> None:
    clone_dir = ROOT.parent / "analyzed_repos" / slug
    if clone_dir.exists():
        try:
            shutil.rmtree(clone_dir)
            log(f"    cleaned clones: {clone_dir}")
        except Exception as e:
            log(f"    cleanup WARN: {e}")


def format_duration(seconds: float) -> str:
    s = int(seconds)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}h{m:02d}m{s:02d}s"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--orgs-limit", type=int, default=10,
        help="Number of orgs to process from the CSV in order. 0 = all. Default: 10.",
    )
    parser.add_argument(
        "--start-from", type=int, default=0,
        help="Skip the first N orgs in the CSV before applying --orgs-limit. "
             "Use to partition the CSV across parallel sweeps.",
    )
    parser.add_argument(
        "--defer-org-id", type=int, action="append", default=[],
        help="Move this org id to the end of the queue (repeatable). Useful for "
             "parking very large orgs until after the smaller ones complete.",
    )
    parser.add_argument("--orgs-csv", default=str(DEFAULT_ORGS_CSV))
    parser.add_argument("--index-csv", default=str(DEFAULT_INDEX_CSV))
    parser.add_argument("--sweep-dir", default=str(DEFAULT_SWEEP_DIR))
    args = parser.parse_args()

    orgs_csv = Path(args.orgs_csv)
    index_csv = Path(args.index_csv)
    sweep_dir = Path(args.sweep_dir)
    orgs_dir = ROOT / "orgs"

    for p in (orgs_csv, index_csv):
        if not p.exists():
            print(f"Error: required file missing: {p}", file=sys.stderr)
            return 2

    sweep_dir.mkdir(parents=True, exist_ok=True)
    sweep_log_path = sweep_dir / "sweep.log"

    def log(msg: str) -> None:
        stamped = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
        print(stamped, flush=True)
        with sweep_log_path.open("a") as f:
            f.write(stamped + "\n")

    org_order = load_org_order(orgs_csv)
    grouped = load_index_by_org(index_csv)

    # Partition support: --start-from skips the leading N orgs before limit applies.
    if args.start_from > 0:
        org_order = org_order[args.start_from:]

    if args.orgs_limit > 0:
        org_order = org_order[: args.orgs_limit]

    # Apply --defer-org-id: pull these ids out in place and append at the end,
    # preserving their relative order. Deferred orgs that aren't in the slice
    # are silently ignored.
    if args.defer_org_id:
        deferred_ids = list(args.defer_org_id)
        kept = [(oid, name) for oid, name in org_order if oid not in deferred_ids]
        deferred = [(oid, name) for oid, name in org_order if oid in deferred_ids]
        # sort deferred by the user-specified order
        deferred.sort(key=lambda pair: deferred_ids.index(pair[0]))
        org_order = kept + deferred

    total_conns = sum(len(grouped.get(oid, [])) for oid, _ in org_order)
    total_repos = sum(
        int(c.get("repo_count", 0) or 0)
        for oid, _ in org_order
        for c in grouped.get(oid, [])
    )

    log("=" * 64)
    log(f"Sweep start: {len(org_order)} orgs, {total_conns} connections, "
        f"{total_repos} repos (full 23-snapshot run per connection)")
    log("=" * 64)

    sweep_start = time.time()
    ok = fail = skip_empty = missing_conn = 0

    for org_idx, (oid, org_name) in enumerate(org_order, 1):
        conns = grouped.get(oid, [])
        if not conns:
            log(f"\n[{org_idx}/{len(org_order)}] {org_name} (id={oid}) — NO active non-AI connections")
            missing_conn += 1
            continue

        log(f"\n[{org_idx}/{len(org_order)}] {org_name} (id={oid}) — {len(conns)} connection(s)")

        for conn_idx, conn in enumerate(conns, 1):
            slug = conn["slug"]
            repo_count = int(conn.get("repo_count", 0) or 0)
            prefix = f"  [{conn_idx}/{len(conns)}] {slug}"

            if repo_count == 0:
                log(f"{prefix}: SKIP (0 repos)")
                skip_empty += 1
                continue

            log(f"{prefix}: START ({repo_count} repos)")
            status, rc, elapsed = run_connection(conn, orgs_dir, sweep_dir, log)
            dur = format_duration(elapsed)

            if status == "ok":
                log(f"{prefix}: OK in {dur}")
                ok += 1
            else:
                log(f"{prefix}: FAIL rc={rc} in {dur} (stderr → {sweep_dir / (slug + '.err')})")
                fail += 1

            cleanup_clones(slug, log)

    total_elapsed = time.time() - sweep_start
    log("\n" + "=" * 64)
    log("Sweep finished")
    log(f"  orgs processed:          {len(org_order)}")
    log(f"  orgs with no connection: {missing_conn}")
    log(f"  connections OK:          {ok}")
    log(f"  connections FAIL:        {fail}")
    log(f"  connections skipped:     {skip_empty}  (repo_count=0)")
    log(f"  total elapsed:           {format_duration(total_elapsed)}")
    log("=" * 64)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
