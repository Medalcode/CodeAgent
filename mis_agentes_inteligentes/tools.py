import sqlite3
import requests
from datetime import date
from langchain.tools import tool

@tool("Consultar base de datos")
def consultar_db(query: str):
    """Extrae eventos desde MisEventos.db. La base de datos tiene una tabla 'eventos' con columnas: id, fecha, titulo, descripcion, prioridad."""
    conn = sqlite3.connect('MisEventos.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        data = str(cursor.fetchall())
    except Exception as e:
        data = f"Error al ejecutar la consulta: {e}"
    finally:
        conn.close()
    return data

@tool("Guardar reporte")
def guardar_reporte(analisis: str):
    """Archiva el análisis para memoria a largo plazo."""
    with open("historial_analisis.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- {date.today()} ---\n{analisis}\n")
    return "Reporte guardado con éxito."

@tool("Consultar Github")
def consultar_github(token: str):
    """Usa esta herramienta cuando el usuario te proporcione un token de Github para acceder a sus repositorios.
    Le pasas el token como argumento y te devolverá la lista de repositorios del usuario.
    """
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get("https://api.github.com/user/repos?sort=updated&per_page=100", headers=headers)
        if response.status_code == 200:
            repos = response.json()
            if not repos:
                return "El usuario no tiene repositorios públicos o el token no tiene permisos suficientes."
            
            repo_info = ["Repositorios más recientes del usuario:"]
            for r in repos:
                repo_info.append(f"- Nombre completo: {r.get('full_name')} | Lenguaje: {r.get('language')} | Estrellas: {r.get('stargazers_count')}\n  Descripción: {r.get('description')}")
            
            return "\n".join(repo_info)
        elif response.status_code == 401:
            return "Error: El token de GitHub proporcionado es inválido o ha expirado."
        else:
            return f"Error al consultar la API de Github: HTTP {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de red o conexión al intentar consultar Github: {str(e)}"

import base64

@tool("Leer Repositorio Github")
def leer_repositorio_github(token: str, nombres_repos: str):
    """Usa esta herramienta para analizar a fondo uno o VARIOS repositorios. 
    Debes pasarle el token y el nombre completo de los repositorios separados por comas (ejemplo: 'usuario/repo1, usuario/repo2').
    Devolverá el contenido del archivo README.md y la lista de archivos de TODOS los repositorios solicitados para que puedas analizarlos a todos a la vez.
    """
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    resultado_final = ""
    
    # Procesar cada repo separado por comas
    lista_repos = [r.strip() for r in nombres_repos.split(",")]
    
    for full_name in lista_repos:
        if not full_name:
            continue
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
import os
import subprocess

@tool("Listar Directorio Local")
def listar_directorio_local(ruta: str = "."):
    """Lista los archivos y carpetas de un directorio local. Útil para entender la estructura del proyecto. Por defecto usa la carpeta actual '.'"""
    try:
        archivos = os.listdir(ruta)
        return f"Contenido de {os.path.abspath(ruta)}:\n" + "\n".join(archivos)
    except Exception as e:
        return f"Error al listar {ruta}: {e}"

@tool("Leer Archivo Local")
def leer_archivo_local(ruta_archivo: str):
    """Lee el contenido de un archivo local en tu disco duro para poder analizar su código. Debes pasarle la ruta completa o relativa al archivo."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return f"Contenido de {ruta_archivo}:\n\n" + f.read()
    except Exception as e:
        return f"Error al leer {ruta_archivo}: {e}"

@tool("Escribir Archivo Local")
def escribir_archivo_local(ruta_archivo: str, contenido: str):
    """Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para programar, refactorizar o crear tests."""
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

@tool("Ejecutar Comando Terminal")
def ejecutar_comando_terminal(comando: str):
    """Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, npm install, python script.py). Úsalo para probar el código o instalar dependencias."""
    try:
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

@tool("Buscar en Internet")
def buscar_en_internet(query: str):
    """Realiza una búsqueda en internet usando Google para obtener información actualizada (noticias, documentación, soluciones a errores)."""
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

@tool("Editar Archivo (Search/Replace)")
def editar_archivo_search_replace(ruta_archivo: str, busqueda: str, reemplazo: str):
    """
    IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.
    Busca el bloque exacto de código en 'busqueda' y lo reemplaza con 'reemplazo'.
    'busqueda' debe coincidir EXACTAMENTE con el contenido actual del archivo (incluyendo espacios).
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if busqueda not in contenido:
            return "Error: No se encontró el bloque exacto de 'busqueda' en el archivo. Asegúrate de incluir los espacios en blanco e indentación correctos."
            
        nuevo_contenido = contenido.replace(busqueda, reemplazo, 1)
        
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
            
        return f"Éxito: Archivo {ruta_archivo} editado correctamente."
    except Exception as e:
        return f"Error al editar {ruta_archivo}: {e}"
