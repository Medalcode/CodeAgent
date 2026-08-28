import os
import tempfile
import unittest

from tools import get_active_workspace, set_active_workspace

from desktop_app import DesktopIDEApi


class TestDesktopIDEApi(unittest.TestCase):

    def setUp(self):
        self.api = DesktopIDEApi()
        self.temp_dir = tempfile.mkdtemp()

    def test_write_file_direct(self):
        target_path = os.path.join(self.temp_dir, "test_file.py")
        content = "print('Hello CodeAgent IDE v5.0')"

        success = self.api.write_file(target_path, content)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(target_path))

        with open(target_path, encoding="utf-8") as f:
            read_content = f.read()
        self.assertEqual(read_content, content)

    def test_workspace_management(self):
        old_ws = get_active_workspace()
        set_active_workspace(self.temp_dir)
        self.assertEqual(get_active_workspace(), self.temp_dir)
        if old_ws:
            set_active_workspace(old_ws)


if __name__ == "__main__":
    unittest.main()
