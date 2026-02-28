# YouTube Transcript Tool — Combined Implementation Plan

## Context

**Problem**: Getting YouTube transcripts to feed into AI chat tools is difficult. This project provides a simple CLI that takes a YouTube URL and outputs a clean `.txt` transcript file ready for AI ingestion.

**Outcome**: A working Python CLI + full agent/skill infrastructure for ongoing development.

**Approach**: Rather than implementing the monolithic plan directly, we create the planning agent first so it can decompose the work into smaller, focused sub-plans. All other agents and production code follow after the planning agent validates and decomposes the work.

---

## Critical Files

| Path | Status | Role |
|------|--------|------|
| `plans/transcript_system_plan.md` | Exists | Source plan (all implementation detail) |
| `plans/agent_first_plan.md` | Exists | Step ordering reference |
| `plans/combined_plan.md` | Exists | This combined plan |
| `.claude/agents/planning-agent.md` | Exists | Decomposition agent |
| `.claude/agents/orchestrator.md` | Create (Step 3) | Routes tasks to specialist agents |
| `.claude/agents/coding-agent.md` | Create (Step 3) | Python code writer |
| `.claude/agents/test-planning-agent.md` | Create (Step 3) | Test strategy designer |
| `.claude/agents/tester-agent.md` | Create (Step 3) | Runs pytest, reports results |
| `.claude/agents/review-agent.md` | Create (Step 3) | Checklist-driven code review |
| `~/.claude/commands/git.md` | Create (Step 3) | `/git` smart git skill |
| `~/.claude/commands/github.md` | Create (Step 3) | `/github` gh CLI skill |
| `requirements.txt` | Create (Step 4) | `youtube-transcript-api==1.2.4` |
| `transcript.py` | Create (Step 4) | Core logic module |
| `main.py` | Rewrite (Step 4) | CLI entry point |
| `tests/__init__.py` | Create (Step 4) | Empty package marker |
| `tests/test_transcript.py` | Create (Step 4) | Full pytest suite |
| `plans/pending/` | Populated (Step 2) | Sub-plans from decomposition |

---

## Step 0 — Save this plan to the project

> **Status: COMPLETE.** `plans/agent_first_plan.md` and `plans/combined_plan.md` exist in the repository.

---

## Step 1 — Create the `.claude/agents/` directory and `planning-agent.md`

> **Status: COMPLETE.** `.claude/agents/planning-agent.md` exists with valid YAML front matter and a full system prompt.

The planning agent is configured with:
- **Model:** opus
- **Tools:** Read, Glob, Grep, Write, Edit
- **Mission:** Break large plans into small, focused, self-contained sub-plans
- **Output:** Sub-plans saved to `plans/in_review/NN-kebab-case-name.md`
- **Rules:** One concern per sub-plan, max 15 steps, DAG prerequisites, exact file/function references

---

## Step 2 — Feed `plans/transcript_system_plan.md` to the planning agent

The planning agent decomposed the source plan into the following sub-plans:

| Sub-plan file                                | Concern |
|----------------------------------------------|---------|
| `plans/in_review/00-coverage-checklist.md`   | Maps every source plan item to a sub-plan |
| `plans/in_review/01-requirements-txt.md`       | Dependency pinning |
| `plans/in_review/02-claude-agents.md`          | Remaining 5 agent definitions |
| `plans/in_review/03-global-skills.md`          | `/git` and `/github` global skills |
| `plans/in_review/04-transcript-core-module.md` | Core logic (`transcript.py`) |
| `plans/in_review/05-main-cli-entry-point.md`   | CLI entry point (`main.py`) |
| `plans/in_review/06-test-suite-structure.md`   | Test suite (`tests/test_transcript.py`) |

Work through these in numeric order, moving each file to `plans/done/` when complete.

---

## Step 3 — Create remaining agents and global skills

Create the remaining 5 agents in `.claude/agents/` and 2 global skills in `~/.claude/commands/`.

> `~/.claude/commands/` does not exist yet — create it with `mkdir -p ~/.claude/commands/`.

Detailed instructions are in `plans/pending/02-claude-agents.md` and `plans/pending/03-global-skills.md`.

### Agent System Prompts

#### orchestrator

Routes tasks to specialist agents. Decision rules:
- **New feature:** planning-agent → test-planning-agent → coding-agent → tester-agent → review-agent
- **Bug fix:** planning-agent → coding-agent → tester-agent → review-agent
- Always run review-agent after non-trivial code changes.

**File:** `.claude/agents/orchestrator.md`

#### coding-agent

Python 3.12 specialist. Enforces:
- Type hints on all function signatures
- Docstrings on all public functions
- No `print()` in `transcript.py`
- No business logic in `main.py`
- Testable `main(argv=None)` signature
- UTF-8 file writes

**File:** `.claude/agents/coding-agent.md`

#### planning-agent

> Already exists. Produces structured plans with: Problem Statement, Files Affected, Numbered Steps, Edge Cases (≥3), Acceptance Criteria, Risks.

**File:** `.claude/agents/planning-agent.md`

#### test-planning-agent

Designs test strategies. Rules:
- 100% branch coverage on `extract_video_id`
- All 4 API error types tested
- No real network in unit tests
- Use `tmp_path` + `monkeypatch.chdir` for file I/O tests

**File:** `.claude/agents/test-planning-agent.md`

#### tester-agent

Runs `.venv/bin/pytest`, reports pass/fail/skip counts, diagnoses failures (test bug vs production bug), flags coverage below 80%.

**File:** `.claude/agents/tester-agent.md`

#### review-agent

