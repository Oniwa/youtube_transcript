# CLAUDE.md — Project Rules for Claude Code

## Plan Implementation

- **Always delegate plan implementation to the orchestrator agent.** Never implement plans directly in the main conversation.
- Only plans in `plans/pending/` are eligible for implementation. Plans in `plans/needs_human_approval/` must not be touched until a human moves them to `plans/pending/`.
- The orchestrator is responsible for creating feature branches, coordinating specialist agents, and opening PRs. Do not perform any of those steps outside of the orchestrator.
