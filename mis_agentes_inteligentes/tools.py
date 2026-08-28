import base64
import contextlib
import difflib
import logging
import os
import shlex
import sqlite3
import subprocess
import tempfile
import threading
import time
from datetime import date
from enum import Enum
from typing import Any

import requests
from benchmark_metrics import metrics_collector
from smolagents import tool

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if os.name == "nt" else 0


def track_tool_event(tool_name: str, success: bool, duration: float = 0.0, error_type: str | None = None):
    """Rastrea e informa la ejecución de herramientas al colector de métricas."""
    try:
        metrics_collector.record_tool_event(
            tool_name=tool_name,
            success=success,
            duration_seconds=duration,
            error_type=error_type
        )
    except Exception as e:
        logging.warning(f"Error rastreando evento de herramienta {tool_name}: {e}")


class PermissionLevel(Enum):
    """Niveles de autorización para la ejecución segura de herramientas agénticas."""
    LOW = "LOW"            # Operaciones de lectura sin riesgo (read, search, diff)
    MEDIUM = "MEDIUM"        # Modificaciones locales de archivos o tests
    HIGH = "HIGH"          # Commits en VCS
    CRITICAL = "CRITICAL"      # Pushes externos o ejecución arbitraria en consola


TOOL_PERMISSIONS = {
    "listar_directorio_local": PermissionLevel.LOW,
    "leer_archivo": PermissionLevel.LOW,
    "consultar_db": PermissionLevel.LOW,
    "obtener_contexto_workspace": PermissionLevel.LOW,
    "guardar_reporte": PermissionLevel.MEDIUM,
    "editar_archivo_search_replace": PermissionLevel.MEDIUM,
    "ejecutar_comando_terminal": PermissionLevel.CRITICAL
}


def check_tool_permission(tool_name: str, current_level: PermissionLevel = PermissionLevel.CRITICAL) -> bool:
    """Valida si el permiso actual autoriza la ejecución de la herramienta."""
    required = TOOL_PERMISSIONS.get(tool_name, PermissionLevel.MEDIUM)
    hierarchy = [PermissionLevel.LOW, PermissionLevel.MEDIUM, PermissionLevel.HIGH, PermissionLevel.CRITICAL]
    return hierarchy.index(current_level) >= hierarchy.index(required)


@tool
def consultar_db(query: str) -> str:
    """Extrae eventos desde MisEventos.db. La base de datos tiene una tabla 'eventos' con columnas: id, fecha, titulo, descripcion, prioridad. Solo se permiten consultas SELECT.

    Args:
        query: La consulta SQL SELECT.
    """
    # Validar que sea únicamente una consulta de solo lectura
    query_clean = query.strip().upper()
    if not (query_clean.startswith("SELECT") or query_clean.startswith("PRAGMA") or query_clean.startswith("EXPLAIN")):
        return "Error de Seguridad: Solo se permiten consultas SQL de solo lectura (SELECT, PRAGMA, EXPLAIN)."

    # Conectar en modo estricto de solo lectura usando URI con context manager
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MisEventos.db')
    try:
        with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return str(cursor.fetchall())
    except sqlite3.OperationalError as e:
        return f"Error: Operación no permitida o base de datos bloqueada. (Detalle: {e})"
    except Exception as e:
        return f"Error al ejecutar la consulta: {e}"


