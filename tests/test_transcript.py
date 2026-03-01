"""
tests/test_transcript.py — Unit tests for the transcript.py core logic module.

All tests are isolated (no real network calls). The youtube_transcript_api is
mocked via unittest.mock where network interaction would otherwise occur.
"""
from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

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


# ---------------------------------------------------------------------------
# extract_video_id
# ---------------------------------------------------------------------------

class TestExtractVideoId:
    """Tests for extract_video_id()."""

    VALID_ID = "jNQXAC9IVRw"

    def test_bare_id_returned_as_is(self) -> None:
        """A bare 11-character alphanumeric/dash/underscore ID is returned unchanged."""
        assert extract_video_id(self.VALID_ID) == self.VALID_ID

    def test_bare_id_with_dashes_and_underscores(self) -> None:
        """An 11-char ID using dashes and underscores is accepted."""
        assert extract_video_id("abc-_defGHI") == "abc-_defGHI"

    def test_standard_watch_url(self) -> None:
        """Standard youtube.com/watch?v=<id> URL extracts the ID correctly."""
        url = f"https://www.youtube.com/watch?v={self.VALID_ID}"
        assert extract_video_id(url) == self.VALID_ID

    def test_www_youtube_watch_url(self) -> None:
        """www.youtube.com watch URL is handled."""
        assert extract_video_id(
            f"https://www.youtube.com/watch?v={self.VALID_ID}&feature=share"
        ) == self.VALID_ID

    def test_mobile_youtube_watch_url(self) -> None:
        """m.youtube.com watch URL is handled."""
        assert extract_video_id(
            f"https://m.youtube.com/watch?v={self.VALID_ID}"
        ) == self.VALID_ID

    def test_youtu_be_short_url(self) -> None:
        """youtu.be/<id> short URL extracts the ID correctly."""
        assert extract_video_id(f"https://youtu.be/{self.VALID_ID}") == self.VALID_ID

    def test_shorts_url(self) -> None:
        """youtube.com/shorts/<id> URL extracts the ID correctly."""
        assert extract_video_id(
            f"https://www.youtube.com/shorts/{self.VALID_ID}"
        ) == self.VALID_ID

    def test_youtube_without_www(self) -> None:
        """youtube.com (no www) watch URL is handled."""
        assert extract_video_id(
            f"https://youtube.com/watch?v={self.VALID_ID}"
        ) == self.VALID_ID

    def test_empty_string_raises_value_error(self) -> None:
        """An empty string raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("")

    def test_non_youtube_url_raises_value_error(self) -> None:
        """A non-YouTube URL raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id(f"https://vimeo.com/{self.VALID_ID}")

    def test_too_short_id_raises_value_error(self) -> None:
        """A 10-character string is rejected (not 11 chars)."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("short1234X")

    def test_too_long_id_raises_value_error(self) -> None:
        """A 12-character string is rejected (not 11 chars)."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("toolongid123")

    def test_id_with_invalid_chars_raises_value_error(self) -> None:
        """An 11-char string with invalid characters (!) raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("jNQXAC9IV!w")

    def test_error_message_contains_input(self) -> None:
        """The ValueError message contains the offending input."""
        bad = "not-a-real-url"
        with pytest.raises(ValueError, match="not-a-real-url"):
            extract_video_id(bad)

    def test_plain_string_not_11_chars_raises_value_error(self) -> None:
        """A plain string that is not 11 chars and not a URL raises ValueError."""
        with pytest.raises(ValueError, match="Could not extract"):
            extract_video_id("hello")

    def test_shorts_url_without_www(self) -> None:
        """youtube.com/shorts/<id> without www is handled."""
        assert extract_video_id(
            f"https://youtube.com/shorts/{self.VALID_ID}"
        ) == self.VALID_ID


# ---------------------------------------------------------------------------
# fetch_transcript
# ---------------------------------------------------------------------------

class TestFetchTranscript:
    """Tests for fetch_transcript()."""

    VIDEO_ID = "jNQXAC9IVRw"

    def _make_snippet(self, text: str) -> MagicMock:
        """Create a mock snippet with a .text attribute."""
        snippet = MagicMock()
        snippet.text = text
        return snippet

    @patch("transcript.YouTubeTranscriptApi")
    def test_returns_joined_text(self, mock_api_cls: MagicMock) -> None:
        """Snippet texts are joined with newlines and returned."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = [
            self._make_snippet("Hello"),
            self._make_snippet("World"),
        ]
        result = fetch_transcript(self.VIDEO_ID)
        assert result == "Hello\nWorld"

    @patch("transcript.YouTubeTranscriptApi")
    def test_single_snippet(self, mock_api_cls: MagicMock) -> None:
        """A single snippet is returned without a trailing newline."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = [self._make_snippet("Only line")]
        result = fetch_transcript(self.VIDEO_ID)
        assert result == "Only line"

    @patch("transcript.YouTubeTranscriptApi")
    def test_empty_transcript_returns_empty_string(self, mock_api_cls: MagicMock) -> None:
        """Zero snippets produce an empty string."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = []
        result = fetch_transcript(self.VIDEO_ID)
        assert result == ""

    @patch("transcript.YouTubeTranscriptApi")
    def test_passes_languages_kwarg(self, mock_api_cls: MagicMock) -> None:
        """When languages is provided, it is forwarded to api.fetch()."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = [self._make_snippet("Hola")]
        fetch_transcript(self.VIDEO_ID, languages=["es"])
        mock_api.fetch.assert_called_once_with(self.VIDEO_ID, languages=["es"])

    @patch("transcript.YouTubeTranscriptApi")
    def test_no_languages_kwarg_when_none(self, mock_api_cls: MagicMock) -> None:
        """When languages is None, the languages kwarg is NOT passed to api.fetch()."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = [self._make_snippet("Hello")]
        fetch_transcript(self.VIDEO_ID, languages=None)
        # Only called with video_id, no languages kwarg
        mock_api.fetch.assert_called_once_with(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_reraises_transcripts_disabled(self, mock_api_cls: MagicMock) -> None:
        """TranscriptsDisabled is re-raised without wrapping."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.side_effect = TranscriptsDisabled(video_id=self.VIDEO_ID)
        with pytest.raises(TranscriptsDisabled):
            fetch_transcript(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_reraises_no_transcript_found(self, mock_api_cls: MagicMock) -> None:
        """NoTranscriptFound is re-raised without wrapping."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.side_effect = NoTranscriptFound(
            video_id=self.VIDEO_ID,
            requested_language_codes=["en"],
            transcript_data={},
        )
        with pytest.raises(NoTranscriptFound):
            fetch_transcript(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_reraises_video_unavailable(self, mock_api_cls: MagicMock) -> None:
        """VideoUnavailable is re-raised without wrapping."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.side_effect = VideoUnavailable(video_id=self.VIDEO_ID)
        with pytest.raises(VideoUnavailable):
            fetch_transcript(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_reraises_could_not_retrieve(self, mock_api_cls: MagicMock) -> None:
        """CouldNotRetrieveTranscript is re-raised without wrapping."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.side_effect = CouldNotRetrieveTranscript(video_id=self.VIDEO_ID)
        with pytest.raises(CouldNotRetrieveTranscript):
            fetch_transcript(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_wraps_unexpected_exception_in_runtime_error(
        self, mock_api_cls: MagicMock
    ) -> None:
        """An unexpected exception is wrapped in RuntimeError with a descriptive message."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.side_effect = ConnectionError("Network unreachable")
        with pytest.raises(RuntimeError, match=r"Unexpected error.*jNQXAC9IVRw"):
            fetch_transcript(self.VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_unicode_snippets(self, mock_api_cls: MagicMock) -> None:
        """Non-ASCII snippet text is joined correctly."""
        mock_api = mock_api_cls.return_value
        mock_api.fetch.return_value = [
            self._make_snippet("日本語"),
            self._make_snippet("العربية"),
            self._make_snippet("Emoji: "),
        ]
        result = fetch_transcript(self.VIDEO_ID)
        assert result == "日本語\nالعربية\nEmoji: "


# ---------------------------------------------------------------------------
# save_transcript
# ---------------------------------------------------------------------------

class TestSaveTranscript:
    """Tests for save_transcript()."""

    def test_writes_text_to_file(self) -> None:
        """The transcript text is written to the given output path."""
        with tempfile.NamedTemporaryFile(mode="r", suffix=".txt", delete=False) as fh:
            path = fh.name
        try:
            save_transcript("Hello, World!", path)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            assert content == "Hello, World!"
        finally:
            os.unlink(path)

    def test_writes_utf8_encoding(self) -> None:
        """Non-ASCII text (Japanese, Arabic, emoji) is written correctly in UTF-8."""
        text = "日本語\nالعربية\nEmoji: "
        with tempfile.NamedTemporaryFile(
            mode="rb", suffix=".txt", delete=False
        ) as fh:
            path = fh.name
        try:
            save_transcript(text, path)
            with open(path, "rb") as fh:
                raw = fh.read()
            assert raw == text.encode("utf-8")
        finally:
            os.unlink(path)

    def test_overwrites_existing_file(self) -> None:
        """Calling save_transcript twice overwrites the previous content."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as fh:
            fh.write("old content")
            path = fh.name
        try:
            save_transcript("new content", path)
            with open(path, encoding="utf-8") as fh:
                assert fh.read() == "new content"
        finally:
            os.unlink(path)

    def test_empty_string_creates_empty_file(self) -> None:
        """Saving an empty string produces an empty file."""
        with tempfile.NamedTemporaryFile(mode="r", suffix=".txt", delete=False) as fh:
            path = fh.name
        try:
            save_transcript("", path)
            with open(path, encoding="utf-8") as fh:
                assert fh.read() == ""
        finally:
            os.unlink(path)

    def test_raises_oserror_for_missing_parent_directory(self) -> None:
        """Writing to a path whose parent directory doesn't exist raises OSError."""
        with pytest.raises(OSError):
            save_transcript("hello", "/nonexistent_dir/transcript.txt")

    def test_returns_none(self) -> None:
        """save_transcript returns None."""
        with tempfile.NamedTemporaryFile(mode="r", suffix=".txt", delete=False) as fh:
            path = fh.name
        try:
            result = save_transcript("text", path)
            assert result is None
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# get_transcript
# ---------------------------------------------------------------------------

class TestGetTranscript:
    """Tests for get_transcript() end-to-end orchestration."""

    VALID_ID = "jNQXAC9IVRw"
    TRANSCRIPT_TEXT = "Line one\nLine two"

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_calls_all_three_functions_in_order(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """get_transcript calls extract_video_id, fetch_transcript, save_transcript."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.return_value = self.TRANSCRIPT_TEXT

        get_transcript("https://www.youtube.com/watch?v=jNQXAC9IVRw", "/tmp/out.txt")

        mock_extract.assert_called_once_with(
            "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        )
        mock_fetch.assert_called_once_with(self.VALID_ID, languages=None)
        mock_save.assert_called_once_with(self.TRANSCRIPT_TEXT, "/tmp/out.txt")

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_returns_transcript_text(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """get_transcript returns the fetched transcript text."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.return_value = self.TRANSCRIPT_TEXT

        result = get_transcript(self.VALID_ID, "/tmp/out.txt")
        assert result == self.TRANSCRIPT_TEXT

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_passes_languages_to_fetch(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """Languages list is forwarded to fetch_transcript."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.return_value = self.TRANSCRIPT_TEXT

        get_transcript(self.VALID_ID, "/tmp/out.txt", languages=["fr", "en"])

        mock_fetch.assert_called_once_with(self.VALID_ID, languages=["fr", "en"])

    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_propagates_value_error_from_extract(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
    ) -> None:
        """ValueError from extract_video_id propagates unchanged."""
        mock_extract.side_effect = ValueError("bad input")
        with pytest.raises(ValueError, match="bad input"):
            get_transcript("bad_input", "/tmp/out.txt")

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_propagates_transcripts_disabled(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """TranscriptsDisabled from fetch_transcript propagates unchanged."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.side_effect = TranscriptsDisabled(video_id=self.VALID_ID)
        with pytest.raises(TranscriptsDisabled):
            get_transcript(self.VALID_ID, "/tmp/out.txt")

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_propagates_oserror_from_save(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """OSError from save_transcript propagates unchanged."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.return_value = self.TRANSCRIPT_TEXT
        mock_save.side_effect = OSError("Disk full")
        with pytest.raises(OSError, match="Disk full"):
            get_transcript(self.VALID_ID, "/tmp/out.txt")

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_returns_text_not_none(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """get_transcript always returns a string, never None."""
        mock_extract.return_value = self.VALID_ID
        mock_fetch.return_value = ""

        result = get_transcript(self.VALID_ID, "/tmp/out.txt")
        assert isinstance(result, str)
