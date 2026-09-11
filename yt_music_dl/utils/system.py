import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def log_info(msg: str):
    console.print(f"[bold cyan][INFO][/bold cyan] {msg}")


def log_success(msg: str):
    console.print(f"[bold green][SUCCESS][/bold green] {msg}")


def log_warning(msg: str):
    console.print(f"[bold yellow][WARNING][/bold yellow] {msg}")


def log_error(msg: str):
    console.print(f"[bold red][ERROR][/bold red] {msg}")


def check_dependencies() -> bool:
    """
    Checks whether all required dependencies (yt-dlp, ffmpeg, node) are installed.
    Prints helpful installation instructions if any are missing.
    """
    all_ok = True

    # 1. Check Python yt-dlp module
    try:
        import yt_dlp
    except ImportError:
        all_ok = False
        console.print(
            Panel.fit(
                "[bold red]yt-dlp Python package is not installed![/bold red]\n\n"
                "Install it using:\n"
                "[bold green]pip install -U yt-dlp[/bold green]",
                title="Missing Dependency: yt-dlp",
                border_style="red",
            )
        )

    # 2. Check ffmpeg
    if not shutil.which("ffmpeg"):
        all_ok = False
        console.print(
            Panel.fit(
                "[bold red]ffmpeg executable was not found on your system PATH![/bold red]\n\n"
                "ffmpeg is required for audio conversion (mp3, flac, opus, m4a) and thumbnail embedding.\n\n"
                "Install via winget (Windows):\n"
                "[bold green]winget install Gyan.FFmpeg[/bold green]\n\n"
                "Or download from: https://www.gyan.dev/ffmpeg/builds/",
                title="Missing Dependency: ffmpeg",
                border_style="red",
            )
        )

    # 3. Check node.js
    if not shutil.which("node"):
        all_ok = False
        console.print(
            Panel.fit(
                "[bold red]Node.js runtime was not found on your system PATH![/bold red]\n\n"
                "Node.js is used by yt-dlp to solve YouTube JS challenge tokens and signatures.\n\n"
                "Install via winget:\n"
                "[bold green]winget install OpenJS.NodeJS[/bold green]\n\n"
                "Or download from: https://nodejs.org",
                title="Missing Dependency: Node.js",
                border_style="red",
            )
        )

    return all_ok


def detect_available_browsers() -> list[str]:
    """
    Detects which supported web browsers are likely installed on this Windows system.
    """
    detected = []
    local_app_data = Path(os.getenv("LOCALAPPDATA", ""))
    app_data = Path(os.getenv("APPDATA", ""))

    paths = {
        "firefox": app_data / "Mozilla" / "Firefox" / "Profiles",
        "chrome": local_app_data / "Google" / "Chrome" / "User Data",
        "edge": local_app_data / "Microsoft" / "Edge" / "User Data",
        "brave": local_app_data / "BraveSoftware" / "Brave-Browser" / "User Data",
        "opera": app_data / "Opera Software" / "Opera Stable",
        "vivaldi": local_app_data / "Vivaldi" / "User Data",
    }

    for browser, b_path in paths.items():
        if b_path.exists():
            detected.append(browser)

    return detected or ["firefox"]


def handle_cookie_error_suggestion(browser_name: str = "firefox", cookie_file: str = None):
    """
    Provides context-aware help based on browser or file-based cookie extraction failures.
    """
    b_upper = (browser_name or "Browser").capitalize()

    if cookie_file:
        content = (
            f"[bold yellow]Could not read cookies file at:[/bold yellow] [white]{cookie_file}[/white]\n\n"
            "• Ensure the file exists, is formatted as a standard Netscape/Mozilla cookies.txt file,\n"
            "  and is not locked by another process."
        )
    elif browser_name.lower() in ("chrome", "edge"):
        content = (
            f"[bold yellow]Failed to read cookies from {b_upper}![/bold yellow]\n\n"
            f"1. [bold white]Windows App-Bound Encryption:[/bold white] Recent versions of Chrome/Edge\n"
            "   encrypt cookies so external scripts cannot read them directly.\n"
            "2. [bold green]Recommended Fix:[/bold green]\n"
            "   • Use [bold cyan]Firefox[/bold cyan] (unaffected by App-Bound encryption), OR\n"
            "   • Export cookies to a [bold cyan]cookies.txt[/bold cyan] using an extension like 'Get cookies.txt LOCALLY',\n"
            "   • Or rely on [bold green]Android Phone Emulation[/bold green] (which requires NO cookies at all!)."
        )
    else:
        content = (
            f"[bold yellow]Failed to load browser cookies from {b_upper}![/bold yellow]\n\n"
            f"1. [bold white]{b_upper} is currently open & locking the sqlite cookie database.[/bold white]\n"
            f"   → Please [bold green]close {b_upper}[/bold green] completely and try again.\n"
            "2. Profile is stored in a custom non-standard directory.\n"
            "3. Switch to default [bold green]Android Emulation (No Cookies Needed)[/bold green]."
        )

    console.print(
        Panel.fit(
            content,
            title=f"Cookie Extraction Help ({b_upper})",
            border_style="yellow",
        )
    )
