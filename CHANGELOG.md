# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-09-12

### Added
- **100% Cookie-Free Android Phone Emulation**: Uses InnerTube mobile player client (`android`, `ios`) with dynamic modern device fingerprints (Pixel 8 Pro, Galaxy S24 Ultra, OnePlus 12, Xiaomi 14, Nothing Phone 2) to bypass desktop web bot-checks and 429 rate limits.
- **Multi-Browser & Cookiefile Fallback**: Added support for selecting browser cookies (`--browser firefox`, `chrome`, `edge`, `brave`, `opera`) or custom Netscape `cookies.txt` files (`--cookies`).
- **Professional Package Architecture**: Modularized into `yt_music_dl/` (`core`, `ui`, `utils`, `cli`) with modern `pyproject.toml` and console script `yt-music-dl`.
- **Automated GitHub CI/CD**: Added GitHub Actions testing workflow for multi-OS (Ubuntu, Windows) across Python 3.10, 3.11, and 3.12.
- **GitHub Open-Source Assets**: Added Issue templates, PR template, `CONTRIBUTING.md`, `SECURITY.md`, and `LICENSE`.

### Changed
- Refactored `downloader.py`, `utils.py`, `config.py`, and `interactive.py` to maintain 100% root-level backward compatibility bridges.
- Silenced benign experimental desktop web warnings (SABR and PO Token skips) for a clean progress terminal experience.

---

## [1.0.0] - 2026-09-11

### Added
- Initial release of YouTube Music Audio Downloader CLI.
- High-quality audio extraction: MP3 (320kbps), M4A, FLAC, and OPUS.
- 1:1 Square Album Artwork cropping and ID3v2.3 metadata embedding.
- Interactive REPL studio dashboard.
- 4-in-1 multi-bitrate transcode engine.
- Filename styling selection: Clean vs Formal.
