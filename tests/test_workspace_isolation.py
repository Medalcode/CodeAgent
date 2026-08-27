import os
import tempfile
import unittest

from tools import _detectar_raiz_proyecto, set_active_workspace


class TestWorkspaceIsolation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        set_active_workspace(None)

    def test_set_active_workspace_isolation(self):
        set_active_workspace(self.temp_dir)
        detected_root = _detectar_raiz_proyecto(".")
        self.assertEqual(os.path.abspath(detected_root), os.path.abspath(self.temp_dir))


if __name__ == '__main__':
    unittest.main()
