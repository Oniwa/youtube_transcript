"""
test_transcript.py — Pytest test suite for the YouTube transcript tool.

Unit tests use mocks; no real network calls are made outside of
tests decorated with @pytest.mark.integration.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from unittest.mock import MagicMock, patch

import main as main_module
from transcript import (
    VideoMetadata,
    extract_video_id,
    fetch_transcript,
    fetch_video_metadata,
    format_header,
    get_transcript,
    make_output_filename,
    save_transcript,
    slugify,
)
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)
from main import main

FAKE_METADATA = VideoMetadata(title="Test Title", channel="Test Channel")
TRANSCRIPTS_DIR = Path(main_module.__file__).resolve().parent / "transcripts"


# ---------------------------------------------------------------------------
# extract_video_id
# ---------------------------------------------------------------------------


class TestExtractVideoId:
    """Tests for extract_video_id covering all supported URL formats."""

    def test_bare_id(self) -> None:
        """A bare 11-character ID is returned unchanged."""
        assert extract_video_id("jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_standard_watch_url(self) -> None:
        """Standard youtube.com/watch?v=<id> URL extracts the ID correctly."""
        assert extract_video_id("https://www.youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_watch_url_with_extra_params(self) -> None:
        """Watch URL with additional query parameters extracts the ID."""
        url = "https://www.youtube.com/watch?v=jNQXAC9IVRw&t=30s&list=PLabc"
        assert extract_video_id(url) == "jNQXAC9IVRw"

    def test_youtu_be_short_url(self) -> None:
        """youtu.be/<id> short URL extracts the ID correctly."""
        assert extract_video_id("https://youtu.be/jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_youtu_be_with_query_params(self) -> None:
        """youtu.be/<id>?t=30 short URL with query params extracts the ID."""
        assert extract_video_id("https://youtu.be/jNQXAC9IVRw?t=30") == "jNQXAC9IVRw"

    def test_shorts_url(self) -> None:
        """youtube.com/shorts/<id> URL extracts the ID correctly."""
        assert extract_video_id("https://www.youtube.com/shorts/jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_mobile_url(self) -> None:
        """m.youtube.com watch URL is handled."""
        assert extract_video_id("https://m.youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_youtube_without_www(self) -> None:
        """youtube.com (no www) watch URL is handled."""
        assert extract_video_id("https://youtube.com/watch?v=jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_shorts_url_without_www(self) -> None:
        """youtube.com/shorts/<id> without www is handled."""
        assert extract_video_id("https://youtube.com/shorts/jNQXAC9IVRw") == "jNQXAC9IVRw"

    def test_bare_id_with_dashes_and_underscores(self) -> None:
        """An 11-char ID using dashes and underscores is accepted."""
        assert extract_video_id("abc-_defGHI") == "abc-_defGHI"

    def test_invalid_empty_string_raises(self) -> None:
        """An empty string raises ValueError mentioning 11-character."""
        with pytest.raises(ValueError, match="11-character"):
            extract_video_id("")

    def test_invalid_non_youtube_url_raises(self) -> None:
        """A non-YouTube URL raises ValueError mentioning 11-character."""
        with pytest.raises(ValueError, match="11-character"):
            extract_video_id("https://vimeo.com/jNQXAC9IVRw")

    def test_invalid_too_short_raises(self) -> None:
        """A 10-character string is rejected (not 11 chars)."""
        with pytest.raises(ValueError):
            extract_video_id("abc123")

    def test_invalid_too_long_raises(self) -> None:
        """A 12-character string is rejected (not 11 chars)."""
        with pytest.raises(ValueError):
            extract_video_id("jNQXAC9IVRwXXX")

    def test_watch_url_missing_v_param_raises(self) -> None:
        """A watch URL without a v= parameter raises ValueError."""
        with pytest.raises(ValueError):
            extract_video_id("https://www.youtube.com/watch?list=PLabc")

    def test_error_message_contains_input(self) -> None:
        """The ValueError message contains the offending input."""
        bad = "not-a-real-url"
        with pytest.raises(ValueError, match="not-a-real-url"):
            extract_video_id(bad)


# ---------------------------------------------------------------------------
# fetch_transcript
# ---------------------------------------------------------------------------


class TestFetchTranscript:
    """Tests for fetch_transcript using mocked YouTubeTranscriptApi."""

    _VIDEO_ID = "jNQXAC9IVRw"

    def _make_snippet(self, text: str) -> MagicMock:
        """Create a mock snippet object with a .text attribute."""
        snippet = MagicMock()
        snippet.text = text
        return snippet

    @patch("transcript.YouTubeTranscriptApi")
    def test_successful_fetch_joins_with_newline(self, mock_api_cls: MagicMock) -> None:
        """Snippet texts are joined with newlines and returned."""
        snippets = [self._make_snippet("Hello"), self._make_snippet("World")]
        mock_api_cls.return_value.fetch.return_value = snippets
        result = fetch_transcript(self._VIDEO_ID)
        assert result == "Hello\nWorld"

    @patch("transcript.YouTubeTranscriptApi")
    def test_successful_fetch_with_languages(self, mock_api_cls: MagicMock) -> None:
        """When languages is provided, it is forwarded to api.fetch()."""
        snippets = [self._make_snippet("Bonjour")]
        mock_api_cls.return_value.fetch.return_value = snippets
        result = fetch_transcript(self._VIDEO_ID, languages=["fr", "en"])
        mock_api_cls.return_value.fetch.assert_called_once_with(
            self._VIDEO_ID, languages=["fr", "en"]
        )
        assert result == "Bonjour"

    @patch("transcript.YouTubeTranscriptApi")
    def test_raises_transcripts_disabled(self, mock_api_cls: MagicMock) -> None:
        """TranscriptsDisabled is re-raised without wrapping."""
        mock_api_cls.return_value.fetch.side_effect = TranscriptsDisabled(self._VIDEO_ID)
        with pytest.raises(TranscriptsDisabled):
            fetch_transcript(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_raises_no_transcript_found(self, mock_api_cls: MagicMock) -> None:
        """NoTranscriptFound is re-raised without wrapping."""
        mock_api_cls.return_value.fetch.side_effect = NoTranscriptFound(
            self._VIDEO_ID, ["en"], {}
        )
        with pytest.raises(NoTranscriptFound):
            fetch_transcript(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_raises_video_unavailable(self, mock_api_cls: MagicMock) -> None:
        """VideoUnavailable is re-raised without wrapping."""
        mock_api_cls.return_value.fetch.side_effect = VideoUnavailable(self._VIDEO_ID)
        with pytest.raises(VideoUnavailable):
            fetch_transcript(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_raises_could_not_retrieve_transcript(self, mock_api_cls: MagicMock) -> None:
        """CouldNotRetrieveTranscript is re-raised without wrapping."""
        mock_api_cls.return_value.fetch.side_effect = CouldNotRetrieveTranscript(
            self._VIDEO_ID
        )
        with pytest.raises(CouldNotRetrieveTranscript):
            fetch_transcript(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_unknown_exception_wrapped_in_runtime_error(self, mock_api_cls: MagicMock) -> None:
        """An unexpected exception is wrapped in RuntimeError with its message."""
        mock_api_cls.return_value.fetch.side_effect = Exception("network failure")
        with pytest.raises(RuntimeError, match="network failure"):
            fetch_transcript(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_empty_transcript_returns_empty_string(self, mock_api_cls: MagicMock) -> None:
        """Zero snippets produce an empty string."""
        mock_api_cls.return_value.fetch.return_value = []
        result = fetch_transcript(self._VIDEO_ID)
        assert result == ""

    @patch("transcript.YouTubeTranscriptApi")
    def test_no_languages_kwarg_when_none(self, mock_api_cls: MagicMock) -> None:
        """When languages is None, the languages kwarg is NOT passed to api.fetch()."""
        mock_api_cls.return_value.fetch.return_value = [self._make_snippet("Hello")]
        fetch_transcript(self._VIDEO_ID, languages=None)
        mock_api_cls.return_value.fetch.assert_called_once_with(self._VIDEO_ID)

    @patch("transcript.YouTubeTranscriptApi")
    def test_unicode_snippets(self, mock_api_cls: MagicMock) -> None:
        """Non-ASCII snippet text is joined correctly."""
        mock_api_cls.return_value.fetch.return_value = [
            self._make_snippet("日本語"),
            self._make_snippet("العربية"),
        ]
        result = fetch_transcript(self._VIDEO_ID)
        assert result == "日本語\nالعربية"


# ---------------------------------------------------------------------------
# save_transcript
# ---------------------------------------------------------------------------


class TestSaveTranscript:
    """Tests for save_transcript using pytest's tmp_path fixture."""

    def test_creates_file(self, tmp_path: pytest.TempdirFactory) -> None:
        """The transcript file is created at the given path."""
        out = tmp_path / "transcript.txt"
        save_transcript("Hello, world!", str(out))
        assert out.exists()

    def test_file_contents_match(self, tmp_path: pytest.TempdirFactory) -> None:
        """The written file contents match the input text."""
        out = tmp_path / "transcript.txt"
        save_transcript("Line one\nLine two", str(out))
        assert out.read_text(encoding="utf-8") == "Line one\nLine two"

    def test_utf8_encoding(self, tmp_path: pytest.TempdirFactory) -> None:
        """Non-ASCII text is written correctly in UTF-8."""
        text = "こんにちは\n日本語テスト\U0001F600"
        out = tmp_path / "unicode.txt"
        save_transcript(text, str(out))
        assert out.read_text(encoding="utf-8") == text

    def test_overwrites_existing_file(self, tmp_path: pytest.TempdirFactory) -> None:
        """Calling save_transcript on an existing file overwrites its content."""
        out = tmp_path / "transcript.txt"
        out.write_text("old content", encoding="utf-8")
        save_transcript("new content", str(out))
        assert out.read_text(encoding="utf-8") == "new content"

    def test_missing_parent_dir_raises_os_error(self, tmp_path: pytest.TempdirFactory) -> None:
        """Writing to a path whose parent dir does not exist raises OSError."""
        out = tmp_path / "nonexistent" / "transcript.txt"
        with pytest.raises(OSError):
            save_transcript("text", str(out))

    def test_returns_none(self, tmp_path: pytest.TempdirFactory) -> None:
        """save_transcript returns None."""
        out = tmp_path / "transcript.txt"
        result = save_transcript("text", str(out))
        assert result is None

    def test_empty_string_creates_empty_file(self, tmp_path: pytest.TempdirFactory) -> None:
        """Saving an empty string produces an empty file."""
        out = tmp_path / "empty.txt"
        save_transcript("", str(out))
        assert out.read_text(encoding="utf-8") == ""


