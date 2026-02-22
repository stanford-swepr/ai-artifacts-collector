# Official OpenHands Artifacts by Maturity Level

**Note:** OpenHands (formerly OpenDevin) is an open-source platform for AI software development agents.

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of OpenHands without structured persistence or version control of configuration.

## L1 - Grounded Prompting

### `config.toml`
- **Path:** Repository base directory (default) or configurable via `--config-file`
- **Format:** TOML
- **Purpose:** Project-specific configuration for core settings, LLM, security, sandbox, and agent options
- **Scope:** Project-level
- **Status:** Stable
- **Sections:** `[core]`, `[llm]`, `[security]`, `[sandbox]`, `[agent]`, `[agent.<agent_name>]`
- **Template:** Available at `config.template.toml` in official repository
- **Note:** Can be overridden by environment variables (e.g., `LLM_<OPTION>` for LLM settings)

### `.openhands/microagents/repo.md`
- **Path:** `.openhands/microagents/repo.md`
- **Format:** Markdown
- **Purpose:** General repository microagent providing guidelines for OpenHands to work effectively with the repository
- **Scope:** Project-level
- **Status:** Stable
- **Loading:** Always loaded as part of the context

### `.openhands/microagents/*.md`
- **Path:** `.openhands/microagents/` directory
- **Format:** Markdown
- **Purpose:** Custom microagents with specific instructions for different tasks or workflows
- **Scope:** Project-level
- **Status:** Stable
- **Naming:** `<microagent_name>.md` files
- **Use Cases:** Trigger-based microagents for specific scenarios

## L2 - Agent-Augmented Dev

### OpenHands Agent System
- **Path:** Configured via `config.toml` and microagents
- **Format:** TOML configuration + Markdown microagents
- **Purpose:** Autonomous software development agent with repository context
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Code generation, bug fixing, repository exploration, task execution
- **Configuration:** `[agent]` and `[agent.<agent_name>]` sections in config.toml

### Microagent-Based Workflows
- **Path:** `.openhands/microagents/*.md`
- **Format:** Markdown with task-specific instructions
- **Purpose:** Define specialized workflows and behaviors for different scenarios
- **Scope:** Project-level
- **Status:** Stable
- **Features:** Trigger-based activation, context-specific instructions, always-loaded repo guidelines

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While OpenHands provides an autonomous agent system with microagent support for specialized instructions, it operates as a single agent with modular prompting (microagents) rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

Microagents provide contextual instructions but do not constitute a multi-agent orchestration framework with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 3     | `config.toml`, `.openhands/microagents/repo.md`, `.openhands/microagents/*.md` | Static Instructions |
| L2    | 2     | `config.toml` (agent settings), `.openhands/microagents/*.md` (workflows) | Executable Workflows |
| L3    | 0     | No official artifacts (single agent with microagent prompts, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://docs.openhands.dev/ - Main documentation
- https://docs.all-hands.dev/modules/usage/configuration-options - Configuration options
- https://docs.all-hands.dev/modules/usage/prompting/microagents-overview - Microagents overview
- https://docs.all-hands.dev/modules/usage/prompting/microagents-repo - General repository microagents
- https://github.com/All-Hands-AI/OpenHands - Official GitHub repository
- https://github.com/All-Hands-AI/OpenHands/blob/main/config.template.toml - Configuration template
- https://github.com/All-Hands-AI/OpenHands/blob/main/.openhands/microagents/repo.md - Example repo microagent

**Notes:**
- **Configuration File Location:** Repository base directory by default, configurable via `--config-file`
- **Environment Variables:** All LLM settings can be set as `LLM_<OPTION>` (uppercase)
- **Configuration Sections:**
  - `[core]` - Core OpenHands settings
  - `[llm]` - LLM model and API configuration
  - `[security]` - Security settings for agent execution
  - `[sandbox]` - Sandbox environment configuration
  - `[agent]` - Agent behavior settings
  - `[agent.<agent_name>]` - Agent-specific configurations
- **Microagents Directory:** `.openhands/microagents/` in repository root
- **Microagent Types:**
  - `repo.md` - Always-loaded general repository guidelines
  - `<name>.md` - Trigger-based microagents for specific scenarios
- **Workspace Configuration:** Can be set via `SANDBOX_VOLUMES` environment variable or deprecated `workspace_base` in config.toml
- **Running Modes:** CLI, headless, development, Docker
- **Template:** `config.template.toml` provides reference for all available options
- **Platform:** Open-source platform for AI software development agents
- **Formerly:** Previously known as OpenDevin
- **Microagent Loading:** General repository microagents always loaded; trigger-based microagents activated as needed
- **Customization:** Microagents allow repository-specific customization of agent behavior
