> ⛔ **HUMAN GATE** — Do not implement this plan until a human has reviewed it and moved it to `plans/pending/`.

# Sub-plan 06: Create the Full Pytest Test Suite in `tests/`

### Problem Statement
Create the complete pytest test suite in `tests/` covering all 4 public functions in `transcript.py`, the CLI in `main.py`, and one integration-gated class for real-network verification, ensuring 100% branch coverage on `extract_video_id` with no real network calls in unit tests.

### Prerequisites
- `04-transcript-core-module.md` — `transcript.py` with all 4 public functions must exist.
- `05-main-cli-entry-point.md` — `main.py` with `main(argv=None)` must exist.

### Files Affected
| File Path | Action | Description |
|-----------|--------|-------------|
| `tests/__init__.py` | Create | Empty package marker so pytest collects the `tests/` directory |
| `tests/test_transcript.py` | Overwrite | Full pytest suite with 6 test classes (file already exists from plan 04; this plan replaces it with the complete suite) |
| `tests/conftest.py` | Create | Registers the `integration` marker to suppress `PytestUnknownMarkWarning` |
| `.claude/agents/tester-agent.md` | Update | Add Phase 3 lint section (ruff + pylint) so quality checks run on every future task |

### Steps

1. **Create the `tests/` directory** if it does not exist:
   ```bash
   mkdir -p /home/oniwa/PycharmProjects/youtube_transcript/tests
   ```
   - Success: directory exists.

2. **Create `tests/__init__.py`** as a completely empty file (zero bytes or a single newline — no imports, no content):
   - Success: file exists; `wc -c tests/__init__.py` reports 0 or 1 byte.

3. **Install pytest** into the virtual environment if not already present:
   ```bash
   .venv/bin/pip install pytest pytest-cov
   ```
   - Success: `.venv/bin/pytest --version` exits with code 0.
   - Note: tests use `unittest.mock` (stdlib); `pytest-mock` is not required and should not be installed.

4. **Create `tests/test_transcript.py`** and write the file header:
   ```python
   """
   test_transcript.py — Pytest test suite for the YouTube transcript tool.

   Unit tests use mocks; no real network calls are made outside of
   tests decorated with @pytest.mark.integration.
   """
   from __future__ import annotations

   import pytest
   from unittest.mock import MagicMock, patch

   import transcript
   from transcript import (
       extract_video_id,
       fetch_transcript,
       get_transcript,
       save_transcript,
   )
   from youtube_transcript_api._errors import (
       CouldNotRetrieveTranscript,
       NoTranscriptFound,
       TranscriptsDisabled,
       VideoUnavailable,
   )
   from main import main
   ```
   - Success: file exists with the import block.

5. **Implement `TestExtractVideoId`** — 100% branch coverage on all URL formats and invalid inputs:
   ```python
   class TestExtractVideoId:
       """Tests for extract_video_id covering all supported URL formats."""

       def test_bare_id(self) -> None:
           assert extract_video_id("jNQXAC9IVRw") == "jNQXAC9IVRw"

       def test_standard_watch_url(self) -> None:
           assert extract_video_id("https://www.youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"

       def test_watch_url_with_extra_params(self) -> None:
           url = "https://www.youtube.com/watch?v=jNQXAC9IVRw&t=30s&list=PLabc"
           assert extract_video_id(url) == "jNQXAC9IVRw"

       def test_youtu_be_short_url(self) -> None:
           assert extract_video_id("https://youtu.be/jNQXAC9IVRw") == "jNQXAC9IVRw"

       def test_youtu_be_with_query_params(self) -> None:
           assert extract_video_id("https://youtu.be/jNQXAC9IVRw?t=30") == "jNQXAC9IVRw"

       def test_shorts_url(self) -> None:
           assert extract_video_id("https://www.youtube.com/shorts/jNQXAC9IVRw") == "jNQXAC9IVRw"

       def test_mobile_url(self) -> None:
           assert extract_video_id("https://m.youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"

       def test_invalid_empty_string_raises(self) -> None:
           with pytest.raises(ValueError, match="11-character"):
               extract_video_id("")

       def test_invalid_non_youtube_url_raises(self) -> None:
           with pytest.raises(ValueError, match="11-character"):
               extract_video_id("https://vimeo.com/jNQXAC9IVRw")

       def test_invalid_too_short_raises(self) -> None:
           with pytest.raises(ValueError):
               extract_video_id("abc123")

       def test_invalid_too_long_raises(self) -> None:
           with pytest.raises(ValueError):
               extract_video_id("jNQXAC9IVRwXXX")

       def test_watch_url_missing_v_param_raises(self) -> None:
           with pytest.raises(ValueError):
               extract_video_id("https://www.youtube.com/watch?list=PLabc")
   ```
   - Success: all methods are present; `pytest tests/test_transcript.py::TestExtractVideoId -v` collects 12 tests.

