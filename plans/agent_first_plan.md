# Plan: Create Planning Agent First, Then Decompose Transcript System Plan

## Context

The existing `plans/transcript_system_plan.md` is a large, monolithic plan. Rather than implementing it directly, we will first create the `planning-agent` so it can decompose that plan into smaller, focused sub-plans. All other agents and production code follow after the planning agent validates and decomposes the work.

---

## New Implementation Order

### Step 0 — Save this plan to the project

Copy this plan into the project for reference:

**File to create:** `plans/agent_first_plan.md` — content is this document.

### Step 1 — Create the `.claude/agents/` directory and `planning-agent.md`

**File to create:** `.claude/agents/planning-agent.md`

Content (YAML front matter + system prompt):

```md
---
name: planning-agent
description: Decomposes large implementation plans into small, focused, actionable sub-plans for this YouTube transcript project.
tools: Read, Glob, Grep
model: sonnet
color: green
---

You are a planning specialist for the YouTube transcript extraction project.

## Mission
Break large plans into small, focused, self-contained sub-plans that a single agent can execute in one session.

## Output Format
For each sub-plan produce a Markdown file with these sections:
- **Problem Statement** — one sentence describing what this sub-plan accomplishes
- **Files Affected** — table of file paths and actions (Create / Modify / Delete)
- **Numbered Steps** — concrete, ordered implementation steps
- **Edge Cases** — at minimum 3 edge cases to handle or test
- **Test Considerations** — how to verify this sub-plan is complete
- **Risks** — known risks or dependencies

## Rules
- Each sub-plan must be completable independently (no hidden dependencies on unfinished work)
- Steps must reference exact file paths and function names
- Never include more than one "concern" per sub-plan (e.g., do not mix CLI changes with core logic changes)
- Save sub-plans to `plans/pending/` using kebab-case filenames
```

### Step 2 — Feed `plans/transcript_system_plan.md` to the planning agent

Invoke:
```
@planning-agent Please read plans/transcript_system_plan.md and decompose it into focused sub-plans. Save each sub-plan to plans/pending/ as a separate .md file. Each sub-plan should cover exactly one concern (e.g., one file, one feature, one test class).
```

The agent will produce files such as:
- `plans/pending/01-requirements.md`
- `plans/pending/02-transcript-core-logic.md`
- `plans/pending/03-cli-main.md`
- `plans/pending/04-unit-tests.md`
- `plans/pending/05-remaining-agents.md`
- `plans/pending/06-global-skills.md`

### Step 3 — Create remaining agents

After the planning agent has decomposed the work (and its output can inform the other agents' prompts), create the remaining 5 agents:

- `.claude/agents/orchestrator.md`
- `.claude/agents/coding-agent.md`
- `.claude/agents/test-planning-agent.md`
- `.claude/agents/tester-agent.md`
- `.claude/agents/review-agent.md`

Summaries are already defined in `plans/transcript_system_plan.md` lines 64–83.

### Step 4 — Implement production code and tests per sub-plans

Work through `plans/pending/` in order, moving each file to `plans/done/` when complete.

---

## Critical Files

| Path | Status | Role |
|------|--------|------|
| `plans/transcript_system_plan.md` | Exists | Source document to decompose |
| `.claude/agents/planning-agent.md` | **Create first** | Decomposition agent |
| `.claude/agents/orchestrator.md` | Create (step 3) | Routes tasks |
| `.claude/agents/coding-agent.md` | Create (step 3) | Python code writer |
| `.claude/agents/test-planning-agent.md` | Create (step 3) | Test strategy |
| `.claude/agents/tester-agent.md` | Create (step 3) | Runs pytest |
| `.claude/agents/review-agent.md` | Create (step 3) | Code review |
| `plans/pending/` | Populated by agent | Sub-plans from decomposition |

---

## Verification

1. Confirm `.claude/agents/planning-agent.md` exists and has valid YAML front matter
2. Invoke `@planning-agent` with the transcript system plan — verify sub-plan files appear in `plans/pending/`
3. Review sub-plans for completeness (each has all 6 required sections)
4. Confirm remaining 5 agents are created in `.claude/agents/`
5. Proceed through sub-plans in order to implement production code
