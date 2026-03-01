# Sub-plan 03: Create the 2 Global Skill Files

### Problem Statement
Create the 2 global skill files (`git.md` and `github.md`) in `~/.claude/commands/` so that the `/git` and `/github` slash commands are available in any Claude Code session, providing safe, natural-language-driven git and GitHub operations.

### Prerequisites
None (can run in parallel with `01-requirements-txt.md` and `02-claude-agents.md`).

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `~/.claude/commands/git.md` | Create | `/git` skill for natural-language git operations |
| `~/.claude/commands/github.md` | Create | `/github` skill for GitHub operations via `gh` CLI |

### Steps

1. **Create the `~/.claude/commands/` directory** by running `mkdir -p ~/.claude/commands/`. This directory does not exist by default; `mkdir -p` is safe to run even if it already exists.
   - Success: `ls ~/.claude/commands/` exits with code 0.

2. **Create `~/.claude/commands/git.md`** with the following content:
   ```markdown
   # /git — Smart Git Operations

   Interpret the user's natural language git request, construct the appropriate git command(s), show them to the user, execute them, and summarise the output.

   ## Covered Operations
   - **status**: Show working tree status (`git status -sb`).
   - **commit**: Stage specified files and commit with a provided or generated message (`git add <files> && git commit -m "..."`).
   - **branch**: List, create, switch, or delete branches.
   - **push**: Push the current branch to its upstream remote.
   - **pull**: Pull (rebase preferred: `git pull --rebase`) the current branch.
   - **diff**: Show unstaged or staged changes (`git diff` / `git diff --cached`).
   - **log**: Show recent commits (`git log --oneline -15`).
   - **stash**: Save (`git stash push -m "..."`) or restore (`git stash pop`) uncommitted changes.

   ## Safety Rules
   1. **Never force-push `main` or `master`**: If the user requests `git push --force` targeting `main` or `master`, refuse and explain the risk. Offer to push to a different branch instead.
   2. **Never `reset --hard` without confirmation**: Before running any `git reset --hard`, print the exact command and ask the user to confirm ("Type YES to continue"). Do not proceed unless the user confirms.
   3. **Never run `git clean -f` without confirmation**: Same confirmation requirement as `reset --hard`.
   4. **Always show the command first**: Print the exact git command(s) you will run before executing them.
   5. **Summarise after execution**: After each command, summarise what changed (e.g., "Committed 3 files to branch `feature/add-cli` with message 'Add argparse CLI'").

   ## Workflow
   1. Parse the user's request to identify the git operation and parameters.
   2. Construct the minimal, safe git command(s) needed.
   3. Display the command(s) to the user.
   4. Execute the command(s) using the Bash tool.
   5. Summarise the output in plain language.
   6. If the command fails, explain the error and suggest a fix.

   ## Examples
   - "commit my changes with message 'fix video ID parser'" → `git add -A && git commit -m "fix video ID parser"`
   - "push this branch" → `git push -u origin <current-branch>`
   - "show me what changed since yesterday" → `git log --oneline --since="1 day ago"`
   - "stash my work in progress" → `git stash push -m "wip: <description>"`
   ```
   - Success: file exists and `wc -l ~/.claude/commands/git.md` shows at least 30 lines.

