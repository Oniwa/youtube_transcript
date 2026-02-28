# 05 — Claude Agent Definitions

### Problem Statement
Create the six project-local agent definition files in `.claude/agents/` to establish the agent-based development workflow for this project.

### Prerequisites
None (agent definitions are documentation and do not depend on production code, though logically they are created after the code structure is known)

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `.claude/agents/orchestrator.md` | Create | Routes tasks and coordinates other agents |
| `.claude/agents/coding-agent.md` | Create | Python code writing specialist |
| `.claude/agents/planning-agent.md` | Create | Feature plan and breakdown designer |
| `.claude/agents/test-planning-agent.md` | Create | Test strategy and test case designer |
| `.claude/agents/tester-agent.md` | Create | Pytest runner and results reporter |
| `.claude/agents/review-agent.md` | Create | Code quality and correctness reviewer |

### Steps
1. Ensure `.claude/agents/` directory exists by running `mkdir -p .claude/agents/`.
   - **Success**: Directory exists at `/home/oniwa/PycharmProjects/youtube_transcript/.claude/agents/`.
2. Create `orchestrator.md` with the routing rules: new feature -> planning -> test-planning -> coding -> tester -> review; bug fix -> planning -> coding -> tester -> review. Include the rule to always run review after non-trivial code changes.
   - **Success**: File exists and contains routing decision rules for both new features and bug fixes.
3. Create `coding-agent.md` with the Python 3.12 specialist prompt. Include rules: type hints on all functions, docstrings, no `print()` in `transcript.py`, no business logic in `main.py`, testable `main(argv)` signature, UTF-8 file writes.
   - **Success**: File exists and contains all six coding rules.
4. Create `planning-agent.md` with the structured plan format: Problem Statement, Files Affected, Numbered Steps, Edge Cases (minimum 3), Test Considerations, Risks.
   - **Success**: File exists and specifies all six sections of the plan format.
5. Create `test-planning-agent.md` with test strategy rules: 100% branch coverage on `extract_video_id`, all 4 API error types tested, no real network in unit tests, use `tmp_path` and `monkeypatch.chdir` for file I/O.
   - **Success**: File exists and contains all four testing rules.
6. Create `tester-agent.md` with instructions to run `.venv/bin/pytest`, report pass/fail/skip counts, diagnose failures (test bug vs production bug), flag coverage below 80%.
   - **Success**: File exists and contains test execution and reporting instructions.
7. Create `review-agent.md` with the checklist: correctness, security (no `eval`/`shell=True`, safe filenames), code quality (docstrings, type hints, PEP 8), robustness (empty transcript, disk full, missing output dir).
   - **Success**: File exists and contains all four checklist categories.

### Edge Cases
- **Input**: Agent prompt files must be valid markdown — avoid special characters that could break rendering.
- **Runtime**: `.claude/` directory may be gitignored — ensure `.claude/agents/` is tracked if intended.
- **Environment**: `.claude/agents/` directory may already exist with stale files — steps are idempotent (create or overwrite).

### Acceptance Criteria
- All six files exist in `.claude/agents/`.
- Each file contains a system prompt matching the summaries in the source plan.
- `orchestrator.md` includes routing rules for both "new feature" and "bug fix" workflows.
- `coding-agent.md` lists all six coding rules.
- `test-planning-agent.md` specifies coverage and mocking requirements.
- `review-agent.md` contains the four-category checklist.

### Risks
- Agent prompts are project-specific and may need tuning as the project evolves. These are initial versions based on the source plan.
- If `.claude/` is gitignored, agent files will not be version-controlled. Verify `.gitignore` does not exclude this directory.
