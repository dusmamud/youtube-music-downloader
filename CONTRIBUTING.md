# Contributing to YouTube Music Audio Downloader

Thank you for your interest in contributing to **YouTube Music Audio Downloader**! We welcome bug fixes, documentation improvements, and new feature proposals.

---

## Getting Started

### 1. Fork and Clone
```bash
git clone https://github.com/dusmamud/youtube-music-downloader.git
cd youtube-music-downloader
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

---

## Running Tests

Before submitting any code changes, ensure all automated tests pass:

```bash
# Run full package test suite:
python -m unittest discover tests

# Or run root test runner:
python test_download.py
```

---

## Code Guidelines

- **Style**: Follow PEP 8 style guidelines.
- **Type Hints**: Include type hints on all new public functions and methods.
- **Zero Mock Policy**: Use real types and testable architectures where possible.
- **Clean Architecture**: Place business logic inside `yt_music_dl/core/`, user interface inside `yt_music_dl/ui/`, and shared helpers in `yt_music_dl/utils/`.
- **Backward Compatibility**: Never break existing CLI flags or root-level scripts (`main.py`).

---

## Submitting a Pull Request

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Commit your changes with clear, concise commit messages.
3. Push to your branch and open a Pull Request against the `main` branch.
4. Ensure the PR checklist is completed in `.github/PULL_REQUEST_TEMPLATE.md`.
