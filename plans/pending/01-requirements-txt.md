# 01 — requirements.txt

### Problem Statement
Create the project dependency file pinning `youtube-transcript-api` so that all downstream modules and tests can be installed reproducibly.

### Prerequisites
None

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `requirements.txt` | Create | Pin `youtube-transcript-api==1.2.4` |

### Steps
1. Create `requirements.txt` in the project root with a single line: `youtube-transcript-api==1.2.4`.
   - **Success**: File exists at `/home/oniwa/PycharmProjects/youtube_transcript/requirements.txt` and contains exactly the pinned dependency.
2. Install the dependency into the project virtual environment by running `.venv/bin/pip install -r requirements.txt`.
   - **Success**: `pip install` exits with code 0 and `youtube-transcript-api` is importable from `.venv`.
3. Verify the installed version by running `.venv/bin/pip show youtube-transcript-api` and confirming version `1.2.4`.
   - **Success**: Output shows `Version: 1.2.4`.

### Edge Cases
- **Input**: A developer adds an unpinned or differently-versioned dependency later — the pinned version here protects against silent breakage.
- **Runtime**: `pip install` fails due to network issues — retry or use a local cache.
- **Environment**: `.venv` does not exist — must be created first with `python3 -m venv .venv`.

### Acceptance Criteria
- `requirements.txt` exists in the project root.
- It contains exactly one dependency: `youtube-transcript-api==1.2.4`.
- `.venv/bin/pip install -r requirements.txt` succeeds.
- `.venv/bin/python -c "import youtube_transcript_api"` exits with code 0.

### Risks
- The `youtube-transcript-api` package uses private error modules (`_errors`). Pinning to `1.2.4` mitigates breakage but any future upgrade requires re-testing error handling.
- If the virtual environment `.venv` does not already exist, the coding agent must create it first.
