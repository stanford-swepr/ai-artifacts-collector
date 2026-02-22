# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Artifact Data Collection System** — A Stanford Software Engineering Productivity research project that scans git repositories for AI coding tool configuration files (e.g., `CLAUDE.md`, `.cursorrules`, `AGENTS.md`), extracts their content, generates semantic embeddings, and produces self-contained output bundles for downstream clustering analysis.

**Research Program**: [Stanford AI Practices Benchmark](https://softwareengineeringproductivity.stanford.edu/ai-practices-benchmark)

## Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run a single test file
pytest tests/test_pipeline.py -v

# Run a single test
pytest tests/test_pipeline.py::test_function_name -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Batch collection CLI (public repos, no token needed)
python scripts/artifacts_collection.py https://github.com/ORG

# Batch collection CLI (all repos including private)
python scripts/artifacts_collection.py --token TOKEN https://github.com/ORG

# Single-repo collection (branch auto-detected)
python scripts/artifacts_collection.py https://github.com/ORG/REPO.git
```

## Architecture

### Pipeline (`src/pipeline.py`)

The central orchestrator. Both the batch CLI (`scripts/artifacts_collection.py`) and notebooks import from `pipeline.py` as a single source of truth. The pipeline runs 8 phases sequentially via `run_pipeline()`:

1. Load tool configs from `Artifacts/*.json` → `load_tool_configs()`
2. Clone/checkout/pull repo → `clone_and_prepare_repo()`
3. Discover artifacts via pattern matching → `discover_and_extract()`
4. Extract text content (same function, reads files inline)
5. Load embedding model → `load_model()`
6. Generate 768-dim embeddings → `generate_embeddings()`
7. Build file metadata → `build_metadata()`
8. Temporal analysis (git history) → `run_temporal_analysis()`

Key design: `run_pipeline()` accepts an optional pre-loaded `SentenceTransformer` model. In batch mode, the model is loaded once and passed to each repo's pipeline run. When `model=None`, the pipeline loads/unloads it internally.

### Data Flow

Artifacts flow through the pipeline as `List[Dict[str, Any]]` (plain dicts, not dataclass instances). Each dict accumulates fields across phases: `file_path` → `text_content` → `embedding` → `file_id`. The `PipelineResult` dataclass wraps the final outputs.

`PipelineConfig` and `PipelineResult` are dataclasses defined in `pipeline.py`. The Pydantic-style models in `data_models.py` (`ToolConfig`, `ArtifactPattern`, `ToolRegistry`) are used for loading and validating `Artifacts/*.json` configs.

### Discovery Steps (ordered, deduplicated)

`file_discovery.py` uses a `DiscoveryContext` to track already-discovered files across 5 steps:

1. **tool_standard** — Tool-specific patterns (`.cursorrules`, `.cursor/rules/*.mdc`)
2. **shared_in_tool_folder** — Shared patterns inside tool config folders (e.g., `AGENTS.md` in `.claude/`)
3. **shared_in_root** — Shared patterns in repo root (`AGENTS.md`, `README.md`)
4. **non_standard_root** — Any `*.md`/`*.mdc` in root not yet found (excludes `CHANGELOG.md`, `LICENSE.md`, etc.)
5. **non_standard_other** — Any `*.md`/`*.mdc` elsewhere, skipping excluded dirs (`node_modules`, `.git`, etc.)

Each file appears at most once; earlier steps take priority.

### Tool Configuration

Tool patterns are defined in `Artifacts/{tool}-files.json`. Each file contains a `ToolConfig` with `artifact_patterns` (discovery rules using `exact_path`, `glob`, or `regex` methods). Cross-tool shared patterns (like `AGENTS.md`) live in `Artifacts/shared-artifacts.json` and are loaded separately via `load_shared_config()`.

To add a new AI tool: create `Artifacts/{tool}-files.json` following the schema in existing files (see `cursor-files.json` for reference).

### Embedding Generation

`embedding_generator.py` uses `nomic-ai/nomic-embed-text-v1.5` (768-dim, 8192-token context). Texts exceeding the token limit are chunked with overlap and mean-pooled. Batch encoding uses length-adaptive batching with memory-mapped temp files to prevent OOM on large collections. All texts are prefixed with `"clustering: "` for the nomic model.

### Temporal Analysis

`temporal_analyzer.py` analyzes git history for discovered artifacts. Author identities are privacy-protected via two strategies: `obfuscate` (SHA256 + salt) or `anonymize` (HMAC-SHA256, compatible with reference PHP implementation). The strategy is configured via `PipelineConfig.author_strategy`.

### Pipeline Configuration (`config.yaml`)

User-tunable settings (embedding batch size, temporal date range, author privacy params, output/clone/artifacts paths) are externalized to `config.yaml`. Copy `config.example.yaml` to `config.yaml` to customize. If `config.yaml` is absent, all defaults from `PipelineConfig` apply. Secrets (tokens, author secrets) stay in environment variables — never in config files. The batch CLI accepts `--config path/to/config.yaml` to override the default location. Path values in the `paths` section support an `{organisation}` placeholder that the batch CLI resolves at runtime; CLI flags (e.g., `--output_dir`) still override YAML paths.

`load_config()` reads and validates the YAML; `config_to_pipeline_config()` merges YAML values with per-repo overrides into a `PipelineConfig`.

### Output Bundle

Each collection run produces a self-contained bundle at `{output_dir}/` containing:
- `Artifacts/` — snapshot of tool configs used during collection
- `manifest.json` — schema version, timestamp, model info
- `{repo}/` — per-repo CSVs (metadata, timeseries, commits) and PKL (embeddings)

Raw text content is **not** exported — only embeddings and metadata.

## Testing Patterns

Tests are in `tests/test_{module}.py`, one per source module. All heavy dependencies (model loading, git operations, file I/O) are mocked with `unittest.mock`. Tests use `pytest` fixtures with `tmp_path` for filesystem operations. No conftest.py — fixtures are defined per test file.

## Key Conventions

- All `pipeline.py` functions are side-effect-free (no print) except `run_pipeline()` which prints phase progress
- Module imports use `from src.module import ...` (project root must be on `sys.path`)
- Git providers supported: GitHub, GitLab, Azure DevOps, Bitbucket (via `git_operations.get_repo_details()`)
- `check_output_complete()` enables skip-if-done behavior in batch mode (checks for 4+ CSVs and 1+ PKL)
