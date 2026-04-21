"""Fetch per-connection collection config from the optimus prod DB.

Iterates organisations listed in `prod_orgs_to_process.csv`. For each org,
finds every non-AI (github/gitlab/azure/bitbucket) git connection that is
`status='active'` and `is_deleted=0` — a single org may have multiple — and
emits one set of files per connection:

    orgs/<type>-<id_connection>.txt        # repo clone URLs, one per line
    orgs/<type>-<id_connection>.token      # provider token (chmod 600)
    orgs/<type>-<id_connection>.meta.json  # org + connection metadata (no token)

A summary row is appended to `orgs/index.csv` for every connection processed.
The flat layout matches the default pipeline output path convention described
in README.md — the pipeline will place outputs under `output/<organisation>/`
based on each repo's URL when these lists are passed to the collection CLI.

DB credentials are read from ~/.mysql-remote. Tokens are never printed to
stdout and are written with 0600 permissions.

Usage:
    python scripts/fetch_org_config.py                        # process all rows in the CSV
    python scripts/fetch_org_config.py --org-id 102086        # single org
    python scripts/fetch_org_config.py --orgs-csv other.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

NON_AI_TYPES = ("github", "gitlab", "azure", "bitbucket")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_db_creds(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def run_query(creds: dict, sql: str) -> list[dict]:
    """Run a SELECT via the mysql CLI and parse tab-separated output.

    Uses MYSQL_PWD env var so the password never appears in argv / ps output.
    The mysql CLI's --batch mode emits the literal string "NULL" for SQL NULL
    values; normalise those to empty strings so downstream callers can treat
    missing fields uniformly without the "NULL"/None/"" trap.
    """
    env = os.environ.copy()
    env["MYSQL_PWD"] = creds["password"]
    result = subprocess.run(
        [
            "mysql",
            "-h", creds["host"],
            "-P", str(creds["port"]),
            "-u", creds["user"],
            creds["database"],
            "--batch",
            "--raw",
            "-e", sql,
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.rstrip("\n").split("\n")
    if not lines or lines == [""]:
        return []
    header = lines[0].split("\t")
    out: list[dict] = []
    for line in lines[1:]:
        cells = line.split("\t")
        row = {h: ("" if v == "NULL" else v) for h, v in zip(header, cells)}
        out.append(row)
    return out


def fetch_connections(creds: dict, org_ids: list[int]) -> list[dict]:
    """All non-AI, active, non-deleted connections for the given org ids."""
    if not org_ids:
        return []
    id_list = ",".join(str(i) for i in org_ids)
    types = ",".join(repr(t) for t in NON_AI_TYPES)
    return run_query(
        creds,
        f"""SELECT id_connection, id_organisation, type, git_organisation,
                   git_username, git_token, custom_host, label, is_data_center
            FROM connection
            WHERE id_organisation IN ({id_list})
              AND type IN ({types})
              AND status = 'active'
              AND is_deleted = 0
            ORDER BY id_organisation, type, id_connection""",
    )


def fetch_repos_for_connections(creds: dict, conn_ids: list[int]) -> dict[int, list[dict]]:
    """Repos grouped by id_connection."""
    if not conn_ids:
        return {}
    id_list = ",".join(str(i) for i in conn_ids)
    rows = run_query(
        creds,
        f"""SELECT id_repo, id_connection, git_url, branch, repository_name, is_fork
            FROM repo
            WHERE id_connection IN ({id_list})
            ORDER BY id_connection, repository_name""",
    )
    grouped: dict[int, list[dict]] = {}
    for r in rows:
        grouped.setdefault(int(r["id_connection"]), []).append(r)
    return grouped


def build_clone_url(conn_type: str, git_url: str, custom_host: str) -> str:
    """Turn relative git_url ('Org/Repo') into a full https clone URL.

    Honours custom_host for self-hosted instances (GHE, GitLab self-managed,
    Bitbucket Data Center, Azure DevOps Server). Azure DevOps uses a different
    path structure (`/{org}/{project}/_git/{repo}`).
    """
    host = custom_host.strip() if custom_host else ""
    if conn_type == "github":
        host = host or "github.com"
        return f"https://{host}/{git_url}.git"
    if conn_type == "gitlab":
        host = host or "gitlab.com"
        return f"https://{host}/{git_url}.git"
    if conn_type == "bitbucket":
        host = host or "bitbucket.org"
        return f"https://{host}/{git_url}.git"
    if conn_type == "azure":
        host = host or "dev.azure.com"
        parts = git_url.split("/")
        if len(parts) >= 3:
            org, project = parts[0], parts[1]
            repo = "/".join(parts[2:])
            return f"https://{host}/{org}/{project}/_git/{repo}"
        return f"https://{host}/{git_url}"
    raise ValueError(f"Unsupported connection type: {conn_type!r}")


def load_orgs_csv(csv_path: Path) -> list[tuple[int, str]]:
    """Returns list of (id_organisation, name) tuples from the CSV."""
    if not csv_path.exists():
        print(f"Error: orgs CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(2)
    out: list[tuple[int, str]] = []
    with csv_path.open() as f:
        for row in csv.DictReader(f):
            try:
                out.append((int(row["id_organisation"]), row["name"]))
            except (KeyError, ValueError):
                continue
    return out


def write_connection_bundle(
    outdir: Path,
    conn: dict,
    org_name: str,
    repos: list[dict],
) -> dict:
    """Write .txt, .token, .meta.json for a single connection. Returns summary dict."""
    id_connection = int(conn["id_connection"])
    conn_type = conn["type"]
    stem = f"{conn_type}-{id_connection}"

    # Each line: "<url>\t<branch>". Branch comes from repo.branch in the DB;
    # if missing we skip the tab so the pipeline falls back to auto-detect.
    lines: list[str] = []
    urls: list[str] = []
    skipped: list[str] = []
    for r in repos:
        git_url = r.get("git_url") or ""
        if not git_url or git_url == "NULL":
            skipped.append(f"{r.get('repository_name', '?')} (empty git_url)")
            continue
        try:
            clone_url = build_clone_url(conn_type, git_url, conn.get("custom_host", "") or "")
        except ValueError as e:
            skipped.append(f"{r.get('repository_name', '?')} ({e})")
            continue
        urls.append(clone_url)
        branch = (r.get("branch") or "").strip()
        # Some DB rows store the full ref path ("refs/heads/main"); git
        # accepts both but the pipeline's checkout/rev-list use the short
        # form, so normalise here.
        if branch.startswith("refs/heads/"):
            branch = branch[len("refs/heads/"):]
        lines.append(f"{clone_url}\t{branch}" if branch else clone_url)

    token = conn.get("git_token") or ""

    (outdir / f"{stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""))

    token_path = outdir / f"{stem}.token"
    token_path.write_text(token)
    token_path.chmod(0o600)

    meta = {
        "id_organisation": int(conn["id_organisation"]),
        "organisation_name": org_name,
        "connection": {
            "id_connection": id_connection,
            "type": conn_type,
            "git_organisation": conn.get("git_organisation"),
            "git_username": conn.get("git_username"),
            "custom_host": conn.get("custom_host") or None,
            "is_data_center": conn.get("is_data_center"),
            "label": conn.get("label"),
        },
        "repo_count": len(urls),
        "skipped": skipped,
    }
    (outdir / f"{stem}.meta.json").write_text(json.dumps(meta, indent=2))

    org_slug = _slugify(org_name)
    return {
        "id_organisation": conn["id_organisation"],
        "organisation_name": org_name,
        "id_connection": id_connection,
        "type": conn_type,
        "git_organisation": conn.get("git_organisation") or "",
        "custom_host": conn.get("custom_host") or "",
        "repo_count": len(urls),
        "has_token": "yes" if token else "no",
        "bundle_stem": stem,
        "slug": f"{org_slug}__{stem}",
    }


def _slugify(name: str) -> str:
    import re
    s = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return s or "org"


def write_index_csv(outdir: Path, rows: list[dict]) -> None:
    index_path = outdir / "index.csv"
    fieldnames = [
        "id_organisation", "organisation_name", "id_connection", "type",
        "git_organisation", "custom_host", "repo_count", "has_token",
        "bundle_stem", "slug",
    ]
    with index_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--org-id", type=int, default=None,
        help="Process only this single organisation id (default: all rows in --orgs-csv)",
    )
    parser.add_argument(
        "--orgs-csv",
        default=str(PROJECT_ROOT / "prod_orgs_to_process.csv"),
        help="CSV with id_organisation,name",
    )
    parser.add_argument(
        "--creds",
        default=str(Path.home() / ".mysql-remote"),
        help="Path to JSON file with MySQL credentials",
    )
    parser.add_argument(
        "--outdir",
        default=str(PROJECT_ROOT / "orgs"),
        help="Directory for flat per-connection bundles (default: <project>/orgs)",
    )
    args = parser.parse_args()

    creds = load_db_creds(Path(args.creds))
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    csv_orgs = load_orgs_csv(Path(args.orgs_csv))
    if args.org_id is not None:
        csv_orgs = [(oid, name) for oid, name in csv_orgs if oid == args.org_id]
        if not csv_orgs:
            print(f"Error: org-id {args.org_id} not in {args.orgs_csv}", file=sys.stderr)
            return 2

    org_id_to_name = dict(csv_orgs)
    org_ids = list(org_id_to_name.keys())

    connections = fetch_connections(creds, org_ids)
    if not connections:
        print(f"No active non-AI connections found for any of {len(org_ids)} organisation(s).")
        return 0

    conn_ids = [int(c["id_connection"]) for c in connections]
    repos_by_conn = fetch_repos_for_connections(creds, conn_ids)

    summary_rows: list[dict] = []
    orgs_with_conn: set[int] = set()
    for conn in connections:
        oid = int(conn["id_organisation"])
        orgs_with_conn.add(oid)
        org_name = org_id_to_name.get(oid, "(unknown)")
        repos = repos_by_conn.get(int(conn["id_connection"]), [])
        summary_rows.append(write_connection_bundle(outdir, conn, org_name, repos))

    write_index_csv(outdir, summary_rows)

    # -- Summary --
    missing = [f"{oid} ({org_id_to_name[oid]})" for oid in org_ids if oid not in orgs_with_conn]
    total_repos = sum(r["repo_count"] for r in summary_rows)
    print(f"Organisations in CSV:        {len(org_ids)}")
    print(f"  with ≥1 active connection: {len(orgs_with_conn)}")
    print(f"  without any:               {len(missing)}")
    if missing:
        for m in missing:
            print(f"    - {m}")
    print(f"Connections written:         {len(summary_rows)}")
    print(f"Total repos across all:      {total_repos}")
    print(f"Output dir:                  {outdir}")
    print(f"Index:                       {outdir / 'index.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