6. **Implement `TestFetchTranscript`** — all 4 API error types and unknown exceptions, all mocked:
   ```python
   class TestFetchTranscript:
       """Tests for fetch_transcript using mocked YouTubeTranscriptApi."""

       _VIDEO_ID = "jNQXAC9IVRw"

       def _make_snippet(self, text: str) -> MagicMock:
           snippet = MagicMock()
           snippet.text = text
           return snippet

       @patch("transcript.YouTubeTranscriptApi")
       def test_successful_fetch_joins_with_newline(self, mock_api_cls: MagicMock) -> None:
           snippets = [self._make_snippet("Hello"), self._make_snippet("World")]
           mock_api_cls.return_value.fetch.return_value = snippets
           result = fetch_transcript(self._VIDEO_ID)
           assert result == "Hello\nWorld"

       @patch("transcript.YouTubeTranscriptApi")
       def test_successful_fetch_with_languages(self, mock_api_cls: MagicMock) -> None:
           snippets = [self._make_snippet("Bonjour")]
           mock_api_cls.return_value.fetch.return_value = snippets
           result = fetch_transcript(self._VIDEO_ID, languages=["fr", "en"])
           mock_api_cls.return_value.fetch.assert_called_once_with(
               self._VIDEO_ID, languages=["fr", "en"]
           )
           assert result == "Bonjour"

       @patch("transcript.YouTubeTranscriptApi")
       def test_raises_transcripts_disabled(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.side_effect = TranscriptsDisabled(self._VIDEO_ID)
           with pytest.raises(TranscriptsDisabled):
               fetch_transcript(self._VIDEO_ID)

       @patch("transcript.YouTubeTranscriptApi")
       def test_raises_no_transcript_found(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.side_effect = NoTranscriptFound(
               self._VIDEO_ID, ["en"], {}
           )
           with pytest.raises(NoTranscriptFound):
               fetch_transcript(self._VIDEO_ID)

       @patch("transcript.YouTubeTranscriptApi")
       def test_raises_video_unavailable(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.side_effect = VideoUnavailable(self._VIDEO_ID)
           with pytest.raises(VideoUnavailable):
               fetch_transcript(self._VIDEO_ID)

       @patch("transcript.YouTubeTranscriptApi")
       def test_raises_could_not_retrieve_transcript(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.side_effect = CouldNotRetrieveTranscript(
               self._VIDEO_ID
           )
           with pytest.raises(CouldNotRetrieveTranscript):
               fetch_transcript(self._VIDEO_ID)

       @patch("transcript.YouTubeTranscriptApi")
       def test_unknown_exception_wrapped_in_runtime_error(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.side_effect = Exception("network failure")
           with pytest.raises(RuntimeError, match="network failure"):
               fetch_transcript(self._VIDEO_ID)

       @patch("transcript.YouTubeTranscriptApi")
       def test_empty_transcript_returns_empty_string(self, mock_api_cls: MagicMock) -> None:
           mock_api_cls.return_value.fetch.return_value = []
           result = fetch_transcript(self._VIDEO_ID)
           assert result == ""
   ```
   - Success: all 8 methods are present covering all 4 error types plus success, unknown exception, empty transcript, and language forwarding.

