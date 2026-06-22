import sqlite3
import requests
from datetime import date
from smolagents import tool

@tool
def consultar_db(query: str) -> str:
    """Extrae eventos desde MisEventos.db. La base de datos tiene una tabla 'eventos' con columnas: id, fecha, titulo, descripcion, prioridad. Solo se permiten consultas SELECT.
    
    Args:
        query: La consulta SQL SELECT.
    """
    # Conectar en modo estricto de solo lectura usando URI
    try:
        conn = sqlite3.connect('file:MisEventos.db?mode=ro', uri=True)
        cursor = conn.cursor()
        cursor.execute(query)
        data = str(cursor.fetchall())
    except sqlite3.OperationalError as e:
        data = f"Error: Operación no permitida o base de datos bloqueada. (Detalle: {e})"
    except Exception as e:
        data = f"Error al ejecutar la consulta: {e}"
    finally:
        if 'conn' in locals():
            conn.close()
    return data

@tool
def guardar_reporte(analisis: str) -> str:
    """Archiva el análisis para memoria a largo plazo.
    
    Args:
        analisis: El texto del reporte a guardar.
    """
    with open("historial_analisis.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- {date.today()} ---\n{analisis}\n")
    return "Reporte guardado con éxito."

@tool
def consultar_github(token: str) -> str:
    """Usa esta herramienta cuando el usuario te proporcione un token de Github para acceder a sus repositorios.
    Le pasas el token como argumento y te devolverá la lista de repositorios del usuario.
    
    Args:
        token: Token de acceso personal de GitHub.
    """
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get("https://api.github.com/user/repos?sort=updated&per_page=10", headers=headers)
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

import base64

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
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    resultado_final = ""
    
    # Procesar cada repo separado por comas
    lista_repos = [r.strip() for r in nombres_repos.split(",")]
    
    for full_name in lista_repos:
        if not full_name:
            continue
            
        # Lógica Robusta: Si el LLM manda "usuario/steam-hunter", "username/steam-hunter", o solo "steam-hunter"
        nombre_buscar = full_name.split("/")[-1].lower() # Ej: 'steam-hunter'
        
        try:
            # Obtener repositorios del usuario para encontrar el nombre completo real
            r_search = requests.get("https://api.github.com/user/repos?per_page=100", headers=headers)
            if r_search.status_code == 200:
                for repo in r_search.json():
                    if repo["name"].lower() == nombre_buscar:
                        full_name = repo["full_name"]
                        break
        except Exception:
            pass
                
        resultado = f"--- Análisis profundo del repositorio: {full_name} ---\n\n"
        try:
            # 1. Obtener la lista de archivos (Contents)
            resp_contents = requests.get(f"https://api.github.com/repos/{full_name}/contents", headers=headers)
            if resp_contents.status_code == 200:
                contents = resp_contents.json()
                if isinstance(contents, list):
                    archivos = [f"- {item['name']} ({item['type']})" for item in contents]
                    resultado += "Estructura de archivos en la raíz:\n" + "\n".join(archivos) + "\n\n"
            else:
                resultado += "No se pudo obtener la estructura de archivos.\n\n"

            # 2. Obtener el README.md
            resp_readme = requests.get(f"https://api.github.com/repos/{full_name}/readme", headers=headers)
            if resp_readme.status_code == 200:
                readme_data = resp_readme.json()
                # GitHub devuelve el contenido en base64
                if "content" in readme_data:
                    contenido_decodificado = base64.b64decode(readme_data["content"]).decode("utf-8")
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
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    # Lógica Robusta: resolver nombre real del repo
    nombre_buscar = repo_full_name.split("/")[-1].lower()
    try:
        r_search = requests.get("https://api.github.com/user/repos?per_page=100", headers=headers)
        if r_search.status_code == 200:
            for repo in r_search.json():
                if repo["name"].lower() == nombre_buscar:
                    repo_full_name = repo["full_name"]
                    break
    except Exception:
        pass

    try:
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{ruta_archivo}"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("encoding") == "base64":
                contenido = base64.b64decode(data["content"]).decode("utf-8")
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
import os
import subprocess

@tool
def listar_directorio_local(ruta: str = ".") -> str:
    """Lista los archivos y carpetas de un directorio local. Útil para entender la estructura del proyecto. Por defecto usa la carpeta actual '.'
    
    Args:
        ruta: Ruta al directorio local a listar.
    """
    try:
        archivos = os.listdir(ruta)
        return f"Contenido de {os.path.abspath(ruta)}:\n" + "\n".join(archivos)
    except Exception as e:
        return f"Error al listar {ruta}: {e}"

