"""
Backward compatibility bridge for interactive imports.
Redirects to yt_music_dl.ui.interactive and yt_music_dl.ui.banner.
"""
from yt_music_dl.ui.interactive import run_interactive_session, fetch_track_preview
from yt_music_dl.ui.banner import print_banner, display_preview_card

__all__ = [
    "run_interactive_session",
    "fetch_track_preview",
    "print_banner",
    "display_preview_card",
]

if __name__ == "__main__":
    run_interactive_session()
