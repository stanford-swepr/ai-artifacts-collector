# Official GitHub Copilot CLI Artifacts by Maturity Level

**Note:** GitHub Copilot CLI is the standalone `copilot` command (replacing the deprecated `gh copilot` extension as of October 2025).

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Copilot CLI for command suggestions and explanations without structured persistence or version control.

## L1 - Grounded Prompting

### `.github/agents/*.md` or `.github/agents/*.agent.md`
- **Path:** `.github/agents/` directory (repository root)
- **Format:** Markdown with YAML frontmatter
- **Purpose:** Repository-level custom agent configurations defining specialized agent behaviors
- **Scope:** Project-level (repository)
- **Status:** Stable
- **Frontmatter Properties:** `name`, `description` (required), `target`, `tools`, `metadata`
- **File Extensions:** `.md` or `.agent.md`
- **Note:** Repository-level agents cannot configure MCP servers

### Custom Agent Instructions (Organization/Enterprise)
- **Path:** `{org}/.github/agents/` or `{org}/.github-private/agents/` (organization repositories)
- **Format:** Markdown with YAML frontmatter
- **Purpose:** Organization/enterprise-level custom agents with optional MCP server configuration
- **Scope:** Organization or enterprise-wide
- **Status:** Stable
- **Additional Properties:** `mcp-servers` (organization/enterprise only)
- **Note:** Can be stored in version control as organization-level configuration

## L2 - Agent-Augmented Dev

### Copilot CLI with Tool Permissions
- **Path:** Configuration via command-line flags and `~/.copilot/config.json`
- **Format:** Command-line flags and JSON configuration
- **Purpose:** Control tool access with approval tiers (per-command, session-level, permanent)
- **Scope:** User-level (global)
- **Status:** Stable
- **Tool Flags:** `--allow-all-tools`, `--allow-tool <pattern>`, `--deny-tool <pattern>`
- **Trusted Folders:** `~/.copilot/config.json` contains `trusted_folders` array
- **Note:** Configuration stored locally, not in repository

### Custom Agents with Specialized Tools
- **Path:** `.github/agents/*.md`
- **Format:** YAML frontmatter with `tools` property
- **Purpose:** Define specialized agents with specific tool access
- **Scope:** Project-level, organization-level, or enterprise-level
- **Status:** Stable
- **Tool Control:** Enable all (`["*"]`), specific tools, disable all (`[]`), or MCP server tools
- **Available Tools:** `shell`, `read`, `edit`, `search`, `custom-agent`, `web`, `todo`

### MCP Server Configuration (Organization/Enterprise)
- **Path:** Organization/enterprise agent configuration files with `mcp-servers` property
- **Format:** YAML within agent configuration
- **Purpose:** Connect additional MCP servers to custom agents
- **Scope:** Organization or enterprise-level
- **Status:** Stable
- **Storage:** `~/.copilot/mcp-config.json` (local), defined in organization agents (version-controlled)
- **Note:** Repository agents cannot configure MCP servers; organization/enterprise agents can

### Copilot Coding Agent Delegation
- **Path:** Invoked via `/agent` slash command in Copilot CLI
- **Format:** Interactive CLI workflow
- **Purpose:** Delegate complex coding tasks to autonomous coding agent
- **Scope:** Session-based
- **Status:** Stable
- **Capabilities:** Multi-file editing, test execution, autonomous task completion

## L3 - Agentic Orchestration

### Custom Agent Orchestration System
- **Path:** Configured via `.github/agents/*.md` with cross-agent invocation
- **Format:** YAML frontmatter defining agent roles and tool access
- **Purpose:** Multi-agent system where agents can invoke other custom agents
- **Scope:** Project-level, organization-level, or enterprise-level
- **Status:** Stable
- **Orchestration Features:**
  - Custom agents available as tools to other agents via `custom-agent` tool
  - Model starts new agentic loop using relevant custom agent when necessary
  - Explicit agent invocation via `/agent` slash command
  - Tool-based delegation with controlled access patterns
- **Configuration Hierarchy:** Repository → Organization → Enterprise → VS Code (lowest wins in conflicts)
- **Versioning:** Based on Git commit SHAs for consistency within pull requests
- **Note:** While this provides multi-agent capabilities, it uses a tool-based invocation model rather than explicit workflow orchestration with stage management

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 2     | `.github/agents/*.md`, `{org}/.github/agents/*.md` (organization) | Static Instructions |
| L2    | 2     | `.github/agents/*.md` (with tools), `{org}/.github/agents/*.md` (with mcp-servers) | Executable Workflows |
| L3    | 1     | `.github/agents/*.md` (custom-agent tool orchestration) | Multi-Agent Orchestration |

**Documentation Sources:**
- https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli - About Copilot CLI
- https://docs.github.com/en/copilot/reference/custom-agents-configuration - Custom agents configuration reference
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli - Using Copilot CLI
- https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/extending-copilot-coding-agent-with-mcp - MCP extension guide
- https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents - Creating custom agents
- https://github.blog/changelog/2025-10-28-custom-agents-for-github-copilot/ - Custom agents announcement
- https://github.com/github/copilot-cli - Official GitHub repository

**Notes:**
- **Deprecation:** Old `gh copilot` extension deprecated October 25, 2025; use standalone `copilot` command
- **Global Configuration:** `~/.copilot/config.json` (trusted folders), `~/.copilot/mcp-config.json` (MCP servers)
- **Global Agents:** `~/.copilot/agents/` (user-level custom agents)
- **Tool Patterns:** Glob patterns supported (e.g., `--deny-tool 'shell(rm)'`, `--allow-tool 'shell'`)
- **Approval Tiers:** Per-command, session-level, permanent (via `--allow-all-tools` or `--allow-tool`)
- **MCP Restrictions:** Repository agents cannot configure MCP servers; only org/enterprise agents can
- **Configuration Hierarchy:** Repository-level agents have lowest priority in conflicts
- **Model Selection:** `/model` slash command to switch models (Claude Sonnet 4.5 available in preview)
- **Built-in MCP:** GitHub MCP server pre-configured for GitHub.com interactions
- **Cross-Platform:** macOS, Linux, Windows (via WSL)
- **L3 Classification:** Qualifies for L3 due to custom-agent tool enabling multi-agent invocation and orchestration
- **Versioning:** Custom agents versioned by Git commit SHA for pull request consistency