@tool
def guardar_reporte(analisis: str) -> str:
    """Archiva el análisis para memoria a largo plazo.

    Args:
        analisis: El texto del reporte a guardar.
    """
    try:
        historial_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'historial_analisis.txt')
        with open(historial_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- {date.today()} ---\n{analisis}\n")
        return "Reporte guardado con éxito."
    except Exception as e:
        return f"Error al guardar el reporte en disco: {e}"

GITHUB_API_TIMEOUT = int(os.getenv("GITHUB_API_TIMEOUT", "15"))

def _make_github_request(url: str, token: str) -> requests.Response:
    """Helper centralizado para llamadas HTTP autenticadas a la API de GitHub."""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    return requests.get(url, headers=headers, timeout=GITHUB_API_TIMEOUT)

def _resolver_nombre_repo(token: str, full_name: str) -> str:
    nombre_buscar = full_name.split("/")[-1].lower()
    try:
        r_search = _make_github_request("https://api.github.com/user/repos?per_page=100", token)
        if r_search.status_code == 200:
            for repo in r_search.json():
                if repo["name"].lower() == nombre_buscar:
                    return repo["full_name"]
    except Exception as e:
        logging.warning(f"No se pudo resolver el nombre exacto del repo GitHub {full_name}: {e}")
    return full_name


@tool
def consultar_github(token: str) -> str:
    """Usa esta herramienta cuando el usuario te proporcione un token de Github para acceder a sus repositorios.
    Le pasas el token como argumento y te devolverá la lista de repositorios del usuario.

    Args:
        token: Token de acceso personal de GitHub.
    """
    try:
        response = _make_github_request("https://api.github.com/user/repos?sort=updated&per_page=10", token)
        if response.status_code == 200:
            repos = response.json()
            if not repos:
                return "El usuario no tiene repositorios públicos o el token no tiene permisos suficientes."

            repo_info = ["Repositorios más recientes del usuario (Top 10):"]
            for r in repos:
                repo_info.append(f"- Nombre completo: {r.get('full_name')} | Lenguaje: {r.get('language')}")

            return "\n".join(repo_info)
        elif response.status_code == 401:
            return "Error: El token de GitHub proporcionado es inválido o ha expirado."
        else:
            return f"Error al consultar la API de Github: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de red o conexión al intentar consultar Github: {str(e)}"


@tool
def leer_repositorio_github(token: str, nombres_repos: str) -> str:
    """Usa esta herramienta para analizar a fondo uno o VARIOS repositorios.
    Debes pasarle el token y el nombre del repositorio (ejemplo: 'steam-hunter'). La herramienta encontrará automáticamente el usuario.
    NO es necesario usar consultar_github antes para obtener el nombre exacto.
    Devolverá el contenido del archivo README.md y la lista de archivos.

    Args:
        token: Token de acceso personal de GitHub.
        nombres_repos: Nombre del repositorio (ej: 'steam-hunter').
    """
    resultado_final = ""

    # Procesar cada repo separado por comas
    lista_repos = [r.strip() for r in nombres_repos.split(",")]

    for full_name in lista_repos:
        if not full_name:
            continue

        full_name = _resolver_nombre_repo(token, full_name)

        resultado = f"--- Análisis profundo del repositorio: {full_name} ---\n\n"
        try:
            # 1. Obtener la lista de archivos (Contents)
            resp_contents = _make_github_request(f"https://api.github.com/repos/{full_name}/contents", token)
            if resp_contents.status_code == 200:
                contents = resp_contents.json()
                if isinstance(contents, list):
                    archivos = [f"- {item['name']} ({item['type']})" for item in contents]
                    resultado += "Estructura de archivos en la raíz:\n" + "\n".join(archivos) + "\n\n"
            else:
                resultado += "No se pudo obtener la estructura de archivos.\n\n"

            # 2. Obtener el README.md
            resp_readme = _make_github_request(f"https://api.github.com/repos/{full_name}/readme", token)
            if resp_readme.status_code == 200:
                readme_data = resp_readme.json()
                # GitHub devuelve el contenido en base64
                if "content" in readme_data:
                    contenido_decodificado = base64.b64decode(readme_data["content"]).decode("utf-8", errors="replace")
                    # Limitar el README a 1000 caracteres para no saturar al agente si son múltiples repos
                    resultado += f"Contenido del README.md:\n{contenido_decodificado[:1000]}...\n"
            else:
                resultado += "No se encontró un archivo README.md o no se pudo acceder a él.\n"

            resultado_final += resultado + "\n\n"
        except Exception as e:
            resultado_final += f"Error al intentar leer el repositorio {full_name}: {str(e)}\n\n"

    return resultado_final

@tool
def leer_archivo_github(token: str, repo_full_name: str, ruta_archivo: str) -> str:
    """Lee el contenido de un archivo específico de un repositorio de GitHub.
    Pasa el token, el nombre del repo (ej: 'steam-hunter') y la ruta del archivo dentro del repo (ej: 'src/main.py').
    La herramienta encontrará el repositorio automáticamente. NO es necesario usar consultar_github antes.

    Args:
        token: Token de acceso personal de GitHub.
        repo_full_name: Nombre corto del repositorio (ej: 'steam-hunter').
        ruta_archivo: Ruta del archivo dentro del repositorio.
    """
    repo_full_name = _resolver_nombre_repo(token, repo_full_name)

    try:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{ruta_archivo}"
        resp = _make_github_request(url, token)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("encoding") == "base64":
                contenido = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                # Limitar a 3000 caracteres para no saturar el contexto
                if len(contenido) > 3000:
                    contenido = contenido[:3000] + "\n... [TRUNCADO A 3000 CARACTERES]"
                return f"Contenido de {ruta_archivo}:\n\n{contenido}"
            else:
                return f"El archivo {ruta_archivo} no tiene codificación base64 esperada."
        elif resp.status_code == 404:
            return f"Archivo no encontrado: {ruta_archivo} en {repo_full_name}"
        elif resp.status_code == 401:
            return "Error: Token de GitHub inválido o expirado."
        else:
            return f"Error HTTP {resp.status_code} al leer {ruta_archivo}"
    except Exception as e:
        return f"Error al leer archivo de GitHub: {e}"

_WORKSPACE_LOCK = threading.Lock()
ACTIVE_WORKSPACE_DIR = None


def set_active_workspace(path: str):
    """Establece el directorio del espacio de trabajo activo de forma thread-safe para las herramientas agénticas."""
    global ACTIVE_WORKSPACE_DIR
    with _WORKSPACE_LOCK:
        if path and os.path.exists(path):
            ACTIVE_WORKSPACE_DIR = os.path.abspath(path)
        elif path is None:
            ACTIVE_WORKSPACE_DIR = None


def get_active_workspace() -> str | None:
    """Devuelve el espacio de trabajo activo de forma thread-safe."""
    global ACTIVE_WORKSPACE_DIR
    with _WORKSPACE_LOCK:
        return ACTIVE_WORKSPACE_DIR


def _detectar_raiz_proyecto(inicio=".") -> str:
    """Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md, graphify-out) o usa ACTIVE_WORKSPACE_DIR."""
    active_dir = get_active_workspace()

    if (inicio == "." or not inicio) and active_dir and os.path.exists(active_dir):
        return active_dir

    actual = os.path.abspath(inicio)
    posible = actual
    while True:
        if (
            os.path.exists(os.path.join(posible, ".git"))
            or os.path.exists(os.path.join(posible, "AGENTS.md"))
            or os.path.exists(os.path.join(posible, "graphify-out"))
        ):
            return posible
        padre = os.path.dirname(posible)
        if padre == posible:
            break
        posible = padre

    if active_dir and os.path.exists(active_dir):
        return active_dir

    return actual

@tool
def listar_directorio_local(ruta: str = ".") -> str:
    """Lista los archivos y carpetas de un directorio local y devuelve el contenido como un texto formateado (str). Útil para entender la estructura del proyecto. Por defecto usa la carpeta raíz del proyecto.

    Args:
        ruta: Ruta al directorio local a listar.
    """
    t0 = time.time()
    try:
        if not ruta or ruta == ".":
            ruta = _detectar_raiz_proyecto(".")
        archivos = os.listdir(ruta)
        res = f"Contenido de {os.path.abspath(ruta)}:\n" + "\n".join(archivos)
        track_tool_event("listar_directorio_local", True, time.time() - t0)
        return res
    except Exception as e:
        track_tool_event("listar_directorio_local", False, time.time() - t0, str(e))
        return f"Error al listar {ruta}: {e}"

@tool
def leer_archivo_local(ruta_archivo: str) -> str:
    """Lee el contenido de un archivo local en tu disco duro para poder analizar su código. Devuelve SOLO el contenido limpio (sin cabeceras). Debes pasarle la ruta completa o relativa al archivo.

    Args:
        ruta_archivo: Ruta al archivo local a leer.
    """
    t0 = time.time()
    try:
        if not os.path.isabs(ruta_archivo):
            ruta_archivo = os.path.join(_detectar_raiz_proyecto("."), ruta_archivo)
        with open(ruta_archivo, encoding='utf-8') as f:
            contenido = f.read(150000)
            if f.read(1):
                contenido += "\n\n... [CONTENIDO TRUNCADO POR LÍMITE DE TAMAÑO (150KB)]"
            track_tool_event("leer_archivo_local", True, time.time() - t0)
            return contenido
    except Exception as e:
        track_tool_event("leer_archivo_local", False, time.time() - t0, str(e))
        return f"Error al leer {ruta_archivo}: {e}"

def _verificar_sintaxis_post_edicion(ruta_archivo: str) -> str:
    """Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para Python)."""
    if ruta_archivo.endswith('.py'):
        try:
            with open(ruta_archivo, encoding='utf-8') as f:
                code = f.read()
            import ast
            ast.parse(code, filename=ruta_archivo)
            return ""
        except SyntaxError as se:
            return f"\n⚠️ ADVERTENCIA DE SINTAXIS POST-EDICIÓN: Se detectó SyntaxError en línea {se.lineno}: {se.msg}. Por favor corrige la sintaxis."
        except Exception:
            return ""
    return ""

def _atomic_write_file(abs_path: str, contenido: str) -> None:
    """Escribe un archivo de forma atómica con limpieza segura de temporales en caso de fallo."""
    directorio = os.path.dirname(abs_path)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    temp_name = None
    try:
        with tempfile.NamedTemporaryFile('w', dir=directorio, delete=False, encoding='utf-8') as tf:
            tf.write(contenido)
            temp_name = tf.name
        os.replace(temp_name, abs_path)
    except Exception:
        if temp_name and os.path.exists(temp_name):
            import contextlib
            with contextlib.suppress(Exception):
                os.remove(temp_name)
        raise

@tool
def escribir_archivo_local(ruta_archivo: str, contenido: str) -> str:
    """Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para programar, refactorizar o crear tests.

    Args:
        ruta_archivo: Ruta del archivo a escribir.
        contenido: Contenido a escribir en el archivo.
    """
    t0 = time.time()
    try:
        if not os.path.isabs(ruta_archivo):
            abs_path = os.path.abspath(os.path.join(_detectar_raiz_proyecto("."), ruta_archivo))
        else:
            abs_path = os.path.abspath(ruta_archivo)

        _atomic_write_file(abs_path, contenido)
        warn = _verificar_sintaxis_post_edicion(abs_path)
        track_tool_event("escribir_archivo_local", True, time.time() - t0)
        return f"Éxito: Archivo {ruta_archivo} guardado correctamente.{warn}"
    except Exception as e:
        track_tool_event("escribir_archivo_local", False, time.time() - t0, str(e))
        return f"Error al escribir {ruta_archivo}: {e}"

@tool
def ejecutar_comando_terminal(comando: str, directorio: str = "") -> str:
    """Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip install, python script.py).
    Úsalo para probar el código, instalar dependencias o verificar resultados.

    Args:
        comando: Comando de terminal a ejecutar.
        directorio: Directorio de trabajo donde ejecutar el comando (opcional). Si está vacío, usa la raíz del proyecto.
    """
    try:
        # BUG 3 FIX: blacklist ampliada para Windows y Unix
        blacklist = [
            'rm -rf', 'mkfs', 'dd ', 'sudo rm', 'format c:', 'format d:',
            'shutdown', 'reboot', 'del /f /s /q c:', 'rmdir /s /q c:',
            'mv /', 'cp /', ':(){:|:&};:',  # fork bomb
        ]
        if any(b in comando.lower() for b in blacklist):
            return "Error de Seguridad: El comando contiene operaciones destructivas que están bloqueadas."

        raiz = _detectar_raiz_proyecto(".")
        cwd = directorio if directorio and os.path.isdir(directorio) else raiz

        # Configurar variables de entorno con PYTHONPATH enriquecido para resolución de módulos
        env = os.environ.copy()
        sub_module = os.path.join(raiz, "mis_agentes_inteligentes")
        env["PYTHONPATH"] = os.pathsep.join([raiz, sub_module, env.get("PYTHONPATH", "")])

        try:
            cmd_args = shlex.split(comando, posix=(os.name != 'nt'))
            use_shell = False
        except Exception:
            cmd_args = comando
            use_shell = True

        # Human-In-The-Loop (HITL): Verificación de autorización de comando sensible
        if is_sensitive_command(comando) and not is_command_approved(comando):
            return f"⚠️ AUTORIZACIÓN REQUERIDA (HITL): El comando '{comando}' requiere confirmación explícita del usuario."

        # PR 6: Allowlist Sandboxing (defensa en profundidad)
        from config import ALLOWED_COMMANDS, STRICT_SANDBOX
        allowed_env = os.getenv("ALLOWED_COMMANDS", "")
        if allowed_env:
            allowlist = {c.strip().lower() for c in allowed_env.split(",") if c.strip()}
        else:
            allowlist = ALLOWED_COMMANDS

        binary_token = cmd_args[0] if isinstance(cmd_args, list) and cmd_args else comando.split()[0]
        binary_name = os.path.basename(binary_token).lower().replace(".exe", "")
        if (STRICT_SANDBOX or os.getenv("STRICT_SANDBOX", "0") == "1") and binary_name not in allowlist:
            return f"Error de Seguridad (Sandbox): El comando '{binary_name}' no está en la lista de binarios autorizados."

        try:
            result = subprocess.run(
                cmd_args,
                stdin=subprocess.DEVNULL,
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
                env=env,
                encoding='utf-8',
                errors='replace',
                creationflags=CREATE_NO_WINDOW,
            )
        except FileNotFoundError:
            result = subprocess.run(
                comando,
                stdin=subprocess.DEVNULL,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
                env=env,
                encoding='utf-8',
                errors='replace',
                creationflags=CREATE_NO_WINDOW,
            )
        salida = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr else ""

        # Registrar tarea en el buffer para renderizado en el UI de Chat
        with contextlib.suppress(Exception):
            TERMINAL_TASKS_BUFFER.append({
                "comando": comando,
                "cwd": cwd,
                "exit_code": result.returncode,
                "output": salida if result.returncode == 0 else (error or salida)
            })

        header = f"[Ejecutado en: {cwd}]\n"
        if result.returncode == 0:
            return f"{header}✅ Éxito (código 0)\n{salida}"
        else:
            return f"{header}❌ Falló (código {result.returncode})\nSTDERR:\n{error}\nSTDOUT:\n{salida}"
    except subprocess.TimeoutExpired:
        return "Error: Timeout de 60 segundos superado. El comando tardó demasiado."
    except Exception as e:
        return f"Error de ejecución crítica: {e}"

TERMINAL_TASKS_BUFFER: list[dict[str, Any]] = []

def get_terminal_tasks_buffer() -> list[dict[str, Any]]:
    return list(TERMINAL_TASKS_BUFFER)

def clear_terminal_tasks_buffer() -> None:
    global TERMINAL_TASKS_BUFFER
    TERMINAL_TASKS_BUFFER.clear()
try:
    from googlesearch import search
except ImportError:
    search = None

@tool
def buscar_en_internet(query: str) -> str:
    """Realiza una búsqueda en internet usando Google para obtener información actualizada (noticias, documentación, soluciones a errores).

    Args:
        query: Búsqueda a realizar en Google.
    """
    if search is None:
        return "Error: El módulo googlesearch-python no está instalado."

    try:
        # advanced=True permite obtener título, url y descripción
        resultados = list(search(query, num_results=5, advanced=True))

        if not resultados:
            return f"No se encontraron resultados en Google para la búsqueda: {query}"

        formateado = f"Resultados de Google para '{query}':\n\n"
        for i, r in enumerate(resultados, 1):
            formateado += f"{i}. Título: {r.title}\n"
            formateado += f"   Enlace: {r.url}\n"
            formateado += f"   Resumen: {r.description}\n\n"

        return formateado
    except Exception as e:
        return f"Error al intentar buscar en Google: {e}"

@tool
def editar_archivo_search_replace(ruta_archivo: str, busqueda: str, reemplazo: str) -> str:
    """
    IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.
    Busca el bloque exacto de código en 'busqueda' y lo reemplaza con 'reemplazo'.

    Args:
        ruta_archivo: Ruta del archivo a editar.
        busqueda: Texto a buscar.
        reemplazo: Texto de reemplazo.
    """
    t0 = time.time()
    try:
        with open(ruta_archivo, encoding='utf-8') as f:
            contenido = f.read()

        ocurrencias = contenido.count(busqueda)
        if ocurrencias == 0:
            return "Error: No se encontró el bloque exacto de 'busqueda' en el archivo. Asegúrate de incluir los espacios en blanco e indentación correctos."
        if ocurrencias > 1:
            return f"Error: Se encontraron {ocurrencias} coincidencias del bloque 'busqueda' en el archivo. Proporciona más líneas de contexto alrededor del texto para hacerlo único."

        nuevo_contenido = contenido.replace(busqueda, reemplazo, 1)
        abs_path = os.path.abspath(ruta_archivo)
        _atomic_write_file(abs_path, nuevo_contenido)
        warn = _verificar_sintaxis_post_edicion(abs_path)

        # Generar diff visual para confianza del usuario
        diff = list(difflib.unified_diff(
            contenido.splitlines(keepends=True),
            nuevo_contenido.splitlines(keepends=True),
            fromfile=f"a/{ruta_archivo}",
            tofile=f"b/{ruta_archivo}",
            n=3
        ))

        diff_str = "".join(diff)
        track_tool_event("editar_archivo_search_replace", True, time.time() - t0)

        return f"Éxito: Archivo {ruta_archivo} editado correctamente.{warn}\n\nA continuación el diff de los cambios (asegúrate de mostrarlo al usuario):\n```diff\n{diff_str}\n```"
    except Exception as e:
        track_tool_event("editar_archivo_search_replace", False, time.time() - t0, str(e))
        return f"Error al editar {ruta_archivo}: {e}"

@tool
def git_status(ruta_repo: str = ".") -> str:
    """Muestra el estado del repositorio Git (archivos modificados, untracked, etc).

    Args:
        ruta_repo: Ruta del repositorio git local.
    """
    try:
        result = subprocess.run(["git", "status"], cwd=ruta_repo, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error ejecutando git status: {e}"

@tool
def git_diff(ruta_repo: str = ".") -> str:
    """Muestra los cambios no commiteados en el repositorio.

    Args:
        ruta_repo: Ruta del repositorio git local.
    """
    try:
        result = subprocess.run(["git", "diff"], cwd=ruta_repo, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return result.stdout if result.stdout else "No hay cambios no commiteados."
    except Exception as e:
        return f"Error ejecutando git diff: {e}"

@tool
def git_add(archivos: str, ruta_repo: str = ".") -> str:
    """Añade archivos al staging area de Git. Pasa los archivos separados por espacios, o '.' para añadir todos.

    Args:
        archivos: Archivos a agregar al stage (separados por espacios).
        ruta_repo: Ruta del repositorio git local.
    """
    try:
        args = ["git", "add"] + shlex.split(archivos, posix=(os.name != 'nt'))
        result = subprocess.run(args, cwd=ruta_repo, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return f"Archivos añadidos al stage: {archivos}" if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error ejecutando git add: {e}"

@tool
def git_commit(mensaje: str, ruta_repo: str = ".") -> str:
    """Crea un commit con los archivos en el staging area.

    Args:
        mensaje: Mensaje del commit.
        ruta_repo: Ruta del repositorio git local.
    """
    try:
        result = subprocess.run(["git", "commit", "-m", mensaje], cwd=ruta_repo, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error ejecutando git commit: {e}"

@tool
def git_push(ruta_repo: str = ".", rama: str = "main") -> str:
    """Sube los commits locales al repositorio remoto (GitHub). Opcionalmente especifica la rama.

    Args:
        ruta_repo: Ruta del repositorio git local.
        rama: Rama a pushear (por defecto 'main').
    """
    try:
        result = subprocess.run(["git", "push", "origin", rama], cwd=ruta_repo, capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        if result.returncode == 0:
            return f"Push exitoso a origin/{rama}.\n{result.stdout}"
        else:
            return f"Error en git push: {result.stderr}"
    except Exception as e:
        return f"Error ejecutando git push: {e}"

def obtener_contexto_workspace(ruta="."):
    """Función de utilidad para el comando @workspace. Genera un resumen del entorno."""
    if not ruta or ruta == ".":
        ruta = _detectar_raiz_proyecto(".")

    contexto = f"### CONTEXTO AUTOMÁTICO DEL WORKSPACE ###\n\nDirectorio Raíz Detectado: {os.path.abspath(ruta)}\n\n"

    # 1. Leer README.md si existe
    readme_path = os.path.join(ruta, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, encoding="utf-8") as f:
            contexto += f"Contenido de README.md:\n{f.read()[:1500]}\n\n"

    # 2. Inyectar reglas de proyecto (AGENTS.md y .agents/rules/*.md)
    reglas_paths = ["AGENTS.md", os.path.join(".agents", "rules")]
    for r_path in reglas_paths:
        full_r = os.path.join(ruta, r_path)
        if os.path.isfile(full_r):
            with open(full_r, encoding="utf-8") as f:
                contexto += f"### Reglas del proyecto ({r_path}) ###\n{f.read()[:2000]}\n\n"
        elif os.path.isdir(full_r):
            for fname in sorted(os.listdir(full_r)):
                if fname.endswith(".md"):
                    with open(os.path.join(full_r, fname), encoding="utf-8") as f:
                        contexto += f"### Regla ({fname}) ###\n{f.read()[:1000]}\n\n"

    # 3. Señal explícita si existe un knowledge graph de graphify
    if os.path.isdir(os.path.join(ruta, "graphify-out")):
        contexto += (
            "⚠️ Este proyecto YA TIENE graphify implementado (existe graphify-out/graph.json).\n"
            "Para consultarlo usa `ejecutar_comando_terminal('graphify query \"tu pregunta\"')` o `graphify explain`. "
            "NO intentes `import graphify` en Python — es una herramienta CLI de terminal, no un paquete Python.\n\n"
        )

    # 4. Detectar lenguaje por archivos clave
    archivos_clave = {
        "requirements.txt": "Python (Pip)",
        "Pipfile": "Python (Pipenv)",
        "pyproject.toml": "Python (Poetry/Modern)",
        "package.json": "Node.js / JavaScript / TypeScript",
        "Cargo.toml": "Rust",
        "go.mod": "Go",
        "pom.xml": "Java (Maven)",
        "build.gradle": "Java (Gradle)"
    }

    archivos_locales = os.listdir(ruta)
    lenguajes_detectados = []
    for archivo, lang in archivos_clave.items():
        if archivo in archivos_locales:
            lenguajes_detectados.append(lang)

    if lenguajes_detectados:
        contexto += f"Lenguajes/Entornos detectados: {', '.join(lenguajes_detectados)}\n\n"

    # 5. Estructura de carpetas principal (1 nivel de profundidad)
    estructura = []
    for item in archivos_locales:
        if item.startswith('.') or item == "__pycache__":
            continue
        item_path = os.path.join(ruta, item)
        if os.path.isdir(item_path):
            estructura.append(f"📁 {item}/")
        else:
            estructura.append(f"📄 {item}")

    contexto += "Estructura del directorio raíz:\n" + "\n".join(estructura) + "\n\n"
    return contexto

APPROVED_COMMANDS_SET: set[str] = set()

def is_sensitive_command(cmd: str) -> bool:
    cmd_lower = cmd.lower().strip()
    from config import REQUIRE_TERMINAL_APPROVAL, SENSITIVE_COMMAND_PATTERNS
    if not REQUIRE_TERMINAL_APPROVAL:
        return False
    return any(pattern in cmd_lower for pattern in SENSITIVE_COMMAND_PATTERNS)

def pre_approve_command(cmd: str) -> None:
    APPROVED_COMMANDS_SET.add(cmd.strip())

def is_command_approved(cmd: str) -> bool:
    return cmd.strip() in APPROVED_COMMANDS_SET
