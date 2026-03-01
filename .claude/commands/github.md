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
