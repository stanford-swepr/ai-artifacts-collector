# Official Google IDX (Firebase Studio) Artifacts by Maturity Level

**Note:** Project IDX is now part of Firebase Studio as of 2025.

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Gemini chat, code completion, and inline suggestions without structured persistence or version control.

## L1 - Grounded Prompting

### `.idx/airules.md`
- **Path:** `.idx/airules.md`
- **Format:** Markdown
- **Purpose:** Primary rules file for Gemini in Firebase chat; provides project-specific instructions, coding standards, persona definitions
- **Scope:** Project-level (workspace)
- **Status:** Stable
- **Priority:** Highest priority for Gemini in Firebase chat

### `GEMINI.md`
- **Path:** Project root
- **Format:** Markdown
- **Purpose:** Rules file for Gemini CLI; fallback for Gemini in Firebase if `.idx/airules.md` doesn't exist
- **Scope:** Project-level
- **Status:** Stable
- **Content:** Project standards, coding style, persona definitions, technology preferences

### `.gemini/styleguide.md`
- **Path:** `.gemini/styleguide.md`
- **Format:** Markdown
- **Purpose:** Alternative rules file (lower precedence than airules.md and GEMINI.md)
- **Scope:** Project-level
- **Status:** Stable

### `AGENTS.md`
- **Path:** Project root
- **Format:** Markdown
- **Purpose:** Alternative rules file (recognized by Gemini in Firebase)
- **Scope:** Project-level
- **Status:** Stable

### `.cursorrules`
- **Path:** Project root
- **Format:** Plain text/Markdown
- **Purpose:** Alternative rules file (lowest precedence, compatibility with Cursor IDE)
- **Scope:** Project-level
- **Status:** Stable

### `.aiexclude`
- **Path:** Any directory level
- **Format:** Plain text (similar to `.gitignore` syntax, with limitations)
- **Purpose:** Control which files are hidden from Gemini (prevents indexing, chat assistance, code completion, inline editing)
- **Scope:** Directory and subdirectories
- **Status:** Stable
- **Limitations:** No negation patterns (`!` prefix not supported); empty file blocks all files in directory

### `.idx/dev.nix`
- **Path:** `.idx/dev.nix`
- **Format:** Nix language
- **Purpose:** Workspace environment configuration (packages, extensions, environment variables, lifecycle hooks, preview configuration)
- **Scope:** Project-level (workspace)
- **Status:** Stable
- **Options:** `packages`, `channel`, `env`, `idx.extensions`, `idx.workspace.onCreate`, `idx.workspace.onStart`, `idx.previews`, `services`

## L2 - Agent-Augmented Dev

### Gemini Agent Mode
- **Path:** Configured via `.idx/airules.md`, `GEMINI.md`, and other rules files
- **Format:** Markdown-based instructions
- **Purpose:** Step-by-step autonomous coding with approval for each change
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Multi-file edits, test writing, error fixing, refactoring with human approval gates

### Gemini Agent (Auto-run) Mode
- **Path:** Configured via `.idx/airules.md`, `GEMINI.md`, and other rules files
- **Format:** Markdown-based instructions
- **Purpose:** Fully autonomous coding across multiple files from single prompt
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Generate entire apps, add features, multi-file coding, test writing, error fixing, refactoring
- **Safety:** Requires permission before deleting files, running terminal commands, or using external tools

### MCP Server Configuration
- **Path:** Workspace settings (Firebase Studio)
- **Format:** IDE-managed configuration
- **Purpose:** Extend Gemini capabilities via Model Context Protocol servers
- **Scope:** Project-level (workspace)
- **Status:** Preview
- **Note:** Configuration is workspace-based, not stored as repository files

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Firebase Studio provides powerful autonomous agent modes (Agent and Agent Auto-run) with multi-step reasoning and execution capabilities, it operates as a single sophisticated agent rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

The agent modes provide autonomous multi-file coding, testing, and refactoring but lack the multi-agent orchestration framework with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 7     | `.idx/airules.md`, `GEMINI.md`, `.gemini/styleguide.md`, `AGENTS.md`, `.cursorrules`, `.aiexclude`, `.idx/dev.nix` | Static Instructions |
| L2    | 2     | `.idx/airules.md` (Agent Mode workflows), `.idx/airules.md` (Agent Auto-run workflows) | Executable Workflows |
| L3    | 0     | No official artifacts (single powerful agent, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://firebase.google.com/docs/studio/set-up-gemini - Configure Gemini (airules.md, GEMINI.md, .aiexclude)
- https://firebase.google.com/docs/studio/devnix-reference - dev.nix configuration reference
- https://firebase.google.com/docs/studio/ai-assistance - AI assistance overview
- https://firebase.google.com/docs/studio/idx-is-firebase-studio - IDX to Firebase Studio transition
- https://developers.googleblog.com/en/advancing-agentic-ai-development-with-firebase-studio/ - Agentic AI development
- https://firebase.blog/posts/2025/07/firebase-studio-gemini-cli/ - Gemini CLI integration
- https://firebase.google.com/docs/studio - Main Firebase Studio documentation

**Notes:**
- **Precedence Order for Rules Files:** `.idx/airules.md` > `GEMINI.md` > `.gemini/styleguide.md` > `AGENTS.md` > `.cursorrules`
- **Built-in Model:** Gemini 2.5 Pro (no API key required as of 2025)
- **Interaction Modes:** Ask Mode, Agent Mode (step-by-step with approval), Agent (Auto-run) Mode (fully autonomous)
- **MCP Support:** Preview feature for extending Gemini capabilities
- **Gemini CLI:** Integrated directly in Firebase Studio, uses `GEMINI.md` and `.gemini/settings.json`
