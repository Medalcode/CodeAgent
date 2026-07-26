# Changelog

Todos los cambios notables realizados en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.1] - 2026-07-26

### Fixed
- **security(tools):** Eliminación de riesgo de Shell Injection en `ejecutar_comando_terminal` mediante evaluación de operadores de shell, bloqueos de comandos y tokenización con `shlex.split`.
- **fix(app):** Eliminación del efecto secundario global `os.chdir` en `app.py` mediante la definición de `BASE_DIR`.
- **fix(app):** Adición de `_truncar_markdown` en la compresión del historial para cerrar bloques de código ```` ``` ```` incompletos y mantener la integridad sintáctica del prompt.
- **fix(agents):** Inclusión de subagentes dinámicos (`subagents/*.md`) en el enrutamiento automático por scoring ponderado de `route_prompt`.
- **fix(tools):** Decodificación resiliente de contenido base64 en la API de GitHub usando `errors="replace"` para evitar `UnicodeDecodeError` en archivos binarios.
- **config(tools):** Configuración desacoplada del timeout HTTP en llamadas a GitHub API usando la variable de entorno `GITHUB_API_TIMEOUT` (por defecto 15s).

### Added
- **test(agents):** Adición de `test_route_prompt_subagents` en `tests/test_agents.py` para validar el enrutamiento automático hacia subagentes dinámicos.

---

## [2.2.0] - 2026-07-25

### Fixed
- **security(tools):** Validación estricta de consultas SQL en `consultar_db` limitando ejecuciones exclusivamente a comandos de lectura (`SELECT`, `PRAGMA`, `EXPLAIN`).
- **fix(tools):** Verificación de ambigüedad en `editar_archivo_search_replace` para prevenir reemplazos accidentales cuando existen múltiples ocurrencias del texto buscado.
- **fix(tools):** Manejo explícito de excepciones IO al guardar reportes en `guardar_reporte`.
- **fix(session_manager):** Reemplazo de silencio de excepciones (`except Exception: pass`) por registro detallado (`logging.warning`) al parsear sesiones JSON corruptas.
- **fix(agents):** Sustitución de `print()` sin formato por `logging.warning()` durante la lectura y parseo YAML de subagentes.

### Refactored
- **refactor(main):** Eliminación de la función duplicada `_construir_contexto_workspace` en favor de `mis_herramientas.obtener_contexto_workspace()` (Principio DRY).
- **refactor(tools):** Creación del helper `_make_github_request` para centralizar llamadas HTTP autenticadas con timeout y headers a la API de GitHub.

### Added
- **test(session_manager):** Creación de `tests/test_session_manager.py` con pruebas unitarias exhaustivas para el ciclo de vida CRUD y exportación Markdown de sesiones.
- **test(tools):** Extensión de `tests/test_tools.py` con cobertura para validación de SQL, comprobación de ambigüedad en search/replace y reporte de análisis.
- **test(agents):** Extensión de `tests/test_agents.py` con pruebas para `get_available_agents`, `load_subagents_from_disk` y excepciones de `get_model`.
- **chore(package):** Creación de `mis_agentes_inteligentes/__init__.py` para habilitar la importación del proyecto como paquete Python nativo.
