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
        response = requests.get("https://api.github.com/user/repos?sort=updated&per_page=5", headers=headers)
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
