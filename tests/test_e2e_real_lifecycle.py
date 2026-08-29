"""
Prueba E2E Real OS Lifecycle para Windows (Sin Mocks).
Verifica que dos instancias de Desktop lanzan servidores dedicados en puertos y PIDs independientes,
y que el cierre de Desktop A no interfiere con Server B.
"""
import unittest
import os
import sys
import time
import json
import socket
import urllib.request
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULE_DIR = os.path.join(PROJECT_ROOT, "mis_agentes_inteligentes")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

import desktop_app
from mis_agentes_inteligentes.version import CODEAGENT_VERSION


def is_port_listening(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            res = s.connect_ex(("127.0.0.1", port))
            return res == 0
    except Exception:
        return False


def get_health(port: int, timeout: int = 5) -> dict | None:
    url = f"http://localhost:{port}/api/health"
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CodeAgent-E2E"})
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception:
            time.sleep(0.3)
    return None


@unittest.skipUnless(sys.platform == "win32", "Prueba E2E Real disponible únicamente en entorno Windows OS")
class TestE2ERealLifecycle(unittest.TestCase):
    def test_e2e_real_desktop_instances_isolation(self):
        """Ejecuta dos subprocesos Python reales de localcode_server.py simulando Desktop A y Desktop B."""
        python_exe = sys.executable
        server_script = os.path.join(PROJECT_ROOT, "mis_agentes_inteligentes", "localcode_server.py")

        port_A = desktop_app.find_free_port()
        port_B = desktop_app.find_free_port()
        self.assertNotEqual(port_A, port_B)

        # 1. Lanzar Backend A simulando Desktop A
        env_A = os.environ.copy()
        env_A["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env_A["NO_BROWSER"] = "1"
        env_A["CODEAGENT_PORT"] = str(port_A)
        env_A["CODEAGENT_INSTANCE_ID"] = "e2e-instance-A-111"
        env_A["CODEAGENT_PARENT_PID"] = str(os.getpid())
        env_A["CODEAGENT_PARENT_CREATION_TIME"] = str(desktop_app.get_process_creation_time(os.getpid()))

        proc_A = subprocess.Popen([python_exe, server_script, "--port", str(port_A)], cwd=PROJECT_ROOT, env=env_A)

        health_A = get_health(port_A, timeout=10)
        self.assertIsNotNone(health_A, f"Server A no arrancó a tiempo en puerto {port_A}")
        self.assertEqual(health_A.get("instance_id"), "e2e-instance-A-111")
        self.assertEqual(health_A.get("port"), port_A)
        pid_A = health_A.get("process_id")

        # 2. Lanzar Backend B simulando Desktop B
        env_B = os.environ.copy()
        env_B["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env_B["NO_BROWSER"] = "1"
        env_B["CODEAGENT_PORT"] = str(port_B)
        env_B["CODEAGENT_INSTANCE_ID"] = "e2e-instance-B-222"
        env_B["CODEAGENT_PARENT_PID"] = str(os.getpid())
        env_B["CODEAGENT_PARENT_CREATION_TIME"] = str(desktop_app.get_process_creation_time(os.getpid()))

        proc_B = subprocess.Popen([python_exe, server_script, "--port", str(port_B)], cwd=PROJECT_ROOT, env=env_B)

        health_B = get_health(port_B, timeout=10)
        self.assertIsNotNone(health_B, f"Server B no arrancó a tiempo en puerto {port_B}")
        self.assertEqual(health_B.get("instance_id"), "e2e-instance-B-222")
        self.assertEqual(health_B.get("port"), port_B)
        pid_B = health_B.get("process_id")

        # 3. Verificar A != B en puerto, instance_id y PID
        self.assertNotEqual(health_A.get("instance_id"), health_B.get("instance_id"))
        self.assertNotEqual(pid_A, pid_B)

        # 4. Apagar Server A
        try:
            req = urllib.request.Request(f"http://localhost:{port_A}/api/server/shutdown", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass

        proc_A.wait(timeout=5)
        time.sleep(1)

        # 5. Verificar que Server A murió y port_A está libre
        self.assertFalse(is_port_listening(port_A))

        # 6. Verificar que Server B sigue 100% VIVO y respondiendo HTTP 200
        health_B_check = get_health(port_B, timeout=2)
        self.assertIsNotNone(health_B_check)
        self.assertEqual(health_B_check.get("instance_id"), "e2e-instance-B-222")

        # 7. Apagar Server B
        try:
            req = urllib.request.Request(f"http://localhost:{port_B}/api/server/shutdown", data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass

        proc_B.wait(timeout=5)
        time.sleep(1)

        # 8. Verificar que Server B murió y port_B está libre
        self.assertFalse(is_port_listening(port_B))


if __name__ == "__main__":
    unittest.main()
