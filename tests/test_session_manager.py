import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mis_agentes_inteligentes')))

import session_manager


class TestSessionManager(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.original_sessions_dir = session_manager.SESSIONS_DIR
        session_manager.SESSIONS_DIR = self.tmp_dir.name

    def tearDown(self):
        session_manager.SESSIONS_DIR = self.original_sessions_dir
        self.tmp_dir.cleanup()

    def test_create_and_load_session(self):
        session_id = session_manager.create_new_session("Test Session")
        self.assertIsNotNone(session_id)

        data = session_manager.load_session(session_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Test Session")
        self.assertEqual(data["messages"], [])

    def test_list_sessions(self):
        id1 = session_manager.create_new_session("Session 1")
        id2 = session_manager.create_new_session("Session 2")

        sessions = session_manager.list_sessions()
        self.assertEqual(len(sessions), 2)
        session_ids = [s["id"] for s in sessions]
        self.assertIn(id1, session_ids)
        self.assertIn(id2, session_ids)

    def test_rename_session(self):
        session_id = session_manager.create_new_session("Old Name")
        session_manager.rename_session(session_id, "New Name")

        data = session_manager.load_session(session_id)
        self.assertEqual(data["name"], "New Name")

    def test_delete_session(self):
        session_id = session_manager.create_new_session("To Delete")
        session_manager.delete_session(session_id)

        data = session_manager.load_session(session_id)
        self.assertIsNone(data)

    def test_delete_session_none(self):
        # Should not raise exception
        session_manager.delete_session(None)

    def test_export_session_to_markdown(self):
        session_id = session_manager.create_new_session("Export Test")
        data = session_manager.load_session(session_id)
        data["messages"].append({"role": "user", "content": "Hello", "time": "12:00:00"})
        session_manager.save_session(session_id, data)

        md = session_manager.export_session_to_markdown(session_id)
        self.assertIn("# Sesión: Export Test", md)
        self.assertIn("👤 Usuario", md)
        self.assertIn("Hello", md)


if __name__ == '__main__':
    unittest.main()
