# Official Aider Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Aider chat without structured persistence or version control of configuration.

## L1 - Grounded Prompting

### `.aider.conf.yml`
- **Path:** Home directory, git repository root, or current directory
- **Format:** YAML
- **Purpose:** Configure Aider behavior, models, API settings, git integration, file handling, testing
- **Scope:** Can be user-level (home) or project-level (git root/current dir)
- **Status:** Stable
- **Priority:** Files loaded in order: home → git root → current directory (last takes precedence)
- **Key Sections:** Model settings, API keys (OpenAI/Anthropic only), git integration, output/display, repository mapping, file handling, chat/history, testing/linting, voice features
- **Note:** File must use `.yml` extension (`.yaml` not recognized)

### `.aiderignore`
- **Path:** Git repository root (default) or configurable location
- **Format:** Plain text (similar to `.gitignore` syntax)
- **Purpose:** Specify files and directories Aider should ignore
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** Location customizable via `aiderignore` option in `.aider.conf.yml`

### `.env`
- **Path:** Repository root
- **Format:** Plain text (environment variables)
- **Purpose:** Store LLM API keys for all providers
- **Scope:** Project-level
- **Status:** Stable
- **Format:** `AIDER_xxx=value` or provider-specific key variables
- **Note:** Recommended for API key storage over YAML config

### Reference Files (via `read` configuration)
- **Path:** Configurable in `.aider.conf.yml`
- **Format:** Any text files (e.g., `CONVENTIONS.md`)
- **Purpose:** Read-only reference files providing context to Aider
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** Specified via `read` option in YAML config (supports list or inline format)

## L2 - Agent-Augmented Dev

### Architect Mode
- **Path:** Configured via `.aider.conf.yml` and command-line options
- **Format:** Interactive CLI workflow
- **Purpose:** Two-model workflow where architect model proposes solutions and editor model implements specific edits
- **Scope:** Project-level
- **Status:** Stable
- **Activation:** `--architect` flag, `/architect` command, or `--chat-mode architect`
- **Capabilities:** Separate reasoning (architect) from code editing (editor), optimized for reasoning models like o1
- **Performance:** R1+Sonnet achieved 64% on polyglot benchmark (14X less cost than previous SOTA)

### Automated Testing Integration
- **Path:** Configured via `.aider.conf.yml`
- **Format:** YAML configuration with `test-cmd` and `auto-test` options
- **Purpose:** Automatic test execution after code changes
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** `test-cmd` (test command), `auto-test` (boolean)

### Automated Linting Integration
- **Path:** Configured via `.aider.conf.yml`
- **Format:** YAML configuration with `lint-cmd` and `auto-lint` options
- **Purpose:** Automatic linting after code changes
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** `lint` (enable), `lint-cmd` (language-specific commands), `auto-lint` (boolean)

### Git Auto-Commits
- **Path:** Configured via `.aider.conf.yml`
- **Format:** YAML configuration
- **Purpose:** Automatic commit of LLM-generated changes
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** `auto-commits` (boolean), `commit-prompt` (custom message generation)

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Aider provides powerful autonomous capabilities through Architect Mode (two-model workflow) and can be scripted for complex workflows, it operates as a single or dual-model system rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

The Architect Mode provides a reasoning/editing separation but lacks the multi-agent orchestration framework with multiple specialized agent roles and workflow state coordination required for L3. Community members are building multi-agent workflows by combining multiple Aider instances externally, but this is not an officially documented repository-storable artifact pattern.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 4     | `.aider.conf.yml`, `.aiderignore`, `.env`, Reference files (via `read` config) | Static Instructions |
| L2    | 4     | `.aider.conf.yml` (Architect Mode), `.aider.conf.yml` (test-cmd), `.aider.conf.yml` (lint-cmd), `.aider.conf.yml` (auto-commits) | Executable Workflows |
| L3    | 0     | No official artifacts (dual-model system, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://aider.chat/docs/ - Main documentation
- https://aider.chat/docs/config/aider_conf.html - YAML configuration guide
- https://aider.chat/docs/config/options.html - Options reference
- https://aider.chat/docs/config/dotenv.html - .env configuration
- https://aider.chat/docs/usage/modes.html - Chat modes documentation
- https://github.com/Aider-AI/aider - Official GitHub repository
- https://github.com/paul-gauthier/aider/blob/main/aider/website/assets/sample.aider.conf.yml - Sample configuration

**Notes:**
- **Configuration Priority:** Home directory → Git root → Current directory (last wins)
- **Override:** `--config <filename>` loads only specified file
- **File Extension:** Must use `.yml` not `.yaml`
- **API Keys:** Only OpenAI/Anthropic keys in YAML; all other providers use `.env`
- **Chat Modes:** Code (default), Ask, Architect, Help
- **Mode Switching:** `/code`, `/ask`, `/architect`, `/help` (per-message) or `/chat-mode <mode>` (persistent)
- **Architect Launch:** `--architect` shortcut or `--chat-mode architect`
- **Edit Formats:** "editor-diff" and "editor-whole" recommended for architect mode
- **List Formats:** Supports bulleted (`- item`) or inline (`[item1, item2]`) in YAML
- **Auto-commits:** LLM changes automatically committed if enabled
- **Git Attribution:** Customizable with `attribute-author` and `attribute-committer`
- **History Files:** `input-history-file`, `chat-history-file`, `llm-history-file` for conversation persistence
- **Repository Mapping:** `map-tokens` controls context size for codebase understanding
