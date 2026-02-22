# Official Cursor Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal AI use through Cursor's chat and Composer without structured persistence or version control.

## L1 - Grounded Prompting

### `.cursor/rules/*.mdc`
- **Path:** `.cursor/rules/` directory, nested in subdirectories as needed
- **Format:** MDC (Markdown with YAML frontmatter metadata)
- **Purpose:** Version-controlled project rules for AI behavior customization
- **Scope:** Project-level, scoped to codebase and nested subdirectories
- **Status:** Stable, recommended approach
- **Metadata Properties:** `description`, `globs`, `alwaysApply`
- **Rule Types:** Always Apply, Apply Intelligently, Apply to Specific Files, Apply Manually (via @-mentions)

### `.cursorrules`
- **Path:** Project root
- **Format:** Plain text/Markdown
- **Purpose:** Legacy project-wide AI rules configuration
- **Scope:** Project-level
- **Status:** Deprecated, migration to `.cursor/rules/*.mdc` recommended

### `AGENTS.md`
- **Path:** Project root and subdirectories
- **Format:** Plain Markdown (no metadata support)
- **Purpose:** Simple alternative to structured `.cursor/rules` for defining AI behavior
- **Scope:** Project-level with hierarchical application from subdirectories
- **Status:** Stable, simplified option without MDC metadata

## L2 - Agent-Augmented Dev

### Agent Mode Configuration (via Rules)
- **Path:** `.cursor/rules/*.mdc` with agent-specific instructions
- **Format:** MDC files containing autonomous task instructions
- **Purpose:** Define autonomous coding tasks, test execution workflows, and verification procedures
- **Scope:** Project-level
- **Status:** Stable
- **Features:** Supports web search, terminal command execution (Yolo mode), autonomous code exploration

### Yolo Mode Workflows (defined in Rules)
- **Path:** Embedded in `.cursor/rules/*.mdc` files
- **Format:** MDC with task instructions and verification steps
- **Purpose:** Enable autonomous terminal command execution for test suites and validation
- **Scope:** Project-level
- **Status:** Stable

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

Cursor's Agent mode and Composer provide autonomous multi-step workflows but do not include code-development-specific multi-agent orchestration with specialized role coordination, task dependency management, or workflow state management that can be version-controlled in the repository.

The Agent mode operates as a single autonomous agent with multiple tools rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and orchestration logic.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 3     | `.cursor/rules/*.mdc`, `.cursorrules` (deprecated), `AGENTS.md` | Static Instructions |
| L2    | 2     | `.cursor/rules/*.mdc` (Agent Mode workflows), `.cursor/rules/*.mdc` (Yolo Mode execution) | Executable Workflows |
| L3    | 0     | No official artifacts (lacks multi-agent orchestration framework) | N/A |

**Documentation Sources:**
- https://cursor.com/docs/context/rules - Official Rules documentation
- https://docs.cursor.com/agent - Agent Mode documentation
- https://docs.cursor.com/composer - Composer documentation
- https://cursordocs.com/en/docs/beta/notepads - Notepads (beta, not repository-stored)
- https://github.com/PatrickJS/awesome-cursorrules - Community examples
- https://cursor.com/changelog - Official changelog

**Note:** Notepads are currently in beta and are NOT stored in the repository, thus excluded from this analysis per requirements. Team Rules (enterprise feature) are managed via Cursor dashboard and not stored in code repositories.
