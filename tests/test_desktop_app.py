import unittest
from unittest.mock import MagicMock, patch

from desktop_app import check_ollama_running, check_server_running


class TestDesktopApp(unittest.TestCase):

    @patch("urllib.request.urlopen")
    def test_check_ollama_running_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertTrue(check_ollama_running())

    @patch("urllib.request.urlopen")
    def test_check_ollama_running_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        self.assertFalse(check_ollama_running())

    @patch("urllib.request.urlopen")
    def test_check_server_running_success(self, mock_urlopen):
        import json, os, desktop_app
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            "service": "codeagent-backend",
            "version": desktop_app.CODEAGENT_VERSION,
            "base_dir": os.path.abspath(desktop_app.BASE_DIR),
            "parent_pid": os.getpid(),
            "parent_creation_time": desktop_app.get_process_creation_time(os.getpid()),
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertTrue(check_server_running("http://localhost:8000/api/health"))

    @patch("urllib.request.urlopen")
    def test_check_server_running_failure(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection refused")
        self.assertFalse(check_server_running("http://localhost:8000/localcode_claude_ui.html"))


if __name__ == "__main__":
    unittest.main()
