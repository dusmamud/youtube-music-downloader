import time
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

import yt_dlp
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

from yt_music_dl import config
from yt_music_dl.utils.system import (
    console,
    log_info,
    log_success,
    log_warning,
    log_error,
    handle_cookie_error_suggestion,
)
from yt_music_dl.utils.formatters import format_filename
from yt_music_dl.core.device_profiler import get_random_android_device
from yt_music_dl.core.metadata import (
    get_square_cover_bytes,
    apply_perfect_metadata,
    cleanup_dangling_thumbnails,
)


class YtMusicDownloader:
    def __init__(
        self,
        output_dir: Optional[str] = None,
        audio_format: str = config.DEFAULT_FORMAT,
        quality: str = config.DEFAULT_QUALITY,
        auth_mode: str = config.DEFAULT_AUTH_MODE,
        browser: Optional[str] = None,
        cookiefile: Optional[str] = None,
        player_clients: Optional[List[str]] = None,
        use_cookies: Optional[bool] = None,
        dry_run: bool = False,
        batch: bool = False,
        max_retries: int = config.MAX_RETRIES,
        retry_delay: int = config.RETRY_DELAY,
    ):
        self.output_dir = Path(output_dir or config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_format = audio_format.lower()
        self.quality = quality.lower()
        self.dry_run = dry_run
        self.batch = batch
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Resolve auth mode and cookie settings
        self.cookiefile = Path(cookiefile) if cookiefile else None
        self.browser = browser

        if cookiefile:
            self.auth_mode = "cookiefile"
        elif browser:
            self.auth_mode = "browser"
        elif use_cookies is True:
            self.auth_mode = "browser"
            self.browser = self.browser or config.DEFAULT_BROWSER
        elif use_cookies is False or auth_mode in ("android", "none"):
            self.auth_mode = "android"
        else:
            self.auth_mode = auth_mode

        self.player_clients = player_clients or config.DEFAULT_PLAYER_CLIENTS

        # Generate a fresh randomized modern Android smartphone profile for this session
        self.device_profile = get_random_android_device()

        # Progress tracking
        self.progress: Optional[Progress] = None
        self.task_id = None

    def _progress_hook(self, d: Dict[str, Any]):
        """Hook called by yt-dlp during download progress."""
        if self.dry_run:
            return

        status = d.get("status")
        if status == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0

            if self.progress is None:
                self.progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(bar_width=40),
                    "[progress.percentage]{task.percentage:>3.0f}%",
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console,
                )
                self.progress.start()
                self.task_id = self.progress.add_task(
                    "Downloading audio...", total=total_bytes
                )

            if self.task_id is not None:
                if total_bytes and self.progress.tasks[self.task_id].total != total_bytes:
                    self.progress.update(self.task_id, total=total_bytes)
                self.progress.update(self.task_id, completed=downloaded)

        elif status == "finished":
            if self.progress and self.task_id is not None:
                self.progress.update(
                    self.task_id, description="[bold green]Download complete! Converting & Tagging..."
                )
                self.progress.stop()
                self.progress = None
                self.task_id = None

    def _build_ydl_opts(self, simulate_override: Optional[bool] = None) -> Dict[str, Any]:
        """
        Builds dictionary of options passed to yt_dlp.YoutubeDL.
        Optimizes audio stream selection, mobile InnerTube client spoofing, and bitrates.
        """
        is_simulated = self.dry_run if simulate_override is None else simulate_override

        # Output template
        if self.batch:
            out_template = str(
                self.output_dir / "%(playlist_title,playlist)s" / "%(playlist_index)02d - %(artist,uploader)s - %(title)s.%(ext)s"
            )
        else:
            out_template = str(self.output_dir / "%(artist,uploader)s - %(title)s.%(ext)s")

        # Determine optimal audio stream format and conversion bitrate
        if self.audio_format == "mp3":
            if self.quality in ("best", "0"):
                pref_quality = "320"
            elif self.quality in ("medium", "5"):
                pref_quality = "192"
            elif self.quality in ("low", "9"):
                pref_quality = "128"
            else:
                pref_quality = "320"
            format_spec = "ba[vcodec=none]/bestaudio/best"

        elif self.audio_format == "m4a":
            if self.quality in ("best", "0"):
                pref_quality = "256"
            elif self.quality in ("256", "192", "128", "48"):
                pref_quality = self.quality
            else:
                pref_quality = "256"
            format_spec = "ba[vcodec=none]/bestaudio/best"

        elif self.audio_format == "opus":
            # Select native Opus format 251 directly
            pref_quality = "160"
            format_spec = "251/ba[ext=webm]/ba[vcodec=none]/bestaudio/best"

        else:  # flac
            pref_quality = "0"
            format_spec = "ba[vcodec=none]/bestaudio/best"

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": self.audio_format,
                "preferredquality": pref_quality,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ]

        ydl_opts: Dict[str, Any] = {
            "format": format_spec,
            "outtmpl": out_template,
            "writethumbnail": not is_simulated,
            "postprocessors": [] if is_simulated else postprocessors,
            "noplaylist": not self.batch,
            "nopart": True,  # Disables .part files to avoid Windows file locks [WinError 32]
            "continuedl": False,  # Disables partial resume to prevent HTTP 416 range errors
            "windowsfilenames": True,  # Strips/replaces illegal Windows filesystem characters
            "quiet": True,
            "no_warnings": True,  # Clean terminal experience: suppresses benign SABR/PO Token warnings
            "progress_hooks": [self._progress_hook],
            "retries": 3,
            "fragment_retries": 3,
            "socket_timeout": config.SOCKET_TIMEOUT,
            "simulate": is_simulated,
            # Node.js challenge solving runtime
            "js_runtimes": {"node": {}},
            "remote_components": {"ejs:github"},
        }

        # Client Spoofing / Cookie Authentication Routing
        if self.auth_mode == "android":
            # Mobile Phone Emulation (Android / iOS InnerTube API) - NO COOKIES REQUIRED
            ydl_opts["extractor_args"] = {
                "youtube": {
                    "player_client": self.player_clients,
                }
            }
            ydl_opts["http_headers"] = {
                "User-Agent": self.device_profile["user_agent"],
            }
        elif self.auth_mode == "browser":
            b_name = self.browser or config.DEFAULT_BROWSER
            ydl_opts["cookiesfrombrowser"] = (b_name,)
        elif self.auth_mode == "cookiefile" and self.cookiefile:
            ydl_opts["cookiefile"] = str(self.cookiefile)

        return ydl_opts

    def list_formats(self, url: str) -> bool:
        """Inspects and lists all available audio streams for the given URL."""
        from yt_music_dl.ui.banner import display_formats_table
        log_info(f"Extracting format details for: [white]{url}[/white]")
        ydl_opts = self._build_ydl_opts(simulate_override=True)
        ydl_opts["extract_flat"] = False

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    log_error("Could not fetch information for URL.")
                    return False

                title = info.get("title", "Unknown Title")
                formats = info.get("formats", [])
                display_formats_table(formats, title=f"Formats for: {title}")
                return True
        except Exception as e:
            self._handle_extraction_exception(e)
            return False

    def download(self, url: str, naming_style: str = "clean") -> bool:
        """Executes download, square cover extraction, and metadata tagging."""
        if self.dry_run:
            log_info(f"[DRY-RUN] Simulating download for: [white]{url}[/white]")
        else:
            log_info(f"Starting download for: [white]{url}[/white]")
            log_info(f"Target format: [green]{self.audio_format.upper()}[/green] | Quality: [green]{self.quality}[/green]")
            log_info(f"Output folder: [dim]{self.output_dir}[/dim]")

        if self.auth_mode == "android":
            log_info(f"Mode: [bold green]Android Phone Emulation[/bold green] (Device: [cyan]{self.device_profile['brand']} {self.device_profile['model']}[/cyan] • [yellow]Cookie-Free[/yellow])")
        elif self.auth_mode == "browser":
            log_info(f"Mode: [bold cyan]Browser Cookies Auth[/bold cyan] (Browser: [white]{self.browser or config.DEFAULT_BROWSER}[/white])")
        elif self.auth_mode == "cookiefile":
            log_info(f"Mode: [bold cyan]Cookiefile Auth[/bold cyan] (File: [white]{self.cookiefile}[/white])")

        attempt = 0
        current_delay = self.retry_delay
        self._clean_part_files()

        while attempt < self.max_retries:
            attempt += 1
            try:
                ydl_opts = self._build_ydl_opts()
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=not self.dry_run)
                    if not info:
                        log_error("No track info received.")
                        return False

                    title = info.get("title", "Unknown Title")
                    artist = (
                        info.get("artist")
                        or (", ".join(info["artists"]) if info.get("artists") else None)
                        or info.get("creator")
                        or info.get("channel")
                        or info.get("uploader")
                        or "Unknown Artist"
                    )

                    if self.dry_run:
                        log_success(f"[DRY-RUN] Successfully simulated: [bold white]{artist} - {title}[/bold white]")
                        return True

                    # Find generated audio file
                    raw_filename = ydl.prepare_filename(info)
                    base_path = Path(raw_filename).with_suffix("")
                    target_audio_file = base_path.with_suffix(f".{self.audio_format}")

                    # Fallback search if exact name differed
                    if not target_audio_file.exists():
                        candidates = list(self.output_dir.glob(f"*{self.audio_format}"))
                        if candidates:
                            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                            target_audio_file = candidates[0]

                    if target_audio_file.exists():
                        # Fetch 1:1 square cover art
                        cover_bytes = get_square_cover_bytes(info, base_path.with_suffix(".jpg"))
                        # Apply complete metadata & 1:1 album art
                        apply_perfect_metadata(target_audio_file, info, cover_bytes)
                        # Clean up standalone thumbnail images
                        cleanup_dangling_thumbnails(base_path)

                        # Apply filename styling preference
                        final_filename = format_filename(
                            artist,
                            title,
                            self.quality if self.quality not in ("best", "0") else "320kbps",
                            self.audio_format,
                            naming_style=naming_style,
                        )
                        final_file_path = self.output_dir / final_filename
                        if target_audio_file != final_file_path:
                            try:
                                if final_file_path.exists():
                                    final_file_path.unlink(missing_ok=True)
                                target_audio_file.replace(final_file_path)
                                target_audio_file = final_file_path
                            except Exception:
                                pass

                        filesize_mb = target_audio_file.stat().st_size / (1024 * 1024)
                        log_success(
                            f"Successfully processed: [bold white]{target_audio_file.name}[/bold white] "
                            f"([green]{filesize_mb:.2f} MB[/green], 1:1 Album Art embedded)"
                        )
                    else:
                        log_success(f"Successfully processed: [bold white]{artist} - {title}[/bold white]")

                    return True

            except Exception as e:
                if self.progress:
                    try:
                        self.progress.stop()
                    except Exception:
                        pass
                    self.progress = None

                is_retryable, delay_to_use = self._analyze_error(e, attempt, current_delay)
                if not is_retryable or attempt >= self.max_retries:
                    log_error(f"Download failed after {attempt} attempt(s): {e}")
                    return False

                log_warning(f"Attempt {attempt} failed. Retrying in {delay_to_use:.1f}s...")
                time.sleep(delay_to_use)
                current_delay *= config.BACKOFF_FACTOR

        return False

    def download_multi_quality(
        self,
        url: str,
        qualities: Optional[List[str]] = None,
        naming_style: str = "clean",
    ) -> List[Dict[str, Any]]:
        """
        Downloads source audio once, then transcodes it locally into multiple
        bitrates (e.g. 320k, 256k, 192k, 128k) using FFmpeg.
        """
        if qualities is None:
            qualities = ["320k", "256k", "192k", "128k"]

        log_info(f"Starting Multi-Quality download for: [white]{url}[/white]")
        log_info(f"Target format: [green]{self.audio_format.upper()}[/green] | Bitrates: [cyan]{', '.join(qualities)}[/cyan]")
        log_info(f"Naming style: [yellow]{'Clean (Default)' if naming_style in ('clean', '1') else 'Formal'}[/yellow]")

        if self.auth_mode == "android":
            log_info(f"Mode: [bold green]Android Phone Emulation[/bold green] (Device: [cyan]{self.device_profile['brand']} {self.device_profile['model']}[/cyan] • [yellow]Cookie-Free[/yellow])")
        elif self.auth_mode == "browser":
            log_info(f"Mode: [bold cyan]Browser Cookies Auth[/bold cyan] (Browser: [white]{self.browser or config.DEFAULT_BROWSER}[/white])")
        elif self.auth_mode == "cookiefile":
            log_info(f"Mode: [bold cyan]Cookiefile Auth[/bold cyan] (File: [white]{self.cookiefile}[/white])")

        temp_dir = self.output_dir / ".cache_stream"
        temp_dir.mkdir(parents=True, exist_ok=True)
        for old_f in temp_dir.glob("*"):
            try:
                old_f.unlink(missing_ok=True)
            except Exception:
                pass

        temp_source_path = temp_dir / "raw_audio"

        ydl_opts: Dict[str, Any] = {
            "format": "251/ba[vcodec=none]/bestaudio/best",
            "outtmpl": str(temp_source_path) + ".%(ext)s",
            "writethumbnail": False,
            "nopart": True,
            "continuedl": False,
            "windowsfilenames": True,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self._progress_hook],
            "retries": 3,
            "socket_timeout": config.SOCKET_TIMEOUT,
            "js_runtimes": {"node": {}},
            "remote_components": {"ejs:github"},
        }

        # Apply Auth / Client Routing
        if self.auth_mode == "android":
            ydl_opts["extractor_args"] = {
                "youtube": {
                    "player_client": self.player_clients,
                }
            }
            ydl_opts["http_headers"] = {
                "User-Agent": self.device_profile["user_agent"],
            }
        elif self.auth_mode == "browser":
            b_name = self.browser or config.DEFAULT_BROWSER
            ydl_opts["cookiesfrombrowser"] = (b_name,)
        elif self.auth_mode == "cookiefile" and self.cookiefile:
            ydl_opts["cookiefile"] = str(self.cookiefile)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                log_error("Could not fetch information for URL.")
                return []

        raw_candidates = list(temp_dir.glob("raw_audio.*"))
        if not raw_candidates:
            log_error("Raw audio file was not found in temp cache.")
            return []
        raw_audio_file = raw_candidates[0]

        title = info.get("track") or info.get("title") or "Unknown Title"
        artist = (
            info.get("artist")
            or (", ".join(info["artists"]) if info.get("artists") else None)
            or info.get("creator")
            or info.get("channel")
            or info.get("uploader")
            or "Unknown Artist"
        )

        log_info("Fetching 1:1 square album art...")
        cover_bytes = get_square_cover_bytes(info)

        results = []
        for q in qualities:
            q_clean = str(q).lower().replace("k", "")
            final_filename = format_filename(
                artist,
                title,
                f"{q_clean}kbps",
                self.audio_format,
                naming_style=naming_style,
            )
            dest_file = self.output_dir / final_filename

            log_info(f"Generating [bold white]{q_clean}kbps[/bold white] version -> [dim]{final_filename}[/dim]...")

            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(raw_audio_file), "-vn"]
            if self.audio_format == "mp3":
                cmd.extend(["-acodec", "libmp3lame", "-b:a", f"{q_clean}k"])
            elif self.audio_format == "m4a":
                cmd.extend(["-acodec", "aac", "-b:a", f"{q_clean}k"])
            elif self.audio_format == "opus":
                cmd.extend(["-acodec", "libopus", "-b:a", f"{q_clean}k"])
            elif self.audio_format == "flac":
                cmd.extend(["-acodec", "flac"])
            cmd.append(str(dest_file))

            ret = subprocess.run(cmd, capture_output=True, text=True)
            if ret.returncode != 0:
                log_warning(f"FFmpeg encoding failed for {q}: {ret.stderr}")
                continue

            apply_perfect_metadata(dest_file, info, cover_bytes)
            size_mb = dest_file.stat().st_size / (1024 * 1024)
            results.append({
                "filename": final_filename,
                "path": dest_file,
                "size_mb": size_mb,
                "quality": f"{q_clean}kbps",
            })
            log_success(f"Created: [bold white]{final_filename}[/bold white] ({size_mb:.2f} MB)")

        # Clean up temp stream cache
        try:
            for f in temp_dir.glob("*"):
                f.unlink(missing_ok=True)
            temp_dir.rmdir()
        except Exception:
            pass

        return results

    def _clean_part_files(self):
        """Cleans lingering partial .part files to avoid Windows file locks and 416 errors."""
        try:
            for part in self.output_dir.glob("*.part"):
                part.unlink(missing_ok=True)
        except Exception:
            pass

    def _analyze_error(self, e: Exception, attempt: int, current_delay: float) -> tuple[bool, float]:
        msg = str(e).lower()
        if "429" in msg or "too many requests" in msg:
            backoff_delay = max(current_delay, 10.0) * (1.5 ** attempt)
            log_warning(f"HTTP 429 Rate Limit detected! Applying exponential backoff ({backoff_delay:.1f}s)...")
            return True, backoff_delay

        if "416" in msg or "requested range not satisfiable" in msg or "winerror 32" in msg or "being used by another process" in msg:
            log_warning("Windows file lock or partial range mismatch detected. Purging partial downloads...")
            self._clean_part_files()
            return True, current_delay + 2.0

        if "confirm you're not a bot" in msg or "sign in" in msg or "age" in msg:
            log_warning("YouTube authentication challenge or age-restriction encountered.")
            if self.auth_mode == "android":
                log_info("[dim]Tip: For age-restricted/private tracks, use [bold cyan]--browser firefox[/bold cyan] or [bold cyan]--cookies cookies.txt[/bold cyan].[/dim]")
            return True, current_delay

        if "cookie" in msg or "sqlite" in msg or "database is locked" in msg:
            handle_cookie_error_suggestion(browser_name=self.browser or "firefox", cookie_file=str(self.cookiefile) if self.cookiefile else None)
            return False, current_delay

        if "timeout" in msg or "connection reset" in msg or "temporary failure" in msg:
            log_warning("Network glitch/timeout detected.")
            return True, current_delay

        return True, current_delay

    def _handle_extraction_exception(self, e: Exception):
        msg = str(e).lower()
        if "cookie" in msg or "sqlite" in msg or "database is locked" in msg:
            handle_cookie_error_suggestion(browser_name=self.browser or "firefox", cookie_file=str(self.cookiefile) if self.cookiefile else None)
        else:
            log_error(f"Failed to inspect formats: {e}")
