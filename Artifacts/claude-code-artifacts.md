# Official Claude Code Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Claude Code chat and inline suggestions without structured persistence or version control.

## L1 - Grounded Prompting

### `.claude/settings.json`
- **Path:** `.claude/settings.json`
- **Format:** JSON
- **Purpose:** Project-level settings checked into source control and shared with team
- **Scope:** Project-level
- **Status:** Stable
- **Key Settings:** `permissions`, `model`, `env`, `apiKeyHelper`, `companyAnnouncements`, `hooks`, `sandbox`, `extraKnownMarketplaces`

### `.claude/settings.local.json`
- **Path:** `.claude/settings.local.json`
- **Format:** JSON
- **Purpose:** Personal project preferences not committed to version control
- **Scope:** Project-level (local)
- **Status:** Stable
- **Note:** Git-ignored for personal experimentation

### `CLAUDE.md`
- **Path:** Project root or any directory
- **Format:** Markdown
- **Purpose:** Project-specific instructions and context automatically loaded at startup
- **Scope:** Project-level
- **Status:** Stable
- **Content:** Repository etiquette, developer environment setup, project-specific behaviors
- **Note:** No required format; keep concise and human-readable

### `AGENTS.md`
- **Path:** Project root (community pattern)
- **Format:** Markdown
- **Purpose:** Cross-tool compatibility for agent instructions
- **Scope:** Project-level
- **Status:** Community-adopted pattern (not officially documented but widely used)

## L2 - Agent-Augmented Dev

### `.claude/commands/*.md`
- **Path:** `.claude/commands/` directory (supports subdirectories for namespacing)
- **Format:** Markdown with YAML frontmatter
- **Purpose:** Custom slash commands for frequently-used prompts
- **Scope:** Project-level (shared with team)
- **Status:** Stable
- **Frontmatter Properties:** `description`, `allowed-tools`, `model`, `argument-hint`, `disable-model-invocation`
- **Argument Handling:** `$ARGUMENTS` (all args), `$1`, `$2`, etc. (positional args)
- **Advanced Features:** Bash execution (`!` prefix), file references (`@` prefix)

### `.claude/agents/*.md`
- **Path:** `.claude/agents/` directory
- **Format:** Markdown with YAML frontmatter
- **Purpose:** Project-specific subagents with specialized roles
- **Scope:** Project-level
- **Status:** Stable
- **Frontmatter Properties:** `name`, `description`, `tools` (comma-separated or omit to inherit all), `model` (sonnet/opus/haiku/inherit)
- **Capabilities:** Separate conversation history, context isolation, intelligent routing by coordinator

### `.claude/.mcp.json`
- **Path:** `.claude/.mcp.json`
- **Format:** JSON
- **Purpose:** MCP (Model Context Protocol) server definitions for project
- **Scope:** Project-level
- **Status:** Stable

## L3 - Agentic Orchestration

### Subagent Coordination System
- **Path:** Configured via `.claude/agents/*.md`
- **Format:** Markdown with YAML frontmatter defining agent roles and tools
- **Purpose:** Multi-agent orchestration with coordinator model routing requests to specialized subagents
- **Scope:** Project-level
- **Status:** Stable
- **Orchestration Features:**
  - Coordinator Claude intelligently routes requests based on context analysis
  - Each subagent maintains separate conversation history and context
  - Supports specialized roles (code reviewer, tester, security analyst, etc.)
  - Tool restriction per subagent via `tools` frontmatter property
  - Model selection per subagent for optimized performance/cost
- **Note:** While this provides multi-agent capabilities, it uses a coordinator-based routing model rather than explicit workflow orchestration with stage management

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 4     | `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.md`, `AGENTS.md` | Static Instructions |
| L2    | 3     | `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/.mcp.json` | Executable Workflows |
| L3    | 1     | `.claude/agents/*.md` (Subagent Coordination System) | Multi-Agent Orchestration |

**Documentation Sources:**
- https://code.claude.com/docs/en/settings - Settings documentation
- https://code.claude.com/docs/en/slash-commands - Slash commands guide
- https://docs.claude.com/en/docs/claude-code/sub-agents - Subagents documentation
- https://docs.anthropic.com/en/docs/claude-code/overview - Claude Code overview
- https://www.anthropic.com/engineering/claude-code-best-practices - Best practices

**Notes:**
- **Settings Hierarchy:** Managed policies > CLI args > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`
- **Global Settings:** `~/.claude/settings.json` (user-level, applies across all projects)
- **Global Commands:** `~/.claude/commands/` (personal commands available everywhere)
- **Global Agents:** `~/.claude/agents/` (user-level subagents)
- **Permissions:** Support `allow`, `ask`, `deny` modes with pattern matching
- **Hooks:** Before/after tool use command execution
- **Environment Variables:** All settings can be set via env vars
- **Command Namespacing:** Subdirectories in `.claude/commands/` create namespaced commands
- **Subagent Invocation:** Coordinator model analyzes context and routes to appropriate subagent
- **Tool Inheritance:** Subagents can inherit all tools (including MCP) or specify restricted tool sets
- **Model Options:** sonnet, opus, haiku, or inherit from main conversation
- **Enterprise Deployment:** Managed policies can be deployed to system-level paths
- **L3 Classification:** The subagent system qualifies for L3 due to its coordinator-based multi-agent routing with role specialization, though it differs from explicit workflow orchestration frameworks
