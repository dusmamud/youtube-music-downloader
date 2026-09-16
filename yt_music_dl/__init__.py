"""
YouTube Music Studio Pro
High-performance audio downloader with Android phone emulation, 1:1 album art, and multi-bitrate transcoding.
"""

from yt_music_dl.core.downloader import YtMusicDownloader
from yt_music_dl.ui.interactive import run_interactive_session
from yt_music_dl.cli import main

__version__ = "1.1.5"

__all__ = [
    "YtMusicDownloader",
    "run_interactive_session",
    "main",
    "__version__",
]
