# 00 — Coverage Checklist

This table maps every item from the source plan (`plans/transcript_system_plan.md`) to the sub-plan that covers it. Items intentionally deferred are listed at the bottom with reasons.

## Files to Create / Modify

| Source Plan Item | Sub-Plan | Status |
|-----------------|----------|--------|
| `requirements.txt` — Create, pin `youtube-transcript-api==1.2.4` | `01-requirements-txt.md` | Covered |
| `transcript.py` — Create, core logic module | `02-transcript-core-module.md` | Covered |
| `main.py` — Rewrite, CLI entry point | `03-main-cli-entry-point.md` | Covered |
| `tests/__init__.py` — Create (empty) | `04-test-suite-structure.md` | Covered |
| `tests/test_transcript.py` — Create, pytest suite | `04-test-suite-structure.md` | Covered (stubs only; implementation deferred to test-planning-agent) |
| `.claude/agents/orchestrator.md` | `05-claude-agents.md` | Covered |
| `.claude/agents/coding-agent.md` | `05-claude-agents.md` | Covered |
| `.claude/agents/planning-agent.md` | `05-claude-agents.md` | Covered |
| `.claude/agents/test-planning-agent.md` | `05-claude-agents.md` | Covered |
| `.claude/agents/tester-agent.md` | `05-claude-agents.md` | Covered |
| `.claude/agents/review-agent.md` | `05-claude-agents.md` | Covered |
| `~/.claude/commands/git.md` | `06-global-skills.md` | Covered |
| `~/.claude/commands/github.md` | `06-global-skills.md` | Covered |

## Implementation Steps

| Source Plan Step | Sub-Plan | Status |
|-----------------|----------|--------|
| 1. Create `requirements.txt` | `01-requirements-txt.md` | Covered |
| 2. Create `transcript.py` — `extract_video_id`, `fetch_transcript`, `save_transcript`, `get_transcript` | `02-transcript-core-module.md` | Covered |
| 3. Rewrite `main.py` — argparse CLI with `--output`/`-o` and `--lang`/`-l` | `03-main-cli-entry-point.md` | Covered |
| 4. Create `tests/__init__.py` | `04-test-suite-structure.md` | Covered |
| 5. Create `tests/test_transcript.py` — pytest classes and test stubs | `04-test-suite-structure.md` | Covered (stubs only) |
| 6. Install dependencies | `01-requirements-txt.md` | Covered |
| 7. Run tests | `04-test-suite-structure.md` | Covered (verification step) |
| 8. Create `.claude/agents/` and write 6 agent files | `05-claude-agents.md` | Covered |
| 9. Create `~/.claude/commands/` and write `git.md` and `github.md` | `06-global-skills.md` | Covered |

## Functions / Components

| Component | Sub-Plan | Status |
|-----------|----------|--------|
| `extract_video_id(url_or_id)` — parse watch/youtu.be/Shorts/mobile/bare IDs | `02-transcript-core-module.md` | Covered |
| `fetch_transcript(video_id, languages)` — API call, join text, error handling | `02-transcript-core-module.md` | Covered |
| `save_transcript(text, output_path)` — UTF-8 file write | `02-transcript-core-module.md` | Covered |
| `get_transcript(url_or_id, output_path, languages)` — convenience wrapper | `02-transcript-core-module.md` | Covered |
| `main(argv=None)` — argparse CLI, exit codes, stderr/stdout | `03-main-cli-entry-point.md` | Covered |

## Test Classes

| Test Class | Sub-Plan | Status |
|-----------|----------|--------|
| `TestExtractVideoId` | `04-test-suite-structure.md` | Covered (stubs) |
| `TestFetchTranscript` | `04-test-suite-structure.md` | Covered (stubs) |
| `TestSaveTranscript` | `04-test-suite-structure.md` | Covered (stubs) |
| `TestGetTranscript` | `04-test-suite-structure.md` | Covered (stubs) |
| `TestMain` | `04-test-suite-structure.md` | Covered (stubs) |
| `TestIntegration` | `04-test-suite-structure.md` | Covered (stubs) |

## Verification Steps

| Verification Item | Sub-Plan | Status |
|-------------------|----------|--------|
| Install dependencies | `01-requirements-txt.md` | Covered |
| Unit tests (fast, no network) | `04-test-suite-structure.md` | Covered (structure only) |
| Smoke test (real network) | — | Deferred |
| Error handling verification | — | Deferred |
| Integration tests | `04-test-suite-structure.md` | Covered (stubs only) |
| Coverage measurement (`pytest-cov`) | — | Deferred |

## Intentionally Deferred Items

| Item | Reason |
|------|--------|
| **Test implementations** (filling in real assertions and mocks) | Deferred to the test-planning-agent per project workflow. Sub-plan 04 creates stubs only. |
| **Smoke test** (`python main.py` with a real URL) | Manual verification step; not automatable in a sub-plan without network access. Will be performed after all production code is implemented. |
| **Error handling manual verification** (`python main.py https://vimeo.com/...`) | Manual verification step; requires running the CLI interactively. |
| **Coverage measurement** (`pytest-cov` install and run) | Requires test implementations to exist first. Deferred until test-planning-agent fills in test bodies. |
| **`pytest-cov` installation** | Dependency for coverage measurement; deferred alongside coverage measurement. |

## Dependency Graph

```
01-requirements-txt
  └── 02-transcript-core-module
        └── 03-main-cli-entry-point
              └── 04-test-suite-structure (depends on 02 and 03)

05-claude-agents (independent)
06-global-skills (independent)
```

Sub-plans 05 and 06 have no code dependencies and can be executed in parallel with sub-plans 01-04.
