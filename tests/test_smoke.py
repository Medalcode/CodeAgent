import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

import setup_db


class TestSmokeSystem(unittest.TestCase):
    def test_imports_integrity(self):
        import agents
        import main
        import session_manager
        import tools
        self.assertIsNotNone(agents)
        self.assertIsNotNone(main)
        self.assertIsNotNone(session_manager)
        self.assertIsNotNone(tools)

    def test_setup_dummy_db(self):
        import tempfile
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                os.chdir(tmpdir)
                setup_db.create_dummy_db()
                db_path = os.path.join(tmpdir, 'MisEventos.db')
                self.assertTrue(os.path.exists(db_path))

                conn = sqlite3.connect(db_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM eventos")
                    count = cursor.fetchone()[0]
                    self.assertTrue(count > 0)
                finally:
                    conn.close()
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
