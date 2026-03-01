"""
main.py — CLI entry point for the YouTube transcript extraction tool.

Usage:
    python main.py <url>
    python main.py <url> --output transcript.txt
    python main.py <url> --lang en --lang fr
"""
from __future__ import annotations

import argparse
import sys

from transcript import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    extract_video_id,
    get_transcript,
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
            "Output file path. Defaults to <video_id>.txt in the current directory."
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

    output_path = args.output if args.output is not None else f"{video_id}.txt"

    try:
        text = get_transcript(args.url, output_path, languages=args.languages)
    except (TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript) as err:
        print(f"Error: No transcript available — {err}", file=sys.stderr)
        return 1
    except VideoUnavailable as err:
        print(f"Error: Video unavailable — {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"Error: Could not save transcript — {err}", file=sys.stderr)
        return 1
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(f"Transcript saved to: {output_path}")
    print(f"Length: {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
