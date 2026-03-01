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
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

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
        CouldNotRetrieveTranscript: No transcript could be retrieved for this video.
        RuntimeError: An unexpected API error occurred.
    """
    try:
        api = YouTubeTranscriptApi()
        kwargs: dict[str, object] = {}
        if languages is not None:
            kwargs["languages"] = languages
        fetched = api.fetch(video_id, **kwargs)
        return "\n".join(snippet.text for snippet in fetched)
    except (
        TranscriptsDisabled,
        NoTranscriptFound,
        VideoUnavailable,
        CouldNotRetrieveTranscript,
    ):
        raise
    except Exception as err:
        raise RuntimeError(
            f"Unexpected error fetching transcript for video '{video_id}': {err}"
        ) from err


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
        CouldNotRetrieveTranscript: No transcript could be retrieved for this video.
        RuntimeError: An unexpected error occurred during fetching.
        OSError: If the transcript cannot be saved to output_path.
    """
    video_id = extract_video_id(url_or_id)
    text = fetch_transcript(video_id, languages=languages)
    save_transcript(text, output_path)
    return text
