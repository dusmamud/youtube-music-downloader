import sys
import re
from typing import Dict, Any

import yt_dlp
from rich.prompt import Prompt, Confirm
from rich.table import Table

from yt_music_dl import config
from yt_music_dl.utils.system import (
    console,
    check_dependencies,
    log_warning,
)
from yt_music_dl.core.device_profiler import get_random_android_device, get_device_headers
from yt_music_dl.core.downloader import YtMusicDownloader
from yt_music_dl.ui.banner import print_banner, display_preview_card


def fetch_track_preview(url: str, auth_mode: str = "android", browser: str = None, cookiefile: str = None) -> Dict[str, Any]:
    """Fetches track metadata to display an interactive preview card."""
    device = get_random_android_device()
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "js_runtimes": {"node": {}},
        "remote_components": {"ejs:github"},
    }
    if auth_mode == "android":
        ydl_opts["extractor_args"] = {"youtube": {"player_client": ["android", "ios"]}}
        ydl_opts["http_headers"] = get_device_headers(device)
    elif auth_mode == "browser" and browser:
        ydl_opts["cookiesfrombrowser"] = (browser,)
    elif auth_mode == "cookiefile" and cookiefile:
        ydl_opts["cookiefile"] = str(cookiefile)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info or {}
    except Exception:
        return {}


