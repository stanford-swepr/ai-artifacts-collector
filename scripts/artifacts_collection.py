#!/usr/bin/env python3
"""Artifact collection CLI.

Thin wrapper around ``src.pipeline`` that processes repositories in a git
organisation (batch mode) or a single repository (single-repo mode).  The
embedding model is loaded once and reused across repos.

Usage (batch, public):
    python scripts/artifacts_collection.py https://github.com/ORG

Usage (batch, private + public):
    python scripts/artifacts_collection.py --token TOKEN https://github.com/ORG

Usage (single repo, public):
    python scripts/artifacts_collection.py https://github.com/ORG/REPO.git

Usage (single repo, private):
    python scripts/artifacts_collection.py --token TOKEN https://github.com/ORG/REPO.git

Usage (repos file — one URL per line, model loaded once):
    python scripts/artifacts_collection.py --repos-file repos.txt
"""

import argparse
import gc
import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Ensure project root is on sys.path regardless of cwd
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.git_operations import detect_default_branch, extract_qualified_repo_name, get_repo_details, parse_target
from src.pipeline import (
    PipelineConfig,
    bundle_artifacts_config,
    check_output_complete,
    config_to_pipeline_config,
    load_config,
    load_model,
    run_pipeline,
    write_manifest,
)


# ---------------------------------------------------------------------------
# Permanent-failure cache
# ---------------------------------------------------------------------------
# Stored at <output_dir>/.permanent_failures.json as {"<url>": "<reason>"}.
# Populated when a repo fails for a reason that cannot change between
# snapshots (not-found / auth / permission). Subsequent snapshots read this
# file and skip cached URLs without touching the network.
#
# Transient failures (timeouts, 5xx, network errors) are NOT cached so they
# can retry in the next snapshot.
# Per-date failures ("No commits found before <date>") are also NOT cached:
# a later snapshot's cutoff may include the repo's first commit.

PERMANENT_FAILURE_PATTERNS = (
    "repository not found",
    "does not exist",
    "authentication failed",
    "permission denied",
    "access denied",
    "unknown git provider",
)
TRANSIENT_FAILURE_MARKERS = (
    "timed out",
    "timeout",
    "no commits found",
    "500",
    "502",
    "503",
    "504",
    "connection refused",
    "connection reset",
    "could not resolve host",
    "temporary failure",
    "network is unreachable",
)


def _classify_failure(error_msg: str) -> str:
    """Return 'permanent' if the error can never succeed, 'transient' otherwise."""
    lower = error_msg.lower()
    for marker in TRANSIENT_FAILURE_MARKERS:
        if marker in lower:
            return "transient"
    for marker in PERMANENT_FAILURE_PATTERNS:
        if marker in lower:
            return "permanent"
    return "transient"  # fail-safe: retry unknown errors


def _load_permanent_failures(output_dir: Path) -> dict[str, str]:
    cache_path = output_dir / ".permanent_failures.json"
    if not cache_path.exists():
        return {}
    try:
        import json
        return json.loads(cache_path.read_text())
    except (ValueError, OSError):
        return {}


def _persist_permanent_failure(output_dir: Path, url: str, reason: str) -> None:
    cache_path = output_dir / ".permanent_failures.json"
    import json
    data = _load_permanent_failures(output_dir)
    if url in data:
        return
    data[url] = reason
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(data, indent=2))
    except OSError:
        pass  # best effort


