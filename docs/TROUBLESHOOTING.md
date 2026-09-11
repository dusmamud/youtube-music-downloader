# 🛠️ Comprehensive Troubleshooting Guide

This guide details common errors, root causes, and verified fixes when downloading audio from YouTube Music using this CLI tool.

---

## Table of Contents
- [1. Bot Detection: "Sign in to confirm you're not a bot" / HTTP 403](#1-bot-detection-sign-in-to-confirm-youre-not-a-bot--http-403)
- [2. FFmpeg / FFprobe Not Found](#2-ffmpeg--ffprobe-not-found)
- [3. Node.js Runtime Not Found / JS Challenge Solving](#3-nodejs-runtime-not-found--js-challenge-solving)
- [4. Chromium Cookie Database Locked (`sqlite3.OperationalError`)](#4-chromium-cookie-database-locked-sqlite3operationalerror)
- [5. HTTP 429 "Too Many Requests"](#5-http-429-too-many-requests)
- [6. Corrupted or Missing Album Art](#6-corrupted-or-missing-album-art)
- [7. Understanding Bitrates: Fake 320kbps vs Native YouTube Stream](#7-understanding-bitrates-fake-320kbps-vs-native-youtube-stream)
- [8. Windows Long Path Limit (>260 characters)](#8-windows-long-path-limit-260-characters)
- [9. Cancelling Downloads (Graceful Exit)](#9-cancelling-downloads-graceful-exit)

---

## 1. Bot Detection: "Sign in to confirm you're not a bot" / HTTP 403

### Symptoms:
```text
ERROR: [youtube] VIDEO_ID: Sign in to confirm you're not a bot. This helps protect our community.
HTTP Error 403: Forbidden
```

### Root Cause:
YouTube continuously updates anti-scraping systems on its desktop web interface (`web` client). Desktop web requests from automated scripts or VPN/datacenter IP addresses trigger Proof-of-Origin (PoToken) or reCAPTCHA verification.

### Solutions:

#### Solution A: Default Android Phone Emulation (Cookie-Free)
This project is pre-configured to use **Android phone client emulation** (`player_client: ["android", "ios"]`) combined with authentic mobile User-Agents (Google Pixel, Samsung Galaxy, OnePlus, Xiaomi). Android mobile API requests rarely trigger bot challenges.

Make sure you are running in Android emulation mode:
```powershell
# In interactive mode: Select Step 4 Option 1 (Android Phone Emulation)
python main.py

# Or in CLI direct mode:
python main.py "https://music.youtube.com/watch?v=VIDEO_ID" --auth-mode android
```

#### Solution B: Authenticate via Mozilla Firefox Cookies
Firefox stores cookies in a plaintext SQLite format that does **not** lock when the browser is open:
1. Open Firefox and log into [YouTube Music](https://music.youtube.com).
2. Run with the `--browser firefox` flag:
   ```powershell
   python main.py "https://music.youtube.com/watch?v=VIDEO_ID" --browser firefox
   ```

#### Solution C: Export Netscape `cookies.txt`
1. Install a reputable cookie export extension in your browser (e.g., *Get cookies.txt LOCALLY* for Chrome/Firefox).
2. Visit `music.youtube.com` and export your cookies as `cookies.txt`.
3. Pass the file to the downloader:
   ```powershell
   python main.py "https://music.youtube.com/watch?v=VIDEO_ID" --cookies "C:\path\to\cookies.txt"
   ```

---

## 2. FFmpeg / FFprobe Not Found

### Symptoms:
```text
WARNING: ffmpeg not found! Converting audio and embedding thumbnails will fail.
FileNotFoundError: [WinError 2] The system cannot find the file specified: 'ffmpeg'
```

### Root Cause:
FFmpeg is either not installed or its `bin` folder is missing from your system `PATH` environment variable.

### Fix:

#### Windows:
1. Install via Winget:
   ```powershell
   winget install Gyan.FFmpeg
   ```
2. Close all terminal windows and open a fresh PowerShell session.
3. Test with:
   ```powershell
   ffmpeg -version
   ```
4. If still not recognized, manually add `C:\Users\<YourUser>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg...\bin` to your User Environment Variable `Path`.

#### Linux / macOS:
```bash
# Ubuntu / Debian
sudo apt install -y ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

---

## 3. Node.js Runtime Not Found / JS Challenge Solving

### Symptoms:
```text
WARNING: JavaScript engine could not be spawned. Node.js is recommended for solving YouTube signature tokens.
```

### Root Cause:
YouTube scrambles stream URLs using obfuscated JavaScript n-sig challenge functions. `yt-dlp` relies on Node.js on PATH to execute these scripts in an isolated sandbox.

### Fix:
1. Install Node.js:
   - **Windows**: `winget install OpenJS.NodeJS.LTS`
   - **macOS**: `brew install node`
   - **Linux**: `sudo apt install -y nodejs`
2. Restart terminal and verify:
   ```bash
   node --version
   ```

---

## 4. Chromium Cookie Database Locked (`sqlite3.OperationalError`)

### Symptoms:
```text
sqlite3.OperationalError: database is locked
yt_dlp.utils.ExtractorError: Could not copy Chrome cookie database.
```

### Root Cause:
Chromium-based browsers (Google Chrome, Microsoft Edge, Brave, Opera) lock their `Cookies` SQLite file while the browser process is active.

### Fix:
1. **Option 1 (Recommended)**: Use Firefox (`--browser firefox`) or Android emulation (`--auth-mode android`).
2. **Option 2**: Completely close all Google Chrome or Microsoft Edge windows (check Task Manager for background processes) before running `--browser chrome`.
3. **Option 3**: Use an exported `cookies.txt` file via `--cookies cookies.txt`.

---

## 5. HTTP 429 "Too Many Requests"

### Symptoms:
```text
HTTP Error 429: Too Many Requests
The server is refusing to respond due to rate limiting.
```

### Root Cause:
Downloading too many consecutive songs within a short time frame from the same IP address.

### Fix:
1. **Built-in Backoff**: The downloader automatically pauses and applies exponential backoff for transient 429 responses.
2. **Use 4-in-1 Transcoding**: If you want multiple bitrates (320k, 256k, 192k, 128k), always use `-m` (`--multi-quality`). It downloads the track from YouTube **only once** and generates the extra bitrates locally via FFmpeg, reducing network calls by 75%.
3. Add a slight sleep between batch items or rotate network connection if rate-limited for an extended duration.

---

## 6. Corrupted or Missing Album Art

### Symptoms:
- Audio player shows blank default artwork or distorted aspect ratio.

### Root Cause:
YouTube serves 16:9 widescreen video thumbnails (`maxresdefault.jpg` or `hqdefault.jpg`) with black pillarboxes, or WebP thumbnails which older offline players (car stereos, iPods) cannot decode.

### Fix:
Our tool includes a dedicated Pillow-based **1:1 Center-Cropping Pipeline**:
- Downloads the highest resolution thumbnail.
- Converts WebP/PNG thumbnails to standard JPEG RGB.
- Crops cleanly from the center into a crisp 1:1 square (e.g. 1200x1200px).
- Embeds standard ID3v2.3 `APIC` cover art frames supported by all hardware/software players.

---

## 7. Understanding Bitrates: Fake 320kbps vs Native YouTube Stream

### Explanation:
- YouTube stores audio as:
  - **Opus**: ~141 kbps (format 251) — High transparency, equivalent to 256-320kbps MP3 in perceptual quality.
  - **AAC**: ~129 kbps (format 140) — Apple standard.
- YouTube **does not** store native 320kbps MP3 files.
- When you choose `--format mp3 -q 320k`, the tool extracts the pristine native Opus/AAC stream and transcodes it to 320kbps CBR/VBR MP3 using FFmpeg's `libmp3lame` encoder with maximum quality flags.
- If you prefer uncompressed 1:1 stream reproduction without any re-encoding generation loss, use:
  ```powershell
  python main.py "URL" --format opus
  # Or native M4A
  python main.py "URL" --format m4a
  ```

---

## 8. Windows Long Path Limit (>260 characters)

### Symptoms:
```text
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

### Fix:
1. In `main.py`, choose `--naming-style clean` to strip long metadata strings:
   ```powershell
   python main.py "URL" --naming-style clean
   ```
2. Enable Windows Long Path support in PowerShell (Admin):
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

---

## 9. Cancelling Downloads (Graceful Exit)

- You can press `Ctrl + C` at any time during interactive prompts or ongoing downloads.
- The CLI catches `KeyboardInterrupt` and `EOFError` gracefully, removes temporary `.part` and `.ytdl` files, prints a clean exit message, and terminates without traceback.