def _interactive_loop(output_dir: str = None):
    active_output = output_dir or config.OUTPUT_DIR
    print_banner(output_dir=active_output)

    # Safe divider width for mobile screens (Termux)
    sep_len = min(console.width or 50, 50)

    while True:
        console.print("\n" + "─" * sep_len, style="dim")
        url = Prompt.ask(
            "[bold cyan]YouTube URL[/bold cyan] ([bold red]q[/bold red] to quit)"
        ).strip()

        if url.lower() in ("q", "quit", "exit"):
            console.print("\n[bold green]Exiting DUS YouTube Music Studio Pro. Goodbye![/bold green] 👋\n")
            break

        if not url:
            continue

        # Fetch and show preview
        with console.status("[bold yellow]Inspecting YouTube Music stream..."):
            info = fetch_track_preview(url)

        if info:
            display_preview_card(info)
        else:
            log_warning("Could not fetch pre-download preview, but proceeding directly to download...")

        # 1. Format Selection
        console.print("\n[bold yellow]Step 1: Choose Audio Format[/bold yellow]")
        console.print("  [bold cyan][1][/bold cyan] MP3   - Universal Compatibility (320k, 256k, 192k, 128k) [bold green][Default][/bold green]")
        console.print("  [bold cyan][2][/bold cyan] M4A   - Pristine Apple AAC (Native 129k Stream Copy / 256k)")
        console.print("  [bold cyan][3][/bold cyan] FLAC  - Lossless PCM Uncompressed (Studio Quality)")
        console.print("  [bold cyan][4][/bold cyan] OPUS  - Next-Gen High-Efficiency Audio")

        fmt_choice = Prompt.ask("Select Format", choices=["1", "2", "3", "4"], default="1")
        fmt_map = {"1": "mp3", "2": "m4a", "3": "flac", "4": "opus"}
        chosen_format = fmt_map[fmt_choice]

        # 2. Quality Selection
        console.print("\n[bold yellow]Step 2: Choose Audio Quality / Bitrate[/bold yellow]")
        is_multi_quality = False
        qualities_to_download = []
        chosen_single_quality = "best"

        if chosen_format == "mp3":
            console.print("  [bold cyan][1][/bold cyan] 320 kbps (Best Quality) [bold green][Default][/bold green]")
            console.print("  [bold cyan][2][/bold cyan] 256 kbps (High Quality)")
            console.print("  [bold cyan][3][/bold cyan] 192 kbps (Medium Quality - Matches YouTube Source)")
            console.print("  [bold cyan][4][/bold cyan] 128 kbps (Low Quality - Compact)")
            console.print("  [bold cyan][5][/bold cyan] [bold green]ALL 4 QUALITIES (320k + 256k + 192k + 128k ek saath download karo!)[/bold green]")
            console.print("  [dim]💡 Tip: '1' for 320k, '5' ya '1,2,3,4' type karke 4 files ek saath paayein![/dim]")

            raw_choice = Prompt.ask("Choose Bitrate [1/2/3/4/5 or e.g. 1,2,3,4]", default="1").strip().lower()
            mp3_map = {"1": "320k", "2": "256k", "3": "192k", "4": "128k"}

            if raw_choice in ("5", "all", "all 4", "4", "4-in-1", "1,2,3,4", "1 2 3 4") and raw_choice != "4":
                is_multi_quality = True
                qualities_to_download = ["320k", "256k", "192k", "128k"]
            elif "," in raw_choice or " " in raw_choice:
                tokens = [t.strip() for t in re.split(r"[\s,]+", raw_choice) if t.strip()]
                selected = []
                for t in tokens:
                    if t in mp3_map:
                        selected.append(mp3_map[t])
                    elif t.replace("k", "").isdigit():
                        selected.append(f"{t.replace('k', '')}k")
                if len(selected) > 1:
                    is_multi_quality = True
                    qualities_to_download = list(dict.fromkeys(selected))
                elif len(selected) == 1:
                    chosen_single_quality = selected[0].replace("k", "")
                else:
                    chosen_single_quality = "320"
            elif raw_choice in mp3_map:
                chosen_single_quality = mp3_map[raw_choice].replace("k", "")
            elif raw_choice in ("5", "all"):
                is_multi_quality = True
                qualities_to_download = ["320k", "256k", "192k", "128k"]
            else:
                chosen_single_quality = "320"

        elif chosen_format == "m4a":
            console.print("  [bold cyan][1][/bold cyan] 256 kbps AAC (High Quality - Apple Master Standard) [bold green][Default][/bold green]")
            console.print("  [bold cyan][2][/bold cyan] 192 kbps AAC (Medium Quality)")
            console.print("  [bold cyan][3][/bold cyan] 128 kbps AAC (Low Quality - Compact)")
            console.print("  [bold cyan][4][/bold cyan] 48 kbps AAC (Ultra Compact - ~1 MB Tiny Size)")
            console.print("  [bold cyan][5][/bold cyan] [bold green]ALL 4 QUALITIES (256k + 192k + 128k + 48k simultaneously!)[/bold green]")
            console.print("  [dim]💡 Tip: '1' for 256k, '5' ya '1,2,3,4' type karke 4 files ek saath paayein![/dim]")

            raw_choice = Prompt.ask("Choose Bitrate [1/2/3/4/5 or e.g. 1,2,3,4]", default="1").strip().lower()
            m4a_map = {"1": "256k", "2": "192k", "3": "128k", "4": "48k"}

            if raw_choice in ("5", "all", "all 4", "4-in-1", "1,2,3,4", "1 2 3 4") and raw_choice != "4":
                is_multi_quality = True
                qualities_to_download = ["256k", "192k", "128k", "48k"]
            elif "," in raw_choice or " " in raw_choice:
                tokens = [t.strip() for t in re.split(r"[\s,]+", raw_choice) if t.strip()]
                selected = [m4a_map[t] for t in tokens if t in m4a_map]
                if len(selected) > 1:
                    is_multi_quality = True
                    qualities_to_download = list(dict.fromkeys(selected))
                elif len(selected) == 1:
                    chosen_single_quality = selected[0].replace("k", "")
                else:
                    chosen_single_quality = "256"
            elif raw_choice in m4a_map:
                chosen_single_quality = m4a_map[raw_choice].replace("k", "")
            elif raw_choice in ("5", "all"):
                is_multi_quality = True
                qualities_to_download = ["256k", "192k", "128k", "48k"]
            else:
                chosen_single_quality = "256"

        elif chosen_format == "opus":
            console.print("  [bold cyan][1][/bold cyan] Native Opus (~141 kbps) [bold green][Default][/bold green]")
            console.print("  [bold cyan][2][/bold cyan] 160 kbps Opus")
            console.print("  [bold cyan][3][/bold cyan] 128 kbps Opus")
            console.print("  [bold cyan][4][/bold cyan] 96 kbps Opus")
            console.print("  [bold cyan][5][/bold cyan] [bold green]ALL QUALITIES simultaneously![/bold green]")

            raw_choice = Prompt.ask("Choose Bitrate [1/2/3/4/5 or e.g. 1,2,3,4]", default="1").strip().lower()
            opus_map = {"1": "141k", "2": "160k", "3": "128k", "4": "96k"}
            if raw_choice in ("5", "all", "1,2,3,4", "1 2 3 4"):
                is_multi_quality = True
                qualities_to_download = ["160k", "141k", "128k", "96k"]
            elif "," in raw_choice or " " in raw_choice:
                tokens = [t.strip() for t in re.split(r"[\s,]+", raw_choice) if t.strip()]
                selected = [opus_map[t] for t in tokens if t in opus_map]
                if len(selected) > 1:
                    is_multi_quality = True
                    qualities_to_download = list(dict.fromkeys(selected))
                elif len(selected) == 1:
                    chosen_single_quality = selected[0].replace("k", "")
                else:
                    chosen_single_quality = "best"
            elif raw_choice in opus_map:
                chosen_single_quality = opus_map[raw_choice].replace("k", "")
            else:
                chosen_single_quality = "best"

        else:  # flac
            console.print("  [bold cyan][1][/bold cyan] Studio Lossless PCM (Native Best) [bold green][Default][/bold green]")
            chosen_single_quality = "best"

        # 3. Filename Style Selection
        console.print("\n[bold yellow]Step 3: Choose Filename Style[/bold yellow]")
        console.print("  [bold cyan][1][/bold cyan] Clean / Safe: [bold white]Artist-Title-320kbps.mp3[/bold white] (No spaces, clean hyphens/underscores) [bold green][Default][/bold green]")
        console.print("  [bold cyan][2][/bold cyan] Formal:       [bold white]Artist - Title (320kbps).mp3[/bold white]")

        name_choice = Prompt.ask("Select Filename Style", choices=["1", "2"], default="1")
        naming_style = "clean" if name_choice == "1" else "formal"

        # 4. Device & Authentication Mode Selection
        console.print("\n[bold yellow]Step 4: Device Identity & Authentication[/bold yellow]")
        console.print("  [bold cyan][1][/bold cyan] [bold green]Android Phone Emulation[/bold green] (Zero cookies needed, random mobile device identity) [bold green][Default][/bold green]")
        console.print("  [bold cyan][2][/bold cyan] Firefox Browser Cookies (Windows Safe)")
        console.print("  [bold cyan][3][/bold cyan] Chrome Browser Cookies")
        console.print("  [bold cyan][4][/bold cyan] Microsoft Edge Browser Cookies")
        console.print("  [bold cyan][5][/bold cyan] Custom cookies.txt File Path")

        auth_choice = Prompt.ask("Select Mode", choices=["1", "2", "3", "4", "5"], default="1")
        chosen_browser = None
        chosen_cookiefile = None

        if auth_choice == "1":
            chosen_auth_mode = "android"
        elif auth_choice == "2":
            chosen_auth_mode = "browser"
            chosen_browser = "firefox"
        elif auth_choice == "3":
            chosen_auth_mode = "browser"
            chosen_browser = "chrome"
        elif auth_choice == "4":
            chosen_auth_mode = "browser"
            chosen_browser = "edge"
        else:
            chosen_auth_mode = "cookiefile"
            chosen_cookiefile = Prompt.ask("Enter full path to cookies.txt").strip(' "\'')

        # 5. Perform Download
        downloader = YtMusicDownloader(
            output_dir=active_output,
            audio_format=chosen_format,
            quality=chosen_single_quality,
            auth_mode=chosen_auth_mode,
            browser=chosen_browser,
            cookiefile=chosen_cookiefile,
        )

        console.print("\n" + "─" * sep_len, style="dim")
        if is_multi_quality:
            results = downloader.download_multi_quality(
                url,
                qualities=qualities_to_download,
                naming_style=naming_style,
            )
            # Show summary table
            if results:
                summary_table = Table(title="✨ Multi-Quality Download Summary", border_style="green")
                summary_table.add_column("Filename", style="bold white")
                summary_table.add_column("Bitrate", style="cyan", justify="center")
                summary_table.add_column("Filesize", style="green", justify="right")
                summary_table.add_column("Cover Art", style="magenta", justify="center")

                for res in results:
                    summary_table.add_row(
                        res["filename"],
                        res["quality"],
                        f"{res['size_mb']:.2f} MB",
                        "1:1 Square (1200x1200)",
                    )
                console.print(summary_table)
        else:
            downloader.download(url, naming_style=naming_style)

        # 6. Prompt: Download another track?
        console.print("\n")
        download_another = Confirm.ask(
            "[bold cyan]Would you like to download another song?[/bold cyan]",
            default=True,
        )

        if not download_another:
            console.print("\n[bold green]All downloads finished. Enjoy your music![/bold green] 🎧\n")
            break


def run_interactive_session(output_dir: str = None):
    """Main interactive REPL loop with graceful exit on Ctrl+C."""
    if not check_dependencies():
        sys.exit(1)

    try:
        _interactive_loop(output_dir=output_dir)
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n[bold yellow]Operation cancelled by user. Goodbye![/bold yellow] 👋\n")
        sys.exit(0)