7. **Implement `TestSaveTranscript`** — file I/O tests using `tmp_path`:
   ```python
   class TestSaveTranscript:
       """Tests for save_transcript using pytest's tmp_path fixture."""

       def test_creates_file(self, tmp_path: pytest.TempdirFactory) -> None:
           out = tmp_path / "transcript.txt"
           save_transcript("Hello, world!", str(out))
           assert out.exists()

       def test_file_contents_match(self, tmp_path: pytest.TempdirFactory) -> None:
           out = tmp_path / "transcript.txt"
           save_transcript("Line one\nLine two", str(out))
           assert out.read_text(encoding="utf-8") == "Line one\nLine two"

       def test_utf8_encoding(self, tmp_path: pytest.TempdirFactory) -> None:
           text = "こんにちは\n日本語テスト\U0001F600"
           out = tmp_path / "unicode.txt"
           save_transcript(text, str(out))
           assert out.read_text(encoding="utf-8") == text

       def test_overwrites_existing_file(self, tmp_path: pytest.TempdirFactory) -> None:
           out = tmp_path / "transcript.txt"
           out.write_text("old content", encoding="utf-8")
           save_transcript("new content", str(out))
           assert out.read_text(encoding="utf-8") == "new content"

       def test_missing_parent_dir_raises_os_error(self, tmp_path: pytest.TempdirFactory) -> None:
           out = tmp_path / "nonexistent" / "transcript.txt"
           with pytest.raises(OSError):
               save_transcript("text", str(out))
   ```
   - Success: all 5 methods present; file I/O uses `tmp_path` exclusively.

8. **Implement `TestGetTranscript`** — end-to-end wrapper with fully mocked dependencies:
   ```python
   class TestGetTranscript:
       """Tests for get_transcript with mocked sub-functions."""

       @patch("transcript.save_transcript")
       @patch("transcript.fetch_transcript")
       @patch("transcript.extract_video_id")
       def test_end_to_end_calls_all_three(
           self,
           mock_extract: MagicMock,
           mock_fetch: MagicMock,
           mock_save: MagicMock,
           tmp_path: pytest.TempdirFactory,
       ) -> None:
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_fetch.return_value = "transcript text"
           out = str(tmp_path / "out.txt")
           result = get_transcript("https://youtu.be/jNQXAC9IVRw", out)
           mock_extract.assert_called_once_with("https://youtu.be/jNQXAC9IVRw")
           mock_fetch.assert_called_once_with("jNQXAC9IVRw", languages=None)
           mock_save.assert_called_once_with("transcript text", out)
           assert result == "transcript text"

       @patch("transcript.save_transcript")
       @patch("transcript.fetch_transcript")
       @patch("transcript.extract_video_id")
       def test_passes_languages_to_fetch(
           self,
           mock_extract: MagicMock,
           mock_fetch: MagicMock,
           mock_save: MagicMock,
           tmp_path: pytest.TempdirFactory,
       ) -> None:
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_fetch.return_value = "text"
           out = str(tmp_path / "out.txt")
           get_transcript("jNQXAC9IVRw", out, languages=["fr"])
           mock_fetch.assert_called_once_with("jNQXAC9IVRw", languages=["fr"])

       @patch("transcript.extract_video_id")
       def test_propagates_value_error(self, mock_extract: MagicMock) -> None:
           mock_extract.side_effect = ValueError("bad url")
           with pytest.raises(ValueError, match="bad url"):
               get_transcript("bad", "out.txt")
   ```
   - Success: all 3 methods present; all sub-functions are mocked; `get_transcript` itself is not mocked.

