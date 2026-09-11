import random
from typing import Dict, Any

from yt_music_dl import config


def get_random_android_device() -> Dict[str, Any]:
    """
    Returns a randomized modern Android smartphone profile (Pixel, Galaxy, OnePlus, Xiaomi)
    to spoof real mobile app requests and bypass desktop web bot-checks.
    """
    profiles = getattr(config, "ANDROID_DEVICE_PROFILES", [])
    if not profiles:
        return {
            "brand": "Google",
            "model": "Pixel 8 Pro",
            "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        }
    return random.choice(profiles)


def get_device_headers(device_profile: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Constructs HTTP headers tailored to the selected mobile device profile.
    """
    profile = device_profile or get_random_android_device()
    return {
        "User-Agent": profile["user_agent"],
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-CH-UA-Mobile": "?1",
        "Sec-CH-UA-Platform": '"Android"',
    }
