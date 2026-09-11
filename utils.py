"""
Backward compatibility bridge for utils imports.
Redirects to yt_music_dl.utils.
"""
from yt_music_dl.utils import (
    console,
    log_info,
    log_success,
    log_warning,
    log_error,
    check_dependencies,
    detect_available_browsers,
    handle_cookie_error_suggestion,
    sanitize_name,
    format_filename,
    cleanup_test_files,
)
from yt_music_dl.core.device_profiler import get_random_android_device

__all__ = [
    "console",
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
    "check_dependencies",
    "detect_available_browsers",
    "handle_cookie_error_suggestion",
    "sanitize_name",
    "format_filename",
    "cleanup_test_files",
    "get_random_android_device",
]
