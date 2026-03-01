# Sub-plan 05: Rewrite `main.py` — CLI Entry Point

### Problem Statement
Rewrite `main.py` as the CLI entry point that uses argparse to accept a YouTube URL (or video ID), optional output path, and optional language codes, then delegates all business logic to `transcript.py` and returns a proper integer exit code.

### Prerequisites
- `04-transcript-core-module.md` — `transcript.py` must exist with all 4 public functions before `main.py` can import them.

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `main.py` | Modify / Rewrite | CLI entry point using argparse; no business logic |

### Steps

1. **Read the current `main.py`** (if it exists) to understand what is already there before overwriting:
   - Success: file contents are noted; proceed to overwrite regardless of current contents.

2. **Write the complete `main.py`** with the following exact structure. The file must contain only the import block, `_build_parser()`, `main()`, and the `__main__` guard — nothing else:

   ```python
   """
   main.py — CLI entry point for the YouTube transcript extraction tool.

   Usage:
       python main.py <url>
       python main.py <url> --output transcript.txt
       python main.py <url> --lang en --lang fr
   """
   from __future__ import annotations

   import argparse
   import sys

   from transcript import (
       NoTranscriptAvailable,
       NoTranscriptFound,
       TranscriptsDisabled,
       VideoUnavailable,
       extract_video_id,
       get_transcript,
   )
   ```
   Note: the error classes are imported from `transcript` which re-exports them (see Step 3). Alternatively, import them from `youtube_transcript_api._errors` directly — pick one approach and be consistent.
   - Success: file starts with the module docstring and imports.

3. **Ensure `transcript.py` re-exports the error classes** so `main.py` can import them from a single location. Add the following line to `transcript.py` after the existing imports (do not add it if already present):
   This is the preferred approach: expose the error types publicly from `transcript.py` so that `main.py` does not need to reference the private `._errors` submodule.
   - In `transcript.py`, after the `from youtube_transcript_api._errors import ...` block, add nothing extra — they are already importable from `transcript` as module-level names. Confirm that `from transcript import TranscriptsDisabled` works.
   - Success: `.venv/bin/python -c "from transcript import TranscriptsDisabled"` exits with code 0.

4. **Implement `_build_parser() -> argparse.ArgumentParser`** — a private helper that constructs the argument parser:
   ```python
   def _build_parser() -> argparse.ArgumentParser:
       """Build and return the CLI argument parser."""
       parser = argparse.ArgumentParser(
           prog="youtube-transcript",
           description="Download a YouTube video transcript to a text file.",
       )
       parser.add_argument(
           "url",
           help="YouTube video URL or bare 11-character video ID.",
       )
       parser.add_argument(
           "--output",
           "-o",
           metavar="FILE",
           default=None,
           help=(
               "Output file path. Defaults to <video_id>.txt in the current directory."
           ),
       )
       parser.add_argument(
           "--lang",
           "-l",
           metavar="LANG",
           action="append",
           dest="languages",
           default=None,
           help=(
               "Language code (BCP-47) for the transcript. "
               "Repeat to specify multiple languages in preference order "
               "(e.g., --lang en --lang fr)."
           ),
       )
       return parser
   ```
   - Success: `_build_parser().parse_args(["https://youtu.be/jNQXAC9IVRw"])` does not raise an exception.

5. **Implement `main(argv: list[str] | None = None) -> int`** — the primary function:
   ```python
   def main(argv: list[str] | None = None) -> int:
       """Run the YouTube transcript CLI.

       Args:
           argv: Argument list. If None, reads from sys.argv[1:].

       Returns:
           0 on success, 1 on any error.
       """
       parser = _build_parser()
       args = parser.parse_args(argv)

       # Determine the output path: use --output if given, else <video_id>.txt
       try:
           video_id = extract_video_id(args.url)
       except ValueError as err:
           print(f"Error: {err}", file=sys.stderr)
           return 1

       output_path = args.output if args.output is not None else f"{video_id}.txt"

       try:
           text = get_transcript(args.url, output_path, languages=args.languages)
       except (TranscriptsDisabled, NoTranscriptFound, NoTranscriptAvailable) as err:
           print(f"Error: No transcript available — {err}", file=sys.stderr)
           return 1
       except VideoUnavailable as err:
           print(f"Error: Video unavailable — {err}", file=sys.stderr)
           return 1
       except OSError as err:
           print(f"Error: Could not save transcript — {err}", file=sys.stderr)
           return 1
       except RuntimeError as err:
           print(f"Error: {err}", file=sys.stderr)
           return 1

       print(f"Transcript saved to: {output_path}")
       print(f"Length: {len(text.splitlines())} lines")
       return 0
   ```
   - Success: function signature is `main(argv: list[str] | None = None) -> int`.

