# Official GitHub Copilot X Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Copilot inline suggestions, chat, and edits without structured persistence or version control.

## L1 - Grounded Prompting

### `.github/copilot-instructions.md`
- **Path:** `.github/copilot-instructions.md`
- **Format:** Markdown
- **Purpose:** Repository-wide custom instructions for all Copilot requests
- **Scope:** Project-level, applies across entire repository
- **Status:** Stable

### `.github/instructions/*.instructions.md`
- **Path:** `.github/instructions/` directory
- **Format:** Markdown with YAML frontmatter
- **Purpose:** Path-specific custom instructions with glob pattern matching
- **Scope:** Project-level, scoped to specific file patterns via `applyTo` property
- **Status:** Stable
- **Frontmatter Properties:** `applyTo` (glob patterns), `excludeAgent` (optional: "code-review" or "coding-agent")

### `AGENTS.md`
- **Path:** Any directory (hierarchical, nearest file takes precedence)
- **Format:** Markdown
- **Purpose:** Agent-specific instructions, follows OpenAI agents.md specification
- **Scope:** Project-level with directory-scoped precedence
- **Status:** Stable
- **Reference:** https://github.com/openai/agents.md

### `CLAUDE.md` / `GEMINI.md`
- **Path:** Repository root
- **Format:** Markdown
- **Purpose:** Model-specific instructions for Claude or Gemini models
- **Scope:** Project-level
- **Status:** Stable

### `.github/prompts/*.prompt.md`
- **Path:** `.github/prompts/` directory
- **Format:** Markdown with `.prompt.md` extension
- **Purpose:** Reusable prompt templates for VS Code and JetBrains
- **Scope:** Project-level
- **Status:** Stable (requires `"chat.promptFiles": true` in workspace settings)

### `.vscode/settings.json`
- **Path:** `.vscode/settings.json`
- **Format:** JSON
- **Purpose:** Workspace-level Copilot configuration and settings
- **Scope:** Project-level (workspace)
- **Status:** Stable

## L2 - Agent-Augmented Dev

### Copilot Edits (Multi-File Editing)
- **Path:** Configuration via workspace settings and agent instructions
- **Format:** Defined through `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md`
- **Purpose:** Enable autonomous multi-file editing workflows with natural language prompts
- **Scope:** Project-level
- **Status:** Stable (Generally Available)

### Agent Mode Workflows
- **Path:** Configured via custom instructions files
- **Format:** Instructions in `.github/copilot-instructions.md` and `.github/instructions/*.instructions.md`
- **Purpose:** Autonomous coding agent that creates apps, refactors code, writes/runs tests, generates documentation
- **Scope:** Project-level
- **Status:** Stable (VS Code Stable and Insiders)
- **Features:** Autonomous context determination, multi-file edits, terminal command execution

### Coding Agent (GitHub Actions-based)
- **Path:** `copilot/*` branch prefix (agent-created branches)
- **Format:** GitHub Actions workflow in sandboxed environment
- **Purpose:** Autonomous SWE agent that works independently in background to complete tasks
- **Scope:** Repository-level
- **Status:** Stable (Copilot Pro, Pro+, Business, Enterprise)
- **Constraints:** Creates branches with `copilot/` prefix, requires PR review approval, includes automated CodeQL/secret scanning

## L3 - Agentic Orchestration

### Code Review Agent (Automated PR Reviews)
- **Path:** GitHub repository settings (branch rules)
- **Format:** GitHub Actions-based automated workflow
- **Purpose:** Multi-stage code review with planning, analysis, and issue detection
- **Scope:** Organization/repository-level
- **Status:** Stable
- **Configuration:** Repository branch rules with "Automatically request Copilot code review" option
- **Features:** Automatic review on PR creation, review on new pushes, multi-perspective analysis (planning, customization, deduplication)

**Note:** While the Code Review Agent provides automated multi-stage workflows, it operates as a single specialized agent rather than a coordinated multi-agent system with distinct roles (planner, coder, reviewer, tester) and explicit orchestration logic. However, it does qualify for L3 due to its automated workflow stages and systematic analysis approach within the code review domain.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 7     | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/prompts/*.prompt.md`, `.vscode/settings.json` | Static Instructions |
| L2    | 3     | `.github/copilot-instructions.md` (Edits workflows), `.github/instructions/*.instructions.md` (Agent Mode), `copilot/*` branches (Coding Agent) | Executable Workflows |
| L3    | 1     | Branch protection rules (Code Review Agent automation) | Multi-Agent Orchestration |

**Documentation Sources:**
- https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot - Custom instructions
- https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent - Coding agent
- https://docs.github.com/en/copilot/concepts/agents/code-review - Code review agent
- https://docs.github.com/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review - Automatic review configuration
- https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode - Agent mode introduction
- https://github.blog/changelog/2025-11-12-copilot-code-review-and-coding-agent-now-support-agent-specific-instructions/ - Agent-specific instructions (Nov 2025)
- https://github.com/openai/agents.md - AGENTS.md specification
- https://github.com/github/awesome-copilot - Community customizations
