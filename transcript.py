"""
transcript.py — Core logic for YouTube transcript extraction.

This module has no CLI concerns. All functions are pure logic:
extract a video ID, fetch a transcript, save it, or do all three.
"""
from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# Windows reserved device names that cannot be used as filenames.
_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})

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


@dataclass
class VideoMetadata:
    """Metadata for a YouTube video."""

    title: str
    channel: str


def fetch_video_metadata(video_id: str) -> VideoMetadata:
    """Fetch the title and channel name for a YouTube video via oEmbed.

    Uses YouTube's public oEmbed endpoint — no API key required.

    Args:
        video_id: The 11-character YouTube video ID.

    Returns:
        A VideoMetadata instance with title and channel.

    Raises:
        RuntimeError: If the metadata cannot be retrieved.
    """
    url = (
        f"https://www.youtube.com/oembed"
        f"?url=https://www.youtube.com/watch?v={video_id}&format=json"
    )
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
        return VideoMetadata(title=data["title"], channel=data["author_name"])
    except Exception as err:
        raise RuntimeError(
            f"Could not fetch metadata for video '{video_id}': {err}"
        ) from err


def slugify(text: str, max_len: int = 50, fallback: str = "unknown") -> str:
    """Convert text into a safe filename component.

    Removes characters invalid on Windows, collapses whitespace to underscores,
    strips trailing dots/underscores, and guards against Windows reserved names.

    Args:
        text: The input string to slugify.
        max_len: Maximum length of the returned slug (default 50).
        fallback: Value returned when the result would otherwise be empty.

    Returns:
        A filename-safe string.
    """
    # Remove Windows-invalid filename characters.
    text = re.sub(r'[\\/:*?"<>|]', "", text)
    # Collapse all whitespace runs to a single underscore.
    text = re.sub(r"\s+", "_", text.strip())
    # Strip trailing dots and underscores (invalid endings on Windows).
    text = text.rstrip("._")
    # Truncate to max_len and strip again in case truncation left a trailing dot/underscore.
    text = text[:max_len].rstrip("._")
    # Guard against Windows reserved device names.
    if text.upper() in _RESERVED_NAMES:
        text = f"{text}_file"
    return text if text else fallback


def make_output_filename(metadata: VideoMetadata) -> str:
    """Build a default output filename from video metadata.

    Args:
        metadata: The video's title and channel name.

    Returns:
        A filename in the form ``<channel>_<title>.txt``.
    """
    channel = slugify(metadata.channel, fallback="unknown-channel")
    title = slugify(metadata.title, fallback="untitled")
    return f"{channel}_{title}.txt"


def format_header(metadata: VideoMetadata) -> str:
    """Format a human-readable header block for a transcript file.

    Args:
        metadata: The video's title and channel name.

    Returns:
        A header string ending with a blank line, ready to prepend to a transcript.
    """
    separator = "=" * 80
    return f"Title:   {metadata.title}\nChannel: {metadata.channel}\n{separator}\n\n"


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
    header: str = "",
) -> str:
    """Extract a video ID, fetch its transcript, save it, and return the text.

    This is a convenience wrapper around extract_video_id, fetch_transcript,
    and save_transcript.

    Args:
        url_or_id: A YouTube URL in any supported format, or a bare video ID.
        output_path: Destination file path for the saved transcript.
        languages: Optional list of BCP-47 language codes in preference order.
        header: Optional header string to prepend to the saved file content.
            Does not affect the returned text. Defaults to an empty string.

    Returns:
        The full transcript text (without header) that was saved.

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
    save_transcript(header + text, output_path)
    return text