6. **Add the `__main__` guard** at the very end of `main.py`:
   ```python
   if __name__ == "__main__":
       sys.exit(main())
   ```
   - Success: the guard is the last 2 lines of the file.

7. **Verify `main.py` imports cleanly** by running:
   ```bash
   .venv/bin/python -c "from main import main, _build_parser; print('OK')"
   ```
   - Success: output is `OK` with no import errors.

8. **Verify `--help` output** by running:
   ```bash
   .venv/bin/python main.py --help
   ```
   - Success: output contains `url`, `--output`, and `--lang` and exits with code 0.

9. **Verify error exit code** by running with a non-YouTube URL:
   ```bash
   .venv/bin/python main.py "https://vimeo.com/12345678901"; echo "Exit: $?"
   ```
   - Success: exit code is `1` and error message appears on stderr.

10. **Verify `main(argv=None)` returns int** by running:
    ```bash
    .venv/bin/python -c "
    from main import main
    import inspect
    hints = inspect.get_annotations(main)
    assert hints.get('return') is int or str(hints.get('return')) == 'int', f'Expected int return, got {hints}'
    print('Type hint OK')
    "
    ```
    - Success: output is `Type hint OK`.

11. **Verify no business logic in `main.py`** by confirming that `main.py` contains no calls to `YouTubeTranscriptApi`, no regex patterns, and no URL parsing logic:
    - Search `main.py` for `YouTubeTranscriptApi`, `re.compile`, `urlparse` — none should be found.
    - Success: none of these strings appear in `main.py`.

### Edge Cases

- **Input**: No `url` argument given on the command line — argparse prints its usage message to stderr and exits with code 2 (standard argparse behaviour for missing required arguments; this is acceptable and does not need special handling).
- **Input**: `url` argument is not a YouTube URL — `extract_video_id` raises `ValueError`; caught in `main()`, printed to stderr, returns exit code 1.
- **Input**: `--output` points to a path whose parent directory does not exist (e.g., `--output /nonexistent/dir/out.txt`) — `save_transcript` raises `OSError`; caught in `main()`, printed to stderr, returns exit code 1.
- **Input**: `--output` points to a read-only file — `open(..., "w")` raises `PermissionError` (a subclass of `OSError`); caught in the `OSError` handler, returns exit code 1.
- **Input**: `--lang` flag provided with an unrecognised language code — the API raises `NoTranscriptFound`; caught and reported to stderr with exit code 1.
- **Runtime**: `get_transcript` raises an unexpected `RuntimeError` — caught by the `RuntimeError` handler; error message printed to stderr; exit code 1.
- **Environment**: `transcript.py` is not importable (e.g., `youtube-transcript-api` not installed) — `ImportError` at module load time; not caught by `main()` itself. Resolution: complete `01-requirements-txt.md` first.

### Acceptance Criteria

- `main.py` exists at the project root.
- `main.py` defines `main(argv: list[str] | None = None) -> int` with a return type hint of `int`.
- `main.py` contains no calls to `YouTubeTranscriptApi`, no `re.compile`, and no `urlparse` — all business logic is in `transcript.py`.
- `python main.py --help` prints usage with `url`, `--output`/`-o`, and `--lang`/`-l` arguments and exits with code 0.
- `python main.py <valid_url>` exits with code 0 and prints "Transcript saved to: <file>".
- `python main.py <invalid_url>` exits with code 1 and prints an error message to stderr.
- Error messages are written to `sys.stderr`; success messages are written to `sys.stdout`.
- Default output filename is `<video_id>.txt` (derived by calling `extract_video_id`).
- The `if __name__ == "__main__": sys.exit(main())` guard is present.

### Risks

- **Import of error classes**: `main.py` imports `TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable`, and `NoTranscriptAvailable` from `transcript`. This is possible because `transcript.py` imports them at module level, making them available as names in the `transcript` namespace. If `transcript.py` moves these imports into a function body, the re-export will break. Mitigation: keep the imports at module level in `transcript.py`.
- **argparse exit code**: argparse uses exit code 2 for argument parsing errors, which differs from the project's convention of exit code 1. This is standard Python behaviour and is acceptable — document it in the user-facing help if needed.
- **Assumption**: The default filename `<video_id>.txt` is written to the current working directory. If the cwd is read-only, the write will fail. This is a known limitation documented in the project's `Known Risks` section.
- **Open question**: Should `main.py` support a `--version` flag? Deferred to a future sub-plan.
