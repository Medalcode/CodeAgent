# Changelog

Todos los cambios notables realizados en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.4.0] - 2026-08-26

### Fixed
- **fix(ui):** Eliminación de redeclaración duplicada de `cleanHistory` en `sendMessage()` que causaba un `SyntaxError` e inhabilitaba controladores de eventos de botones en `localcode_claude_ui.html`.
- **fix(deps):** Adición de polyfill de compatibilidad en `agents.py` para `typing.NotRequired` e inyección de `ChatCompletionReasoningSummaryTextBlock` con `model_rebuild()` en esquemas Pydantic v2 de LiteLLM.
- **fix(proxy):** Incremento del timeout de proxy HTTP de 10s a 120s en `localcode_server.py` y solución a conexiones colgadas en socket local de Ollama (HTTP 502).

### Refactored
- **refactor(quality):** Centralización de `DEFAULT_AGENT_TOOLS` en `agents.py` como fuente única de verdad para la asignación predeterminada de herramientas.
- **refactor(quality):** Estandarización de la resolución de rutas relativas dinámicas para `MisEventos.db` en `setup_db.py`.
- **refactor(devops):** Actualización de `Iniciar_OpenCode.bat` para priorizar la detección del entorno virtual unificado de la raíz (`..\.venv` en Python 3.11+).

### Added
- **test(qa):** Creación de la suite de pruebas de integración HTTP `tests/test_localcode_server.py` para validar endpoints estáticos, tree de workspace y manejo de errores.
- **test(qa):** Adición de casos borde en `tests/test_tools.py` para escrituras anidadas profundas y validación de seguridad en `ejecutar_comando_terminal` (46 tests totales pasando).

---

## [2.3.0] - 2026-08-04

### Refactored
- **refactor(session_manager):** Anclaje de `SESSIONS_DIR` a `BASE_DIR` del módulo para evitar rutas relativas dependientes del directorio de ejecución.
- **refactor(rag_tools):** Anclaje de `DB_DIR` a `BASE_DIR` e inclusión de `logging.debug` en captura de errores de lectura durante indexación.
- **refactor(tools):** Uso de context manager `with sqlite3.connect(...) as conn:` en `consultar_db` para liberación limpia de recursos SQLite.
- **refactor(imports):** Elevación de importaciones internas (`difflib`, `shlex`, `traceback`, `logging`) al encabezado principal de los módulos `tools.py`, `main.py`, `agents.py` y `app.py`.

### Performance
- **perf(agents):** Implementación de caché basada en timestamp de modificación (`mtime`) en `load_subagents_from_disk()` para optimizar `route_prompt` y la instanciación de agentes.

### Added
- **test(qa):** Creación de `tests/test_regression.py` para validar truncamiento markdown, resiliencia de entradas nulas y operaciones Git.
- **test(qa):** Creación de `tests/test_integration_pipeline.py` para pruebas de integración del pipeline `ejecutar_agentes` en `main.py`.

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
