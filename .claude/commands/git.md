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
