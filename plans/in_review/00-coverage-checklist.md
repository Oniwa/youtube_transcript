# Coverage Checklist

This file maps every item in `plans/transcript_system_plan.md` to the sub-plan that covers it.

## Production Code

| Source Plan Item | Sub-plan |
|-----------------|----------|
| `requirements.txt` — pin youtube-transcript-api==1.2.4 | `01-requirements-txt.md` |
| `transcript.py` — extract_video_id | `04-transcript-core-module.md` |
| `transcript.py` — fetch_transcript | `04-transcript-core-module.md` |
| `transcript.py` — save_transcript | `04-transcript-core-module.md` |
| `transcript.py` — get_transcript | `04-transcript-core-module.md` |
| `main.py` — argparse CLI with --output/-o and --lang/-l | `05-main-cli-entry-point.md` |
| `main.py` — main(argv=None) returns int | `05-main-cli-entry-point.md` |
| `main.py` — errors → stderr, output → stdout | `05-main-cli-entry-point.md` |
| `main.py` — default filename = <video_id>.txt | `05-main-cli-entry-point.md` |

## Tests

| Source Plan Item | Sub-plan |
|-----------------|----------|
| `tests/__init__.py` — empty | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestExtractVideoId | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestFetchTranscript | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestSaveTranscript | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestGetTranscript | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestMain | `06-test-suite-structure.md` |
| `tests/test_transcript.py` — TestIntegration | `06-test-suite-structure.md` |

## Agents

| Source Plan Item | Sub-plan |
|-----------------|----------|
| `.claude/agents/orchestrator.md` | `02-claude-agents.md` |
| `.claude/agents/coding-agent.md` | `02-claude-agents.md` |
| `.claude/agents/planning-agent.md` | Already exists (Step 1) — deferred |
| `.claude/agents/test-planning-agent.md` | `02-claude-agents.md` |
| `.claude/agents/tester-agent.md` | `02-claude-agents.md` |
| `.claude/agents/review-agent.md` | `02-claude-agents.md` |

## Global Skills

| Source Plan Item | Sub-plan |
|-----------------|----------|
| `~/.claude/commands/git.md` — /git skill | `03-global-skills.md` |
| `~/.claude/commands/github.md` — /github skill | `03-global-skills.md` |

## Deferred Items

| Item | Reason |
|------|--------|
| `.venv/bin/pip install -r requirements.txt` (runtime) | Covered as acceptance criterion in `01-requirements-txt.md`; not a separate sub-plan |
| Install pytest-cov | Covered in verification commands; not a separate sub-plan |
