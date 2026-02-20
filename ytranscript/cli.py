"""CLI entry point for YTranscript."""

import argparse
import os
import sys

from ytranscript import __version__
from ytranscript.formatter import format_transcript
from ytranscript.playlist import get_video_ids
from ytranscript.transcript import fetch_transcript, list_languages


def _sanitize_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    # Replace problematic characters with underscores
    sanitized = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
    # Collapse multiple underscores/spaces
    sanitized = "_".join(sanitized.split())
    return sanitized[:100]  # Limit length


def _get_extension(fmt: str) -> str:
    return {"txt": ".txt", "srt": ".srt", "json": ".json"}[fmt]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytranscript",
        description="Download YouTube video transcripts from playlists or individual videos.",
    )
    parser.add_argument(
        "url",
        help="YouTube playlist or video URL",
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "srt", "json"],
        default="txt",
        help="Output format (default: txt)",
    )
    parser.add_argument(
        "-l", "--language",
        default="en",
        help="Transcript language code, e.g. 'en', 'es', 'de' (default: en). "
             "Comma-separated for fallback order, e.g. 'en,es'.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="./transcripts",
        help="Output directory (default: ./transcripts)",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        default=False,
        help="Include timestamps in txt output (always included in srt/json)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        default=False,
        help="Disable text cleaning (artifact removal, whitespace normalization)",
    )
    parser.add_argument(
        "--cookies",
        metavar="FILE",
        help="Path to cookies.txt file for accessing private/unlisted playlists",
    )
    parser.add_argument(
        "--list-languages",
        action="store_true",
        default=False,
        help="List available transcript languages for each video and exit",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Parse language fallback list
    languages = tuple(lang.strip() for lang in args.language.split(","))

    # Extract video IDs
    print(f"Extracting video IDs from: {args.url}")
    try:
        videos = get_video_ids(args.url, cookies_file=args.cookies)
    except Exception as e:
        print(f"Error extracting videos: {e}", file=sys.stderr)
        return 1

    print(f"Found {len(videos)} video(s).\n")

    # List languages mode
    if args.list_languages:
        for i, video in enumerate(videos, 1):
            label = video["title"] or video["id"]
            print(f"[{i}/{len(videos)}] {label}")
            try:
                langs = list_languages(video["id"])
                for lang in langs:
                    gen = " (auto-generated)" if lang["is_generated"] else ""
                    print(f"  {lang['code']:>5s}  {lang['language']}{gen}")
            except Exception as e:
                print(f"  Error: {e}")
            print()
        return 0

    # Create output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    ext = _get_extension(args.format)
    success = 0
    errors = []

    for i, video in enumerate(videos, 1):
        vid = video["id"]
        label = video["title"] or vid
        print(f"[{i}/{len(videos)}] {label}")

        try:
            transcript = fetch_transcript(vid, languages=languages)
        except Exception as e:
            msg = f"  Skipped: {e}"
            print(msg)
            errors.append((vid, label, str(e)))
            print()
            continue

        formatted = format_transcript(
            transcript,
            fmt=args.format,
            timestamps=args.timestamps,
            do_clean=not args.no_clean,
        )

        # Build filename: NN_title.ext or NN_videoId.ext
        if video["title"]:
            safe_title = _sanitize_filename(video["title"])
            filename = f"{i:03d}_{safe_title}{ext}"
        else:
            filename = f"{i:03d}_{vid}{ext}"

        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(formatted)

        print(f"  Saved: {filepath}")
        success += 1
        print()

    # Summary
    print("=" * 50)
    print(f"Done. {success}/{len(videos)} transcript(s) saved to {output_dir}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for vid, label, err in errors:
            print(f"  - {label} ({vid}): {err}")

    return 0 if success > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