9. **Implement `TestMain`** — CLI tests using argparse and `monkeypatch`:
   ```python
   class TestMain:
       """Tests for the main() CLI entry point."""

       @patch("main.get_transcript")
       @patch("main.extract_video_id")
       def test_success_exit_code_zero(
           self, mock_extract: MagicMock, mock_get: MagicMock, tmp_path: pytest.TempdirFactory, monkeypatch: pytest.MonkeyPatch
       ) -> None:
           monkeypatch.chdir(tmp_path)
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_get.return_value = "transcript text"
           result = main(["https://youtu.be/jNQXAC9IVRw"])
           assert result == 0

       @patch("main.extract_video_id")
       def test_invalid_url_exit_code_one(
           self, mock_extract: MagicMock, capsys: pytest.CaptureFixture
       ) -> None:
           mock_extract.side_effect = ValueError("bad url")
           result = main(["https://vimeo.com/12345"])
           assert result == 1
           captured = capsys.readouterr()
           assert "Error" in captured.err

       @patch("main.get_transcript")
       @patch("main.extract_video_id")
       def test_custom_output_path(
           self, mock_extract: MagicMock, mock_get: MagicMock, tmp_path: pytest.TempdirFactory
       ) -> None:
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_get.return_value = "text"
           out = str(tmp_path / "custom.txt")
           result = main(["https://youtu.be/jNQXAC9IVRw", "--output", out])
           assert result == 0
           mock_get.assert_called_once_with(
               "https://youtu.be/jNQXAC9IVRw", out, languages=None
           )

       @patch("main.get_transcript")
       @patch("main.extract_video_id")
       def test_lang_flag_forwarded(
           self, mock_extract: MagicMock, mock_get: MagicMock, tmp_path: pytest.TempdirFactory, monkeypatch: pytest.MonkeyPatch
       ) -> None:
           monkeypatch.chdir(tmp_path)
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_get.return_value = "text"
           result = main(["https://youtu.be/jNQXAC9IVRw", "--lang", "en", "--lang", "fr"])
           assert result == 0
           mock_get.assert_called_once_with(
               "https://youtu.be/jNQXAC9IVRw",
               "jNQXAC9IVRw.txt",
               languages=["en", "fr"],
           )

       @patch("main.get_transcript")
       @patch("main.extract_video_id")
       def test_transcripts_disabled_exit_one(
           self, mock_extract: MagicMock, mock_get: MagicMock,
           tmp_path: pytest.TempdirFactory, monkeypatch: pytest.MonkeyPatch,
           capsys: pytest.CaptureFixture
       ) -> None:
           monkeypatch.chdir(tmp_path)
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_get.side_effect = TranscriptsDisabled("jNQXAC9IVRw")
           result = main(["https://youtu.be/jNQXAC9IVRw"])
           assert result == 1
           assert "Error" in capsys.readouterr().err

       @patch("main.get_transcript")
       @patch("main.extract_video_id")
       def test_os_error_exit_one(
           self, mock_extract: MagicMock, mock_get: MagicMock,
           monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
       ) -> None:
           mock_extract.return_value = "jNQXAC9IVRw"
           mock_get.side_effect = OSError("permission denied")
           result = main(["https://youtu.be/jNQXAC9IVRw", "--output", "/ro/out.txt"])
           assert result == 1
           assert "Error" in capsys.readouterr().err

       def test_default_output_filename_uses_video_id(
           self, tmp_path: pytest.TempdirFactory, monkeypatch: pytest.MonkeyPatch
       ) -> None:
           monkeypatch.chdir(tmp_path)
           with patch("main.get_transcript") as mock_get, \
                patch("main.extract_video_id") as mock_extract:
               mock_extract.return_value = "jNQXAC9IVRw"
               mock_get.return_value = "text"
               main(["https://youtu.be/jNQXAC9IVRw"])
               mock_get.assert_called_once_with(
                   "https://youtu.be/jNQXAC9IVRw",
                   "jNQXAC9IVRw.txt",
                   languages=None,
               )
   ```
   - Success: all 7 methods present; `monkeypatch.chdir(tmp_path)` used for default filename tests.

