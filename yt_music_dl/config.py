import os
from pathlib import Path

# Base Paths
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent


def is_termux_environment() -> bool:
    """Detects if the application is running inside an Android Termux environment."""
    if os.getenv("TERMUX_VERSION"):
        return True
    prefix = os.getenv("PREFIX", "")
    if "com.termux" in prefix:
        return True
    if Path("/data/data/com.termux").exists():
        return True
    return False


def get_default_download_dir() -> Path:
    """
    Intelligently detects the most suitable download directory:
    1. If user passed custom env var YT_DOWNLOAD_DIR, use it.
    2. If user is in a custom working directory (NOT Termux home ~):
       - If CWD is already a Download/Music folder (e.g. ~/storage/downloads or /sdcard/Music), use CWD.
       - Otherwise (e.g. E:\dusmamud), use CWD / "downloads".
    3. If user is in Termux home (~):
       - Route directly to phone's canonical shared storage (/storage/emulated/0/Download or /sdcard/Download)
         so files are public and visible in native music players.
    """
    env_dir = os.getenv("YT_DOWNLOAD_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    cwd = Path.cwd().resolve()

    # If inside Termux environment
    if is_termux_environment():
        termux_home = Path.home().resolve()
        
        # Check if user has navigated to a specific folder outside of Termux private ~ home
        # e.g., cd ~/storage/downloads, cd /sdcard/Music, cd /storage/emulated/0/Download
        is_in_termux_home = (cwd == termux_home or str(cwd).startswith(str(termux_home / ".cache")))
        
        if not is_in_termux_home:
            # User specifically chose this working directory!
            # If current directory is already a Download/Music folder, save directly in it
            if cwd.name.lower() in ("download", "downloads", "music"):
                return cwd
            return cwd / "downloads"

        # User is at Termux home root (~)
        # Auto-route to real Android public storage so files appear in phone's Music player
        canonical_candidates = [
            Path("/storage/emulated/0/Download"),
            Path("/sdcard/Download"),
            (Path.home() / "storage" / "downloads").resolve(),
            (Path.home() / "storage" / "shared" / "Download").resolve(),
        ]
        for candidate in canonical_candidates:
            if candidate.exists() and os.access(candidate, os.W_OK):
                return candidate

        # If shared storage not granted, fallback to CWD / downloads
        return cwd / "downloads"

    # Standard Desktop / PC (Windows, macOS, Linux)
    # If in cloned source repo root, use repo downloads
    if (PROJECT_ROOT / "pyproject.toml").exists() and cwd == PROJECT_ROOT.resolve():
        return PROJECT_ROOT / "downloads"

    # If current directory is already named 'downloads' or 'download', save directly in it
    if cwd.name.lower() in ("download", "downloads", "music"):
        return cwd

    # In any other folder (e.g. E:\dusmamud), create a downloads subfolder
    return cwd / "downloads"


DEFAULT_DOWNLOAD_DIR = get_default_download_dir()
OUTPUT_DIR = str(DEFAULT_DOWNLOAD_DIR)


def set_output_dir(custom_path: str):
    """Dynamically updates the active output directory."""
    global OUTPUT_DIR
    if custom_path:
        # Expand user path (e.g. ~/storage/music)
        resolved = Path(custom_path).expanduser()
        OUTPUT_DIR = str(resolved)

# Browser & Auth Modes
# Modes: 'android' (Cookie-free mobile phone emulation, default), 'browser' (load from browser), 'cookiefile', 'none'
DEFAULT_AUTH_MODE = "android"
DEFAULT_BROWSER = "firefox"
SUPPORTED_BROWSERS = ["firefox", "chrome", "edge", "brave", "opera", "vivaldi", "chromium"]
DEFAULT_PLAYER_CLIENTS = ["android", "ios"]

# Android Device Emulation Pool
# Realistic modern Android smartphone profiles rotated per session
ANDROID_DEVICE_PROFILES = [
    {
        "brand": "Google",
        "model": "Pixel 8 Pro",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro Build/UD1A.231105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/128.0.6613.127 Mobile Safari/537.36",
    },
    {
        "brand": "Samsung",
        "model": "Galaxy S24 Ultra",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/127.0.6533.103 Mobile Safari/537.36",
    },
    {
        "brand": "OnePlus",
        "model": "OnePlus 12",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; CPH2583 Build/UKQ1.230924.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/126.0.6478.122 Mobile Safari/537.36",
    },
    {
        "brand": "Xiaomi",
        "model": "Xiaomi 14 Pro",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; 23116PN5BC Build/UKQ1.230804.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/128.0.6613.88 Mobile Safari/537.36",
    },
    {
        "brand": "Nothing",
        "model": "Nothing Phone (2)",
        "user_agent": "Mozilla/5.0 (Linux; Android 14; A065 Build/UP1A.231005.007; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36",
    },
]

# Audio Settings
DEFAULT_FORMAT = "mp3"
DEFAULT_QUALITY = "0"  # "0" is best in ffmpeg VBR / 320kbps in CBR
SUPPORTED_FORMATS = ["mp3", "m4a", "flac", "opus"]

QUALITY_PRESETS = {
    "best": {"mp3": "320K", "m4a": "256K", "ffmpeg_quality": "0"},
    "medium": {"mp3": "192K", "m4a": "160K", "ffmpeg_quality": "2"},
    "low": {"mp3": "128K", "m4a": "128K", "ffmpeg_quality": "5"},
}

# Network & Retry Defaults
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds
BACKOFF_FACTOR = 2.0  # Exponential backoff factor for 429
SOCKET_TIMEOUT = 30  # seconds

# JS Runtime Engine
JS_ENGINE = "node"
