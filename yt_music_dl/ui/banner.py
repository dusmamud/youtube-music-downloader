from rich.panel import Panel
from rich.table import Table

from yt_music_dl import config
from yt_music_dl.utils.system import console


def print_banner():
    banner_text = (
        "[bold cyan]██████╗  ██╗   ██╗ ███████╗[/bold cyan]\n"
        "[bold cyan]██╔══██╗ ██║   ██║ ██╔════╝[/bold cyan]\n"
        "[bold magenta]██║  ██║ ██║   ██║ ███████╗[/bold magenta]\n"
        "[bold magenta]██║  ██║ ██║   ██║ ╚════██║[/bold magenta]\n"
        "[bold white]██████╔╝ ╚██████╔╝ ███████║[/bold white]\n"
        "[bold white]╚═════╝   ╚═════╝  ╚══════╝[/bold white]\n\n"
        "[bold yellow]🎵 DUS YouTube Music Studio Pro CLI[/bold yellow] | [dim]Android Phone Emulation (Cookie-Free) • 1:1 Square Art[/dim]\n"
        f"[dim]Output Destination: {config.OUTPUT_DIR}[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", padding=(1, 2)))


def display_preview_card(info: dict):
    if not info:
        return

    title = info.get("title", "Unknown Title")
    uploader = info.get("uploader") or info.get("channel") or info.get("artist") or "Unknown Artist"
    duration = info.get("duration")
    dur_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "Unknown"

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold cyan", width=12)
    table.add_column("Val", style="bold white")

    table.add_row("🎵 Title", title)
    table.add_row("🎤 Artist", uploader)
    table.add_row("⏱️ Duration", dur_str)
    table.add_row("🔗 URL", info.get("webpage_url") or info.get("url", ""))

    console.print(Panel(table, title="[bold green]Track Identified[/bold green]", border_style="green"))


def display_formats_table(formats: list, title: str = "Available Audio Formats"):
    """
    Renders a formatted table of audio formats using Rich.
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Format ID", style="cyan", width=12)
    table.add_column("Extension", style="green", width=10)
    table.add_column("Audio Codec", style="yellow", width=16)
    table.add_column("Bitrate / ABR", justify="right", style="white", width=14)
    table.add_column("Sample Rate", justify="right", style="white", width=12)
    table.add_column("Filesize Approx", justify="right", style="blue", width=16)

    for fmt in formats:
        # We only display actual audio streams
        acodec = fmt.get("acodec")
        if (fmt.get("vcodec") == "none" or fmt.get("resolution") == "audio only") and acodec and acodec != "none":
            fid = str(fmt.get("format_id", "N/A"))
            ext = str(fmt.get("ext", "N/A"))
            acodec_str = str(acodec)
            abr = f"{int(fmt['abr'])} kbps" if fmt.get("abr") else "N/A"
            asr = f"{fmt['asr']} Hz" if fmt.get("asr") else "N/A"
            filesize = fmt.get("filesize") or fmt.get("filesize_approx")
            if filesize:
                size_str = f"{filesize / (1024 * 1024):.2f} MB"
            else:
                size_str = "Unknown"

            table.add_row(fid, ext, acodec_str, abr, asr, size_str)

    console.print(table)
