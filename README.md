# AI Artifacts Collector

Discovers, extracts, and embeds AI coding tool configuration files from git repositories. Part of the [Stanford AI Practices Benchmark](https://softwareengineeringproductivity.stanford.edu/ai-practices-benchmark) research program.

## What It Does

Scans repositories for AI tool configuration artifacts (e.g., `CLAUDE.md`, `.cursorrules`, `AGENTS.md`), extracts their content, generates semantic embeddings, and produces a self-contained output bundle for downstream analysis.

### Supported AI Tools (14+)

**Agentic IDEs:** Cursor, GitHub Copilot X, Windsurf, JetBrains AI, Google IDX, Kiro, OpenAI Codex

**CLI Tools:** Claude Code, Aider, GitHub Copilot CLI, Gemini CLI, OpenHands, amp

Tool patterns are defined in `Artifacts/*.json` and can be extended by adding new JSON files.

## Getting Started

### Prerequisites

- Python 3.10+
- Git 2.0+
- 2-5 GB disk space (embedding model ~550MB on first run)

### Installation

```bash
git clone git@github.com:stanford-swepr/ai-artifacts-collector.git
cd ai-artifacts-collector
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v  # verify installation
```

## Usage

### CLI Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `target` | Yes | Organisation or repository URL. Ends with `.git` → single-repo mode; otherwise → batch mode. Provider and org are inferred from the URL. |
| `--token` | No | Personal Access Token. Without it, only public repos are accessible. With it, private repos are included too. |
| `--config` | No | Path to `config.yaml`. Defaults to `<project_root>/config.yaml`. |

**Branch detection is automatic.** In single-repo mode the default branch is detected via `git ls-remote`. In batch mode the provider API returns each repo's default branch. No manual branch parameter is needed.

**Provider is inferred from the domain:** `github.com` → GitHub, `gitlab.com` → GitLab, `dev.azure.com` → Azure DevOps, `bitbucket.org` → Bitbucket. Self-hosted instances are matched by domain substring (e.g. `gitlab.mycompany.com`).

### Single Repository

```bash
# Public repo
python scripts/artifacts_collection.py \
    https://github.com/YOUR_ORG/REPO.git

# Private repo — add a token
python scripts/artifacts_collection.py \
    --token YOUR_GITHUB_TOKEN \
    https://github.com/YOUR_ORG/REPO.git
```

### Batch Collection

```bash
# Public repos only (no token needed)
python scripts/artifacts_collection.py \
    https://github.com/YOUR_ORG

# All repos (public + private)
python scripts/artifacts_collection.py \
    --token YOUR_GITHUB_TOKEN \
    https://github.com/YOUR_ORG
```

The embedding model is loaded once and reused across all repositories. Supported providers: GitHub, GitLab, Azure DevOps, Bitbucket.

### Python API

```python
from pathlib import Path
from src.pipeline import load_config, config_to_pipeline_config, run_pipeline, load_model

yaml_cfg = load_config(Path("config.yaml"))
config = config_to_pipeline_config(
    yaml_cfg,
    repo_url="https://github.com/owner/repo.git",
    branch="main",
    repo_name="repo",
    clone_base_dir=Path("repos"),
    artifacts_dir=Path("Artifacts"),
    output_dir=Path("output/my-collection"),
)

model = load_model(config)
result = run_pipeline(config, model=model)
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and adjust values for your study:

```bash
cp config.example.yaml config.yaml
```

`config.yaml` is gitignored so local changes are not committed.

| Setting | Description | Default |
|---------|-------------|---------|
| `paths.output_dir` | Output bundle directory. Supports `{organisation}` placeholder. | `output/{organisation}` |
| `paths.clone_dir` | Repository clone directory. Supports `{organisation}` placeholder. | `../analyzed_repos/{organisation}` |
| `embedding.batch_size` | Texts per encoding batch (reduce on OOM) | `32` |
| `embedding.memory_budget_gib` | Memory budget in GiB for adaptive batch estimation | `2` |
| `git.timeout` | Clone/pull timeout in seconds | `300` |
| `git.log_timeout` | Git log/rev-list/shortlog timeout in seconds | `60` |
| `temporal.start_date` | Git history window start (ISO 8601) | `2020-01-01` |
| `temporal.end_date` | Git history window end (`null` = today) | `null` |
| `author.strategy` | `"obfuscate"` (SHA-256 + salt) or `"anonymize"` (HMAC-SHA-256) | `obfuscate` |
| `author.secret` | Shared secret for `anonymize` strategy | — |
| `author.hash_length` | Hex characters kept from anonymized hash | `12` |
| `author.prefix` | Prefix for anonymized identifiers | `user-` |

The embedding model (`nomic-ai/nomic-embed-text-v1.5`, 768-dim, 8192-token context) is hardcoded and not user-configurable — changing it would invalidate downstream clustering pipelines that depend on consistent embedding dimensions and semantics.

## Pipeline Phases

| Phase | Description |
|-------|-------------|
| 1 | Load tool configs from `Artifacts/*.json` |
| 2 | Clone/checkout repository |
| 3 | Discover artifacts using pattern matching |
| 4 | Extract text content (with encoding detection) |
| 5 | Load embedding model (`nomic-ai/nomic-embed-text-v1.5`) |
| 6 | Generate 768-dim semantic embeddings |
| 7 | Build file metadata |
| 8 | Temporal analysis (git history of artifacts) |

## Output Format

Every collection run produces a **self-contained output bundle**:

```
{output_dir}/
├── Artifacts/                         # Snapshot of tool configs used during collection
│   ├── cursor-files.json
│   ├── claude-code-files.json
│   ├── shared-artifacts.json
│   └── ...
├── manifest.json                      # Schema version + collection metadata
├── {repo1}/
│   ├── {repo1}_file_artifacts.csv     # File-level metadata
│   ├── {repo1}_embeddings.pkl         # Embedding vectors (768-dim)
│   ├── {repo1}_embedding_metadata.csv # Per-file embedding info
│   ├── {repo1}_artifact_timeseries.csv# Git history events
│   ├── {repo1}_commit_aggregated.csv  # Commit statistics
│   └── {repo1}_repo_metrics.json      # Static repo metrics
└── {repo2}/
    └── ...
```

The bundled `Artifacts/` directory and `manifest.json` make the output fully self-contained — downstream analysis tools need nothing from this repository.

### manifest.json

```json
{
  "schema_version": "2.0",
  "collected_at": "2026-02-22T10:30:00+00:00",
  "embedding_model": "nomic-ai/nomic-embed-text-v1.5",
  "embedding_dim": 768
}
```

## Discovery Steps

Artifacts are discovered in 5 ordered steps (recorded in `discovery_step`):

1. **tool_standard** — Tool-specific patterns (`.cursorrules`, `CLAUDE.md`)
2. **shared_in_tool_folder** — Shared patterns inside tool folders (`.claude/docs/*.md`)
3. **shared_in_root** — Shared patterns in repo root (`AGENTS.md`, `README.md`)
4. **non_standard_root** — Non-standard markdown in root (`ARCHITECTURE.md`)
5. **non_standard_other** — Non-standard markdown elsewhere (`docs/design.md`)

Files are deduplicated across steps — a file discovered in an earlier step won't appear again.

## Project Structure

```
├── Artifacts/              # Tool pattern definitions (source of truth)
├── src/
│   ├── pipeline.py         # Orchestrates collection + bundles output
│   ├── artifact_config_loader.py
│   ├── file_discovery.py
│   ├── text_extractor.py
│   ├── embedding_generator.py
│   ├── git_operations.py
│   ├── temporal_analyzer.py
│   ├── data_models.py
│   ├── tokenizer.py
│   └── file_data_collector.py
├── scripts/
│   └── artifacts_collection.py  # Collection CLI (single-repo & batch)
├── tests/                  # pytest suite (280+ tests)
└── requirements.txt
```

## Privacy

Raw text content is **not** stored in the output. Only semantic embeddings (dense 768-dim vectors) are exported. Embeddings cannot be reversed to recover original text. Author identities in temporal data are hashed (obfuscated or anonymized via HMAC).

## Testing

```bash
pytest tests/ -v            # run all tests
pytest tests/ --cov=src     # with coverage
```

## License

This project is part of academic research at Stanford University. Please cite appropriately if using this methodology or data in your research.

## Links

- [Stanford AI Practices Benchmark](https://softwareengineeringproductivity.stanford.edu/ai-practices-benchmark)
