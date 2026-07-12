"""
main.py — CLI entry point for the YouTube transcript extraction tool.

Usage:
    python main.py <url>
    python main.py <url> --output transcript.txt
    python main.py <url> --lang en --lang fr
    python main.py <url> --stdout
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from transcript import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    extract_video_id,
    fetch_transcript,
    fetch_video_metadata,
    format_header,
    get_transcript,
    make_output_filename,
)


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
            "Output file path. Defaults to <channel>_<title>.txt in this project's "
            "transcripts/ directory (falls back to <video_id>.txt if metadata is "
            "unavailable), regardless of the caller's current directory."
        ),
    )
    parser.add_argument(
        "--stdout",
        "-s",
        action="store_true",
        default=False,
        help=(
            "Print the transcript to stdout instead of saving to a file. "
            "A title/channel header is included when metadata is available. "
            "All status messages and errors go to stderr."
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


def main(argv: list[str] | None = None) -> int:
    """Run the YouTube transcript CLI.

    Args:
        argv: Argument list. If None, reads from sys.argv[1:].

    Returns:
        0 on success, 1 on any error.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        video_id = extract_video_id(args.url)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    # Fetch metadata for title/channel; degrade gracefully on failure.
    try:
        metadata = fetch_video_metadata(video_id)
    except RuntimeError as err:
        print(f"Warning: could not fetch video metadata — {err}", file=sys.stderr)
        metadata = None

    header = format_header(metadata) if metadata is not None else ""

    if args.output is not None:
        output_path = args.output
    else:
        transcripts_dir = Path(__file__).resolve().parent / "transcripts"
        transcripts_dir.mkdir(exist_ok=True)
        filename = make_output_filename(metadata) if metadata is not None else f"{video_id}.txt"
        output_path = str(transcripts_dir / filename)

    try:
        if args.stdout:
            text = fetch_transcript(video_id, languages=args.languages)
            print(header + text)
        else:
            text = get_transcript(args.url, output_path, languages=args.languages, header=header)
            print(f"Transcript saved to: {output_path}")
            print(f"Length: {len(text.splitlines())} lines")
    except VideoUnavailable as err:
        print(f"Error: Video unavailable — {err}", file=sys.stderr)
        return 1
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as err:
        print(f"Error: No transcript available — {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"Error: Could not save transcript — {err}", file=sys.stderr)
        return 1
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
