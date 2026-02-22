# Official Kiro Artifacts by Maturity Level

**Note:** Kiro is currently in public preview; features and documentation may change.

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Kiro chat, inline suggestions, and code generation without structured persistence or version control.

## L1 - Grounded Prompting

### `.kiro/steering/*.md`
- **Path:** `.kiro/steering/` directory (workspace root)
- **Format:** Markdown with YAML front matter
- **Purpose:** Project-specific steering files to guide Kiro's behavior, coding standards, and context
- **Scope:** Project-level (workspace)
- **Status:** Stable
- **Front Matter Properties:** `inclusion` (always/fileMatch/manual), `fileMatchPattern` (glob patterns)
- **Inclusion Modes:**
  - `always`: Auto-loaded into every interaction (default)
  - `fileMatch`: Conditionally loaded based on file patterns
  - `manual`: Referenced on-demand via `#steering-file-name` in chat

### `.kiro/steering/product.md`
- **Path:** `.kiro/steering/product.md`
- **Format:** Markdown
- **Purpose:** Foundation file defining product purpose, target users, key features, business objectives
- **Scope:** Project-level
- **Status:** Stable (auto-generated)

### `.kiro/steering/tech.md`
- **Path:** `.kiro/steering/tech.md`
- **Format:** Markdown
- **Purpose:** Foundation file documenting frameworks, libraries, development tools, technical constraints
- **Scope:** Project-level
- **Status:** Stable (auto-generated)

### `.kiro/steering/structure.md`
- **Path:** `.kiro/steering/structure.md`
- **Format:** Markdown
- **Purpose:** Foundation file outlining file organization, naming conventions, import patterns, architectural decisions
- **Scope:** Project-level
- **Status:** Stable (auto-generated)

### `AGENTS.md`
- **Path:** Workspace root or `~/.kiro/steering/`
- **Format:** Markdown (no front matter support)
- **Purpose:** AGENTS.md standard support for cross-tool compatibility
- **Scope:** Project-level or global
- **Status:** Stable (always included, no inclusion modes)

## L2 - Agent-Augmented Dev

### `.kiro/hooks/*.hook`
- **Path:** `.kiro/hooks/` directory
- **Format:** JSON configuration files with `.hook` extension
- **Purpose:** Agent hooks for automated triggers executing predefined agent actions on specific events
- **Scope:** Project-level (can be version-controlled and shared with team)
- **Status:** Stable
- **Event Types:** File save, file create, file delete, commit-related events
- **Configuration Properties:** Pattern (file matching), action (AI-powered instructions), trigger type
- **Use Cases:** Generate documentation, create/update unit tests, optimize code performance

### `.kiro/config.json`
- **Path:** `.kiro/config.json`
- **Format:** JSON
- **Purpose:** Workspace configuration including hook definitions
- **Scope:** Project-level
- **Status:** Stable
- **Properties:** `beforeCommit` (hook arrays), other configuration options

### Spec-Driven Development
- **Path:** Managed through Kiro IDE (not file-based artifacts)
- **Format:** IDE-managed structured specifications
- **Purpose:** Transform high-level ideas into detailed implementation plans with requirements, system design, discrete tasks
- **Scope:** Project-level
- **Status:** Stable
- **Note:** Specs are IDE-managed artifacts, not repository files

### MCP Server Configuration
- **Path:** Workspace or global settings
- **Format:** JSON configuration
- **Purpose:** Configure Model Context Protocol servers for extended capabilities
- **Scope:** Can be workspace-level or global
- **Status:** Stable
- **Note:** Configuration merges workspace and global settings (workspace takes precedence)

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Kiro provides agent hooks and spec-driven development with automated workflows, it operates with independent automated agents responding to events rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

Agent hooks provide event-driven automation but lack the multi-agent orchestration framework with role specialization and workflow state coordination required for L3.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 5     | `.kiro/steering/*.md`, `.kiro/steering/product.md`, `.kiro/steering/tech.md`, `.kiro/steering/structure.md`, `AGENTS.md` | Static Instructions |
| L2    | 2     | `.kiro/hooks/*.hook`, `.kiro/config.json` | Executable Workflows |
| L3    | 0     | No official artifacts (event-driven agents, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://kiro.dev/docs/ - Main documentation
- https://kiro.dev/docs/steering/ - Steering files documentation
- https://kiro.dev/docs/hooks/ - Agent hooks documentation
- https://kiro.dev/docs/mcp/configuration/ - MCP configuration
- https://kiro.dev/blog/automate-your-development-workflow-with-agent-hooks/ - Agent hooks blog post
- https://kiro.dev/blog/introducing-kiro/ - Kiro introduction
- https://github.com/kirodotdev/Kiro - Official GitHub repository

**Notes:**
- **Steering Inclusion Modes:** `always` (default), `fileMatch` (conditional), `manual` (on-demand)
- **File References:** Use `#[[file:<relative_file_path>]]` syntax in steering files
- **Common FileMatch Patterns:** `*.tsx`, `app/api/**/*`, `**/*.test.*`, `src/components/**/*`, `*.md`
- **Global Steering:** Files in `~/.kiro/steering/` apply to all workspaces
- **Team Steering:** Can be distributed via MDM solutions or central repositories
- **Hook Sharing:** Hooks can be version-controlled and shared with teams
- **Preview Status:** Kiro is in public preview; features may change