@tool
def leer_archivo_local(ruta_archivo: str) -> str:
    """Lee el contenido de un archivo local en tu disco duro para poder analizar su código. Devuelve SOLO el contenido limpio (sin cabeceras). Debes pasarle la ruta completa o relativa al archivo.
    
    Args:
        ruta_archivo: Ruta al archivo local a leer.
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read(150000)
            if f.read(1):
                contenido += "\n\n... [CONTENIDO TRUNCADO POR LÍMITE DE TAMAÑO (150KB)]"
            return contenido
    except Exception as e:
        return f"Error al leer {ruta_archivo}: {e}"

@tool
def escribir_archivo_local(ruta_archivo: str, contenido: str) -> str:
    """Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para programar, refactorizar o crear tests.
    
    Args:
        ruta_archivo: Ruta del archivo a escribir.
        contenido: Contenido a escribir en el archivo.
    """
    try:
        # Crear directorios si no existen
        directorio = os.path.dirname(os.path.abspath(ruta_archivo))
        if directorio:
            os.makedirs(directorio, exist_ok=True)
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        return f"Éxito: Archivo {ruta_archivo} guardado correctamente."
    except Exception as e:
        return f"Error al escribir {ruta_archivo}: {e}"

@tool
def ejecutar_comando_terminal(comando: str) -> str:
    """Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, npm install, python script.py). Úsalo para probar el código o instalar dependencias.
    
    Args:
        comando: Comando de terminal a ejecutar.
    """
    try:
        blacklist = ['rm -rf', 'mkfs', 'dd ', 'sudo ', 'format ', 'shutdown', 'reboot', 'mv /', 'cp /']
        if any(b in comando.lower() for b in blacklist):
            return "Error de Seguridad: El comando contiene operaciones destructivas o de sistema que están bloqueadas."
            
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=30)
        salida = result.stdout if result.stdout else ""
        error = result.stderr if result.stderr else ""
        
        if result.returncode == 0:
            return f"Comando ejecutado con éxito.\nSalida:\n{salida}"
        else:
            return f"El comando falló con código {result.returncode}.\nError:\n{error}\nSalida:\n{salida}"
    except subprocess.TimeoutExpired:
        return "Error: El comando tardó demasiado en ejecutarse (Timeout de 30 segundos)."
    except Exception as e:
        return f"Error de ejecución crítica: {e}"

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
    import difflib
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if busqueda not in contenido:
            return "Error: No se encontró el bloque exacto de 'busqueda' en el archivo. Asegúrate de incluir los espacios en blanco e indentación correctos."
            
        nuevo_contenido = contenido.replace(busqueda, reemplazo, 1)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
            
        # Generar diff visual para confianza del usuario
        diff = list(difflib.unified_diff(
            contenido.splitlines(keepends=True),
            nuevo_contenido.splitlines(keepends=True),
            fromfile=f"a/{ruta_archivo}",
            tofile=f"b/{ruta_archivo}",
            n=3
        ))
        
        diff_str = "".join(diff)
        
        return f"Éxito: Archivo {ruta_archivo} editado correctamente.\n\nA continuación el diff de los cambios (asegúrate de mostrarlo al usuario):\n```diff\n{diff_str}\n```"
    except Exception as e:
        return f"Error al editar {ruta_archivo}: {e}"

@tool
def git_status(ruta_repo: str = ".") -> str:
    """Muestra el estado del repositorio Git (archivos modificados, untracked, etc).
    
    Args:
        ruta_repo: Ruta del repositorio git local.
    """
    try:
        result = subprocess.run(["git", "status"], cwd=ruta_repo, capture_output=True, text=True)
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
        result = subprocess.run(["git", "diff"], cwd=ruta_repo, capture_output=True, text=True)
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
        import shlex
        args = ["git", "add"] + shlex.split(archivos)
        result = subprocess.run(args, cwd=ruta_repo, capture_output=True, text=True)
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
        result = subprocess.run(["git", "commit", "-m", mensaje], cwd=ruta_repo, capture_output=True, text=True)
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
        result = subprocess.run(["git", "push", "origin", rama], cwd=ruta_repo, capture_output=True, text=True)
        if result.returncode == 0:
            return f"Push exitoso a origin/{rama}.\n{result.stdout}"
        else:
            return f"Error en git push: {result.stderr}"
    except Exception as e:
        return f"Error ejecutando git push: {e}"

def obtener_contexto_workspace(ruta="."):
    """Función de utilidad para el comando @workspace. Genera un resumen del entorno."""
    contexto = "### CONTEXTO AUTOMÁTICO DEL WORKSPACE ###\n\n"
    
    # 1. Leer README.md si existe
    readme_path = os.path.join(ruta, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            contexto += f"Contenido de README.md:\n{f.read()[:1500]}\n\n"
            
    # 2. Detectar lenguaje por archivos clave
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
        
    # 3. Estructura de carpetas principal (1 nivel de profundidad)
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
