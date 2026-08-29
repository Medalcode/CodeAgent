"""
Unit, Integration and Security Tests for Local Model Provider (LOCAL-ONLY ENFORCED Governance).
Verifica que CodeAgent opere de forma inmutable sobre Ollama local (localhost:11434) y rechace cualquier proveedor cloud.
"""
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from mis_agentes_inteligentes.agents import get_model
from mis_agentes_inteligentes.config import DEFAULT_MODEL_NAME, DEFAULT_MODEL_PROVIDER, OLLAMA_TARGET
from mis_agentes_inteligentes.localcode_server import LocalCodeProxyHandler


class TestLocalModelProviderGovernance(unittest.TestCase):

    def test_001_default_provider_is_ollama_local(self):
        """TEST 1: El proveedor predeterminado debe ser 'Ollama (Local)'."""
        self.assertEqual(DEFAULT_MODEL_PROVIDER, "Ollama (Local)")

    def test_002_default_model_is_qwen_14b(self):
        """TEST 2: El modelo predeterminado debe ser 'qwen2.5-coder:14b'."""
        self.assertEqual(DEFAULT_MODEL_NAME, "qwen2.5-coder:14b")

    def test_003_no_openai_api_key_required(self):
        """TEST 3: La instanciación predeterminada de get_model() no requiere OPENAI_API_KEY."""
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            model = get_model(provider="", model_name="")
            self.assertIsNotNone(model)
            self.assertIn("ollama_chat", str(getattr(model, "model_id", "")))
        finally:
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key

    def test_004_reject_explicit_openai_provider(self):
        """TEST 4: Un proveedor explícito 'OpenAI' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="OpenAI", model_name="gpt-4o-mini")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_005_reject_explicit_anthropic_provider(self):
        """TEST 5: Un proveedor explícito 'Anthropic' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="Anthropic", model_name="claude-3-5-sonnet")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_006_reject_explicit_gemini_provider(self):
        """TEST 6: Un proveedor explícito 'Gemini (Google)' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="Gemini (Google)", model_name="gemini-2.0-flash")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_007_reject_explicit_groq_provider(self):
        """TEST 7: Un proveedor explícito 'Groq' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="Groq", model_name="llama-3.1-8b-instant")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_008_reject_explicit_openrouter_provider(self):
        """TEST 8: Un proveedor explícito 'OpenRouter' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="OpenRouter", model_name="openai/gpt-4o-mini")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_009_reject_explicit_azure_provider(self):
        """TEST 9: Un proveedor explícito 'Azure OpenAI' debe ser RECHAZADO con ValueError."""
        with self.assertRaises(ValueError) as ctx:
            get_model(provider="Azure OpenAI", model_name="gpt-4")
        self.assertIn("LOCAL-ONLY", str(ctx.exception))

    def test_010_cloud_model_name_gpt_sanitized(self):
        """TEST 10: Nombre de modelo 'gpt-4o-mini' con provider vacío se sanitiza al default local 'qwen2.5-coder:14b'."""
        model = get_model(provider="", model_name="gpt-4o-mini")
        self.assertEqual(getattr(model, "model_id", None), f"ollama_chat/{DEFAULT_MODEL_NAME}")

    def test_011_cloud_model_name_claude_sanitized(self):
        """TEST 11: Nombre de modelo 'claude-3-5-sonnet' con provider vacío se sanitiza al default local 'qwen2.5-coder:14b'."""
        model = get_model(provider="", model_name="claude-3-5-sonnet")
        self.assertEqual(getattr(model, "model_id", None), f"ollama_chat/{DEFAULT_MODEL_NAME}")

    def test_012_cloud_model_name_gemini_sanitized(self):
        """TEST 12: Nombre de modelo 'gemini-2.5-pro' con provider vacío se sanitiza al default local 'qwen2.5-coder:14b'."""
        model = get_model(provider="", model_name="gemini-2.5-pro")
        self.assertEqual(getattr(model, "model_id", None), f"ollama_chat/{DEFAULT_MODEL_NAME}")

    def test_013_external_https_url_model_sanitized(self):
        """TEST 13: Intentos de pasar URLs externas HTTPS como modelo se sanitizan al default local."""
        model = get_model(provider="", model_name="https://api.openai.com/v1/chat/completions")
        self.assertEqual(getattr(model, "model_id", None), f"ollama_chat/{DEFAULT_MODEL_NAME}")

    @patch("urllib.request.urlopen")
    def test_014_ollama_unavailable_produces_503_error(self, mock_urlopen):
        """TEST 14: Ollama no disponible en el servidor HTTP responde con HTTP 503 sin fallback cloud."""
        mock_urlopen.side_effect = Exception("Connection refused on port 11434")

        handler = LocalCodeProxyHandler.__new__(LocalCodeProxyHandler)
        handler.headers = {}
        handler._get_post_body = lambda: {"prompt": "Hola", "provider": "", "model": ""}

        sent_responses = []

        def mock_send_json(data, status=200):
            sent_responses.append((data, status))

        handler._send_json = mock_send_json

        os.environ.pop("SKIP_OLLAMA_CHECK", None)
        handler.handle_agent_chat()

        self.assertEqual(len(sent_responses), 1)
        data, status = sent_responses[0]
        self.assertEqual(status, 503)
        self.assertFalse(data.get("success"))
        self.assertIn("Local model runtime unavailable", data.get("error", ""))

    def test_015_network_isolation_no_external_llm_traffic(self):
        """TEST 15 (No Exfiltración): Garantiza que el endpoint LLM resuelto apunta EXCLUSIVAMENTE a localhost:11434."""
        model = get_model(provider="", model_name="")
        api_base = getattr(model, "api_base", "")
        self.assertIn("localhost:11434", api_base)
        self.assertNotIn("api.openai.com", api_base)
        self.assertNotIn("api.anthropic.com", api_base)
        self.assertNotIn("openrouter.ai", api_base)


if __name__ == "__main__":
    unittest.main()
