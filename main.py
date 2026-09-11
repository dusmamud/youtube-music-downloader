#!/usr/bin/env python3
"""
YouTube Music Studio Pro - Root Entry Point Launcher
Maintains 100% backward compatibility for: python main.py [options]
"""
import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from yt_music_dl.cli import main, create_parser

if __name__ == "__main__":
    main()