Checklist-driven review:
- **Correctness:** logic errors, off-by-one, missing returns
- **Security:** no `eval`/`shell=True`, safe filenames
- **Code quality:** docstrings, type hints, PEP 8
- **Robustness:** empty transcript, disk full, missing output dir

**File:** `.claude/agents/review-agent.md`

### Skill Behaviours

#### `/git $ARGUMENTS`

Interprets natural language git requests. Safety rules:
- Never force-push `main`/`master`
- Never `reset --hard` without confirmation
- Always shows the command before running it
- Summarises output after execution

**File:** `~/.claude/commands/git.md`

#### `/github $ARGUMENTS`

GitHub operations via `gh` CLI. Covers: PR (create, list, view, merge, checkout), issues, releases, actions/CI.

PR creation workflow: inspect commits → draft title + body → confirm with user → create.

**File:** `~/.claude/commands/github.md`

---

## Step 4 — Implement production code and tests per sub-plans

Work through `plans/pending/` in numeric order. Move each file to `plans/done/` when its acceptance criteria are met.

### 4.1 — Create `requirements.txt` (sub-plan `01-requirements-txt.md`)

Pin the single dependency:

```
youtube-transcript-api==1.2.4
```

Install into the virtual environment:

```bash
.venv/bin/pip install -r requirements.txt
```

### 4.2 — Create `transcript.py` (sub-plan `02-transcript-core-module.md`)

Pure logic module with no CLI concerns. Four public functions:

**`extract_video_id(url_or_id: str) -> str`**
- Parses standard watch URLs (`youtube.com/watch?v=...`)
- Parses short URLs (`youtu.be/...`)
- Parses Shorts URLs (`youtube.com/shorts/...`)
- Parses mobile URLs (`m.youtube.com/watch?v=...`)
- Accepts bare 11-character video IDs
- Raises `ValueError` on invalid input (message names the 11-char constraint)

**`fetch_transcript(video_id: str, languages: list[str] | None = None) -> str`**
- Calls `YouTubeTranscriptApi().fetch()` with the given video ID
- Joins `snippet.text` lines with `\n`
- Re-raises known API errors (`TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`, `NoTranscriptAvailable`)
- Wraps unknown exceptions in `RuntimeError`

**`save_transcript(text: str, output_path: str) -> None`**
- Writes the transcript text to a file using UTF-8 encoding

**`get_transcript(url_or_id: str, output_path: str, languages: list[str] | None = None) -> str`**
- End-to-end convenience wrapper: extract ID → fetch → save → return text

### 4.3 — Rewrite `main.py` (sub-plan `03-main-cli-entry-point.md`)

**Function signature:** `main(argv: list[str] | None = None) -> int`

**Arguments:**
- Positional: `url` — YouTube URL or video ID
- `--output` / `-o` — output file path (default: `<video_id>.txt`)
- `--lang` / `-l` — language codes (repeatable, passed to `fetch_transcript`)

**Behaviour:**
- Errors print to stderr; normal output prints to stdout
- Returns `int` exit code (0 = success, 1 = error)
- No business logic — delegates everything to `transcript.py`

**Entry point:**
```python
if __name__ == "__main__":
    sys.exit(main())
```

### 4.4 — Create test suite (sub-plan `04-test-suite-structure.md`)

**Files:**
- `tests/__init__.py` — empty
- `tests/test_transcript.py` — full pytest suite

**Test classes:**

| Class | Covers |
|-------|--------|
| `TestExtractVideoId` | All URL formats, bare IDs, invalid inputs; 100% branch coverage |
| `TestFetchTranscript` | Successful fetch, all 4 API error types, unknown exceptions; all mocked |
| `TestSaveTranscript` | File creation, UTF-8 encoding, overwrite behaviour; uses `tmp_path` |
| `TestGetTranscript` | End-to-end wrapper with mocked dependencies |
| `TestMain` | CLI argument parsing, exit codes, stderr output; uses `monkeypatch` |
| `TestIntegration` | Real network calls; gated by `@pytest.mark.integration` |

**Testing rules:**
- No real network calls in unit tests
- Use `tmp_path` for file I/O tests
- Use `monkeypatch.chdir` when testing default output paths
- Integration tests require `-m integration` flag

---

## Verification

```bash
# 1. Install dependencies
.venv/bin/pip install -r requirements.txt

# 2. Unit tests (fast, no network)
.venv/bin/pytest tests/ -m "not integration" -v

# 3. Smoke test (real network)
python main.py https://www.youtube.com/watch?v=jNQXAC9IVRw
head -5 jNQXAC9IVRw.txt

# 4. Error handling (expects exit code 1)
python main.py https://vimeo.com/12345678901; echo "Exit: $?"

# 5. Integration tests (real network)
.venv/bin/pytest tests/ -m integration -v

# 6. Coverage report
.venv/bin/pip install pytest-cov
.venv/bin/pytest tests/ -m "not integration" --cov=transcript --cov=main --cov-report=term-missing
# Target: transcript.py >= 90%, main.py >= 85%
```

---

## Known Risks

- **Private API module:** `youtube_transcript_api._errors` is a private module — the pinned version (`1.2.4`) mitigates breakage, but upgrades require testing.
- **IP blocking:** YouTube may block IPs (`IpBlocked` / `RequestBlocked`) — surfaces as `RuntimeError` with the original message preserved.
- **CWD writes:** Default output writes to the current working directory — `OSError` on read-only directories is not yet handled explicitly (future improvement).
- **Hardcoded ID format:** The 11-character video ID regex is hardcoded — the `ValueError` message names the constraint for easy fixing if YouTube changes the format.
