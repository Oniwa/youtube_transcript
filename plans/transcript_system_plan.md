# YouTube Transcript Tool — Implementation Plan

## Context

**Problem**: Getting YouTube transcripts to feed into AI chat tools is difficult. This project provides a simple CLI that takes a YouTube URL and outputs a clean `.txt` transcript file ready for AI ingestion.

**Outcome**: A working Python CLI + full agent/skill infrastructure for ongoing development.

---

## Files to Create / Modify

### Production Code
| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | Create | `youtube-transcript-api==1.2.4` |
| `transcript.py` | Create | Core logic: `extract_video_id`, `fetch_transcript`, `save_transcript`, `get_transcript` |
| `main.py` | Rewrite | CLI entry point (`argparse`, calls `transcript.py`, formats errors) |

### Tests
| File | Action |
|------|--------|
| `tests/__init__.py` | Create (empty) |
| `tests/test_transcript.py` | Create — full pytest suite, mocked unit tests + `@pytest.mark.integration` tests |

### Project-Local Agents (`.claude/agents/`)
| File | Role |
|------|------|
| `orchestrator.md` | Routes tasks; coordinates all other agents |
| `coding-agent.md` | Writes/edits Python code for this project |
| `planning-agent.md` | Designs feature plans and breakdowns |
| `test-planning-agent.md` | Designs test strategies and writes test cases |
| `tester-agent.md` | Runs pytest, reports results and coverage |
| `review-agent.md` | Reviews code quality, correctness, security |

### Global Skills (`~/.claude/commands/`)
| File | Invocation | Purpose |
|------|-----------|---------|
| `git.md` | `/git` | Smart git operations (status, commit, branch, push, diff, log, stash) |
| `github.md` | `/github` | GitHub via `gh` CLI (PR, issues, releases, CI/actions) |

> `~/.claude/commands/` does not exist yet — must be created with `mkdir -p`.

---

## Implementation Steps

1. **Create `requirements.txt`** — pin `youtube-transcript-api==1.2.4`
2. **Create `transcript.py`** — pure logic module, no CLI concerns:
   - `extract_video_id(url_or_id)` — parses watch URLs, youtu.be, Shorts, mobile, bare IDs; raises `ValueError` on invalid input
   - `fetch_transcript(video_id, languages=None)` — calls `YouTubeTranscriptApi().fetch()`, joins `snippet.text` lines with `\n`; re-raises known API errors, wraps unknown in `RuntimeError`
   - `save_transcript(text, output_path)` — writes UTF-8 file
   - `get_transcript(url_or_id, output_path, languages=None)` — end-to-end convenience wrapper
3. **Rewrite `main.py`** — `argparse` CLI with `--output`/`-o` and `--lang`/`-l` flags; `main(argv=None)` returns int exit code; errors → stderr, output → stdout; default filename = `<video_id>.txt`
4. **Create `tests/__init__.py`** — empty file
5. **Create `tests/test_transcript.py`** — pytest classes: `TestExtractVideoId`, `TestFetchTranscript`, `TestSaveTranscript`, `TestGetTranscript`, `TestMain`, `TestIntegration` (gated by `-m integration`)
6. **Install dependencies** — `.venv/bin/pip install -r requirements.txt`
7. **Run tests** — `.venv/bin/pytest tests/ -m "not integration" -v`
8. **Create `.claude/agents/` directory** and write 6 agent `.md` files
9. **Create `~/.claude/commands/` directory** and write `git.md` and `github.md`

---

## Agent System Prompts (Summary)

### orchestrator
Routes tasks to specialist agents. Decision rules: new feature → planning → test-planning → coding → tester → review. Bug fix → planning → coding → tester → review. Always run review after non-trivial code changes.

### coding-agent
Python 3.12 specialist. Enforces: type hints, docstrings, no `print()` in `transcript.py`, no business logic in `main.py`, testable `main(argv)` signature, UTF-8 file writes.

### planning-agent
Produces structured plans: Problem Statement, Files Affected, Numbered Steps, Edge Cases (≥3), Test Considerations, Risks.

### test-planning-agent
Designs test strategies. Rules: 100% branch coverage on `extract_video_id`, all 4 API error types tested, no real network in unit tests (`tmp_path` + `monkeypatch.chdir` for file I/O).

### tester-agent
Runs `.venv/bin/pytest`, reports pass/fail/skip counts, diagnoses failures (test bug vs production bug), flags coverage below 80%.

### review-agent
Checklist-driven review: correctness, security (no `eval`/`shell=True`, safe filenames), code quality (docstrings, type hints, PEP 8), robustness (empty transcript, disk full, missing output dir).

---

## Skill Behaviours (Summary)

### `/git $ARGUMENTS`
Interprets natural language git requests. Safety: never force-push main/master, never `reset --hard` without confirmation. Always shows command before running, summarises output.

### `/github $ARGUMENTS`
GitHub operations via `gh` CLI. Covers: PR (create/list/view/merge/checkout), issues, releases, actions/CI. PR creation workflow: inspect commits → draft title+body → confirm → create.

---

## Verification

```bash
# 1. Install
.venv/bin/pip install -r requirements.txt

# 2. Unit tests (fast, no network)
.venv/bin/pytest tests/ -m "not integration" -v

# 3. Smoke test (real network)
python main.py https://www.youtube.com/watch?v=jNQXAC9IVRw
head -5 jNQXAC9IVRw.txt

# 4. Error handling
python main.py https://vimeo.com/12345678901; echo "Exit: $?"  # expects exit 1

# 5. Integration tests
.venv/bin/pytest tests/ -m integration -v

# 6. Coverage
.venv/bin/pip install pytest-cov
.venv/bin/pytest tests/ -m "not integration" --cov=transcript --cov=main --cov-report=term-missing
# Target: transcript.py ≥ 90%, main.py ≥ 85%
```

---

## Known Risks

- `youtube_transcript_api._errors` is a private module — pinned version mitigates breakage
- YouTube may block IPs (`IpBlocked` / `RequestBlocked`) — surfaces as `RuntimeError` with original message
- Default output writes to cwd — `OSError` on read-only dirs is not yet named explicitly (future improvement)
- 11-char video ID regex is hardcoded — `ValueError` message names the constraint for easy fixing
