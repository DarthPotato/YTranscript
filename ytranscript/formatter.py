"""Format and clean transcripts for output."""

import json
import re

from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet
from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter, TextFormatter


def clean_text(text: str) -> str:
    """
    Clean transcript text:
    - Normalize whitespace (collapse multiple spaces/newlines)
    - Strip leading/trailing whitespace per line
    - Remove common YouTube auto-caption artifacts like [Music], [Applause], etc.
    """
    # Remove bracketed artifacts like [Music], [Applause], [Laughter]
    text = re.sub(r"\[(?:Music|Applause|Laughter|Inaudible)\]", "", text, flags=re.IGNORECASE)
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip each line
    lines = [line.strip() for line in text.splitlines()]
    # Remove empty lines that result from artifact removal
    cleaned = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned.append("")
            prev_empty = True
        else:
            cleaned.append(line)
            prev_empty = False
    return "\n".join(cleaned).strip()


def _seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


def format_as_txt(transcript: FetchedTranscript, timestamps: bool = False) -> str:
    """Format transcript as plain text, optionally with timestamps."""
    if timestamps:
        lines = []
        for snippet in transcript:
            ts = _seconds_to_timestamp(snippet.start)
            lines.append(f"[{ts}] {snippet.text}")
        return "\n".join(lines)
    else:
        formatter = TextFormatter()
        return formatter.format_transcript(transcript)


def format_as_srt(transcript: FetchedTranscript) -> str:
    """Format transcript as SRT subtitles."""
    formatter = SRTFormatter()
    return formatter.format_transcript(transcript)


def format_as_json(transcript: FetchedTranscript) -> str:
    """Format transcript as JSON."""
    data = {
        "video_id": transcript.video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
        "snippets": transcript.to_raw_data(),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def format_transcript(
    transcript: FetchedTranscript,
    fmt: str = "txt",
    timestamps: bool = False,
    do_clean: bool = True,
) -> str:
    """
    Format a transcript in the requested format.

    Args:
        transcript: The fetched transcript.
        fmt: Output format - 'txt', 'srt', or 'json'.
        timestamps: Include timestamps in txt output.
        do_clean: Apply text cleaning (only affects txt format).

    Returns:
        Formatted transcript string.
    """
    if fmt == "srt":
        return format_as_srt(transcript)
    elif fmt == "json":
        return format_as_json(transcript)
    else:
        text = format_as_txt(transcript, timestamps=timestamps)
        if do_clean and not timestamps:
            text = clean_text(text)
        return text
