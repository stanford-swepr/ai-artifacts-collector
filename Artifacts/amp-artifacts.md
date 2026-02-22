# Official Amp Artifacts by Maturity Level

**Note:** Amp is a frontier coding agent built by Sourcegraph, engineered for teams with unconstrained token usage and state-of-the-art models.

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Amp without structured persistence or version control of configuration.

## L1 - Grounded Prompting

### `AGENTS.md`
- **Path:** Current working directory, parent directories (up to `$HOME`), `~/.config/amp/AGENTS.md`, `~/.config/AGENTS.md`
- **Format:** Markdown with optional YAML front matter
- **Purpose:** Guide Amp on codebase structure, build commands, test execution, and conventions
- **Scope:** Project-level (hierarchical) and user-level (global)
- **Status:** Stable
- **Discovery:** Automatically included from current directory up to `$HOME`; subtree files included when agent reads files in those directories
- **Fallback Names:** `AGENT.md` or `CLAUDE.md` if `AGENTS.md` doesn't exist
- **Features:** `@file-path` syntax for file references, glob patterns (`@doc/*.md`), YAML front matter with `globs:` for language-specific guidance

### `.agents/commands/*.md`
- **Path:** `.agents/commands/` directory (workspace root)
- **Format:** Markdown or executable files
- **Purpose:** Custom command definitions for reusable prompts and automated workflows
- **Scope:** Project-level (workspace)
- **Status:** Stable
- **Behavior:** Command output appended to prompt input; executables receive max 50k character output
- **Access:** Via Amp Command Palette (Cmd/Alt-Shift-A in editors, Ctrl-O in CLI)

### Settings Configuration (Not Repository-Stored)
- **Path:** `~/.config/amp/settings.json` (macOS/Linux), `%APPDATA%\amp\settings.json` (Windows)
- **Format:** JSON
- **Purpose:** User-level Amp configuration
- **Scope:** User-level (global)
- **Status:** Stable
- **Note:** Not repository-stored; user-specific configuration

## L2 - Agent-Augmented Dev

### Amp Coding Agent
- **Path:** Configured via AGENTS.md and custom commands
- **Format:** Interactive agent with CLI and editor extensions
- **Purpose:** Autonomous reasoning, comprehensive code editing, complex task execution
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Multi-file editing, test execution (guided by AGENTS.md), build automation, context-aware coding
- **Modes:** Smart (unconstrained SOTA models), Free (basic models, ad-supported)

### MCP Server Integration
- **Path:** Configured in `~/.config/amp/settings.json`
- **Format:** JSON configuration under `amp.mcpServers`
- **Purpose:** Model Context Protocol server integration for extended capabilities
- **Scope:** User-level (global)
- **Status:** Stable
- **Note:** Configuration stored locally, not in repository

### Custom Commands (Executable)
- **Path:** `.agents/commands/` (workspace) or `~/.config/amp/commands` (user-level)
- **Format:** Executable files with execute bit/shebang
- **Purpose:** Automated workflows and scripted actions
- **Scope:** Project-level or user-level
- **Status:** Stable
- **Limitation:** Max 50k character output

### Tool Permissions
- **Path:** Configured in `~/.config/amp/settings.json`
- **Format:** JSON arrays under `amp.permissions` and `amp.tools.disable`
- **Purpose:** Control tool access and disable specific tools
- **Scope:** User-level (global)
- **Status:** Stable
- **Note:** Security and access control configuration

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Amp provides powerful autonomous capabilities (unconstrained reasoning, comprehensive editing, complex execution) and supports custom commands and AGENTS.md guidance, it operates as a single sophisticated agent rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic stored in repository artifacts.

Custom commands provide workflow automation but do not constitute multi-agent orchestration with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 2     | `AGENTS.md`, `.agents/commands/*.md` | Static Instructions |
| L2    | 2     | `AGENTS.md` (Amp Agent workflows), `.agents/commands/*` (executable commands) | Executable Workflows |
| L3    | 0     | No official artifacts (single powerful agent, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://ampcode.com/ - Main website
- https://ampcode.com/manual - Official Owner's Manual
- https://ampcode.com/how-to-build-an-agent - Agent building guide
- https://sourcegraph.com/amp - Sourcegraph Amp page
- https://ampcode.com/install - Installation instructions
- https://ampcode.com/news/amp-free - Free tier announcement

**Notes:**
- **Global Settings:** `~/.config/amp/settings.json` (respects `$XDG_CONFIG_HOME`)
- **Global AGENTS.md:** `~/.config/amp/AGENTS.md` or `~/.config/AGENTS.md`
- **Global Commands:** `~/.config/amp/commands/`
- **Workspace Commands:** `.agents/commands/`
- **AGENTS.md Discovery:** Current directory → parent directories → `$HOME`; subtree files when reading files in those directories
- **Fallback Names:** `AGENT.md`, `CLAUDE.md` (if `AGENTS.md` missing)
- **File References:** `@file-path` syntax, supports globs (`@doc/*.md`)
- **YAML Front Matter:** `globs:` property for language-specific guidance
- **Custom Command Access:** Amp Command Palette (Cmd/Alt-Shift-A in VS Code/Cursor/Windsurf, Ctrl-O in CLI)
- **Executable Commands:** Must have execute bit or shebang; max 50k char output
- **Settings Namespace:** All settings use `amp.` prefix
- **MCP Configuration:** `amp.mcpServers` object in settings
- **Permissions:** `amp.permissions` array for tool access control
- **Tool Disabling:** `amp.tools.disable` array
- **Thinking Enabled:** `amp.anthropic.thinking.enabled` (default: true)
- **Operating Modes:** Smart (unconstrained SOTA), Free (ad-supported)
- **Platform Support:** VS Code, Cursor, JetBrains, Neovim, CLI
- **Thread Management:** Save and share interactions
- **Built by:** Sourcegraph
- **4 Principles:** (1) Unconstrained tokens, (2) Best models, (3) Raw model power, (4) Evolves with new models
- **Enterprise Deployment:** Managed settings at system-level paths for macOS/Linux/Windows
- **Compatibility Dating:** `amp.admin.compatibilityDate` (YYYY-MM-DD) for enterprise managed settings
