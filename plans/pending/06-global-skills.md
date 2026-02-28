# 06 — Global Claude Skills (git and github)

### Problem Statement
Create the two global skill definition files in `~/.claude/commands/` to provide `/git` and `/github` slash commands for all Claude Code projects.

### Prerequisites
None (skills are global and do not depend on project code)

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `~/.claude/commands/git.md` | Create | `/git` skill for smart git operations |
| `~/.claude/commands/github.md` | Create | `/github` skill for GitHub operations via `gh` CLI |

### Steps
1. Create the global commands directory by running `mkdir -p ~/.claude/commands/`.
   - **Success**: Directory exists at `~/.claude/commands/`.
2. Create `git.md` with the `/git` skill prompt. Include: interpretation of natural language git requests, safety rules (never force-push main/master, never `reset --hard` without confirmation), always show command before running, summarise output.
   - **Success**: File exists and contains the natural language interpretation and safety rules.
3. In `git.md`, specify supported operations: status, commit, branch, push, diff, log, stash.
   - **Success**: All seven operations are mentioned in the skill file.
4. Create `github.md` with the `/github` skill prompt. Include: operations via `gh` CLI, coverage of PRs (create/list/view/merge/checkout), issues, releases, and actions/CI.
   - **Success**: File exists and mentions all operation categories.
5. In `github.md`, describe the PR creation workflow: inspect commits, draft title and body, confirm with user, then create.
   - **Success**: The four-step PR creation workflow is documented.

### Edge Cases
- **Input**: Skill invocation with no arguments — skill should display available sub-commands or usage help.
- **Runtime**: `gh` CLI not installed — `/github` skill should detect this and advise the user to install it.
- **Environment**: `~/.claude/commands/` does not exist — step 1 creates it. If it already exists with other skills, new files must not overwrite them unless they share the same name.

### Acceptance Criteria
- `~/.claude/commands/git.md` exists and contains the `/git` skill definition.
- `~/.claude/commands/github.md` exists and contains the `/github` skill definition.
- The `git.md` skill includes safety rules against destructive operations.
- The `github.md` skill includes the PR creation workflow.
- Both files are valid markdown.

### Risks
- These are global files affecting all Claude Code projects, not just this one. Changes should be reviewed carefully.
- The `~/.claude/commands/` path is user-specific. If the coding agent runs as a different user, the path will differ.
- Existing files at these paths will be overwritten. If the user already has custom skills, they should be backed up.
