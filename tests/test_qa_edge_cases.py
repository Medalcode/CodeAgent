import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mis_agentes_inteligentes")))

from session_manager import JSONSessionRepository
from tools import _atomic_write_file, escribir_archivo_local


class TestQAEdgeCasesAndNegativeScenarios(unittest.TestCase):
    def test_corrupted_session_recovery(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = JSONSessionRepository(sessions_dir=tmpdir)
            corrupted_file = os.path.join(tmpdir, "corrupted-session.json")
            with open(corrupted_file, "w", encoding="utf-8") as f:
                f.write("{ invalid json format... }")

            # Must handle corrupted session cleanly without crash
            session = repo.load_session("corrupted-session")
            self.assertIsNone(session)

    def test_atomic_write_empty_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "empty.txt")
            _atomic_write_file(filepath, "")
            self.assertTrue(os.path.exists(filepath))
            with open(filepath, encoding="utf-8") as f:
                self.assertEqual(f.read(), "")

    def test_write_local_file_invalid_path(self):
        # Trying to write to an invalid path like null character should return error string cleanly
        res = escribir_archivo_local("invalid_\0_path.txt", "content")
        self.assertIn("Error", res)


if __name__ == "__main__":
    unittest.main()
