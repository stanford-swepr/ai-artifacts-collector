# Official Gemini CLI Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Gemini CLI for questions and commands without structured persistence or version control.

## L1 - Grounded Prompting

### `GEMINI.md`
- **Path:** Project root, subdirectories, or `~/.gemini/GEMINI.md` (global)
- **Format:** Markdown
- **Purpose:** Context files providing persistent project-specific instructions, coding styles, and background information
- **Scope:** Global (home directory), project-level (root), or module-level (subdirectories)
- **Status:** Stable
- **Hierarchical Loading:** Global → Project root → Ancestors → Local subdirectories
- **Features:** Supports file imports via `@path/to/file.md` syntax
- **Commands:** `/memory refresh` to reload, `/memory show` to display

### `.gemini/settings.json`
- **Path:** `.gemini/settings.json` (project root)
- **Format:** JSON
- **Purpose:** Project-specific configuration for models, tools, UI, context loading, privacy
- **Scope:** Project-level
- **Status:** Stable
- **Key Sections:** General, UI, Model, Context, Tools, MCP, Privacy & Security
- **Schema:** Available at `https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json`

### `.geminiignore`
- **Path:** Project root or subdirectories
- **Format:** Plain text (similar to `.gitignore` syntax)
- **Purpose:** Specify files to exclude from context discovery
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** Controlled by `fileFiltering.respectGeminiIgnore` setting (default: true)

### `.env`
- **Path:** Extension directories or project root
- **Format:** Plain text (environment variables)
- **Purpose:** Store environment variables for extensions and project configuration
- **Scope:** Project-level or extension-level
- **Status:** Stable
- **Note:** Extensions can have their own `.env` files loaded automatically

## L2 - Agent-Augmented Dev

### `.gemini/extensions/*/gemini-extension.json`
- **Path:** `~/.gemini/extensions/<extension-name>/gemini-extension.json` (user-level) or `.gemini/extensions/` (project-level pattern)
- **Format:** JSON
- **Purpose:** Extension configuration bundling MCP servers, context files, commands, and tool exclusions
- **Scope:** User-level (global) or potentially project-level
- **Status:** Stable
- **Components:** MCP server definitions, GEMINI.md context files, custom commands, excluded tools
- **Ecosystem:** 90+ official integrations (Figma, Stripe, Elastic, Postman, Snyk, Google suite)

### Custom Sandbox Profiles
- **Path:** `.gemini/sandbox-<platform>-custom.sb` or `.gemini/sandbox.Dockerfile`
- **Format:** Sandbox profile or Dockerfile
- **Purpose:** Custom sandbox configurations for tool execution isolation
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** Referenced via `sandbox` setting in `settings.json`

### MCP Server Configuration
- **Path:** `.gemini/settings.json` (MCP section)
- **Format:** JSON within settings
- **Purpose:** Configure Model Context Protocol servers for external tool integration
- **Scope:** Project-level
- **Status:** Stable
- **Properties:** `serverCommand`, `allowed`, `excluded`

### Tool Auto-Accept Configuration
- **Path:** `.gemini/settings.json`
- **Format:** JSON configuration
- **Purpose:** Enable autonomous tool execution for safe operations
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** `autoAccept` (boolean), `tools.allowed` (list), `security.disableYoloMode` (safety override)

### Hooks System
- **Path:** Configured in `.gemini/settings.json`
- **Format:** JSON with hook definitions
- **Purpose:** Lifecycle event interception for custom automation
- **Scope:** Project-level
- **Status:** Stable
- **Configuration:** `tools.enableHooks` (boolean)

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Gemini CLI supports extensions with MCP servers, custom commands, and autonomous workflows (headless mode for scripting), it operates as a single agent with extensible capabilities rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

Extensions can provide sophisticated capabilities (e.g., AI orchestration platform with 9 MCP servers), but these are tool extensions rather than multi-agent orchestration frameworks with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 4     | `GEMINI.md`, `.gemini/settings.json`, `.geminiignore`, `.env` | Static Instructions |
| L2    | 5     | `.gemini/extensions/*/gemini-extension.json`, `.gemini/sandbox-*.sb` or `.gemini/sandbox.Dockerfile`, `.gemini/settings.json` (MCP), `.gemini/settings.json` (autoAccept), `.gemini/settings.json` (hooks) | Executable Workflows |
| L3    | 0     | No official artifacts (single extensible agent, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://github.com/google-gemini/gemini-cli/ - Official GitHub repository
- https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/configuration.md - Configuration guide
- https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/configuration.md - CLI configuration docs
- https://geminicli.com/docs/get-started/configuration/ - Configuration documentation
- https://geminicli.com/extensions/ - Extensions gallery
- https://blog.google/technology/developers/gemini-cli-extensions/ - Extensions announcement
- https://cloud.google.com/gemini/docs/codeassist/gemini-cli - Cloud documentation

**Notes:**
- **Configuration Hierarchy:** Defaults → System defaults → User settings → Project settings → System settings → Env vars → CLI args
- **Global Settings:** `~/.gemini/settings.json` (user-level)
- **Global Context:** `~/.gemini/GEMINI.md` (applies across all projects)
- **Global Extensions:** `~/.gemini/extensions/` (user-level extensions)
- **Context Loading:** Hierarchical from global → project root → ancestors → local subdirectories
- **File Imports:** `@path/to/file.md` syntax for modular context files
- **Memory Commands:** `/memory refresh` (reload), `/memory show` (display)
- **Environment Variables:** `$VAR_NAME` or `${VAR_NAME}` syntax in settings.json
- **Schema Validation:** JSON schema available for IDE autocomplete
- **Context Discovery:** Controlled by `fileName`, `includeDirectories`, `discoveryMaxDirs` settings
- **Git Integration:** `fileFiltering.respectGitIgnore` (default: true)
- **Tool Configuration:** `tools.core` (built-in allowlist), `tools.allowed` (auto-accept), `tools.exclude` (disable)
- **MCP Protocol:** Standardized tool discovery and execution
- **Extension Components:** MCP servers + context files + custom commands + tool exclusions
- **Autonomous Features:** Auto-accept mode, headless scripting, hooks system
- **Sandbox Isolation:** Custom profiles for secure tool execution
- **Session Management:** Checkpointing, retention policies, recovery
- **Model Aliases:** Named presets with inheritance support
- **Accessibility:** Screen reader mode for plain-text output
