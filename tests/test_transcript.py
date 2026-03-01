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
        mock_api_cls.return_value.fetch.side_effect = CouldNotRetrieveTranscript(self._VIDEO_ID)
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


class TestSaveTranscript:
    """Tests for save_transcript using pytest's tmp_path fixture."""

    def test_creates_file(self, tmp_path: pytest.TempPathFactory) -> None:
        out = tmp_path / "transcript.txt"
        save_transcript("Hello, world!", str(out))
        assert out.exists()

    def test_file_contents_match(self, tmp_path: pytest.TempPathFactory) -> None:
        out = tmp_path / "transcript.txt"
        save_transcript("Line one\nLine two", str(out))
        assert out.read_text(encoding="utf-8") == "Line one\nLine two"

    def test_utf8_encoding(self, tmp_path: pytest.TempPathFactory) -> None:
        text = "こんにちは\n日本語テスト\U0001F600"
        out = tmp_path / "unicode.txt"
        save_transcript(text, str(out))
        assert out.read_text(encoding="utf-8") == text

    def test_overwrites_existing_file(self, tmp_path: pytest.TempPathFactory) -> None:
        out = tmp_path / "transcript.txt"
        out.write_text("old content", encoding="utf-8")
        save_transcript("new content", str(out))
        assert out.read_text(encoding="utf-8") == "new content"

    def test_missing_parent_dir_raises_os_error(self, tmp_path: pytest.TempPathFactory) -> None:
        out = tmp_path / "nonexistent" / "transcript.txt"
        with pytest.raises(OSError):
            save_transcript("text", str(out))


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
        tmp_path: pytest.TempPathFactory,
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
        tmp_path: pytest.TempPathFactory,
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


class TestMain:
    """Tests for the main() CLI entry point."""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_success_exit_code_zero(
        self, mock_extract: MagicMock, mock_get: MagicMock,
        tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
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
        self, mock_extract: MagicMock, mock_get: MagicMock,
        tmp_path: pytest.TempPathFactory
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
        self, mock_extract: MagicMock, mock_get: MagicMock,
        tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
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
        tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch,
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
        self, tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
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


@pytest.mark.integration
class TestIntegration:
    """Integration tests that make real network calls to YouTube.

    Run with: .venv/bin/pytest tests/ -m integration -v
    Skipped by default: .venv/bin/pytest tests/ -m "not integration" -v
    """

    # "Me at the zoo" — the first YouTube video, a reliable test fixture.
    KNOWN_VIDEO_ID = "jNQXAC9IVRw"
    KNOWN_VIDEO_URL = f"https://www.youtube.com/watch?v={KNOWN_VIDEO_ID}"

    def test_fetch_known_video(self, tmp_path: pytest.TempPathFactory) -> None:
        out = str(tmp_path / f"{self.KNOWN_VIDEO_ID}.txt")
        text = get_transcript(self.KNOWN_VIDEO_URL, out)
        assert len(text) > 0
        assert (tmp_path / f"{self.KNOWN_VIDEO_ID}.txt").exists()

    def test_invalid_url_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            get_transcript("https://vimeo.com/jNQXAC9IVRw", "unused.txt")