# ---------------------------------------------------------------------------
# get_transcript
# ---------------------------------------------------------------------------


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
        """get_transcript calls extract_video_id, fetch_transcript, save_transcript."""
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
    def test_header_prepended_to_saved_file(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
        tmp_path: pytest.TempdirFactory,
    ) -> None:
        """When header is provided, it is prepended to the saved content."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_fetch.return_value = "transcript text"
        out = str(tmp_path / "out.txt")
        result = get_transcript("https://youtu.be/jNQXAC9IVRw", out, header="HEADER\n")
        mock_save.assert_called_once_with("HEADER\ntranscript text", out)
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
        """Languages list is forwarded to fetch_transcript."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_fetch.return_value = "text"
        out = str(tmp_path / "out.txt")
        get_transcript("jNQXAC9IVRw", out, languages=["fr"])
        mock_fetch.assert_called_once_with("jNQXAC9IVRw", languages=["fr"])

    @patch("transcript.extract_video_id")
    def test_propagates_value_error(self, mock_extract: MagicMock) -> None:
        """ValueError from extract_video_id propagates unchanged."""
        mock_extract.side_effect = ValueError("bad url")
        with pytest.raises(ValueError, match="bad url"):
            get_transcript("bad", "out.txt")

    @patch("transcript.save_transcript")
    @patch("transcript.fetch_transcript")
    @patch("transcript.extract_video_id")
    def test_returns_transcript_text(
        self,
        mock_extract: MagicMock,
        mock_fetch: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        """get_transcript returns the fetched transcript text (without header)."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_fetch.return_value = "Line one\nLine two"
        result = get_transcript("jNQXAC9IVRw", "/tmp/out.txt")
        assert result == "Line one\nLine two"

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
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_fetch.side_effect = TranscriptsDisabled(video_id="jNQXAC9IVRw")
        with pytest.raises(TranscriptsDisabled):
            get_transcript("jNQXAC9IVRw", "/tmp/out.txt")

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
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_fetch.return_value = "text"
        mock_save.side_effect = OSError("Disk full")
        with pytest.raises(OSError, match="Disk full"):
            get_transcript("jNQXAC9IVRw", "/tmp/out.txt")


# ---------------------------------------------------------------------------
# fetch_video_metadata
# ---------------------------------------------------------------------------


class TestFetchVideoMetadata:
    """Tests for fetch_video_metadata using mocked urllib."""

    _VIDEO_ID = "jNQXAC9IVRw"
    _OEMBED_RESPONSE = json.dumps({
        "title": "Me at the zoo",
        "author_name": "jawed",
    }).encode("utf-8")

    @patch("transcript.urllib.request.urlopen")
    def test_returns_title_and_channel(self, mock_urlopen: MagicMock) -> None:
        """Returns VideoMetadata with title and channel from oEmbed JSON."""
        mock_response = MagicMock()
        mock_response.read.return_value = self._OEMBED_RESPONSE
        mock_urlopen.return_value.__enter__ = lambda s: mock_response
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        result = fetch_video_metadata(self._VIDEO_ID)
        assert result.title == "Me at the zoo"
        assert result.channel == "jawed"

    @patch("transcript.urllib.request.urlopen")
    def test_raises_runtime_error_on_network_failure(self, mock_urlopen: MagicMock) -> None:
        """Network failure raises RuntimeError with the video ID in the message."""
        mock_urlopen.side_effect = OSError("Connection refused")
        with pytest.raises(RuntimeError, match=self._VIDEO_ID):
            fetch_video_metadata(self._VIDEO_ID)

    @patch("transcript.urllib.request.urlopen")
    def test_raises_runtime_error_on_bad_json(self, mock_urlopen: MagicMock) -> None:
        """Malformed JSON response raises RuntimeError."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_urlopen.return_value.__enter__ = lambda s: mock_response
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
        with pytest.raises(RuntimeError):
            fetch_video_metadata(self._VIDEO_ID)


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


class TestSlugify:
    """Tests for slugify."""

    def test_spaces_become_underscores(self) -> None:
        assert slugify("hello world") == "hello_world"

    def test_removes_windows_invalid_chars(self) -> None:
        assert slugify('file:name*"test"') == "filenametest"

    def test_strips_trailing_dots(self) -> None:
        assert slugify("name...") == "name"

    def test_strips_trailing_underscores(self) -> None:
        assert slugify("name___") == "name"

    def test_truncates_to_max_len(self) -> None:
        result = slugify("a" * 100, max_len=50)
        assert len(result) == 50

    def test_empty_string_returns_fallback(self) -> None:
        assert slugify("") == "unknown"

    def test_all_invalid_chars_returns_fallback(self) -> None:
        assert slugify('/:*?"<>|\\') == "unknown"

    def test_reserved_name_gets_suffix(self) -> None:
        result = slugify("CON")
        assert result == "CON_file"

    def test_reserved_name_case_insensitive(self) -> None:
        result = slugify("con")
        assert result == "con_file"

    def test_unicode_preserved(self) -> None:
        result = slugify("日本語タイトル")
        assert result == "日本語タイトル"


# ---------------------------------------------------------------------------
# make_output_filename
# ---------------------------------------------------------------------------


class TestMakeOutputFilename:
    """Tests for make_output_filename."""

    def test_basic_channel_and_title(self) -> None:
        meta = VideoMetadata(title="My Video", channel="My Channel")
        assert make_output_filename(meta) == "My_Channel_My_Video.txt"

    def test_special_chars_removed(self) -> None:
        meta = VideoMetadata(title='Title: "Cool"', channel="Chan/Nel")
        assert make_output_filename(meta) == "ChanNel_Title_Cool.txt"

    def test_empty_title_uses_fallback(self) -> None:
        meta = VideoMetadata(title="", channel="Channel")
        assert make_output_filename(meta) == "Channel_untitled.txt"

    def test_empty_channel_uses_fallback(self) -> None:
        meta = VideoMetadata(title="Title", channel="")
        assert make_output_filename(meta) == "unknown-channel_Title.txt"


# ---------------------------------------------------------------------------
# format_header
# ---------------------------------------------------------------------------


class TestFormatHeader:
    """Tests for format_header."""

    def test_contains_title(self) -> None:
        header = format_header(VideoMetadata(title="My Video", channel="My Channel"))
        assert "My Video" in header

    def test_contains_channel(self) -> None:
        header = format_header(VideoMetadata(title="My Video", channel="My Channel"))
        assert "My Channel" in header

    def test_ends_with_blank_line(self) -> None:
        header = format_header(VideoMetadata(title="T", channel="C"))
        assert header.endswith("\n\n")

    def test_contains_separator(self) -> None:
        header = format_header(VideoMetadata(title="T", channel="C"))
        assert "=" * 40 in header


class TestMain:
    """Tests for the main() CLI entry point."""

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_success_exit_code_zero(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
        tmp_path: pytest.TempdirFactory,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A successful run returns exit code 0."""
        monkeypatch.chdir(tmp_path)
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_get.return_value = "transcript text"
        mock_meta.return_value = FAKE_METADATA
        result = main(["https://youtu.be/jNQXAC9IVRw"])
        assert result == 0

    @patch("main.extract_video_id")
    def test_invalid_url_exit_code_one(
        self, mock_extract: MagicMock, capsys: pytest.CaptureFixture
    ) -> None:
        """An invalid URL returns exit code 1 and writes to stderr."""
        mock_extract.side_effect = ValueError("bad url")
        result = main(["https://vimeo.com/12345"])
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_custom_output_path(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
        tmp_path: pytest.TempdirFactory,
    ) -> None:
        """The --output flag is forwarded to get_transcript."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_get.return_value = "text"
        mock_meta.return_value = FAKE_METADATA
        out = str(tmp_path / "custom.txt")
        result = main(["https://youtu.be/jNQXAC9IVRw", "--output", out])
        assert result == 0
        mock_get.assert_called_once_with(
            "https://youtu.be/jNQXAC9IVRw", out, languages=None,
            header=mock_get.call_args[1]["header"]
        )

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_lang_flag_forwarded(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
    ) -> None:
        """Multiple --lang flags are collected and forwarded as a list."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_get.return_value = "text"
        mock_meta.return_value = FAKE_METADATA
        result = main(["https://youtu.be/jNQXAC9IVRw", "--lang", "en", "--lang", "fr"])
        assert result == 0
        mock_get.assert_called_once_with(
            "https://youtu.be/jNQXAC9IVRw",
            str(TRANSCRIPTS_DIR / "Test_Channel_Test_Title.txt"),
            languages=["en", "fr"],
            header=mock_get.call_args[1]["header"],
        )

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_transcripts_disabled_exit_one(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
        tmp_path: pytest.TempdirFactory,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """TranscriptsDisabled causes exit code 1 with an error on stderr."""
        monkeypatch.chdir(tmp_path)
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_meta.return_value = FAKE_METADATA
        mock_get.side_effect = TranscriptsDisabled("jNQXAC9IVRw")
        result = main(["https://youtu.be/jNQXAC9IVRw"])
        assert result == 1
        assert "Error" in capsys.readouterr().err

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_os_error_exit_one(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """OSError from get_transcript causes exit code 1 with an error on stderr."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_meta.return_value = FAKE_METADATA
        mock_get.side_effect = OSError("permission denied")
        result = main(["https://youtu.be/jNQXAC9IVRw", "--output", "/ro/out.txt"])
        assert result == 1
        assert "Error" in capsys.readouterr().err

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_default_output_filename_uses_channel_and_title(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
    ) -> None:
        """Default output filename is <channel>_<title>.txt, anchored to transcripts/."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_get.return_value = "text"
        mock_meta.return_value = FAKE_METADATA
        main(["https://youtu.be/jNQXAC9IVRw"])
        mock_get.assert_called_once_with(
            "https://youtu.be/jNQXAC9IVRw",
            str(TRANSCRIPTS_DIR / "Test_Channel_Test_Title.txt"),
            languages=None,
            header=mock_get.call_args[1]["header"],
        )

    @patch("main.fetch_video_metadata")
    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_default_output_filename_falls_back_on_metadata_failure(
        self,
        mock_extract: MagicMock,
        mock_get: MagicMock,
        mock_meta: MagicMock,
    ) -> None:
        """When metadata fails, default filename is <video_id>.txt and header is empty."""
        mock_extract.return_value = "jNQXAC9IVRw"
        mock_get.return_value = "text"
        mock_meta.side_effect = RuntimeError("oEmbed unavailable")
        main(["https://youtu.be/jNQXAC9IVRw"])
        mock_get.assert_called_once_with(
            "https://youtu.be/jNQXAC9IVRw",
            str(TRANSCRIPTS_DIR / "jNQXAC9IVRw.txt"),
            languages=None,
            header="",
        )


# ---------------------------------------------------------------------------
# integration (real network — gated by marker)
# ---------------------------------------------------------------------------


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
        """Fetching the first YouTube video produces a non-empty transcript file."""
        out = str(tmp_path / f"{self.KNOWN_VIDEO_ID}.txt")
        text = get_transcript(self.KNOWN_VIDEO_URL, out)
        assert len(text) > 0
        assert (tmp_path / f"{self.KNOWN_VIDEO_ID}.txt").exists()

    def test_invalid_url_raises_value_error(self) -> None:
        """A non-YouTube URL raises ValueError even with a real network."""
        with pytest.raises(ValueError):
            get_transcript("https://vimeo.com/jNQXAC9IVRw", "unused.txt")
