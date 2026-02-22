# Official OpenAI Codex Artifacts by Maturity Level

**Note:** OpenAI Codex is generally available as of 2025, powered by codex-1 and GPT-5-Codex models.

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Codex chat and suggestions without structured persistence or version control.

## L1 - Grounded Prompting

### `AGENTS.md`
- **Path:** Repository root and any subdirectory, `~/.codex/AGENTS.md` (global)
- **Format:** Markdown
- **Purpose:** Provide project-specific instructions, coding standards, test commands, and conventions to guide Codex behavior
- **Scope:** Project-level (hierarchical from root to current directory), or global
- **Status:** Stable
- **Discovery:** Walks from repository root down to current working directory, reading files in order
- **Character Limit:** Combined size up to `project_doc_max_bytes` (default 32 KiB)

### `AGENTS.override.md`
- **Path:** Repository root and any subdirectory, `~/.codex/AGENTS.override.md` (global)
- **Format:** Markdown
- **Purpose:** Override default AGENTS.md instructions with higher precedence
- **Scope:** Project-level (hierarchical) or global
- **Status:** Stable
- **Priority:** Checked before AGENTS.md in each directory

### Custom Fallback Filenames
- **Path:** Configurable via `project_doc_fallback_filenames` in `~/.codex/config.toml`
- **Format:** Markdown
- **Purpose:** Alternative instruction filenames treated as AGENTS.md equivalents
- **Scope:** Project-level (hierarchical)
- **Status:** Stable
- **Examples:** `TEAM_GUIDE.md`, `.agents.md`
- **Configuration:** `project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]`

## L2 - Agent-Augmented Dev

### `~/.codex/config.toml`
- **Path:** `~/.codex/config.toml`
- **Format:** TOML
- **Purpose:** Configure Codex behavior, models, approval policies, sandbox settings, MCP servers
- **Scope:** User-level (global), can define project-specific profiles
- **Status:** Stable
- **Key Sections:** Model selection, approval policies, sandbox modes, shell environment, MCP server configuration, authentication, profiles
- **Note:** Not repository-stored but supports project-specific profiles

### Codex Agent Mode (CLI)
- **Path:** Configuration via `~/.codex/config.toml` and repository AGENTS.md files
- **Format:** Interactive CLI workflows
- **Purpose:** Autonomous coding agent that reads, edits, runs commands with approvals for sensitive steps
- **Scope:** Project-level context
- **Status:** Stable
- **Modes:** Chat (drafts changes), Agent (with approvals), Agent Full Access (minimal prompts)
- **Capabilities:** Multi-file editing, command execution, test running, autonomous task completion

### Codex Automation (exec command)
- **Path:** Scriptable workflows using `codex exec` command
- **Format:** Command-line invocation
- **Purpose:** Automate repeatable workflows by scripting Codex
- **Scope:** Project-level
- **Status:** Stable
- **Use Cases:** CI/CD integration, automated refactoring, batch operations

### MCP Server Configuration
- **Path:** `~/.codex/config.toml` under `[mcp.<server-name>]` tables
- **Format:** TOML
- **Purpose:** Connect Codex to external tools and context via Model Context Protocol
- **Scope:** User-level (global), shared between CLI and IDE
- **Status:** Stable
- **Note:** Configuration file itself not repository-stored

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While OpenAI Codex provides powerful autonomous agent capabilities (Agent mode, Full Access mode) with extended runtime (up to 7 hours for GPT-5-Codex), progress tracking via to-do lists, and integration with external tools via MCP, it operates as a single sophisticated autonomous agent rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

The agent provides autonomous multi-step execution but lacks the multi-agent orchestration framework with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 3     | `AGENTS.md`, `AGENTS.override.md`, Custom fallback filenames (configurable) | Static Instructions |
| L2    | 2     | `AGENTS.md` (Agent Mode workflows), `AGENTS.md` (exec automation) | Executable Workflows |
| L3    | 0     | No official artifacts (single powerful agent, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://developers.openai.com/codex/ - Main Codex documentation
- https://developers.openai.com/codex/guides/agents-md/ - AGENTS.md guide
- https://developers.openai.com/codex/local-config/ - Configuration reference
- https://developers.openai.com/codex/cli/ - CLI documentation
- https://developers.openai.com/codex/mcp/ - Model Context Protocol
- https://github.com/openai/codex - Official GitHub repository
- https://github.com/openai/codex/blob/main/docs/config.md - Configuration documentation
- https://github.com/openai/codex/blob/main/docs/agents_md.md - AGENTS.md documentation
- https://github.com/openai/agents.md - AGENTS.md format specification
- https://openai.com/index/codex-now-generally-available/ - General availability announcement

**Notes:**
- **File Discovery Order:** Global `~/.codex/AGENTS.override.md` → Global `~/.codex/AGENTS.md` → Project root to current directory (AGENTS.override.md → AGENTS.md → fallbacks)
- **Character Limits:** Combined instructions limited to `project_doc_max_bytes` (default 32 KiB, configurable)
- **Configuration Sharing:** `~/.codex/config.toml` shared between CLI and IDE extension
- **Approval Modes:** Chat (draft only), Agent (with approvals), Agent Full Access (minimal prompts)
- **Models:** codex-1 (o3-optimized), GPT-5-Codex (agentic coding optimized)
- **Profiles:** Support project-specific configuration profiles via `[profiles.<name>]` in config.toml
- **Automation:** `codex exec` command for scripting workflows
- **Extended Runtime:** GPT-5-Codex can run autonomously for up to 7 hours
- **Platform Support:** macOS, Linux (official), Windows (experimental via WSL)
