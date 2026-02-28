# 02 — transcript.py Core Logic Module

### Problem Statement
Create the `transcript.py` module containing all core business logic for extracting video IDs, fetching transcripts from YouTube, and saving them to disk, with no CLI concerns.

### Prerequisites
- `01-requirements-txt.md` (the `youtube-transcript-api` package must be installed)

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `transcript.py` | Create | Core logic module with four public functions |

### Steps
1. Create `transcript.py` in the project root.
   - **Success**: File exists at `/home/oniwa/PycharmProjects/youtube_transcript/transcript.py`.
2. Add module-level docstring describing the module's purpose and the public API.
   - **Success**: Module has a docstring at the top.
3. Add necessary imports: `re`, `pathlib.Path`, `youtube_transcript_api.YouTubeTranscriptApi`, and the relevant error classes from `youtube_transcript_api._errors`.
   - **Success**: All imports are present and resolvable.
4. Implement `extract_video_id(url_or_id: str) -> str`. Must handle: standard watch URLs (`youtube.com/watch?v=ID`), short URLs (`youtu.be/ID`), Shorts URLs (`youtube.com/shorts/ID`), mobile URLs (`m.youtube.com/watch?v=ID`), and bare 11-character video IDs. Raise `ValueError` with a descriptive message on invalid input.
   - **Success**: Function exists with type hints and docstring; handles all five URL formats.
5. Implement the 11-character video ID regex validation inside `extract_video_id`. The regex pattern should match `[A-Za-z0-9_-]{11}`. The `ValueError` message must name the 11-character constraint.
   - **Success**: Bare IDs matching the regex are returned; non-matching strings raise `ValueError` mentioning "11".
6. Implement `fetch_transcript(video_id: str, languages: list[str] | None = None) -> str`. Instantiate `YouTubeTranscriptApi()` and call `.fetch(video_id, languages=languages)`. Join `snippet.text` lines with `"\n"`.
   - **Success**: Function exists with type hints and docstring; returns a joined string.
7. Add error handling in `fetch_transcript`: catch known API errors (`TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`, `NoTranscriptAvailable`) and re-raise them. Wrap any other exception in `RuntimeError` with the original message preserved.
   - **Success**: Known errors propagate unchanged; unknown errors become `RuntimeError`.
8. Implement `save_transcript(text: str, output_path: str | Path) -> Path`. Write the text to `output_path` using UTF-8 encoding. Return the resolved `Path` object.
   - **Success**: Function exists with type hints and docstring; writes UTF-8 file and returns `Path`.
9. Implement `get_transcript(url_or_id: str, output_path: str | Path, languages: list[str] | None = None) -> Path`. This is a convenience wrapper that calls `extract_video_id`, `fetch_transcript`, and `save_transcript` in sequence. Return the output path.
   - **Success**: Function exists, calls all three sub-functions, and returns the path.
10. Ensure no `print()` calls exist anywhere in `transcript.py`.
    - **Success**: `grep -c "print(" transcript.py` returns 0.
11. Add an `__all__` list exporting `extract_video_id`, `fetch_transcript`, `save_transcript`, and `get_transcript`.
    - **Success**: `__all__` is defined and contains exactly those four names.

### Edge Cases
- **Input**: Empty string or `None` passed to `extract_video_id` — must raise `ValueError`.
- **Input**: URL with extra query parameters (e.g., `&list=...`, `&t=120`) — must still extract the correct video ID.
- **Runtime**: `YouTubeTranscriptApi().fetch()` raises `IpBlocked` or `RequestBlocked` — must surface as `RuntimeError` with original message.
- **Runtime**: Transcript text is empty (video exists but has no content) — `fetch_transcript` returns an empty string; `save_transcript` writes an empty file.
- **Environment**: Output directory does not exist — `save_transcript` should let the `OSError` propagate naturally.

### Acceptance Criteria
- `transcript.py` exists in the project root.
- It exports exactly four public functions: `extract_video_id`, `fetch_transcript`, `save_transcript`, `get_transcript`.
- All functions have type hints and docstrings.
- No `print()` calls in the module.
- `extract_video_id` handles all five URL formats and raises `ValueError` for invalid input.
- `fetch_transcript` re-raises known API errors and wraps unknown errors in `RuntimeError`.
- `save_transcript` writes UTF-8 and returns a `Path`.
- `get_transcript` orchestrates the other three functions.
- The module can be imported without errors: `.venv/bin/python -c "import transcript"`.

### Risks
- The `youtube_transcript_api._errors` module is private. If error class names change in a future version, imports will break. Mitigation: version is pinned in `requirements.txt`.
- The 11-character video ID assumption is hardcoded. If YouTube changes ID length, this will reject valid IDs. The `ValueError` message names the constraint for easy fixing.
- `IpBlocked` / `RequestBlocked` errors from YouTube are outside our control. They are wrapped in `RuntimeError` with the original message so the user can diagnose the issue.
