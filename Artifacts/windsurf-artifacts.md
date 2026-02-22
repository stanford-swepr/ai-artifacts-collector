# Official Windsurf Artifacts by Maturity Level

## L0 - Ad-Hoc AI Use

No official repository-stored artifacts at this level. Characterized by informal use of Cascade chat and code suggestions without structured persistence or version control.

## L1 - Grounded Prompting

### `.windsurf/rules/*.md`
- **Path:** `.windsurf/rules/` directory (workspace and subdirectories)
- **Format:** Markdown with GUI-wrapped editor
- **Purpose:** Workspace-specific rules to guide Cascade AI behavior
- **Scope:** Project-level, discovered from workspace, subdirectories, and up to git root
- **Status:** Stable
- **Character Limit:** 12,000 characters per file (combined limit with global rules)
- **Activation Modes:** Manual (@mention), Always On, Model Decision (natural language description), Glob pattern matching

### `global_rules.md`
- **Path:** User's home directory configuration (not repository-stored, but mentioned for completeness)
- **Format:** Markdown
- **Purpose:** Global rules applicable across all workspaces
- **Scope:** Global (user-level)
- **Status:** Stable
- **Note:** Not stored in repository, but takes priority in combined character limit

### `.windsurfrules`
- **Path:** Project root (community pattern)
- **Format:** Markdown
- **Purpose:** Legacy/alternative rules file
- **Scope:** Project-level
- **Status:** Community-adopted pattern (not officially documented but widely used)

## L2 - Agent-Augmented Dev

### `.windsurf/workflows/*.md`
- **Path:** `.windsurf/workflows/` directory (workspace and subdirectories)
- **Format:** Markdown with title, description, and step-by-step instructions
- **Purpose:** Define repeatable automated task sequences for Cascade agent
- **Scope:** Project-level, discovered from workspace, subdirectories, and up to git root
- **Status:** Stable
- **Character Limit:** 12,000 characters per file
- **Invocation:** Slash command format `/[workflow-name]`
- **Features:** Supports nested workflow calls, task automation (deployment, testing, formatting, dependency management)

### Cascade Agent Configuration (via Rules & Workflows)
- **Path:** Configured through `.windsurf/rules/*.md` and `.windsurf/workflows/*.md`
- **Format:** Markdown-based instructions
- **Purpose:** Enable autonomous coding tasks with deep contextual awareness
- **Scope:** Project-level
- **Status:** Stable
- **Capabilities:** Code and Chat modes, planning agent for long-term tasks, tracks edits/commands/terminal/clipboard for context

## L3 - Agentic Orchestration

**No official repository-stored artifacts exist at this level.**

While Windsurf Cascade includes a background planning agent that works alongside the main coding model, this represents a single autonomous agent with internal planning capabilities rather than a coordinated multi-agent system with specialized roles (planner, coder, reviewer, tester) and explicit orchestration logic for code development workflows.

The planning agent architecture enhances individual agent performance but does not constitute multi-agent orchestration as defined in L3 requirements.

## Summary Table

| Level | Count | Key Files | Artifact Nature |
|-------|-------|-----------|-----------------|
| L0    | 0     | None (ad-hoc usage) | N/A |
| L1    | 2     | `.windsurf/rules/*.md`, `.windsurfrules` (community pattern) | Static Instructions |
| L2    | 2     | `.windsurf/workflows/*.md`, `.windsurf/rules/*.md` (Cascade Agent automation) | Executable Workflows |
| L3    | 0     | No official artifacts (single agent with planning, not multi-agent orchestration) | N/A |

**Documentation Sources:**
- https://docs.windsurf.com/windsurf/cascade/workflows - Official Workflows documentation
- https://docs.windsurf.com/windsurf/cascade/memories - Memories and Rules documentation
- https://docs.windsurf.com/windsurf/cascade/cascade - Cascade overview
- https://windsurf.com/editor/directory - Official Rules Directory (examples)
- https://docs.windsurf.com/windsurf/getting-started - Getting Started guide
- https://windsurf.com/cascade - Cascade feature page
- https://github.com/Windsurf-Samples/cascade-customizations-catalog - Official customizations catalog

**Notes:**
- Memories are workspace-specific and not stored in repositories (excluded per requirements)
- Global rules are user-level configuration, not repository-stored
- Character limits: Rules files limited to 12,000 characters each; combined global + workspace rules cannot exceed 12,000 total
- Workflow files limited to 12,000 characters each