def run_from_file(args):
    """Process repos listed in a text file (one URL per line).

    The embedding model is loaded once and reused across all repos.
    """
    repos_path = Path(args.repos_file)
    if not repos_path.exists():
        print(f"Error: repos file not found: {repos_path}", file=sys.stderr)
        sys.exit(1)

    # Read and filter repo entries. Each non-comment line is either:
    #   "<url>"               — branch will be auto-detected
    #   "<url>\t<branch>"     — preset branch skips detect_default_branch / ls-remote
    lines = repos_path.read_text().splitlines()
    repo_entries: list[tuple[str, str | None]] = []
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if "\t" in s:
            url, branch = s.split("\t", 1)
            repo_entries.append((url.strip(), branch.strip() or None))
        else:
            repo_entries.append((s, None))
    if not repo_entries:
        print("Error: no repository URLs found in file", file=sys.stderr)
        sys.exit(1)
    repo_urls = [u for u, _ in repo_entries]  # kept for logging / len()

    # -- Load YAML config --
    config_path = Path(args.config) if args.config else project_root / "config.yaml"
    yaml_cfg = load_config(config_path)

    paths_cfg = yaml_cfg.get("paths", {})
    embedding_cfg = yaml_cfg.get("embedding", {})
    temporal_cfg = yaml_cfg.get("temporal", {})
    author_cfg = yaml_cfg.get("author", {})
    git_cfg = yaml_cfg.get("git", {})

    batch_size = embedding_cfg.get("batch_size", 32)
    memory_budget_gib = embedding_cfg.get("memory_budget_gib", 2)
    git_timeout = git_cfg.get("timeout", 300)
    git_log_timeout = git_cfg.get("log_timeout", 60)
    start_date = temporal_cfg.get("start_date", "2020-01-01")
    end_date = temporal_cfg.get("end_date", None)
    author_strategy = author_cfg.get("strategy", "obfuscate")
    author_secret = author_cfg.get("secret", "")

    artifacts_dir = project_root / "Artifacts"

    # Use "repos-file" as the org placeholder for paths
    default_org = "repos-file"

    def _resolve_path(raw: str, org: str) -> Path:
        expanded = raw.replace("{organisation}", org)
        p = Path(expanded)
        return p if p.is_absolute() else project_root / p

    output_dir = _resolve_path(paths_cfg["output_dir"], default_org) if "output_dir" in paths_cfg else project_root / "output" / default_org
    clone_base_dir = _resolve_path(paths_cfg["clone_dir"], default_org) if "clone_dir" in paths_cfg else project_root.parent / "analyzed_repos" / default_org

    total_repos = len(repo_urls)

    # -- Log run parameters --
    run_start = time.time()
    print("=" * 60)
    print("Artifact Collection Run (repos-file mode)")
    print("=" * 60)
    print(f"  config_file:      {config_path} ({'loaded' if yaml_cfg else 'defaults'})")
    print(f"  repos_file:       {repos_path}")
    print(f"  total_repos:      {total_repos}")
    print(f"  output_dir:       {output_dir}")
    print(f"  clone_base_dir:   {clone_base_dir}")
    print(f"  batch_size:       {batch_size}")
    print(f"  memory_budget:    {memory_budget_gib} GiB")
    print(f"  git_timeout:      {git_timeout}s")
    print(f"  git_log_timeout:  {git_log_timeout}s")
    print(f"  author_strategy:  {author_strategy}")
    print(f"  start_date:       {start_date}")
    if end_date:
        print(f"  end_date:         {end_date}")
    print(f"  started_at:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Load embedding model ONCE
    dummy_config = PipelineConfig(
        repo_url="", branch="", repo_name="",
        clone_base_dir=clone_base_dir,
        artifacts_dir=artifacts_dir,
        output_dir=output_dir,
    )
    model = load_model(dummy_config)
    print()

    bundle_artifacts_config(artifacts_dir, output_dir)
    write_manifest(output_dir, dummy_config)

    # Load the per-connection permanent-failure cache so we can skip repos
    # that previously failed with a non-retryable error.
    permanent_failures = _load_permanent_failures(output_dir)
    if permanent_failures:
        print(f"  [cache] {len(permanent_failures)} repos marked as permanent failures — will skip")

    # Process repos
    succeeded = []
    failed = []
    skipped = []

    for idx, (url, preset_branch) in enumerate(repo_entries, 1):
        # Short-circuit: if a previous snapshot flagged this URL as a permanent
        # failure (404 / auth / not-found), skip it here without touching git.
        if url in permanent_failures:
            reason = permanent_failures[url]
            print(f"[{idx}/{total_repos}] [skip-cached] {url}: {reason}")
            skipped.append(url)
            continue

        # Parse each URL to extract org info
        try:
            info = parse_target(url)
        except ValueError as e:
            print(f"[{idx}/{total_repos}] [FAIL] {url}: {e}", file=sys.stderr)
            failed.append({"url": url, "error": str(e)})
            if _classify_failure(str(e)) == "permanent":
                _persist_permanent_failure(output_dir, url, str(e))
                permanent_failures[url] = str(e)
            continue

        repo_url = info["repo_url"] if info["repo_url"] else url
        org = info["org"]
        repo_name = extract_qualified_repo_name(repo_url)

        progress = f"[{idx}/{total_repos}]"

        # Branch resolution: trust the preset from the repos file when provided
        # (DB-sourced); otherwise auto-detect.
        if preset_branch:
            branch = preset_branch
        elif info["mode"] == "single-repo":
            branch = detect_default_branch(repo_url, args.token)
            if not branch:
                # Try common default branch names via ls-remote
                for candidate in ("main", "master"):
                    try:
                        result = subprocess.run(
                            ["git", "ls-remote", "--heads", repo_url, candidate],
                            capture_output=True, text=True, timeout=30,
                        )
                        if result.returncode == 0 and candidate in result.stdout:
                            branch = candidate
                            break
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        continue
                else:
                    branch = "main"
        else:
            branch = "main"

        # Skip if already complete
        if check_output_complete(output_dir, repo_name):
            print(f"{progress} [skip] {repo_name}: output already complete")
            skipped.append(repo_name)
            continue

        per_repo_overrides = dict(
            repo_url=repo_url,
            branch=branch,
            repo_name=repo_name,
            clone_base_dir=clone_base_dir,
            artifacts_dir=artifacts_dir,
            output_dir=output_dir,
            author_strategy=author_strategy,
            author_salt=str(uuid.uuid4()),
            author_secret=author_secret,
            author_org=org,
        )
        if end_date is not None:
            per_repo_overrides["end_date"] = end_date

        config = config_to_pipeline_config(yaml_cfg, **per_repo_overrides)

        print(f"\n{progress} [start] {repo_name}")
        print(f"         url:    {repo_url}")
        print(f"         branch: {branch}")
        repo_start = time.time()
        try:
            result = run_pipeline(config, token=args.token, model=model)
            elapsed = time.time() - repo_start
            print(f"{progress} [done]  {repo_name} in {elapsed:.1f}s "
                  f"-- {result.n_with_embedding} embeddings, "
                  f"{result.n_without_embedding} skipped")
            succeeded.append(repo_name)
        except Exception as e:
            elapsed = time.time() - repo_start
            print(f"{progress} [FAIL]  {repo_name} after {elapsed:.1f}s: {e}", file=sys.stderr)
            failed.append({"url": repo_url, "error": str(e)})
            if _classify_failure(str(e)) == "permanent":
                _persist_permanent_failure(output_dir, url, str(e))
                permanent_failures[url] = str(e)

        # Optional per-repo clone cleanup to cap disk usage during large sweeps.
        if args.delete_clone:
            clone_dir = clone_base_dir / repo_name
            if clone_dir.exists():
                shutil.rmtree(clone_dir, ignore_errors=True)

    # Cleanup
    del model
    gc.collect()

    # Summary
    total_elapsed = time.time() - run_start
    minutes, seconds = divmod(int(total_elapsed), 60)
    print()
    print("=" * 60)
    print("Run Summary")
    print("=" * 60)
    print(f"  Repos file:    {repos_path}")
    print(f"  Total repos:   {total_repos}")
    print(f"  Succeeded:     {len(succeeded)}")
    print(f"  Failed:        {len(failed)}")
    print(f"  Skipped:       {len(skipped)}")
    print(f"  Total time:    {minutes}m {seconds}s")
    if failed:
        print("\n  Failed repositories:")
        for f in failed:
            print(f"    {f['url']}: {f['error']}")
    print(f"\n  Finished at:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Artifact collection for git repositories.",
    )
    parser.add_argument("target", nargs="?", default=None,
                        help="Organisation or repository URL (e.g. https://github.com/ORG or https://github.com/ORG/REPO.git)")
    parser.add_argument("--repos-file", default=None,
                        help="Path to a text file with one repo URL per line (model loaded once)")
    parser.add_argument("--token", default=None,
                        help="Personal Access Token (optional; without it only public repos are accessible)")
    parser.add_argument("--config", default=None,
                        help="Path to config.yaml (default: <project_root>/config.yaml)")
    parser.add_argument("--delete-clone", action="store_true",
                        help="Delete each repo's clone directory after processing "
                             "(reduces disk usage for large sweeps at the cost of "
                             "re-cloning on subsequent runs)")
    args = parser.parse_args()

    if args.repos_file:
        return run_from_file(args)

    if not args.target:
        parser.error("target is required when --repos-file is not used")

    # -- Parse target URL --
    try:
        target_info = parse_target(args.target)
    except ValueError as e:
        parser.error(str(e))

    single_repo_mode = target_info["mode"] == "single-repo"
    git_type = target_info["git_type"]
    org = target_info["org"]
    repo_url = target_info["repo_url"]

    # -- Load YAML config --
    config_path = Path(args.config) if args.config else project_root / "config.yaml"
    yaml_cfg = load_config(config_path)

    # -- Resolve paths: YAML defaults → hardcoded defaults → CLI override --
    paths_cfg = yaml_cfg.get("paths", {})

    def _resolve_path(raw: str) -> Path:
        """Resolve a path string, expanding {organisation} and making relative
        paths relative to project_root."""
        expanded = raw.replace("{organisation}", org)
        p = Path(expanded)
        return p if p.is_absolute() else project_root / p

    artifacts_dir = project_root / "Artifacts"
    clone_base_dir = _resolve_path(paths_cfg["clone_dir"]) if "clone_dir" in paths_cfg else project_root.parent / "analyzed_repos" / org
    output_dir = _resolve_path(paths_cfg["output_dir"]) if "output_dir" in paths_cfg else project_root / "output" / org

    embedding_cfg = yaml_cfg.get("embedding", {})
    temporal_cfg = yaml_cfg.get("temporal", {})
    author_cfg = yaml_cfg.get("author", {})
    git_cfg = yaml_cfg.get("git", {})

    batch_size = embedding_cfg.get("batch_size", 32)
    memory_budget_gib = embedding_cfg.get("memory_budget_gib", 2)
    git_timeout = git_cfg.get("timeout", 300)
    git_log_timeout = git_cfg.get("log_timeout", 60)
    start_date = temporal_cfg.get("start_date", "2020-01-01")
    end_date = temporal_cfg.get("end_date", None)
    author_strategy = author_cfg.get("strategy", "obfuscate")
    author_secret = author_cfg.get("secret", "")

    # -- Log run parameters --
    run_start = time.time()
    print("=" * 60)
    print("Artifact Collection Run")
    print("=" * 60)
    print(f"  config_file:      {config_path} ({'loaded' if yaml_cfg else 'defaults'})")
    print(f"  mode:             {'single-repo' if single_repo_mode else 'batch'}")
    if single_repo_mode:
        print(f"  repo_url:         {repo_url}")
    else:
        print(f"  git_type:         {git_type}")
    print(f"  git_organisation: {org}")
    print(f"  output_dir:       {output_dir}")
    print(f"  clone_base_dir:   {clone_base_dir}")
    print(f"  artifacts_dir:    {artifacts_dir}")
    print(f"  batch_size:       {batch_size}")
    print(f"  memory_budget:    {memory_budget_gib} GiB")
    print(f"  git_timeout:      {git_timeout}s")
    print(f"  git_log_timeout:  {git_log_timeout}s")
    print(f"  author_strategy:  {author_strategy}")
    print(f"  start_date:       {start_date}")
    print(f"  started_at:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # 1. Fetch repository list
    if single_repo_mode:
        print(f"Detecting default branch for {repo_url}...")
        branch = detect_default_branch(repo_url, args.token)
        if branch:
            print(f"  detected: {branch}")
        else:
            branch = "main"
            print(f"  detection failed, falling back to: {branch}")
        repositories = [{"url": repo_url, "branch": branch}]
    else:
        repositories = get_repo_details(git_type, org, args.token)
    total_repos = len(repositories)
    if single_repo_mode:
        print(f"Single repo mode: {repo_url}\n")
    else:
        print(f"Found {total_repos} repositories in {org}\n")

    # 2. Load embedding model once
    dummy_config = PipelineConfig(
        repo_url="", branch="", repo_name="",
        clone_base_dir=clone_base_dir,
        artifacts_dir=artifacts_dir,
        output_dir=output_dir,
    )
    model = load_model(dummy_config)
    print()

    # 2b. Bundle Artifacts/ config and manifest into output root
    bundle_artifacts_config(artifacts_dir, output_dir)
    write_manifest(output_dir, dummy_config)

    # 3. Process each repository
    succeeded = []
    failed = []
    skipped = []

    for idx, repo in enumerate(repositories, 1):
        repo_url = repo["url"]
        branch = repo["branch"]
        repo_name = extract_qualified_repo_name(repo_url)

        progress = f"[{idx}/{total_repos}]"

        # Skip if already complete
        if check_output_complete(output_dir, repo_name):
            print(f"{progress} [skip] {repo_name}: output already complete")
            skipped.append(repo_name)
            continue

        per_repo_overrides = dict(
            repo_url=repo_url,
            branch=branch,
            repo_name=repo_name,
            clone_base_dir=clone_base_dir,
            artifacts_dir=artifacts_dir,
            output_dir=output_dir,
            author_strategy=author_strategy,
            author_salt=str(uuid.uuid4()),
            author_secret=author_secret,
            author_org=org,
        )
        if end_date is not None:
            per_repo_overrides["end_date"] = end_date

        config = config_to_pipeline_config(yaml_cfg, **per_repo_overrides)

        print(f"\n{progress} [start] {repo_name}")
        print(f"         url:    {repo_url}")
        print(f"         branch: {branch}")
        repo_start = time.time()
        try:
            result = run_pipeline(config, token=args.token, model=model)
            elapsed = time.time() - repo_start
            print(f"{progress} [done]  {repo_name} in {elapsed:.1f}s "
                  f"-- {result.n_with_embedding} embeddings, "
                  f"{result.n_without_embedding} skipped")
            succeeded.append(repo_name)
        except Exception as e:
            elapsed = time.time() - repo_start
            print(f"{progress} [FAIL]  {repo_name} after {elapsed:.1f}s: {e}", file=sys.stderr)
            failed.append({"url": repo_url, "error": str(e)})

        # Optional per-repo clone cleanup to cap disk usage during large sweeps.
        if args.delete_clone:
            clone_dir = clone_base_dir / repo_name
            if clone_dir.exists():
                shutil.rmtree(clone_dir, ignore_errors=True)

    # 4. Cleanup
    del model
    gc.collect()

    # 5. Summary
    total_elapsed = time.time() - run_start
    minutes, seconds = divmod(int(total_elapsed), 60)
    print()
    print("=" * 60)
    print("Run Summary")
    print("=" * 60)
    if single_repo_mode:
        print(f"  Repo:          {target_info['repo_url']}")
    else:
        print(f"  Organisation:  {org}")
    print(f"  Total repos:   {total_repos}")
    print(f"  Succeeded:     {len(succeeded)}")
    print(f"  Failed:        {len(failed)}")
    print(f"  Skipped:       {len(skipped)}")
    print(f"  Total time:    {minutes}m {seconds}s")
    if failed:
        print("\n  Failed repositories:")
        for f in failed:
            print(f"    {f['url']}: {f['error']}")
    print(f"\n  Finished at:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
