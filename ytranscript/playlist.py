"""Extract video IDs from YouTube playlists using yt-dlp."""

import re
import sys

from yt_dlp import YoutubeDL


def extract_playlist_id(url: str) -> str | None:
    """Extract the playlist ID from a YouTube URL."""
    match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else None


def extract_video_id(url: str) -> str | None:
    """Extract a single video ID from a YouTube URL."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_playlist_url(url: str) -> bool:
    """Check if the URL contains a playlist parameter."""
    return "list=" in url


def get_video_ids(url: str, cookies_file: str | None = None) -> list[dict]:
    """
    Extract video IDs and titles from a YouTube playlist URL.

    Returns a list of dicts with 'id' and 'title' keys.
    """
    if not is_playlist_url(url):
        video_id = extract_video_id(url)
        if video_id:
            return [{"id": video_id, "title": None}]
        print(f"Error: Could not parse video ID from URL: {url}", file=sys.stderr)
        sys.exit(1)

    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
    }
    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = info.get("entries", [])
    if not entries:
        print("Error: No videos found in playlist.", file=sys.stderr)
        sys.exit(1)

    videos = []
    for entry in entries:
        vid = entry.get("id")
        if vid:
            videos.append({"id": vid, "title": entry.get("title")})

    return videos
