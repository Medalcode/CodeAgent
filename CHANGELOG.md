# Changelog

Todos los cambios notables realizados en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.3.0] - 2026-08-27

### Added
- **feat(architecture):** Bucle de Feedback Adaptativo Real con estado `State.DIAGNOSE` e inferencia condicional de re-exploración AST (`DIAGNOSE` ➔ `REPLAN` ➔ `EXPLORE` / `EXECUTE`).
- **feat(metrics):** Instrumentación real de eventos de herramientas (`ToolEvent`) en `tools.py` y `benchmark_metrics.py` calculando la **Tasa de Éxito de Herramientas (Tool Success Rate %)** real.
- **feat(evaluator):** Evaluador determinista de complejidad y riesgo (`ComplexityRiskEvaluator`) para la inferencia adaptativa de niveles de ejecución 1 a 4.
- **test(qa):** Creación de la suite de pruebas `tests/test_feedback_loop.py` e integración global alcanzando `78/78` pruebas pasadas (100% éxito).

---

## [4.2.0] - 2026-08-27

### Added
- **feat(benchmark):** Suite reproducible de 5 Benchmarks Reales de Ingeniería (`benchmark_suite.py`) que evalúa y exporta estadísticas en `benchmark_report_v42.md`.
- **feat(architecture):** Protocolo Estructural Estricto Graphify-First en `_stage_explorer`, clasificando símbolos impactados directamente desde `graph.json`.
- **feat(observability):** Traza de observabilidad en tiempo real de transiciones del autómata agéntico (`🟢 Task Started` ➔ `🧠 PLANNING` ➔ `🔍 EXPLORING` ➔ `🔨 EXECUTING` ➔ `🧪 VERIFYING` ➔ `🔄 REPLANNING` ➔ `👨‍⚖️ CRITIC` ➔ `✅ DONE`).
- **test(qa):** Suite de pruebas `tests/test_benchmark_suite.py` e integración alcanzando `75/75` pruebas pasadas (100% éxito).

---

## [4.0.0] - 2026-08-27

### Added
- **feat(architecture):** Máquina de Estados Determinista (`AgentStateMachineController`) en `agent_pipeline.py` con transiciones de estado explícitas (`PLAN` ➔ `EXPLORE` ➔ `EXECUTE` ➔ `VERIFY` ➔ `CRITIC` ➔ `REPLAN` ➔ `DONE`).
- **feat(architecture):** Niveles Adaptativos de Ejecución 1 a 4 (`LEVEL_1_CHAT`, `LEVEL_2_ACTION`, `LEVEL_3_FEATURE`, `LEVEL_4_FULL`) con enrutamiento inteligente por complejidad de intención.
- **feat(architecture):** Bucle de Re-planificación y Recuperación Autónoma (`State.REPLAN`) que retroalimenta errores sintácticos y de pruebas para auto-corrección inmediata.
- **feat(metrics):** Motor de Métricas Cuantitativas (`benchmark_metrics.py`) registrando `Task Success Rate`, `Autonomous Recovery Rate`, `Average Replans` y `Tool Success Rate` en `metrics_benchmarks.json`.
- **test(qa):** Creación de la suite de pruebas `tests/test_state_machine.py` e integración con la suite global alcanzando `71/71` pruebas pasadas (100% éxito).

---

## [3.5.0] - 2026-08-27

### Added
- **feat(desktop):** Aplicación de escritorio nativa independiente (`desktop_app.py` y `Lanzar_CodeAgent_Desktop.bat`) basada en `pywebview` y modo App.
- **feat(desktop):** Auto-orquestación en 1 clic: verificación y auto-inicio transparente de `ollama serve` y backend proxy en segundo plano.
- **feat(workspace):** Selector dinámico de repositorios `📁 [Workspace] ▾` en la UI y modal interactivo para cambiar de proyecto en tiempo real.
- **feat(security):** Encapsulación thread-safe `_WORKSPACE_LOCK` en `tools.py` para prevenir race conditions en entornos multihilo.
- **test(qa):** Adición de la suite de pruebas unitarias `tests/test_desktop_app.py` e isolación de workspaces (`64/64` tests pasados al 100%).

### Fixed
- **fix(agent):** Inyección automática de `PYTHONPATH` en la terminal e inferencia de rutas contra `_detectar_raiz_proyecto(".")`, resolviendo fallas de sandbox `open()` y `ModuleNotFoundError`.
- **fix(devops):** Configuración de `PYTHONPATH` en GitHub Actions `ci.yml` e inclusión de archivos estáticos en `Dockerfile`.

---

## [2.5.0] - 2026-08-26

### Fixed
- **fix(workspace):** Detección automática de la raíz del proyecto (`_detectar_raiz_proyecto`) mediante ascenso en la jerarquía de directorios localizando `.git`, `AGENTS.md` o `graphify-out/`.
- **fix(ollama):** Expansión de la ventana de contexto `num_ctx` a 8192+ tokens en `agents.py::get_model()` para prevenir el olvido del prompt ReAct en modelos locales.
- **fix(terminal):** Implementación de `_safe_print` en `localcode_server.py` para prevenir fallos `UnicodeEncodeError` por caracteres emoji en terminales Windows con codificación `cp1252`.

### Added
- **feat(agent):** Streaming en tiempo real de pasos `ActionStep` (`stream=True` y `_step_callback`) en `main.py`.
- **feat(agent):** Registro nativo de `Memoria RAG` (`indexar_directorio_local` y `preguntar_a_repositorio`) en `DEFAULT_AGENT_TOOLS`.
- **feat(security):** Verificación sintáctica AST automática (`ast.parse`) post-edición de código Python en `tools.py`.
- **feat(security):** Modo de sandboxing por allowlist (`STRICT_SANDBOX` y `ALLOWED_COMMANDS`) para ejecuciones en terminal.
- **test(qa):** Creación de la suite de pruebas End-to-End `tests/test_e2e_suite.py` alcanzando 57 pruebas pasadas (100% éxito).

---

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