10. **Implement `TestIntegration`** — real network tests gated by marker:
    ```python
    @pytest.mark.integration
    class TestIntegration:
        """Integration tests that make real network calls to YouTube.

        Run with: .venv/bin/pytest tests/ -m integration -v
        Skipped by default: .venv/bin/pytest tests/ -m "not integration" -v
        """

        # "Me at the zoo" — the first YouTube video, a reliable test fixture.
        KNOWN_VIDEO_ID = "jNQXAC9IVRw"
        KNOWN_VIDEO_URL = f"https://www.youtube.com/watch?v={KNOWN_VIDEO_ID}"

        def test_fetch_known_video(self, tmp_path: pytest.TempdirFactory) -> None:
            out = str(tmp_path / f"{self.KNOWN_VIDEO_ID}.txt")
            text = get_transcript(self.KNOWN_VIDEO_URL, out)
            assert len(text) > 0
            assert (tmp_path / f"{self.KNOWN_VIDEO_ID}.txt").exists()

        def test_invalid_url_raises_value_error(self) -> None:
            with pytest.raises(ValueError):
                get_transcript("https://vimeo.com/jNQXAC9IVRw", "unused.txt")
    ```
    - Success: both methods are decorated with `@pytest.mark.integration`; they are skipped when running with `-m "not integration"`.

11. **Add `conftest.py`** to register the `integration` marker and suppress the `PytestUnknownMarkWarning`:
    ```python
    # tests/conftest.py
    import pytest

    def pytest_configure(config: pytest.Config) -> None:
        config.addinivalue_line(
            "markers", "integration: marks tests as requiring a real network connection"
        )
    ```
    Create this file at `tests/conftest.py`.
    - Success: `.venv/bin/pytest tests/ -m "not integration" -v` runs without `PytestUnknownMarkWarning`.

12. **Run the unit test suite** to verify the test file is collected without syntax errors:
    ```bash
    .venv/bin/pytest tests/ -m "not integration" -v --collect-only
    ```
    - Success: all 6 test classes are collected with no collection errors (some tests may show as errors if `transcript.py` or `main.py` are not yet implemented, but collection must succeed).

13. **Run the full unit test suite** (tests may fail if implementation is incomplete — that is acceptable at this stage):
    ```bash
    .venv/bin/pytest tests/ -m "not integration" -v
    ```
    - Success: command runs without crashing; output shows collected test counts.

14. **Run ruff lint check** on `tests/test_transcript.py`:
    ```bash
    .venv/bin/ruff check tests/test_transcript.py
    ```
    - Success: command exits with code 0 and outputs `All checks passed!` (zero findings).
    - If ruff is not installed: `.venv/bin/pip install ruff` first.

15. **Run pylint** on `tests/test_transcript.py`:
    ```bash
    .venv/bin/pylint tests/test_transcript.py
    ```
    - Success: pylint exits with a score of `10.00/10` and zero findings.
    - If pylint is not installed: `.venv/bin/pip install pylint` first.

16. **Update `tester-agent.md`** to add a permanent Phase 3 lint step so all future test runs include quality checks:
    - Append the following section to `.claude/agents/tester-agent.md` after Phase 2:
    ```markdown
    ## Phase 3 — Lint

    After the test suite passes, run lint checks on all modified source and test files:

    ```bash
    # Ruff (zero findings required)
    .venv/bin/ruff check <files>

    # Pylint (10.00/10 required)
    .venv/bin/pylint <files>
    ```

    Report any lint findings to the orchestrator as failures. Do not mark a task complete
    if ruff or pylint produce any findings.
    ```
    - Files Affected: `.claude/agents/tester-agent.md`
    - Success: the Phase 3 section is present in the agent file.

### Edge Cases

