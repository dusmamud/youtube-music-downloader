import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from yt_music_dl.utils.updater import parse_version, check_for_updates, display_update_notification


class TestUpdater(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("1.1.5"), (1, 1, 5))
        self.assertEqual(parse_version("v1.2.0"), (1, 2, 0))
        self.assertTrue(parse_version("1.1.6") > parse_version("1.1.5"))
        self.assertTrue(parse_version("2.0.0") > parse_version("1.9.9"))
        self.assertFalse(parse_version("1.1.5") > parse_version("1.1.5"))
        self.assertFalse(parse_version("1.1.4") > parse_version("1.1.5"))

    @patch("urllib.request.urlopen")
    @patch("yt_music_dl.utils.updater.__version__", "1.1.5")
    def test_check_for_updates_available(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"info": {"version": "1.2.0"}}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        latest = check_for_updates()
        self.assertEqual(latest, "1.2.0")

    @patch("urllib.request.urlopen")
    @patch("yt_music_dl.utils.updater.__version__", "1.1.5")
    def test_check_for_updates_not_available(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({"info": {"version": "1.1.5"}}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        latest = check_for_updates()
        self.assertIsNone(latest)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timed out")
        latest = check_for_updates()
        self.assertIsNone(latest)

    @patch("yt_music_dl.utils.updater.console.print")
    def test_display_update_notification(self, mock_print):
        # Should execute cleanly without throwing
        display_update_notification("1.2.0")
        self.assertTrue(mock_print.called)
        display_update_notification(None)
