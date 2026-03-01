"""
tests/test_main.py — Unit tests for the main.py CLI entry point.

All tests are isolated (no real network calls). Functions in transcript.py
are mocked via unittest.mock wherever network interaction would otherwise occur.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from main import _build_parser, main
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

VALID_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
VALID_ID = "jNQXAC9IVRw"
TRANSCRIPT_TEXT = "Line one\nLine two\nLine three"


# ---------------------------------------------------------------------------
# _build_parser
# ---------------------------------------------------------------------------


class TestBuildParser:
    """Tests for _build_parser()."""

    def test_parser_accepts_url_positional(self) -> None:
        """The parser accepts a positional url argument."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL])
        assert args.url == VALID_URL

    def test_parser_output_defaults_to_none(self) -> None:
        """--output defaults to None when not provided."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL])
        assert args.output is None

    def test_parser_languages_defaults_to_none(self) -> None:
        """--lang defaults to None when not provided."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL])
        assert args.languages is None

    def test_parser_output_long_flag(self) -> None:
        """--output FILE sets args.output correctly."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL, "--output", "out.txt"])
        assert args.output == "out.txt"

    def test_parser_output_short_flag(self) -> None:
        """-o FILE sets args.output correctly."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL, "-o", "out.txt"])
        assert args.output == "out.txt"

    def test_parser_single_lang_flag(self) -> None:
        """--lang en sets languages to ['en']."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL, "--lang", "en"])
        assert args.languages == ["en"]

    def test_parser_short_lang_flag(self) -> None:
        """-l en sets languages to ['en']."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL, "-l", "en"])
        assert args.languages == ["en"]

    def test_parser_multiple_lang_flags(self) -> None:
        """Multiple --lang flags build a list in order."""
        parser = _build_parser()
        args = parser.parse_args([VALID_URL, "--lang", "en", "--lang", "fr"])
        assert args.languages == ["en", "fr"]

    def test_parser_prog_name(self) -> None:
        """The parser's prog name is 'youtube-transcript'."""
        parser = _build_parser()
        assert parser.prog == "youtube-transcript"


# ---------------------------------------------------------------------------
# main — happy path
# ---------------------------------------------------------------------------


class TestMainHappyPath:
    """Tests for main() returning exit code 0."""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_zero_on_success(
        self, mock_extract: object, mock_get: object
    ) -> None:
        """main() returns 0 when the transcript is saved successfully."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 0

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_default_output_filename_is_video_id_txt(
        self, mock_extract: object, mock_get: object, tmp_path: object
    ) -> None:
        """When --output is omitted, the output path is <video_id>.txt."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        main([VALID_URL])
        mock_get.assert_called_once_with(  # type: ignore[attr-defined]
            VALID_URL, f"{VALID_ID}.txt", languages=None
        )

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_explicit_output_path_forwarded(
        self, mock_extract: object, mock_get: object
    ) -> None:
        """When --output is given, that path is forwarded to get_transcript."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        main([VALID_URL, "--output", "custom.txt"])
        mock_get.assert_called_once_with(  # type: ignore[attr-defined]
            VALID_URL, "custom.txt", languages=None
        )

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_languages_forwarded_to_get_transcript(
        self, mock_extract: object, mock_get: object
    ) -> None:
        """--lang flags are forwarded as a list to get_transcript."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        main([VALID_URL, "--lang", "en", "--lang", "fr"])
        mock_get.assert_called_once_with(  # type: ignore[attr-defined]
            VALID_URL, f"{VALID_ID}.txt", languages=["en", "fr"]
        )

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_success_prints_saved_path(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """On success, 'Transcript saved to:' appears on stdout."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        main([VALID_URL, "--output", "out.txt"])
        captured = capsys.readouterr()
        assert "Transcript saved to: out.txt" in captured.out

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_success_prints_line_count(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """On success, the line count appears on stdout."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.return_value = TRANSCRIPT_TEXT  # type: ignore[attr-defined]
        main([VALID_URL, "--output", "out.txt"])
        captured = capsys.readouterr()
        assert "Length: 3 lines" in captured.out


# ---------------------------------------------------------------------------
# main — error paths (exit code 1)
# ---------------------------------------------------------------------------


class TestMainErrorPaths:
    """Tests for main() returning exit code 1 on various errors."""

    @patch("main.extract_video_id")
    def test_returns_one_on_invalid_url(
        self,
        mock_extract: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 and prints to stderr when the URL is invalid."""
        mock_extract.side_effect = ValueError("bad url")  # type: ignore[attr-defined]
        result = main(["https://vimeo.com/12345678901"])
        assert result == 1
        captured = capsys.readouterr()
        assert captured.err != ""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_transcripts_disabled(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when TranscriptsDisabled is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = TranscriptsDisabled(video_id=VALID_ID)  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 1
        assert capsys.readouterr().err != ""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_no_transcript_found(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when NoTranscriptFound is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = NoTranscriptFound(  # type: ignore[attr-defined]
            video_id=VALID_ID,
            requested_language_codes=["xx"],
            transcript_data={},
        )
        result = main([VALID_URL])
        assert result == 1
        assert capsys.readouterr().err != ""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_could_not_retrieve(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when CouldNotRetrieveTranscript is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = CouldNotRetrieveTranscript(video_id=VALID_ID)  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 1
        assert capsys.readouterr().err != ""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_video_unavailable(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when VideoUnavailable is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = VideoUnavailable(video_id=VALID_ID)  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 1
        assert capsys.readouterr().err != ""

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_oserror(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when OSError (e.g. write failure) is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = OSError("Disk full")  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 1
        assert "Could not save" in capsys.readouterr().err

    @patch("main.get_transcript")
    @patch("main.extract_video_id")
    def test_returns_one_on_runtime_error(
        self,
        mock_extract: object,
        mock_get: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """main() returns 1 when an unexpected RuntimeError is raised."""
        mock_extract.return_value = VALID_ID  # type: ignore[attr-defined]
        mock_get.side_effect = RuntimeError("Something went wrong")  # type: ignore[attr-defined]
        result = main([VALID_URL])
        assert result == 1
        assert capsys.readouterr().err != ""

    @patch("main.extract_video_id")
    def test_error_message_written_to_stderr_not_stdout(
        self,
        mock_extract: object,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Error messages go to stderr; stdout stays empty on failure."""
        mock_extract.side_effect = ValueError("bad url")  # type: ignore[attr-defined]
        main(["https://vimeo.com/12345678901"])
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err != ""
