import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from yt_music_dl import config
from yt_music_dl.cli import create_parser, main


class TestConfigPathDetection(unittest.TestCase):
    def setUp(self):
        self.original_output_dir = config.OUTPUT_DIR

    def tearDown(self):
        config.OUTPUT_DIR = self.original_output_dir

    def test_set_output_dir(self):
        """Test dynamic set_output_dir method."""
        test_path = "/custom/download/path"
        config.set_output_dir(test_path)
        self.assertIn("custom", config.OUTPUT_DIR)

    @patch("os.getenv")
    def test_termux_detection_env(self, mock_getenv):
        """Test detection when TERMUX_VERSION environment variable is present."""
        mock_getenv.side_effect = lambda k, default=None: "0.118.0" if k == "TERMUX_VERSION" else default
        self.assertTrue(config.is_termux_environment())

    def test_cli_output_flag_overrides_config(self):
        """Test that passing -o in CLI updates output directory and parser."""
        parser = create_parser()
        args = parser.parse_args(["-o", "/tmp/my_music"])
        self.assertEqual(args.output, "/tmp/my_music")
