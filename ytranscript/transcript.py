"""Download transcripts using youtube_transcript_api."""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import FetchedTranscript


def fetch_transcript(
    video_id: str,
    languages: tuple[str, ...] = ("en",),
) -> FetchedTranscript:
    """
    Fetch a transcript for a single video.

    Raises TranscriptsDisabled, NoTranscriptFound, etc. on failure.
    """
    api = YouTubeTranscriptApi()
    return api.fetch(video_id, languages=languages)


def list_languages(video_id: str) -> list[dict]:
    """List available transcript languages for a video."""
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    return [
        {
            "language": t.language,
            "code": t.language_code,
            "is_generated": t.is_generated,
        }
        for t in transcript_list
    ]
