# 📖 Comprehensive Usage & CLI Reference

This guide provides an in-depth reference for using **YouTube Music Audio Downloader CLI**, covering interactive studio workflows, CLI arguments, multi-quality generation, authentication, and Python programmatic integration.

---

## Table of Contents
- [Quick Start](#quick-start)
- [1. Interactive Studio Mode](#1-interactive-studio-mode)
  - [Workflow Steps](#workflow-steps)
- [2. CLI Command Line Interface](#2-cli-command-line-interface)
  - [CLI Flags Reference Table](#cli-flags-reference-table)
- [3. Practical Recipes & Examples](#3-practical-recipes--examples)
  - [A. High-Quality 320kbps MP3](#a-high-quality-320kbps-mp3)
  - [B. 4-in-1 Multi-Bitrate Batch Generation](#b-4-in-1-multi-bitrate-batch-generation)
  - [C. Lossless FLAC or Studio OPUS](#c-lossless-flac-or-studio-opus)
  - [D. Downloading Entire Playlists / Albums](#d-downloading-entire-playlists--albums)
  - [E. Inspecting Available Audio Streams (`-F`)](#e-inspecting-available-audio-streams--f)
  - [F. Authenticating with Browser Cookies or cookies.txt](#f-authenticating-with-browser-cookies-or-cookiestxt)
  - [G. Custom Output Directory](#g-custom-output-directory)
  - [H. Testing Downloads with Dry-Run Mode](#h-testing-downloads-with-dry-run-mode)
- [4. Filename Naming Schemes](#4-filename-naming-schemes)
- [5. Programmatic Python API](#5-programmatic-python-api)
- [6. Shell Scripting & Automation](#6-shell-scripting--automation)

---

## Quick Start

Launch the interactive studio dashboard without any parameters:

```powershell
python main.py
# Or if installed via pip (dus-yt-music-dl or yt-music-dl)
dus-yt-music-dl
```

---

## 1. Interactive Studio Mode

When launched with no arguments (or with `-i`), the tool presents an interactive CloudCode-style terminal dashboard:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│  ██████╗  ██╗   ██╗ ███████╗                                                │
│  ██╔══██╗ ██║   ██║ ██╔════╝                                                │
│  ██║  ██║ ██║   ██║ ███████╗                                                │
│  ██║  ██║ ██║   ██║ ╚════██║                                                │
│  ██████╔╝ ╚██████╔╝ ███████║                                                │
│  ╚═════╝   ╚═════╝  ╚══════╝                                                │
│                                                                             │
│  🎵 DUS YouTube Music Studio Pro CLI | Android Phone Emulation              │
│  (Cookie-Free) • 1:1 Square Art                                             │
│  Output Destination: downloads                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Workflow Steps:
1. **Enter URL**: Paste any YouTube Music track or playlist link.
2. **Track Inspector**: Displays metadata card (Track Title, Artist/Channel, Duration, Source URL).
3. **Select Format**:
   - `[1] MP3` — Universal compatibility.
   - `[2] M4A` — Apple AAC standard.
   - `[3] FLAC` — Uncompressed lossless PCM.
   - `[4] OPUS` — Next-gen high efficiency audio.
4. **Select Quality / Bitrate**:
   - Single bitrate (e.g. `320k`, `256k`, `192k`, `128k`).
   - Or **ALL 4 QUALITIES** (e.g. `5` or `1,2,3,4`) to generate all 4 files simultaneously in one download pass.
5. **Select Filename Style**:
   - `[1] Clean / Safe` — `Artist-Title-320kbps.mp3` (No spaces, cross-platform filesystem safe).
   - `[2] Formal` — `Artist - Title (320kbps).mp3`.
6. **Select Device & Authentication Mode**:
   - `[1] Android Phone Emulation` (Default, 100% cookie-free).
   - `[2-4] Browser Cookies` (Firefox, Chrome, Edge).
   - `[5] cookies.txt` custom file path.
7. **Repeat Prompt**: Asks *"Would you like to download another song?"* upon completion.

---

## 2. CLI Command Line Interface

You can pass command-line arguments directly for automated scripts or single commands:

```bash
python main.py [URL] [OPTIONS]
```

### CLI Flags Reference Table

| Flag | Long Argument | Type | Default | Description |
|---|---|---|---|---|
| `-i` | `--interactive` | Flag | `False` | Launch interactive REPL dashboard. |
| `-f` | `--format` | Choice | `mp3` | Target audio format: `mp3`, `m4a`, `flac`, `opus`. |
| `-q` | `--quality` | String | `best` | Bitrate or quality preset: `best`, `medium`, `low`, `320`, `256`, `192`, `128`. |
| `-m` | `--multi-quality` | Flag | `False` | 4-in-1 multi-quality download (downloads once, transcodes 4 files locally). |
| | `--qualities` | String | `320k,256k,192k,128k` | Custom comma-separated bitrates for `-m`. |
| `-n` | `--naming-style` | Choice | `clean` | Filename format: `clean` (hyphens) or `formal` (standard spaces/brackets). |
| `-F` | `--list-formats` | Flag | `False` | Inspect and print available audio stream table without downloading. |
| `-b` | `--batch` | Flag | `False` | Download entire playlist or album instead of single track. |
| | `--dry-run` | Flag | `False` | Simulate extraction and print track info without writing files to disk. |
| `-a` | `--auth-mode` | Choice | `android` | Auth mode: `android` (cookie-free), `browser`, `cookiefile`. |
| `-B` | `--browser` | Choice | None | Browser for cookie extraction: `firefox`, `chrome`, `edge`, `brave`. |
| `-C` | `--cookies` | Path | None | Path to Netscape `cookies.txt` file. |
| | `--client` | String | `android,ios` | InnerTube player client names to emulate. |
| | `--no-cookies` | Flag | `False` | Explicitly enforce zero-cookie mode. |
| `-o` | `--output` | Path | `downloads/` | Destination folder for downloaded files. |

---

## 3. Practical Recipes & Examples

### A. High-Quality 320kbps MP3
```powershell
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -f mp3 -q 320k
```

### B. 4-in-1 Multi-Bitrate Batch Generation
Generates `320kbps`, `256kbps`, `192kbps`, and `128kbps` versions in one network request:
```powershell
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -m
```
Custom bitrates:
```powershell
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -m --qualities "320k,128k,64k"
```

### C. Lossless FLAC or Studio OPUS
```powershell
# FLAC Uncompressed
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -f flac

# High-Efficiency Native OPUS (~141kbps)
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -f opus
```

### D. Downloading Entire Playlists / Albums
Add the `-b` (`--batch`) flag:
```powershell
python main.py "https://music.youtube.com/playlist?list=YOUR_PLAYLIST_ID" -b -f mp3 -q 320k
```

### E. Inspecting Available Audio Streams (`-F`)
Print available audio streams, formats, codecs, bitrates, sample rates, and approximate sizes:
```powershell
python main.py "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID" -F
```

Output:
```text
Available Audio Formats:
Format ID  Extension  Audio Codec  Bitrate / ABR  Sample Rate  Filesize Approx
251        webm       opus         141 kbps       48000 Hz     3.24 MB
140        m4a        mp4a.40.2    129 kbps       44100 Hz     2.98 MB
250        webm       opus         70 kbps        48000 Hz     1.62 MB
249        webm       opus         50 kbps        48000 Hz     1.15 MB
```

### F. Authenticating with Browser Cookies or cookies.txt
For age-gated or private playlist items:
```powershell
# Using Firefox cookies:
python main.py "https://music.youtube.com/watch?v=..." --browser firefox

# Using exported cookies.txt:
python main.py "https://music.youtube.com/watch?v=..." --cookies "C:\path\to\cookies.txt"
```

### G. Custom Output Directory
```powershell
python main.py "https://music.youtube.com/watch?v=..." -o "D:\MyMusic\Favorites"
```

### H. Testing Downloads with Dry-Run Mode
Test connectivity, metadata parsing, and track validation without downloading or modifying disk:
```powershell
python main.py "https://music.youtube.com/watch?v=dQw4w9WgXcQ" --dry-run
```

---

## 4. Filename Naming Schemes

You can customize the naming pattern using `-n` or `--naming-style`:

| Scheme | Example Output | Notes |
|---|---|---|
| `clean` *(Default)* | `Artist-Track-Title-320kbps.mp3` | Cross-platform safe, no spaces, hyphens for separators. Ideal for media servers, car stereos, and Linux systems. |
| `formal` | `Artist - Track Title (320kbps).mp3` | Traditional music player display format with clean spaces and parentheses. |

---

## 5. Programmatic Python API

You can import and use `YtMusicDownloader` in your own Python projects:

```python
from yt_music_dl import YtMusicDownloader

# Initialize downloader instance
downloader = YtMusicDownloader(
    output_dir="./my_downloads",
    audio_format="mp3",
    quality="320k",
    auth_mode="android",  # Android InnerTube client profile
)

# Download single track
url = "https://music.youtube.com/watch?v=YOUR_OWN_TRACK_ID"
success = downloader.download(url, naming_style="clean")

# Or download 4-in-1 multi-bitrate package
results = downloader.download_multi_quality(
    url,
    qualities=["320k", "256k", "192k", "128k"],
    naming_style="formal",
)

for item in results:
    print(f"Downloaded: {item['filename']} ({item['quality']}, {item['size_mb']:.2f} MB)")
```

---

## 6. Shell Scripting & Automation

### PowerShell (Download a list of URLs from a text file):
```powershell
Get-Content urls.txt | ForEach-Object {
    if ($_ -match "^https?://") {
        python main.py $_.Trim() -f mp3 -q 320k
    }
}
```

### Bash / Linux:
```bash
while IFS= read -r url || [ -n "$url" ]; do
    [[ -z "$url" || "$url" =~ ^# ]] && continue
    python3 main.py "$url" -f mp3 -q 320k
done < urls.txt
```
