# 📦 Detailed Installation Guide

This guide covers complete step-by-step setup instructions for **YouTube Music Audio Downloader CLI** across **Windows**, **Linux**, and **macOS**, including external prerequisites (**FFmpeg**, **Node.js**) and Python virtual environment configuration.

---

## Table of Contents
- [System Requirements](#system-requirements)
- [Prerequisites Setup](#prerequisites-setup)
  - [1. Windows Installation](#1-windows-installation)
  - [2. macOS Installation](#2-macos-installation)
  - [3. Linux Installation (Ubuntu/Debian, Fedora, Arch)](#3-linux-installation-ubuntudebian-fedora-arch)
- [Project Installation](#project-installation)
  - [Clone Repository](#clone-repository)
  - [Virtual Environment (Recommended)](#virtual-environment-recommended)
  - [Install Dependencies](#install-dependencies)
  - [Global CLI Tool Registration](#global-cli-tool-registration)
- [Verification](#verification)
- [Next Steps](#next-steps)

---

## System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| **Python** | 3.10 | 3.11 or 3.12 |
| **FFmpeg** | 5.0+ | Latest 6.x or 7.x |
| **Node.js** | 18.x LTS | Latest 20.x or 22.x LTS |
| **Disk Space** | 200 MB (app & cache) | 2+ GB (for downloaded audio libraries) |
| **Network** | Stable Internet connection | Broadband / Fiber |

---

## Prerequisites Setup

### 1. Windows Installation

#### Option A: Using Windows Package Manager (`winget`) — Recommended
Open **PowerShell** as Administrator or standard user and run:

```powershell
# 1. Install Python 3.11
winget install Python.Python.3.11

# 2. Install FFmpeg (Full Gyan build with all codecs)
winget install Gyan.FFmpeg

# 3. Install Node.js LTS (Required for YouTube challenge-solving)
winget install OpenJS.NodeJS.LTS
```

> [!NOTE]
> Close and reopen your PowerShell window after running `winget` so the updated `PATH` environment variable takes effect.

#### Option B: Using Chocolatey
```powershell
choco install python ffmpeg nodejs-lts -y
```

#### Option C: Using Scoop
```powershell
scoop install python ffmpeg nodejs-lts
```

#### Manual Verification on Windows:
Run the following in PowerShell:
```powershell
python --version
ffmpeg -version
node --version
```
Ensure all three commands return version strings without errors.

---

### 2. macOS Installation

The easiest method on macOS is via [Homebrew](https://brew.sh/):

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install required packages
brew update
brew install python@3.11 ffmpeg node
```

Verify the installation:
```bash
python3 --version
ffmpeg -version
node --version
```

---

### 3. Linux Installation (Ubuntu/Debian, Fedora, Arch)

#### Debian / Ubuntu / Linux Mint
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv ffmpeg nodejs
```

#### Fedora / RHEL / AlmaLinux
```bash
sudo dnf install -y python3 python3-pip ffmpeg nodejs
```
*(Note: If FFmpeg is unavailable in standard Fedora repos, enable RPM Fusion free repository first).*

#### Arch Linux / Manjaro
```bash
sudo pacman -Syu --noconfirm python python-pip ffmpeg nodejs
```

---

## Project Installation

### Method 1: Install via PyPI (Recommended & Easiest)

Install the package directly into your system or virtual environment in a single command:

```bash
pip install --upgrade dus-yt-music-dl
```

This immediately registers the `dus-yt-music-dl` (and `yt-music-dl`) global CLI command on your PATH.

---

### Method 2: Install from Source (Developer Setup)

#### 1. Clone Repository
```bash
git clone https://github.com/dusmamud/youtube-music-downloader.git
cd youtube-music-downloader
```

#### 2. Virtual Environment (Recommended)

Using a virtual environment prevents conflicting dependencies with other Python tools on your system:

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If you encounter an execution policy error on Windows, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

#### On Linux / macOS (Bash / Zsh):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Install Dependencies

Install all core dependencies specified in `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Core dependencies installed:
- `yt-dlp` (Stream extraction engine)
- `rich` (Terminal dashboard & progress bars)
- `mutagen` (ID3v2 metadata & album art tagger)
- `Pillow` (1:1 square cover art processing)
- `requests` (Network helper)
- `brotli` (High-performance stream decompression engine)

---

### Global CLI Tool Registration

To run `dus-yt-music-dl` (or `yt-music-dl`) directly from any terminal window without typing `python main.py`:

```bash
pip install -e .
```

This installs the project in **editable mode** using `pyproject.toml`, creating the `dus-yt-music-dl` and `yt-music-dl` binary entry points on your PATH.

---

## Verification

Verify your installation by running the built-in diagnostic test:

```powershell
python -c "from yt_music_dl.utils.system import check_dependencies; check_dependencies()"
```

Or run the test suite:
```powershell
python -m unittest discover tests
```

You should see:
```text
[OK] yt-dlp is installed and available.
[OK] ffmpeg is installed and available.
[OK] node is installed and available.
Ran 8 tests ... OK
```

---

## Next Steps

- Check out [docs/USAGE.md](USAGE.md) for detailed CLI examples and the interactive studio guide.
- Encountering network or authentication issues? Read [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md).
