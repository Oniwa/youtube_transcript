# 03 — main.py CLI Entry Point

### Problem Statement
Rewrite `main.py` as the CLI entry point using `argparse`, delegating all business logic to `transcript.py` and handling user-facing output and error formatting.

### Prerequisites
- `02-transcript-core-module.md` (`transcript.py` must exist with its public API)

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `main.py` | Rewrite | Replace PyCharm boilerplate with argparse-based CLI |

### Steps
1. Remove all existing content from `main.py` and add a module-level docstring describing it as the CLI entry point.
   - **Success**: File contains only the new docstring and no PyCharm boilerplate.
2. Add imports: `argparse`, `sys`, and from `transcript` import `extract_video_id`, `get_transcript`.
   - **Success**: All imports are present.
3. Create `def main(argv: list[str] | None = None) -> int` function with a docstring. It must accept an optional `argv` parameter for testability and return an integer exit code.
   - **Success**: Function exists with correct signature, type hints, and docstring.
4. Inside `main`, set up `argparse.ArgumentParser` with a description. Add positional argument `url` (the YouTube URL or video ID).
   - **Success**: Parser accepts a positional `url` argument.
5. Add optional argument `--output` / `-o` for the output file path. Default should be `None` (will be computed as `<video_id>.txt`).
   - **Success**: `--output` / `-o` flag is defined and defaults to `None`.
6. Add optional argument `--lang` / `-l` for transcript language codes, accepting one or more values (`nargs="+"` or similar).
   - **Success**: `--lang` / `-l` flag is defined and accepts multiple values.
7. Parse `argv` with the parser. If `--output` is `None`, compute default filename as `<video_id>.txt` using `extract_video_id`.
   - **Success**: Default output filename is `<video_id>.txt`.
8. Call `get_transcript(url, output_path, languages)` inside a `try/except` block. Catch `ValueError`, known transcript API errors, and `RuntimeError`. Print error messages to `sys.stderr` and return exit code `1`.
   - **Success**: All expected error types are caught, printed to stderr, and cause exit code 1.
9. On success, print a confirmation message to `sys.stdout` (e.g., `"Transcript saved to <path>"`) and return exit code `0`.
   - **Success**: Successful run prints to stdout and returns 0.
10. Add the `if __name__ == "__main__":` block that calls `sys.exit(main())`.
    - **Success**: Running `python main.py` invokes `main()` and exits with its return code.
11. Ensure `main.py` contains no business logic — no URL parsing, no transcript fetching, no file writing beyond what `transcript.py` provides.
    - **Success**: All logic is delegated to `transcript.py`; `main.py` only handles CLI concerns.

### Edge Cases
- **Input**: No arguments provided — `argparse` should print usage and exit with code 2.
- **Input**: Invalid URL (e.g., a Vimeo link) — `ValueError` from `extract_video_id` is caught, message printed to stderr, exit code 1.
- **Runtime**: `get_transcript` raises `RuntimeError` (e.g., IP blocked) — error message printed to stderr, exit code 1.
- **Environment**: Output directory does not exist or is read-only — `OSError` should be caught and reported to stderr with exit code 1.

### Acceptance Criteria
- `main.py` uses `argparse` with positional `url` and optional `--output`/`-o` and `--lang`/`-l` arguments.
- `main(argv=None)` signature allows testable invocation.
- `main()` returns `int` (0 for success, 1 for errors).
- Error messages go to `sys.stderr`; success messages go to `sys.stdout`.
- Default output filename is `<video_id>.txt`.
- No business logic in `main.py` — all delegated to `transcript.py`.
- `python main.py --help` prints usage information without error.

### Risks
- If `extract_video_id` is called separately to compute the default filename before `get_transcript`, the ID extraction happens twice. This is acceptable for simplicity.
- The `OSError` catch for disk/permission errors is not explicitly named in the source plan but is noted as a "future improvement." Including it here is a defensive addition.
