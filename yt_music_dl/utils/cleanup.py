import shutil
from pathlib import Path
from typing import Union, Optional

from yt_music_dl import config
from yt_music_dl.utils.system import log_warning


def cleanup_test_files(target_dir: Optional[Union[str, Path]] = None, pattern_prefix: Optional[str] = None) -> int:
    """
    Cleans up temporary test audio files, .part, .ytdl, and cache directories.
    Prints '[CLEANUP] All test files removed' upon completion.
    """
    target_path = Path(target_dir or config.OUTPUT_DIR)
    removed_count = 0

    if target_path.exists():
        for file in target_path.glob("*"):
            if not file.is_file():
                continue

            name = file.name
            should_remove = False

            # Check incomplete extensions
            if file.suffix.lower() in [".part", ".ytdl", ".temp", ".tmp"]:
                should_remove = True
            elif pattern_prefix and pattern_prefix.lower() in name.lower():
                should_remove = True
            elif "[TEST]" in name or "test_sample" in name or "test_audio" in name:
                should_remove = True

            if should_remove:
                try:
                    file.unlink(missing_ok=True)
                    removed_count += 1
                except Exception as e:
                    log_warning(f"Could not remove {file.name}: {e}")

    # Remove yt-dlp cache folder if created locally
    local_cache = Path(".cache")
    if local_cache.exists() and local_cache.is_dir():
        try:
            shutil.rmtree(local_cache, ignore_errors=True)
        except Exception:
            pass

    if removed_count > 0:
        print(f"[CLEANUP] {removed_count} test file(s) removed")
    return removed_count