3. **Create `~/.claude/commands/github.md`** with the following content:
   ```markdown
   # /github — GitHub Operations via `gh` CLI

   Perform GitHub operations using the `gh` CLI tool. Interpret the user's natural language request, construct the appropriate `gh` command(s), show them to the user, execute them, and summarise the result.

   ## Prerequisites
   - The `gh` CLI must be installed and authenticated (`gh auth status` must succeed).
   - If `gh` is not authenticated, instruct the user to run `gh auth login` first.

   ## Covered Operations

   ### Pull Requests
   - **Create PR**: Follow the workflow below.
   - **List PRs**: `gh pr list` (add `--state open` / `--state closed` / `--state merged` as needed).
   - **View PR**: `gh pr view <number>` (shows title, body, status, reviewers, checks).
   - **Merge PR**: `gh pr merge <number> --squash` (default) or `--merge` / `--rebase`.
   - **Checkout PR locally**: `gh pr checkout <number>`.

   ### Issues
   - **Create issue**: `gh issue create --title "..." --body "..."`.
   - **List issues**: `gh issue list`.
   - **View issue**: `gh issue view <number>`.
   - **Close issue**: `gh issue close <number>`.

   ### Releases
   - **Create release**: `gh release create <tag> --title "..." --notes "..."`.
   - **List releases**: `gh release list`.

   ### Actions / CI
   - **View workflow runs**: `gh run list`.
   - **View specific run**: `gh run view <run-id>`.
   - **Watch a run**: `gh run watch <run-id>`.

   ## PR Creation Workflow
   When the user asks to create a pull request, follow these steps exactly:
   1. Run `git log origin/main..HEAD --oneline` to inspect commits on the current branch.
   2. Draft a PR title (≤ 70 characters) and body (Markdown with Summary and Test Plan sections).
   3. Show the draft title and body to the user and ask for confirmation before creating.
   4. If the user confirms, run `gh pr create --title "..." --body "..."`.
   5. Report the PR URL from the command output.

   ## Safety Rules
   - **Never merge to `main` without confirmation**: Before running `gh pr merge` targeting `main` or `master`, show the merge command and ask the user to confirm.
   - **Always show the command first**: Print the exact `gh` command before executing it.
   - **Summarise after execution**: Report the result in plain language (e.g., "PR #42 created: https://github.com/owner/repo/pull/42").

   ## Error Handling
   - If `gh` is not installed: print "The `gh` CLI is not installed. Install it from https://cli.github.com/ and authenticate with `gh auth login`."
   - If a command fails with an API error: print the full error message and suggest the most likely fix.
   ```
   - Success: file exists and `wc -l ~/.claude/commands/github.md` shows at least 40 lines.

4. **Verify both files exist** by running `ls -la ~/.claude/commands/`:
   - Success: output lists both `git.md` and `github.md`.

5. **Confirm `git.md` contains the safety rules** by searching for "Never force-push" in the file:
   - Success: the phrase appears in `~/.claude/commands/git.md`.

6. **Confirm `github.md` contains the PR creation workflow** by searching for "PR Creation Workflow":
   - Success: the phrase appears in `~/.claude/commands/github.md`.

### Edge Cases

- **Input**: `~/.claude/commands/` already exists with old versions of these files — overwrite them unconditionally to ensure the content matches this sub-plan.
- **Input**: The user's home directory is set to an unexpected path (e.g., `/root`) — use `$HOME` or `~` expansion consistently; do not hard-code `/home/oniwa/`.
- **Runtime**: `mkdir -p ~/.claude/commands/` fails because a file named `.claude` (not a directory) already exists at `~/.claude` — inspect the error, remove or rename the conflicting file, and retry.
- **Runtime**: Disk full when writing skill files — write will fail with `OSError`; free space and retry.
- **Environment**: The user does not have `gh` installed — `github.md` explicitly documents this condition and instructs the user to install and authenticate `gh`. The skill file itself is valid even without `gh` present.
- **Environment**: File permissions on `~/.claude/commands/` are too restrictive — run `chmod u+rw ~/.claude/commands/*.md` after creation to ensure the files are readable.

### Acceptance Criteria

- `~/.claude/commands/` directory exists.
- `~/.claude/commands/git.md` exists and contains:
  - At least 6 covered operation descriptions (status, commit, branch, push, pull, diff, log, stash).
  - All 5 safety rules (no force-push to main/master, no `reset --hard` without confirmation, no `clean -f` without confirmation, show command first, summarise after).
- `~/.claude/commands/github.md` exists and contains:
  - PR operations (create, list, view, merge, checkout).
  - Issue operations (create, list, view, close).
  - The 5-step PR creation workflow.
  - Safety rules (confirm before merging to main, show command first).
- Both files have meaningful, readable system prompts of at least 30 lines each.

### Risks

- **Assumption**: Claude Code loads global skills from `~/.claude/commands/`. If a future version of Claude Code changes this path, the skill files will not be picked up automatically. Check the Claude Code release notes before upgrading.
- **`gh` CLI dependency**: `github.md` relies on the `gh` CLI being installed and authenticated. The file documents this prerequisite, but a team member who does not have `gh` installed will not be able to use the `/github` skill.
- **Open question**: Should the skills include a `tools:` YAML front matter block (like agent files)? As of the current Claude Code version, global skills do not use YAML front matter — they are plain Markdown prompts. If this changes, update the files accordingly.
