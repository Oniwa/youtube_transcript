# 04 — Test Suite Structure

### Problem Statement
Create the test directory and test file structure with pytest test classes and test method stubs for full coverage of `transcript.py` and `main.py`, deferring detailed test implementation to the test-planning-agent.

### Prerequisites
- `02-transcript-core-module.md` (`transcript.py` must exist for import references)
- `03-main-cli-entry-point.md` (`main.py` must exist for import references)

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `tests/__init__.py` | Create | Empty package init file |
| `tests/test_transcript.py` | Create | Pytest test file with class structure and method stubs |

### Steps
1. Create the `tests/` directory if it does not exist.
   - **Success**: Directory exists at `/home/oniwa/PycharmProjects/youtube_transcript/tests/`.
2. Create `tests/__init__.py` as an empty file.
   - **Success**: File exists and is empty.
3. Create `tests/test_transcript.py` with module-level docstring and necessary imports: `pytest`, `pathlib.Path`, `unittest.mock.patch`, `unittest.mock.MagicMock`, and imports from `transcript` module.
   - **Success**: File exists with all imports.
4. Define class `TestExtractVideoId` with stub test methods for: standard watch URL, short URL, Shorts URL, mobile URL, bare video ID, invalid URL raising `ValueError`, empty string raising `ValueError`, URL with extra query params.
   - **Success**: Class exists with at least 8 stub methods.
5. Define class `TestFetchTranscript` with stub test methods for: successful fetch returns joined text, fetch with language parameter, `TranscriptsDisabled` re-raised, `NoTranscriptFound` re-raised, `VideoUnavailable` re-raised, unknown error wrapped in `RuntimeError`.
   - **Success**: Class exists with at least 6 stub methods.
6. Define class `TestSaveTranscript` with stub test methods for: file written with correct content, UTF-8 encoding, returns `Path` object, nonexistent directory raises `OSError`.
   - **Success**: Class exists with at least 4 stub methods.
7. Define class `TestGetTranscript` with stub test methods for: end-to-end with mocked dependencies, error propagation from each sub-function.
   - **Success**: Class exists with at least 3 stub methods.
8. Define class `TestMain` with stub test methods for: successful run returns 0, invalid URL returns 1, API error returns 1, default output filename, custom output flag, language flag, help flag.
   - **Success**: Class exists with at least 6 stub methods.
9. Define class `TestIntegration` marked with `@pytest.mark.integration` at the class level, with stub test methods for: real transcript fetch (gated behind marker), real file save.
   - **Success**: Class exists with the `integration` marker and at least 2 stub methods.
10. Each stub method should contain a single `pytest.skip("Not implemented — awaiting test-planning-agent")` call as its body, making the test suite runnable but explicitly deferred.
    - **Success**: Running `.venv/bin/pytest tests/ -m "not integration" -v` shows all tests as skipped with the expected message.
11. Verify the full test file is syntactically valid by running `.venv/bin/python -c "import tests.test_transcript"`.
    - **Success**: Import succeeds without errors.
12. Install `pytest` into the virtual environment if not already present: `.venv/bin/pip install pytest`.
    - **Success**: `pytest` is importable from `.venv`.

### Edge Cases
- **Input**: Test stubs must not contain any real assertions — they exist solely to define the structure for the test-planning-agent.
- **Runtime**: `pytest` not installed in `.venv` — step 12 handles this explicitly.
- **Environment**: `tests/` directory might already exist from a prior run — step 1 must be idempotent.

### Acceptance Criteria
- `tests/__init__.py` exists and is empty.
- `tests/test_transcript.py` exists and is syntactically valid.
- Six test classes are defined: `TestExtractVideoId`, `TestFetchTranscript`, `TestSaveTranscript`, `TestGetTranscript`, `TestMain`, `TestIntegration`.
- All test methods are stubs containing `pytest.skip(...)`.
- `TestIntegration` is decorated with `@pytest.mark.integration`.
- `.venv/bin/pytest tests/ -m "not integration" -v` runs without errors (all tests skip).
- Total stub count is at least 29 test methods.

### Risks
- The test-planning-agent is responsible for filling in real test implementations. If stub names do not align with final function signatures, they will need updating. Mitigation: stubs reference the functions defined in sub-plan 02 and 03.
- `pytest-cov` is not installed in this sub-plan. Coverage measurement is a verification step described in the source plan but is deferred until test implementations exist.
