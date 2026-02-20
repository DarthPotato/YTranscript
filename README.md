# YTranscript

A command-line tool that downloads YouTube video transcripts from playlists (or individual videos) and saves them as text files. Works with public, unlisted, and private playlists.

## How It Works

1. You give it a YouTube playlist URL (or a single video URL)
2. It uses **yt-dlp** to quickly extract all the video IDs from the playlist — no videos are downloaded, just metadata
3. For each video, it uses **youtube-transcript-api** to grab the transcript (captions/subtitles)
4. It cleans up the text (removes auto-caption junk like `[Music]`, `[Applause]`, etc.) and saves each transcript as a numbered file

The output looks like:
```
transcripts/
├── 001_First_Video_Title.txt
├── 002_Second_Video_Title.txt
├── 003_Third_Video_Title.txt
└── ...
```

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repo
git clone https://github.com/DarthPotato/YTranscript.git
cd YTranscript

# Install dependencies
pip install -r requirements.txt

# Or install as a package (gives you the `ytranscript` command)
pip install -e .
```

## Usage

### Basic — download all transcripts from a playlist

```bash
python -m ytranscript "https://www.youtube.com/playlist?list=PLxxxxx"
```

This saves English transcripts as `.txt` files in a `./transcripts/` folder.

### Single video

```bash
python -m ytranscript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Choose output format

```bash
# Plain text (default)
python -m ytranscript "URL" -f txt

# SRT subtitles (with timestamps baked in)
python -m ytranscript "URL" -f srt

# JSON (structured data with timestamps, duration, language info)
python -m ytranscript "URL" -f json
```

### Include timestamps in text output

By default, text output is just the spoken words. Add `--timestamps` to prepend each line with its time:

```bash
python -m ytranscript "URL" --timestamps
```

Output looks like:
```
[00:00:00.000] Welcome to the video
[00:00:03.500] Today we're going to learn about...
```

### Change language

```bash
# Spanish
python -m ytranscript "URL" -l es

# Try German first, fall back to English if unavailable
python -m ytranscript "URL" -l de,en
```

### See what languages are available

```bash
python -m ytranscript "URL" --list-languages
```

### Change output directory

```bash
python -m ytranscript "URL" -o ./my_folder
```

### Unlisted or private playlists

For playlists that aren't public, you need to export your browser cookies so yt-dlp can authenticate:

1. Install a browser extension like [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to YouTube while logged in and export your cookies
3. Pass the file:

```bash
python -m ytranscript "URL" --cookies cookies.txt
```

### Disable text cleaning

The tool automatically strips out auto-caption artifacts (`[Music]`, `[Applause]`, etc.) and cleans up whitespace. If you want the raw unmodified transcript:

```bash
python -m ytranscript "URL" --no-clean
```

## All Options

| Flag | Short | Description | Default |
|------|-------|-------------|---------|
| `--format` | `-f` | Output format: `txt`, `srt`, `json` | `txt` |
| `--language` | `-l` | Language code(s), comma-separated for fallback | `en` |
| `--output-dir` | `-o` | Where to save files | `./transcripts` |
| `--timestamps` | | Add timestamps to text output | off |
| `--no-clean` | | Don't remove `[Music]` etc. from text | off |
| `--cookies` | | Path to cookies.txt for private playlists | none |
| `--list-languages` | | Show available languages and exit | off |
| `--version` | `-V` | Show version | |

## Troubleshooting

**"No transcript found"** — The video might not have captions. Use `--list-languages` to check what's available, or try `-l en,es,fr` to cast a wider net.

**Private playlist not working** — Make sure your cookies file is fresh (they expire). Re-export from your browser and try again.

**"Transcripts are disabled for this video"** — The video owner has turned off captions. Nothing we can do about that one.
