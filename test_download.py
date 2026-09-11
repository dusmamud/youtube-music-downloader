import os
import sys
import unittest
from pathlib import Path

# Ensure local modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils import check_dependencies, cleanup_test_files
from downloader import YtMusicDownloader
from main import create_parser


class TestYtMusicDownloader(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(config.OUTPUT_DIR) / "test_scratch"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Ensure cleanup function is called and removes test scratch dir
        cleanup_test_files(self.test_dir)
        if self.test_dir.exists():
            try:
                self.test_dir.rmdir()
            except Exception:
                pass

    def test_dependencies(self):
        """Verify yt-dlp, ffmpeg, and node.js availability."""
        self.assertTrue(check_dependencies(), "Required dependencies must be installed and on PATH.")

    def test_backward_compatibility_bridges(self):
        """Verify root imports match yt_music_dl package exports."""
        import yt_music_dl
        import yt_music_dl.config
        self.assertEqual(config.DEFAULT_AUTH_MODE, yt_music_dl.config.DEFAULT_AUTH_MODE)
        self.assertIs(YtMusicDownloader, yt_music_dl.YtMusicDownloader)

    def test_cli_parser(self):
        """Test argument parsing for all required flags."""
        parser = create_parser()

        # Format & quality test
        args = parser.parse_args(["https://music.youtube.com/watch?v=sample", "--format", "flac", "--quality", "best"])
        self.assertEqual(args.format, "flac")
        self.assertEqual(args.quality, "best")
        self.assertFalse(args.dry_run)
        self.assertFalse(args.batch)

        # List formats flag test
        args_lf = parser.parse_args(["https://music.youtube.com/watch?v=sample", "-F"])
        self.assertTrue(args_lf.list_formats)

        # Batch flag test
        args_batch = parser.parse_args(["https://music.youtube.com/playlist?list=sample", "--batch"])
        self.assertTrue(args_batch.batch)

        # Multi-quality flag test
        args_mq = parser.parse_args(["https://music.youtube.com/watch?v=sample", "-m", "--naming-style", "formal"])
        self.assertTrue(args_mq.multi_quality)
        self.assertEqual(args_mq.naming_style, "formal")

        # Android & Auth flags test
        args_auth = parser.parse_args([
            "https://music.youtube.com/watch?v=sample",
            "--browser", "chrome",
            "--client", "android,ios",
            "--cookies", "my_cookies.txt",
        ])
        self.assertEqual(args_auth.browser, "chrome")
        self.assertEqual(args_auth.client, "android,ios")
        self.assertEqual(args_auth.cookies, "my_cookies.txt")

        # Dry-run flag test
        args_dry = parser.parse_args(["https://music.youtube.com/watch?v=sample", "--dry-run"])
        self.assertTrue(args_dry.dry_run)

    def test_filename_formatting(self):
        """Test clean vs formal filename generation."""
        from utils import format_filename
        clean = format_filename("Wahed, Srabony", "Shona Phaki", "320k", "mp3", naming_style="clean")
        self.assertEqual(clean, "Wahed-Srabony-Shona-Phaki-320kbps.mp3")

        formal = format_filename("Wahed, Srabony", "Shona Phaki", "320k", "mp3", naming_style="formal")
        self.assertEqual(formal, "Wahed, Srabony - Shona Phaki (320kbps).mp3")

    def test_android_device_generation(self):
        """Test random Android device profile generation."""
        from utils import get_random_android_device
        device = get_random_android_device()
        self.assertIn("brand", device)
        self.assertIn("model", device)
        self.assertIn("user_agent", device)
        self.assertIn("Android", device["user_agent"])

    def test_downloader_options(self):
        """Test yt-dlp options generation with Android emulation, postprocessors and cookies."""
        # 1. Default Android Emulation Mode (Cookie-free)
        dl_android = YtMusicDownloader(
            output_dir=str(self.test_dir),
            audio_format="mp3",
            quality="best",
            auth_mode="android",
            dry_run=True,
        )
        opts_android = dl_android._build_ydl_opts()
        self.assertTrue(opts_android["simulate"])
        self.assertEqual(opts_android["format"], "ba[vcodec=none]/bestaudio/best")
        self.assertNotIn("cookiesfrombrowser", opts_android)
        self.assertIn("extractor_args", opts_android)
        self.assertIn("android", opts_android["extractor_args"]["youtube"]["player_client"])
        self.assertIn("User-Agent", opts_android["http_headers"])
        self.assertIn("Android", opts_android["http_headers"]["User-Agent"])

        # 2. Browser Cookies Mode
        dl_cookies = YtMusicDownloader(
            output_dir=str(self.test_dir),
            audio_format="opus",
            quality="medium",
            auth_mode="browser",
            browser="firefox",
            dry_run=False,
        )
        opts_cookies = dl_cookies._build_ydl_opts()
        self.assertFalse(opts_cookies["simulate"])
        self.assertEqual(opts_cookies["cookiesfrombrowser"], ("firefox",))
        self.assertTrue(any(pp["key"] == "FFmpegExtractAudio" for pp in opts_cookies["postprocessors"]))
        self.assertTrue(any(pp["key"] == "FFmpegMetadata" for pp in opts_cookies["postprocessors"]))

        # 3. Cookiefile Mode
        dl_cfile = YtMusicDownloader(
            output_dir=str(self.test_dir),
            audio_format="mp3",
            cookiefile="cookies.txt",
            dry_run=True,
        )
        opts_cfile = dl_cfile._build_ydl_opts()
        self.assertEqual(opts_cfile.get("cookiefile"), "cookies.txt")

    def test_dry_run_simulation(self):
        """
        Verify that dry-run extraction completes without saving any media files to disk
        using default cookie-free Android emulation.
        """
        dl = YtMusicDownloader(
            output_dir=str(self.test_dir),
            audio_format="mp3",
            quality="best",
            auth_mode="android",
            dry_run=True,
        )
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        success = dl.download(test_url)
        self.assertTrue(success, "Dry run download simulation with Android emulation should succeed.")

        # Confirm no media files were written
        audio_files = list(self.test_dir.glob("*.mp3")) + list(self.test_dir.glob("*.part"))
        self.assertEqual(len(audio_files), 0, "No audio or part files should be created during dry-run.")

    def test_cleanup_removes_artifacts(self):
        """
        Create dummy artifacts (.part, .ytdl, test_audio.mp3) and verify cleanup_test_files removes them all.
        """
        dummy_files = [
            self.test_dir / "sample_track.mp3.part",
            self.test_dir / "sample_track.ytdl",
            self.test_dir / "[TEST] test_sample.mp3",
            self.test_dir / "temp_cache.tmp",
        ]
        for f in dummy_files:
            f.write_text("dummy test data")

        # Verify files were created
        self.assertEqual(len(list(self.test_dir.glob("*"))), 4)

        # Run cleanup
        cleanup_test_files(self.test_dir)

        # Verify all dummy files are removed
        remaining = list(self.test_dir.glob("*"))
        self.assertEqual(len(remaining), 0, "All test artifacts must be removed by cleanup_test_files().")


if __name__ == "__main__":
    unittest.main()
