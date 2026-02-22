# Official JetBrains AI Assistant Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of AI Assistant inline suggestions, chat, and code generation without structured persistence or version control.

## L1 - Grounded Prompting

### `.aiignore`
- **Path:** Project root
- **Format:** Plain text (same syntax as `.gitignore`)
- **Purpose:** Restrict AI Assistant from processing specific files or folders
- **Scope:** Project-level
- **Status:** Stable
- **Alternative Files:** `.cursorignore`, `.codeiumignore`, `.aiexclude` (also supported if in project root)

### `.junie/guidelines.md`
- **Path:** `.junie/guidelines.md` (project root directory)
- **Format:** Markdown
- **Purpose:** Define coding standards, technology specifications, and best practices for Junie AI agent
- **Scope:** Project-level, version-controlled
- **Status:** Stable
- **Content Types:** Technology specifications, code standards, naming conventions, code examples, anti-patterns
- **Creation:** Manual editing or automated generation via Junie

### Custom Prompts (IDE Settings)
- **Path:** IDE settings (Tools | AI Assistant | Prompt Library)
- **Format:** IDE-managed configuration
- **Purpose:** Custom prompts for specific scenarios (commit messages, code generation, etc.)
- **Scope:** User-level (not repository-stored)
- **Status:** Stable
- **Note:** Not stored in repository, managed through IDE settings

## L2 - Agent-Augmented Dev

### Junie AI Agent Configuration
- **Path:** Configured via `.junie/guidelines.md`
- **Format:** Markdown-based guidelines
- **Purpose:** Autonomous AI agent for delegated coding tasks
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Project exploration, code writing with context awareness, test execution, autonomous multi-step operations (refactoring, feature generation, bug fixes)
- **Performance:** 53.6% task completion on SWEBench Verified

### AI Assistant Agent Mode
- **Path:** IDE-based configuration (no repository artifacts)
- **Format:** IDE settings
- **Purpose:** Enable autonomous complex activities (implementing fixes, refactoring, test generation)
- **Scope:** Project-level context
- **Status:** Stable
- **Supported Agents:** Claude Agent (via Anthropic SDK), GitHub Copilot Agent Mode (preview)

### MCP Server Configuration (Project-Level)
- **Path:** IDE settings with project-level scope option
- **Format:** IDE-managed configuration (Settings | Tools | AI Assistant | Model Context Protocol)
- **Purpose:** Connect external tools and data sources to AI Assistant via Model Context Protocol
- **Scope:** Can be configured as global or project-level
- **Status:** Stable (since version 2025.2)
- **Configuration Parameters:** Name, Command, Arguments, Environment Variables, Working Directory
- **Note:** While MCP servers can be configured at project level, the configuration itself is stored in IDE settings, not as repository files

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While JetBrains offers multiple AI agents (Junie, Claude Agent, Copilot Agent Mode), these operate as independent autonomous agents rather than a coordinated multi-agent system with specialized roles and explicit orchestration logic for code development workflows.

Each agent works autonomously on delegated tasks but lacks the multi-agent orchestration framework with role specialization (planner, coder, reviewer, tester) and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 2     | `.aiignore`, `.junie/guidelines.md` | Static Instructions |
| L2    | 1     | `.junie/guidelines.md` (Junie AI Agent workflows) | Executable Workflows |
| L3    | 0     | No official artifacts (independent agents, not orchestrated multi-agent system) | N/A |

**Documentation Sources:**
- https://www.jetbrains.com/help/ai-assistant/disable-ai-assistant.html - .aiignore configuration
- https://www.jetbrains.com/help/junie/customize-guidelines.html - Junie guidelines
- https://www.jetbrains.com/help/junie/get-started-with-junie.html - Junie getting started
- https://github.com/JetBrains/junie-guidelines - Official Junie guidelines repository
- https://www.jetbrains.com/help/ai-assistant/prompt-library.html - Prompt library
- https://www.jetbrains.com/help/ai-assistant/mcp.html - Model Context Protocol
- https://www.jetbrains.com/help/ai-assistant/configure-an-mcp-server.html - MCP server configuration
- https://blog.jetbrains.com/ai/2025/09/introducing-claude-agent-in-jetbrains-ides/ - Claude Agent announcement
- https://www.jetbrains.com/junie/ - Junie AI agent overview
- https://blog.jetbrains.com/blog/2025/04/16/jetbrains-ides-go-ai/ - JetBrains AI announcement

**Notes:**
- Custom prompts are stored in IDE settings, not in repository
- MCP server configurations can be project-scoped but are managed through IDE settings rather than repository files
- Alternative ignore files (`.cursorignore`, `.codeiumignore`, `.aiexclude`) are supported if present in project root
