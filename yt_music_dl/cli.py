import sys
import argparse

from yt_music_dl import config
from yt_music_dl.version import __version__
from yt_music_dl.utils.system import check_dependencies, console
from yt_music_dl.core.downloader import YtMusicDownloader
from yt_music_dl.ui.interactive import run_interactive_session


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="🎵 YouTube Music High-Quality Audio Downloader CLI & Interactive Studio",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"dus-yt-music-dl {__version__}",
        help="Show program's version number and exit",
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="YouTube Music track or playlist URL (e.g., https://music.youtube.com/watch?v=...)",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Launch interactive CloudCode-style REPL dashboard (Default when run with no arguments)",
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=config.SUPPORTED_FORMATS,
        default=config.DEFAULT_FORMAT,
        help="Audio format to convert into (default: mp3 [320kbps])",
    )

    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        help="Audio quality preset ('best', 'medium', 'low') or numeric bitrate (default: best)",
    )

    parser.add_argument(
        "-m",
        "--multi-quality",
        action="store_true",
        help="4-in-1 multi-quality download (generates 320k, 256k, 192k, 128k simultaneously)",
    )

    parser.add_argument(
        "--qualities",
        default="320k,256k,192k,128k",
        help="Custom comma-separated bitrates for multi-quality download (default: 320k,256k,192k,128k)",
    )

    parser.add_argument(
        "-n",
        "--naming-style",
        choices=["clean", "formal"],
        default="clean",
        help="Filename styling: 'clean' (Artist-Title-320kbps.mp3) or 'formal' (Artist - Title (320kbps).mp3)",
    )

    parser.add_argument(
        "-F",
        "--list-formats",
        action="store_true",
        help="Inspect and display all available audio streams without downloading",
    )

    parser.add_argument(
        "-b",
        "--batch",
        action="store_true",
        help="Download entire playlist or album instead of only single track",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the download and show what would be downloaded without saving files",
    )

    parser.add_argument(
        "-a",
        "--auth-mode",
        choices=["android", "browser", "cookiefile", "none"],
        default=config.DEFAULT_AUTH_MODE,
        help="Authentication mode: 'android' (Cookie-free mobile phone emulation [default]), 'browser', 'cookiefile'",
    )

    parser.add_argument(
        "-B",
        "--browser",
        default=None,
        help="Browser name to extract cookies from if using browser auth (firefox, chrome, edge, brave, opera)",
    )

    parser.add_argument(
        "-C",
        "--cookies",
        default=None,
        help="Path to custom Netscape/Mozilla formatted cookies.txt file",
    )

    parser.add_argument(
        "--client",
        default="android,ios",
        help="Comma-separated YouTube player clients to emulate (default: android,ios)",
    )

    parser.add_argument(
        "--no-cookies",
        action="store_true",
        help="Enforce cookie-free mode (Default behavior is already cookie-free Android emulation)",
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help=f"Directory to save downloaded files (default: {config.OUTPUT_DIR})",
    )

    return parser


def main():
    try:
        # If no CLI arguments passed, start interactive REPL dashboard
        if len(sys.argv) == 1:
            run_interactive_session()
            return

        parser = create_parser()
        args = parser.parse_args()

        if args.output:
            config.set_output_dir(args.output)

        if args.interactive or not args.url:
            run_interactive_session(output_dir=args.output)
            return

        # Verify runtime dependencies (yt-dlp, ffmpeg, node)
        if not check_dependencies():
            sys.exit(1)

        url = args.url.strip()

        # Determine auth mode
        if args.cookies:
            auth_mode = "cookiefile"
        elif args.browser:
            auth_mode = "browser"
        elif args.no_cookies:
            auth_mode = "android"
        else:
            auth_mode = args.auth_mode

        clients = [c.strip() for c in args.client.split(",") if c.strip()]

        downloader = YtMusicDownloader(
            output_dir=args.output,
            audio_format=args.format,
            quality=args.quality,
            auth_mode=auth_mode,
            browser=args.browser,
            cookiefile=args.cookies,
            player_clients=clients,
            dry_run=args.dry_run,
            batch=args.batch,
        )

        if args.list_formats:
            success = downloader.list_formats(url)
            sys.exit(0 if success else 1)

        if args.multi_quality:
            q_list = [q.strip() for q in args.qualities.split(",") if q.strip()]
            results = downloader.download_multi_quality(
                url,
                qualities=q_list,
                naming_style=args.naming_style,
            )
            sys.exit(0 if results else 1)

        # Standard single download
        success = downloader.download(url, naming_style=args.naming_style)
        sys.exit(0 if success else 1)
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n[bold yellow]Operation cancelled by user. Goodbye![/bold yellow] 👋\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
