> ⛔ **HUMAN GATE** — Do not implement this plan until a human has reviewed it and moved it to `plans/pending/`.

# Sub-plan 04: Create `transcript.py` — Core Logic Module

### Problem Statement
Create `transcript.py` as the pure logic module containing the 4 public functions that handle video ID extraction, transcript fetching, file saving, and end-to-end orchestration, with no CLI concerns and strict adherence to the project's coding standards.

### Prerequisites
- `01-requirements-txt.md` — `youtube-transcript-api==1.2.4` must be installed before `transcript.py` can be imported.

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `transcript.py` | Create | Pure logic module with 4 public functions |

### Steps

1. **Create the file header** for `transcript.py` at `/home/oniwa/PycharmProjects/youtube_transcript/transcript.py`. Begin with the module docstring, then the imports:
   ```python
   """
   transcript.py — Core logic for YouTube transcript extraction.

   This module has no CLI concerns. All functions are pure logic:
   extract a video ID, fetch a transcript, save it, or do all three.
   """
   from __future__ import annotations

   import re
   from urllib.parse import urlparse, parse_qs

   from youtube_transcript_api import YouTubeTranscriptApi
   from youtube_transcript_api._errors import (
       NoTranscriptAvailable,
       NoTranscriptFound,
       TranscriptsDisabled,
       VideoUnavailable,
   )
   ```
   - Success: file exists; `.venv/bin/python -c "import transcript"` exits with code 0.

2. **Implement `extract_video_id(url_or_id: str) -> str`**. The function must handle these cases in order:
   - Bare 11-character video ID: matches `^[A-Za-z0-9_-]{11}$` → return as-is.
   - Standard watch URL: `youtube.com/watch?v=<id>` (including `m.youtube.com/watch?v=<id>`) → extract from query param `v`.
   - Short URL: `youtu.be/<id>` → extract from the URL path.
   - Shorts URL: `youtube.com/shorts/<id>` → extract from the URL path.
   - Any other input → raise `ValueError` with message: `"Could not extract an 11-character video ID from: {url_or_id!r}"`.

   ```python
   _VIDEO_ID_RE = re.compile(r'^[A-Za-z0-9_-]{11}$')

   def extract_video_id(url_or_id: str) -> str:
       """Extract the 11-character YouTube video ID from a URL or bare ID.

       Supports: standard watch URLs, youtu.be short URLs, Shorts URLs,
       mobile URLs (m.youtube.com), and bare 11-character IDs.

       Args:
           url_or_id: A YouTube URL in any supported format, or a bare video ID.

       Returns:
           The 11-character video ID string.

       Raises:
           ValueError: If no valid 11-character video ID can be extracted.
       """
       if _VIDEO_ID_RE.match(url_or_id):
           return url_or_id

       parsed = urlparse(url_or_id)
       host = parsed.hostname or ""

       if host in ("youtube.com", "www.youtube.com", "m.youtube.com"):
           if parsed.path == "/watch":
               qs = parse_qs(parsed.query)
               ids = qs.get("v", [])
               if ids and _VIDEO_ID_RE.match(ids[0]):
                   return ids[0]
           elif parsed.path.startswith("/shorts/"):
               candidate = parsed.path.split("/shorts/", 1)[1].split("/")[0]
               if _VIDEO_ID_RE.match(candidate):
                   return candidate

       if host == "youtu.be":
           candidate = parsed.path.lstrip("/").split("/")[0]
           if _VIDEO_ID_RE.match(candidate):
               return candidate

       raise ValueError(
           f"Could not extract an 11-character video ID from: {url_or_id!r}"
       )
   ```
   - Success: `extract_video_id("https://www.youtube.com/watch?v=jNQXAC9IVRw")` returns `"jNQXAC9IVRw"` when called from `.venv/bin/python`.

