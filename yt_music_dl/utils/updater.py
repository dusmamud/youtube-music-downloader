import json
import urllib.request
from typing import Optional, Tuple
from rich.panel import Panel

from yt_music_dl.version import __version__
from yt_music_dl.utils.system import console


def parse_version(ver_str: str) -> Tuple[int, ...]:
    """Parses a semver string like '1.1.5' into a tuple of ints (1, 1, 5)."""
    clean_ver = ver_str.strip().lstrip("v")
    parts = []
    for p in clean_ver.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    return tuple(parts)


def check_for_updates(package_name: str = "dus-yt-music-dl", timeout: float = 1.5) -> Optional[str]:
    """
    Queries PyPI API with a strict low timeout to detect if a newer version is available.
    Returns the latest version string if newer, else None.
    Completely fail-safe (returns None on any network error, offline state, or timeout).
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        req = urllib.request.Request(url, headers={"User-Agent": f"dus-yt-music-dl/{__version__}"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                latest_ver = data.get("info", {}).get("version")
                if latest_ver and parse_version(latest_ver) > parse_version(__version__):
                    return latest_ver
    except Exception:
        # Never crash or block the user if offline, firewalled, or slow network
        return None
    return None


def display_update_notification(latest_version: str):
    """Renders a stylish, professional update notification panel."""
    if not latest_version:
        return

    update_msg = (
        f"[bold yellow]🔔 Update Available![/bold yellow] "
        f"[dim white]{__version__}[/dim white] → [bold green]{latest_version}[/bold green]\n"
        f"[dim]Run to upgrade:[/dim] [bold cyan]pip install --upgrade dus-yt-music-dl[/bold cyan]"
    )
    console.print(
        Panel(
            update_msg,
            border_style="yellow",
            padding=(0, 2),
        )
    )
