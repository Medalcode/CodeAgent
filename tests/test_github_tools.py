import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

from tools import consultar_github, leer_archivo_github, leer_repositorio_github


class TestGithubTools(unittest.TestCase):
    @patch('tools._make_github_request')
    def test_consultar_github_exito(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {"full_name": "user/repo1", "language": "Python"},
            {"full_name": "user/repo2", "language": "JavaScript"},
        ]
        mock_request.return_value = mock_resp

        resultado = consultar_github("ghp_dummy")
        self.assertIn("user/repo1", resultado)
        self.assertIn("Python", resultado)

    @patch('tools._make_github_request')
    def test_consultar_github_invalid_token(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_request.return_value = mock_resp

        resultado = consultar_github("ghp_invalid")
        self.assertIn("Error: El token de GitHub proporcionado es inválido", resultado)

    @patch('tools._make_github_request')
    def test_leer_repositorio_github(self, mock_request):
        # Mock contents request and readme request
        mock_contents = MagicMock()
        mock_contents.status_code = 200
        mock_contents.json.return_value = [{"name": "main.py", "type": "file"}]

        mock_readme = MagicMock()
        mock_readme.status_code = 200
        # base64 encoded "Hello World" -> "SGVsbG8gV29ybGQ="
        mock_readme.json.return_value = {"content": "SGVsbG8gV29ybGQ=\n"}

        mock_request.side_effect = [mock_contents, mock_readme]

        resultado = leer_repositorio_github("ghp_dummy", "user/repo1")
        self.assertIn("main.py", resultado)
        self.assertIn("Hello World", resultado)

    @patch('tools._make_github_request')
    def test_leer_archivo_github_404(self, mock_request):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_request.return_value = mock_resp

        resultado = leer_archivo_github("ghp_dummy", "user/repo1", "nonexistent.py")
        self.assertIn("Archivo no encontrado", resultado)


if __name__ == '__main__':
    unittest.main()