3. **Implement `fetch_transcript(video_id: str, languages: list[str] | None = None) -> str`**. Call the API, join snippet text, and propagate known errors:
   ```python
   def fetch_transcript(video_id: str, languages: list[str] | None = None) -> str:
       """Fetch the transcript for a YouTube video and return it as plain text.

       Each caption snippet is joined with a newline character.

       Args:
           video_id: The 11-character YouTube video ID.
           languages: Optional list of BCP-47 language codes in preference order
               (e.g., ["en", "en-US"]). If None, the API selects the default.

       Returns:
           The full transcript text with snippets separated by newlines.

       Raises:
           TranscriptsDisabled: Transcripts are disabled for this video.
           NoTranscriptFound: No transcript exists in any of the requested languages.
           VideoUnavailable: The video does not exist or is private.
           NoTranscriptAvailable: No transcript is available for this video.
           RuntimeError: An unexpected API error occurred.
       """
       try:
           api = YouTubeTranscriptApi()
           kwargs: dict[str, object] = {}
           if languages is not None:
               kwargs["languages"] = languages
           fetched = api.fetch(video_id, **kwargs)
           return "\n".join(snippet.text for snippet in fetched)
       except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, NoTranscriptAvailable):
           raise
       except Exception as err:
           raise RuntimeError(
               f"Unexpected error fetching transcript for video '{video_id}': {err}"
           ) from err
   ```
   - Success: function body is present; known error types are imported and re-raised without wrapping.

4. **Implement `save_transcript(text: str, output_path: str) -> None`**. Write the text to disk in UTF-8:
   ```python
   def save_transcript(text: str, output_path: str) -> None:
       """Write a transcript string to a file in UTF-8 encoding.

       Args:
           text: The transcript text to write.
           output_path: Destination file path. Parent directory must already exist.

       Raises:
           OSError: If the file cannot be written (e.g., permission denied,
               disk full, parent directory missing).
       """
       with open(output_path, "w", encoding="utf-8") as fh:
           fh.write(text)
   ```
   - Success: after calling `save_transcript("hello", "/tmp/t.txt")`, `cat /tmp/t.txt` outputs `hello`.

5. **Implement `get_transcript(url_or_id: str, output_path: str, languages: list[str] | None = None) -> str`**. End-to-end convenience wrapper:
   ```python
   def get_transcript(
       url_or_id: str,
       output_path: str,
       languages: list[str] | None = None,
   ) -> str:
       """Extract a video ID, fetch its transcript, save it, and return the text.

       This is a convenience wrapper around extract_video_id, fetch_transcript,
       and save_transcript.

       Args:
           url_or_id: A YouTube URL in any supported format, or a bare video ID.
           output_path: Destination file path for the saved transcript.
           languages: Optional list of BCP-47 language codes in preference order.

       Returns:
           The full transcript text that was saved.

       Raises:
           ValueError: If url_or_id is not a valid YouTube URL or video ID.
           TranscriptsDisabled: Transcripts are disabled for this video.
           NoTranscriptFound: No transcript in the requested languages.
           VideoUnavailable: The video does not exist or is private.
           NoTranscriptAvailable: No transcript available for this video.
           RuntimeError: An unexpected error occurred during fetching.
           OSError: If the transcript cannot be saved to output_path.
       """
       video_id = extract_video_id(url_or_id)
       text = fetch_transcript(video_id, languages=languages)
       save_transcript(text, output_path)
       return text
   ```
   - Success: function is present and calls `extract_video_id`, `fetch_transcript`, and `save_transcript` in that order.

6. **Verify the module imports cleanly** by running:
   ```bash
   .venv/bin/python -c "from transcript import extract_video_id, fetch_transcript, save_transcript, get_transcript; print('OK')"
   ```
   - Success: output is `OK` with no import errors or warnings.

7. **Verify no `print()` calls exist** in `transcript.py` by searching the file for the string `print(`:
   - Success: no matches found.

8. **Verify all 4 public functions have type hints** by checking that every `def` line includes parameter type annotations and a `-> <type>` return annotation:
   - Success: all 4 function signatures include both parameter and return type annotations.

9. **Verify all 4 public functions have docstrings** by checking that each `def` block is immediately followed by a `"""..."""` string:
   - Success: all 4 function bodies start with a docstring.

