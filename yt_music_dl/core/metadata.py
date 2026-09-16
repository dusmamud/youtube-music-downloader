import re
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, Optional

import requests
from PIL import Image

from yt_music_dl.utils.system import log_warning


def get_square_cover_bytes(info: Dict[str, Any], temp_thumb_path: Optional[Path] = None) -> Optional[bytes]:
    """
    Retrieves or crops album art to an exact 1:1 square ratio.
    Prefers Google/YouTube Music square CDN covers (1200x1200).
    Falls back to center-cropping the video thumbnail to 1:1 square.
    """
    thumbnails = info.get("thumbnails", [])
    square_url = None

    # 1. Search for square thumbnails in info['thumbnails']
    for t in reversed(thumbnails):
        url = t.get("url", "")
        if "googleusercontent.com" in url:
            square_url = re.sub(r"=w\d+-h\d+.*", "=w1200-h1200-l90-rj", url)
            if not square_url.endswith("=w1200-h1200-l90-rj"):
                square_url += "=w1200-h1200-l90-rj"
            break
        elif t.get("width") and t.get("width") == t.get("height") and t.get("width") >= 500:
            square_url = url
            break

    img = None
    if square_url:
        try:
            resp = requests.get(square_url, timeout=10)
            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content))
        except Exception:
            img = None

    # 2. Fallback to existing downloaded thumbnail file or video thumbnail
    if img is None and temp_thumb_path and temp_thumb_path.exists():
        try:
            img = Image.open(temp_thumb_path)
        except Exception:
            img = None

    if img is None and info.get("thumbnail"):
        try:
            resp = requests.get(info["thumbnail"], timeout=10)
            if resp.status_code == 200:
                img = Image.open(BytesIO(resp.content))
        except Exception:
            img = None

    if img is None:
        return None

    # Convert to RGB mode (avoid PNG RGBA transparency issues)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 3. Center-crop to a perfect 1:1 square if aspect ratio is rectangular (e.g. 16:9)
    w, h = img.size
    if w != h:
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

    out_buf = BytesIO()
    img.save(out_buf, format="JPEG", quality=95)
    return out_buf.getvalue()


def apply_perfect_metadata(audio_file: Path, info: Dict[str, Any], cover_bytes: Optional[bytes]):
    """
    Embeds clean, comprehensive metadata (Title, Artist, Album Artist, Album, Year, Genre)
    and 1:1 square cover art using Mutagen.
    Ensures MP3 is written in ID3v2.3 for full Windows Explorer & mobile player compatibility.
    """
    ext = audio_file.suffix.lower()
    title = info.get("track") or info.get("title") or "Unknown Title"
    artist = (
        info.get("artist")
        or (", ".join(info["artists"]) if info.get("artists") else None)
        or info.get("creator")
        or info.get("channel")
        or info.get("uploader")
        or "Unknown Artist"
    )
    album_artist = artist
    album = info.get("album") or title
    year = info.get("release_year") or (info.get("upload_date")[:4] if info.get("upload_date") else "")
    genre = info.get("genre") or "Music"

    try:
        if ext == ".mp3":
            from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TCON, TDRC, APIC
            try:
                tags = ID3(str(audio_file))
            except Exception:
                tags = ID3()

            # Clean noisy description/synopsis injected by yt-dlp
            tags.delall("COMM")
            tags.delall("TXXX")

            tags.add(TIT2(encoding=3, text=[title]))
            tags.add(TPE1(encoding=3, text=[artist]))        # Contributing Artist
            tags.add(TPE2(encoding=3, text=[album_artist]))  # Album Artist (Windows Explorer column)
            tags.add(TALB(encoding=3, text=[album]))
            tags.add(TCON(encoding=3, text=[genre]))
            if year:
                tags.add(TDRC(encoding=3, text=[str(year)]))

            if cover_bytes:
                tags.delall("APIC")
                tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,  # Cover (front)
                        desc="Cover",
                        data=cover_bytes,
                    )
                )
            # ID3v2.3 standard is required for Windows Explorer to display artists properly
            tags.save(str(audio_file), v2_version=3)

        elif ext == ".m4a":
            from mutagen.mp4 import MP4, MP4Cover
            mp4 = MP4(str(audio_file))
            mp4["©nam"] = [title]
            mp4["©ART"] = [artist]
            mp4["aART"] = [album_artist]  # Album Artist
            mp4["©alb"] = [album]
            mp4["©gen"] = [genre]
            if year:
                mp4["©day"] = [str(year)]
            if cover_bytes:
                mp4["covr"] = [MP4Cover(cover_bytes, imageformat=MP4Cover.FORMAT_JPEG)]
            # Clean descriptions
            if "desc" in mp4:
                del mp4["desc"]
            if "ldes" in mp4:
                del mp4["ldes"]
            mp4.save()

        elif ext == ".flac":
            from mutagen.flac import FLAC, Picture
            flac = FLAC(str(audio_file))
            flac["title"] = [title]
            flac["artist"] = [artist]
            flac["albumartist"] = [album_artist]
            flac["album"] = [album]
            flac["genre"] = [genre]
            if year:
                flac["date"] = [str(year)]
            if cover_bytes:
                pic = Picture()
                pic.type = 3
                pic.mime = "image/jpeg"
                pic.desc = "Cover"
                pic.data = cover_bytes
                flac.clear_pictures()
                flac.add_picture(pic)
            flac.save()

        elif ext in (".opus", ".ogg"):
            import base64
            from mutagen.oggopus import OggOpus
            from mutagen.flac import Picture

            opus = OggOpus(str(audio_file))
            opus["title"] = [title]
            opus["artist"] = [artist]
            opus["albumartist"] = [album_artist]
            opus["album"] = [album]
            opus["genre"] = [genre]
            if year:
                opus["date"] = [str(year)]
            if cover_bytes:
                pic = Picture()
                pic.type = 3
                pic.mime = "image/jpeg"
                pic.desc = "Cover"
                pic.data = cover_bytes
                opus["metadata_block_picture"] = [base64.b64encode(pic.write()).decode("ascii")]
            opus.save()

    except Exception as e:
        log_warning(f"Could not apply extended metadata: {e}")


def cleanup_dangling_thumbnails(base_path: Path):
    """Removes standalone thumbnail files left after extraction."""
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        thumb = base_path.with_suffix(ext)
        if thumb.exists() and thumb.is_file():
            try:
                thumb.unlink(missing_ok=True)
            except Exception:
                pass
