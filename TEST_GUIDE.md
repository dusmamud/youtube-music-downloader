# 🧪 Test Suite & Quality Assurance Guide

This document explains the test architecture, execution commands, coverage areas, and guidelines for adding tests to **YouTube Music Audio Downloader**.

---

## Table of Contents
- [Test Architecture](#test-architecture)
- [Prerequisites](#prerequisites)
- [Running Tests](#running-tests)
  - [1. Using Python Built-in `unittest`](#1-using-python-built-in-unittest)
  - [2. Using `pytest`](#2-using-pytest)
  - [3. Running Individual Test Cases](#3-running-individual-test-cases)
- [Detailed Test Coverage Breakdown](#detailed-test-coverage-breakdown)
  - [1. Dependency Verification (`test_dependencies`)](#1-dependency-verification-test_dependencies)
  - [2. Backward Compatibility Bridges (`test_backward_compatibility_bridges`)](#2-backward-compatibility-bridges-test_backward_compatibility_bridges)
  - [3. CLI Argument Parser (`test_cli_parser`)](#3-cli-argument-parser-test_cli_parser)
  - [4. Filename Sanitization & Formatting (`test_filename_formatting`)](#4-filename-formatting-test_filename_formatting)
  - [5. Android Device Profile Generator (`test_android_device_generation`)](#5-android-device-profile-generator-test_android_device_generation)
  - [6. Downloader Options Builder (`test_downloader_options`)](#6-downloader-options-builder-test_downloader_options)
  - [7. Live Network Dry-Run Simulation (`test_dry_run_simulation`)](#7-live-network-dry-run-simulation-test_dry_run_simulation)
  - [8. Artifact Isolation & Cleanup (`test_cleanup_removes_artifacts`)](#8-artifact-isolation--cleanup-test_cleanup_removes_artifacts)
- [Guidelines for Adding New Tests](#guidelines-for-adding-new-tests)
- [Continuous Integration (CI)](#continuous-integration-ci)

---

## Test Architecture

The test suite is structured into two complementary layers:

```text
youtube-music-downloader/
├── test_download.py         # Root compatibility test suite (invokes legacy import bridges)
└── tests/
    └── test_downloader.py   # Primary package test suite (targets yt_music_dl package exports)
```

Both test files maintain strict sandbox isolation by operating on a temporary scratch directory (`downloads/test_scratch/` and `downloads/test_scratch_pkg/`) and ensuring complete teardown cleanup after every test run.

---

## Prerequisites

Before running tests, ensure the required runtime dependencies are installed and accessible on your `PATH`:

```powershell
python -c "from yt_music_dl.utils.system import check_dependencies; check_dependencies()"
```

Required binaries:
- `python` >= 3.10
- `ffmpeg` >= 5.0
- `node` >= 18.0

---

## Running Tests

### 1. Using Python Built-in `unittest`

Run all package tests:
```powershell
python -m unittest discover tests
```

Run root compatibility tests:
```powershell
python test_download.py
```

Run both test suites in one command (PowerShell):
```powershell
python -m unittest discover -s . -p "*test*.py"
```

### 2. Using `pytest`

If you have `pytest` installed:
```powershell
pip install pytest
pytest
```
*(Configuration is pre-defined in `pyproject.toml`).*

### 3. Running Individual Test Cases

To run a specific test method from `tests/test_downloader.py`:
```powershell
# Test only the CLI parser
python -m unittest tests.test_downloader.TestYtMusicPackage.test_cli_parser

# Test only the filename formatter
python -m unittest tests.test_downloader.TestYtMusicPackage.test_filename_formatting

# Test only the yt-dlp options generation
python -m unittest tests.test_downloader.TestYtMusicPackage.test_downloader_options
```

---

## Detailed Test Coverage Breakdown

### 1. Dependency Verification (`test_dependencies`)
- **Objective**: Confirms that `yt-dlp`, `ffmpeg`, and `node` runtimes are reachable.
- **Assertion**: Ensures `check_dependencies()` returns `True`.

### 2. Backward Compatibility Bridges (`test_backward_compatibility_bridges`)
- **Objective**: Guarantees that root-level imports (`from downloader import YtMusicDownloader`, `import config`, `from interactive import run_interactive_session`) match exports from `yt_music_dl`.
- **Assertion**: Asserts identity (`assertIs`) between legacy module symbols and package symbols.

### 3. CLI Argument Parser (`test_cli_parser`)
- **Objective**: Validates argument parsing for all CLI flags:
  - `-f` / `--format` (`mp3`, `m4a`, `flac`, `opus`)
  - `-q` / `--quality` (`320`, `best`, `medium`)
  - `-m` / `--multi-quality`
  - `-n` / `--naming-style` (`clean`, `formal`)
  - `-F` / `--list-formats`
  - `-b` / `--batch`
  - `--dry-run`
  - `--browser`, `--cookies`, `--client`, `--no-cookies`

### 4. Filename Sanitization & Formatting (`test_filename_formatting`)
- **Objective**: Checks that invalid OS filesystem characters (`\ / : * ? " < > |`) and commas are cleaned properly in both `clean` and `formal` naming schemes:
  - `clean`: `Wahed-Srabony-Shona-Phaki-320kbps.mp3`
  - `formal`: `Wahed, Srabony - Shona Phaki (320kbps).mp3`

### 5. Android Device Profile Generator (`test_android_device_generation`)
- **Objective**: Tests dynamic generation of realistic Android device fingerprints.
- **Assertion**: Confirms the presence of `brand`, `model`, and valid `Android` User-Agent strings.

### 6. Downloader Options Builder (`test_downloader_options`)
- **Objective**: Inspects the internal dictionary produced by `_build_ydl_opts()` across all 3 authentication modes:
  1. **Android Emulation Mode**: Verifies `simulate`, `extractor_args["youtube"]["player_client"]`, and mobile headers.
  2. **Browser Cookies Mode**: Confirms `cookiesfrombrowser` tuple and FFmpeg postprocessor configuration.
  3. **Cookiefile Mode**: Confirms path wiring to `cookies.txt`.

### 7. Live Network Dry-Run Simulation (`test_dry_run_simulation`)
- **Objective**: Executes a live network request to a standard YouTube test video with `--dry-run`.
- **Assertion**: Verifies stream metadata extraction succeeds without writing audio or temporary `.part` files to the filesystem.

### 8. Artifact Isolation & Cleanup (`test_cleanup_removes_artifacts`)
- **Objective**: Generates dummy `.part`, `.ytdl`, `.mp3`, and `.tmp` files in the test scratch directory.
- **Assertion**: Verifies `cleanup_test_files()` discovers and deletes all temporary leftovers.

---

## Guidelines for Adding New Tests

1. **Zero Contamination Policy**:
   - Always run operations inside `self.test_dir`.
   - Never write files directly into the production `downloads/` folder.
   - Always invoke `cleanup_test_files(self.test_dir)` in `tearDown()`.

2. **Avoid Full Media Downloads**:
   - For network tests, always pass `dry_run=True` to simulate downloads without wasting bandwidth or disk I/O.

3. **Fast Execution**:
   - Unit tests should finish in under 1 second.
   - Network simulation tests should finish in under 5 seconds.

4. **Exception Testing**:
   - When testing error conditions (e.g. `KeyboardInterrupt`), use `unittest.mock.patch` to verify graceful exits and clean return codes.

---

## Continuous Integration (CI)

Every pull request and push to `main` triggers automated testing on GitHub Actions:
- **Matrix**: Python 3.10, 3.11, 3.12 across Windows and Ubuntu.
- **Workflow configuration**: [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
- **Linter**: Ruff code formatting and linting.
- **Test Command**: `python -m unittest discover tests`.
