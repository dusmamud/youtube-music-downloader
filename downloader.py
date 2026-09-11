"""
Backward compatibility bridge for downloader imports.
Redirects to yt_music_dl.core.downloader.
"""
from yt_music_dl.core.downloader import YtMusicDownloader

__all__ = ["YtMusicDownloader"]
