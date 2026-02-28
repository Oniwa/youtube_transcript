# Sub-plan 01: Create `requirements.txt`

### Problem Statement
Create `requirements.txt` with the pinned dependency `youtube-transcript-api==1.2.4` and install it into the project virtual environment so all subsequent modules can import the library.

### Prerequisites
None.

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `requirements.txt` | Create | Single pinned dependency for the youtube-transcript-api library |

### Steps

1. **Create `requirements.txt` at the project root** (`/home/oniwa/PycharmProjects/youtube_transcript/requirements.txt`) containing exactly one line: `youtube-transcript-api==1.2.4`. No trailing blank dependencies, no comments, no version ranges.
   - Success: file exists and `cat requirements.txt` outputs exactly `youtube-transcript-api==1.2.4`.

2. **Verify the virtual environment exists** by confirming `.venv/bin/pip` is present at `/home/oniwa/PycharmProjects/youtube_transcript/.venv/bin/pip`. If it is missing, create the venv with `python3.12 -m venv .venv` before proceeding.
   - Success: `.venv/bin/pip --version` exits with code 0.

3. **Install the dependency** by running `.venv/bin/pip install -r requirements.txt` from the project root. Capture stderr in case of failure.
   - Success: command exits with code 0 and output contains `Successfully installed youtube-transcript-api-1.2.4` or `Requirement already satisfied: youtube-transcript-api==1.2.4`.

4. **Verify the installed version** by running `.venv/bin/pip show youtube-transcript-api`. Confirm that the `Version:` field in the output is exactly `1.2.4`.
   - Success: `pip show` output contains `Version: 1.2.4`.

5. **Verify the import works** by running `.venv/bin/python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('OK')"`. Confirm the output is `OK`.
   - Success: command exits with code 0 and prints `OK`.

6. **Verify the error classes are importable** by running `.venv/bin/python -c "from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, NoTranscriptAvailable; print('OK')"`. These are needed by `transcript.py`.
   - Success: command exits with code 0 and prints `OK`.

### Edge Cases

- **Input**: `requirements.txt` already exists with a different pin (e.g., `youtube-transcript-api>=1.0.0`) — overwrite it unconditionally with the exact pin `==1.2.4` to prevent accidental upgrades.
- **Input**: File is created with Windows line endings (`\r\n`) — write the file in text mode (default on Linux) so pip parses it correctly.
- **Runtime**: Network unavailable during `pip install` — pip will print a connection error to stderr; the step fails with a non-zero exit code. Resolution: retry when network is available or install from a local wheel.
- **Runtime**: A conflicting version of `youtube-transcript-api` is already installed in `.venv` (e.g., `1.3.0`) — `pip install -r requirements.txt` will downgrade it. Verify the final installed version is `1.2.4` regardless of what was previously installed.
- **Environment**: `.venv/bin/pip` points to the wrong Python interpreter (e.g., Python 3.9 instead of 3.12) — verify with `.venv/bin/python --version` before installing; recreate the venv with `python3.12 -m venv .venv` if needed.
- **Environment**: Project root is on a read-only filesystem — `pip install` will fail with a permissions error. Resolution: ensure the `.venv/` directory is on a writable filesystem.

### Acceptance Criteria

- `requirements.txt` exists at the project root with contents `youtube-transcript-api==1.2.4` (no other lines, no version ranges).
- `.venv/bin/pip show youtube-transcript-api` outputs `Version: 1.2.4`.
- `.venv/bin/python -c "from youtube_transcript_api import YouTubeTranscriptApi"` exits with code 0.
- `.venv/bin/python -c "from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, NoTranscriptAvailable"` exits with code 0.
- No other packages are pinned in `requirements.txt` (test runner packages such as `pytest` and `pytest-cov` are installed separately).

### Risks

- **Private error module (`_errors`)**: The error classes live in `youtube_transcript_api._errors`, which is a private submodule. The `==1.2.4` pin mitigates breakage if the API is restructured in future versions, but any upgrade must be retested against this import path.
- **Assumption**: The project uses a `.venv` virtual environment at the project root. If a different venv name is used (e.g., `env/`), the install command in Steps 3–6 must be adjusted.
- **Open question**: Should `pytest` and `pytest-cov` be added to a separate `requirements-dev.txt`? For now they are not in scope for this sub-plan; they are installed ad hoc in the Verification commands.