10. **Smoke-test `extract_video_id`** for all supported URL formats:
    ```bash
    .venv/bin/python -c "
    from transcript import extract_video_id
    cases = [
        ('https://www.youtube.com/watch?v=jNQXAC9IVRw', 'jNQXAC9IVRw'),
        ('https://youtu.be/jNQXAC9IVRw', 'jNQXAC9IVRw'),
        ('https://www.youtube.com/shorts/jNQXAC9IVRw', 'jNQXAC9IVRw'),
        ('https://m.youtube.com/watch?v=jNQXAC9IVRw', 'jNQXAC9IVRw'),
        ('jNQXAC9IVRw', 'jNQXAC9IVRw'),
    ]
    for url, expected in cases:
        result = extract_video_id(url)
        assert result == expected, f'FAIL: {url!r} -> {result!r}'
    print('All cases passed')
    "
    ```
    - Success: output is `All cases passed`.

### Edge Cases

- **Input**: `url_or_id` is an empty string — `_VIDEO_ID_RE` does not match; `urlparse("")` returns an empty parsed result; `hostname` is `None`; falls through to `raise ValueError`.
- **Input**: `url_or_id` contains a valid-looking but non-YouTube URL (e.g., `https://vimeo.com/jNQXAC9IVRw`) — hostname check fails; falls through to `raise ValueError`.
- **Input**: Transcript snippets contain non-ASCII characters (e.g., Japanese, Arabic, emoji) — `save_transcript` uses `encoding="utf-8"` which handles all Unicode code points without error.
- **Input**: `languages` parameter is an empty list `[]` — pass it to the API as-is; the API will apply its own default selection logic (behaviour is API-defined, not our responsibility to validate).
- **Runtime**: `YouTubeTranscriptApi().fetch()` raises `TranscriptsDisabled` — re-raised directly without wrapping in `RuntimeError`.
- **Runtime**: `YouTubeTranscriptApi().fetch()` raises an unexpected exception (e.g., `requests.ConnectionError`) — caught by the broad `except Exception` clause and re-raised as `RuntimeError` with a descriptive message.
- **Runtime**: `save_transcript` is called with an `output_path` whose parent directory does not exist — `open()` raises `FileNotFoundError` (a subclass of `OSError`); the caller (e.g., `main.py`) is responsible for handling this.
- **Runtime**: Disk is full when writing — `open().write()` raises `OSError: [Errno 28] No space left on device`; propagates to caller unchanged.
- **Environment**: `youtube_transcript_api` is not installed — `ImportError` at module import time; resolved by completing `01-requirements-txt.md` first.

### Acceptance Criteria

- `transcript.py` exists at the project root.
- `from transcript import extract_video_id, fetch_transcript, save_transcript, get_transcript` succeeds in `.venv/bin/python` with no errors.
- All 4 public functions have type hints on all parameters and the return type.
- All 4 public functions have docstrings.
- No `print()` calls exist anywhere in `transcript.py`.
- `extract_video_id` correctly handles: standard watch URL, youtu.be short URL, Shorts URL, mobile URL, and bare 11-character ID.
- `extract_video_id` raises `ValueError` for invalid or non-YouTube input.
- `fetch_transcript` re-raises `TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`, and `NoTranscriptAvailable` without wrapping.
- `fetch_transcript` wraps unexpected exceptions in `RuntimeError`.
- `save_transcript` writes files with `encoding="utf-8"`.
- `get_transcript` calls all three of the other functions in sequence.

### Risks

- **Private error module**: `youtube_transcript_api._errors` is a private submodule. The `==1.2.4` pin mitigates breakage, but if the library restructures its error hierarchy in a future version, these imports will fail. Mitigation: re-test after any pin upgrade.
- **API method signature**: `YouTubeTranscriptApi().fetch()` is called with a `languages` keyword argument. If the method signature changes in a future version, the call will fail. Mitigation: the version pin prevents accidental upgrades.
- **YouTube format changes**: The regex `^[A-Za-z0-9_-]{11}$` and URL path patterns are hardcoded. If YouTube changes its video ID format or URL structure, `extract_video_id` will silently fail for new URLs. Mitigation: the `ValueError` message names the 11-character constraint, making the point of failure obvious.
- **Assumption**: `fetch_transcript` iterates over the fetched object with `snippet.text` attribute access. Verify this attribute name against the installed version of `youtube-transcript-api==1.2.4` before finalising the implementation.
