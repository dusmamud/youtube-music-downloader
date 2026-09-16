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
    """Intelligently detects the most suitable download directory."""
    env_dir = os.getenv("YT_DOWNLOAD_DIR")
    if env_dir:
        return Path(env_dir)

    # 1. Android Termux Auto-Detection:
    # Prefer phone's shared Downloads folder so media is immediately visible in music players
    if is_termux_environment():
        termux_storage_download = Path.home() / "storage" / "downloads"
        if termux_storage_download.exists() and os.access(termux_storage_download, os.W_OK):
            return termux_storage_download

        android_sdcard_download = Path("/sdcard/Download")
        if android_sdcard_download.exists() and os.access(android_sdcard_download, os.W_OK):
            return android_sdcard_download

        android_emulated_download = Path("/storage/emulated/0/Download")
        if android_emulated_download.exists() and os.access(android_emulated_download, os.W_OK):
            return android_emulated_download

    # 2. Desktop / Local CWD:
    # If running from cloned source repo, can use repo downloads, else current working directory
    if (PROJECT_ROOT / "pyproject.toml").exists() and Path.cwd() == PROJECT_ROOT:
        return PROJECT_ROOT / "downloads"

    return Path.cwd() / "downloads"


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