- **Input**: `TestFetchTranscript` uses `NoTranscriptFound(video_id, languages, transcripts_dict)` — the exact constructor signature may differ between `youtube-transcript-api` versions. Verify the constructor arguments against the installed `==1.2.4` version before finalising the test.
- **Input**: `TestFetchTranscript` uses `CouldNotRetrieveTranscript(video_id)` — verify the constructor signature against the installed `==1.2.4` version. `NoTranscriptAvailable` does not exist in 1.2.4; `CouldNotRetrieveTranscript` is the correct base class.
- **Runtime**: Real network tests (`TestIntegration`) may fail if YouTube rate-limits the IP or the video becomes unavailable. These tests are non-blocking by design (gated by the `integration` marker).
- **Runtime**: `monkeypatch.chdir(tmp_path)` changes the working directory for the duration of one test — verify that subsequent tests are not affected by checking that cwd is restored after each test (pytest's `monkeypatch` fixture handles this automatically).
- **Environment**: `pytest` not installed in `.venv` — Step 3 installs it; if skipped, test collection will fail with `ModuleNotFoundError`. `pytest-mock` is not used; tests rely on `unittest.mock` (stdlib).
- **Environment**: Test file imports `from main import main` — if `main.py` has a top-level import that fails (e.g., `transcript.py` not present), the entire test file will fail to collect. Ensure `04-transcript-core-module.md` is completed before this sub-plan.

### Acceptance Criteria

- `tests/__init__.py` exists and is empty (0 or 1 byte).
- `tests/test_transcript.py` exists and defines exactly 6 test classes: `TestExtractVideoId`, `TestFetchTranscript`, `TestSaveTranscript`, `TestGetTranscript`, `TestMain`, `TestIntegration`.
- `tests/conftest.py` exists and registers the `integration` marker.
- `.venv/bin/pytest tests/ -m "not integration" -v --collect-only` collects at least 35 test items without errors.
- `.venv/bin/pytest tests/ -m "not integration" -v` runs without a crash (individual test failures are acceptable if `transcript.py` or `main.py` are not yet implemented).
- `TestExtractVideoId` has at least 12 test methods covering all URL formats (watch, youtu.be, shorts, mobile), bare IDs, and invalid inputs.
- `TestFetchTranscript` tests all 4 API error types plus success, unknown exception, and empty transcript cases — all with mocked API.
- `TestSaveTranscript` uses `tmp_path` for all file paths.
- `TestMain` uses `monkeypatch.chdir(tmp_path)` for default filename tests and `capsys` for stderr assertions.
- `TestIntegration` methods are decorated with `@pytest.mark.integration` and are excluded when running `-m "not integration"`.
- `.venv/bin/ruff check tests/test_transcript.py` exits with code 0 (zero findings).
- `.venv/bin/pylint tests/test_transcript.py` reports `10.00/10` (zero findings).
- `.claude/agents/tester-agent.md` contains a Phase 3 lint section covering ruff and pylint.

### Risks

- **Constructor argument mismatch**: The exact signatures for `NoTranscriptFound`, `CouldNotRetrieveTranscript`, `TranscriptsDisabled`, and `VideoUnavailable` may differ from what is documented. Run `.venv/bin/python -c "import inspect; from youtube_transcript_api._errors import NoTranscriptFound, CouldNotRetrieveTranscript; print(inspect.signature(NoTranscriptFound)); print(inspect.signature(CouldNotRetrieveTranscript))"` to verify before finalising the test code. Note: `NoTranscriptAvailable` does not exist in `==1.2.4`; use `CouldNotRetrieveTranscript` instead.
- **Mock patch path**: The mock target `"transcript.YouTubeTranscriptApi"` patches the name as it appears in the `transcript` module's namespace. If the import in `transcript.py` is ever changed to `import youtube_transcript_api; youtube_transcript_api.YouTubeTranscriptApi(...)`, the patch path must be updated to `"youtube_transcript_api.YouTubeTranscriptApi"`.
- **Assumption**: `TestIntegration` uses `"jNQXAC9IVRw"` (the first YouTube video) as a stable test fixture. If this video is deleted or its transcript is disabled, the integration test will fail. Mitigation: keep a backup video ID in a comment.
- **Open question**: Should the test suite use `pytest-cov` for coverage enforcement (e.g., `--cov-fail-under=90`)? Deferred — coverage is run manually per the Verification commands in the parent plan.
