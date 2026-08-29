"""
Test E2E Real del ENTRYPOINT Real de CodeAgent Desktop (desktop_app.py).
Ejecuta procesos OS REALES en Windows sin mocks de subprocess, HTTP ni sockets.
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


def kill_process_tree(pid: int):
    if pid <= 0:
        return
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            capture_output=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        try:
            os.kill(pid, 9)
        except OSError:
            pass


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


def discover_desktop_backend(desktop_proc: subprocess.Popen, timeout: int = 15) -> tuple[int, dict] | None:
    """Inspecciona stdout de desktop_proc para obtener el puerto asignado e inspecciona /api/health."""
    start = time.time()
    port = None

    # Leer stdout de desktop_proc para obtener el puerto
    while time.time() - start < timeout:
        if desktop_proc.poll() is not None:
            return None
        line = desktop_proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        line_str = line.decode("utf-8", errors="ignore")
        if "puerto " in line_str:
            try:
                parts = line_str.split("puerto ")
                port = int(parts[1].split()[0].rstrip("..."))
                break
            except Exception:
                pass

    if not port:
        return None

    # Consultar /api/health en el puerto descubierto
    health_url = f"http://localhost:{port}/api/health"
    start_health = time.time()
    while time.time() - start_health < 5:
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "CodeAgent-E2E-Discovery"})
            with urllib.request.urlopen(req, timeout=1) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    return port, data
        except Exception:
            time.sleep(0.3)
    return None


@unittest.skipUnless(sys.platform == "win32", "Prueba E2E Real Entrypoint disponible únicamente en Windows OS")
class TestE2ERealDesktopLifecycle(unittest.TestCase):

    def test_01_real_desktop_entrypoint_identity(self):
        """Test 1: Ejecuta desktop_app.py como proceso real y valida los metadatos de su backend dedicado."""
        python_exe = sys.executable
        desktop_script = os.path.join(PROJECT_ROOT, "desktop_app.py")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env["NO_BROWSER"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        desktop_proc = subprocess.Popen([python_exe, "-u", desktop_script], cwd=PROJECT_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            discovered = discover_desktop_backend(desktop_proc, timeout=15)
            self.assertIsNotNone(discovered, "desktop_app.py no logró iniciar su backend a tiempo")

            port, identity = discovered
            self.assertEqual(identity.get("service"), "codeagent-backend")
            self.assertEqual(identity.get("version"), CODEAGENT_VERSION)
            self.assertGreater(identity.get("process_id", 0), 0)
            self.assertGreater(identity.get("parent_pid", 0), 0)
            self.assertEqual(identity.get("port"), port)
            self.assertEqual(os.path.normpath(identity.get("base_dir", "")).lower(), os.path.normpath(PROJECT_ROOT).lower())
            self.assertTrue(bool(identity.get("instance_id")))
        finally:
            if desktop_proc.stdout: desktop_proc.stdout.close()
            kill_process_tree(desktop_proc.pid)

    def test_02_two_real_desktops_isolation_and_chat(self):
        """Test 2 y 3: Lanza Desktop A y Desktop B reales, valida su aislamiento, ejecuta CHAT real y prueba el cierre."""
        python_exe = sys.executable
        desktop_script = os.path.join(PROJECT_ROOT, "desktop_app.py")

        env_A = os.environ.copy()
        env_A["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env_A["NO_BROWSER"] = "1"
        env_A["PYTHONUNBUFFERED"] = "1"

        env_B = os.environ.copy()
        env_B["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env_B["NO_BROWSER"] = "1"
        env_B["PYTHONUNBUFFERED"] = "1"

        proc_A = subprocess.Popen([python_exe, "-u", desktop_script], cwd=PROJECT_ROOT, env=env_A, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc_B = subprocess.Popen([python_exe, "-u", desktop_script], cwd=PROJECT_ROOT, env=env_B, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        try:
            discovered_A = discover_desktop_backend(proc_A, timeout=15)
            discovered_B = discover_desktop_backend(proc_B, timeout=15)

            self.assertIsNotNone(discovered_A, "Desktop A no inició su backend")
            self.assertIsNotNone(discovered_B, "Desktop B no inició su backend")

            port_A, health_A = discovered_A
            port_B, health_B = discovered_B

            # Validar diferencia estricta A vs B
            self.assertNotEqual(proc_A.pid, proc_B.pid)
            self.assertNotEqual(health_A.get("process_id"), health_B.get("process_id"))
            self.assertNotEqual(health_A.get("instance_id"), health_B.get("instance_id"))
            self.assertNotEqual(port_A, port_B)

            self.assertGreater(health_A.get("parent_pid", 0), 0)
            self.assertGreater(health_B.get("parent_pid", 0), 0)
            self.assertNotEqual(health_A.get("parent_pid"), health_B.get("parent_pid"))

            # Ejecutar Petición REAL de CHAT al backend de Desktop A
            chat_url = f"http://localhost:{port_A}/api/agent/chat"
            chat_prompt = (
                "Responde únicamente con OK. No ejecutes ninguna herramienta. "
                "No abras terminal. No crees archivos. No modifiques el workspace. "
                "No ejecutes tests, Ruff ni análisis AST. No hagas planificación ni replanificación. "
                "Termina inmediatamente."
            )
            payload = json.dumps({
                "prompt": chat_prompt,
                "agent_type": "CodeAgent Developer",
                "model": "gpt-4o-mini",
                "api_key": "mock-key"
            }).encode("utf-8")

            req = urllib.request.Request(chat_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=90) as resp:
                self.assertEqual(resp.status, 200)
                res_data = json.loads(resp.read().decode("utf-8"))
                
                respuesta_text = res_data.get("respuesta", "")
                self.assertIn("OK", respuesta_text)

                metricas = res_data.get("metricas", {})
                self.assertEqual(metricas.get("task_type"), "CHAT")
                self.assertEqual(metricas.get("execution_level"), "Nivel 1 (Chat Directo)")
                self.assertEqual(metricas.get("tool_calls_count"), 0)
                self.assertEqual(metricas.get("replans_count"), 0)

                verifier = metricas.get("verification_results", {})
                self.assertEqual(verifier.get("ast_status"), "NOT_REQUIRED")
                self.assertEqual(verifier.get("tests_status"), "NOT_REQUIRED")
                self.assertEqual(verifier.get("ruff_status"), "NOT_REQUIRED")

            # Cerrar Desktop A
            kill_process_tree(proc_A.pid)

            # Esperar a que el backend A termine y libere el puerto A (~2-4s)
            start_wait_A = time.time()
            port_A_freed = False
            while time.time() - start_wait_A < 6:
                if not is_port_listening(port_A):
                    port_A_freed = True
                    break
                time.sleep(0.5)

            self.assertTrue(port_A_freed, f"El puerto {port_A} del backend A no fue liberado tras cerrar Desktop A")

            # Verificar que Server B sigue 100% VIVO y con su mismo instance_id
            health_B_check = get_health(port_B, timeout=2)
            self.assertIsNotNone(health_B_check)
            self.assertEqual(health_B_check.get("instance_id"), health_B.get("instance_id"))

        finally:
            if proc_A.stdout: proc_A.stdout.close()
            if proc_B.stdout: proc_B.stdout.close()
            kill_process_tree(proc_A.pid)
            kill_process_tree(proc_B.pid)

            # Esperar a que el backend B libere su puerto B
            start_wait_B = time.time()
            port_B_freed = False
            while time.time() - start_wait_B < 6:
                if not is_port_listening(port_B):
                    port_B_freed = True
                    break
                time.sleep(0.5)

            self.assertTrue(port_B_freed, f"El puerto {port_B} del backend B no fue liberado tras cerrar Desktop B")

    def test_03_parent_crash_abrupt_cleanup(self):
        """Test 5: Prueba de cierre anormal (crash abrupto del Desktop padre)."""
        python_exe = sys.executable
        desktop_script = os.path.join(PROJECT_ROOT, "desktop_app.py")

        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([PROJECT_ROOT, MODULE_DIR])
        env["NO_BROWSER"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        desktop_proc = subprocess.Popen([python_exe, "-u", desktop_script], cwd=PROJECT_ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            discovered = discover_desktop_backend(desktop_proc, timeout=15)
            self.assertIsNotNone(discovered, "desktop_app.py no logró iniciar backend")

            port, identity = discovered
            backend_pid = identity.get("process_id")

            # Matar ABRUPTAMENTE Desktop (simulando crash) sin ejecutar stop_server normal
            desktop_proc.kill()
            desktop_proc.wait(timeout=5)

            # Esperar a que el parent monitor del backend detecte la muerte del padre (~2-4s)
            start_wait = time.time()
            backend_died = False
            while time.time() - start_wait < 8:
                if not is_port_listening(port):
                    backend_died = True
                    break
                time.sleep(0.5)

            self.assertTrue(backend_died, f"El backend PID {backend_pid} no se autoterminó tras la muerte abrupta del padre")
        finally:
            if desktop_proc.stdout: desktop_proc.stdout.close()
            if desktop_proc.poll() is None:
                desktop_proc.kill()


if __name__ == "__main__":
    unittest.main()
