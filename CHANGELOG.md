# Changelog

Todos los cambios notables realizados en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.11.0] - 2026-08-28

### Added & Fixed
- **fix(verifier):** Corregido bug crítico en `_stage_verifier()` donde la presencia de archivos de test antiguos en el workspace invalidaba la directiva explícita del usuario (`has_neg: "No crees tests"`). Ahora `has_neg` anula estrictamente la ejecución de `unittest` devolviendo `NOT_REQUIRED`.
- **feat(verifier):** Incorporada **Verificación Basada en Requisitos de Ejecución del Programa Principal (`program_passed` y `program_output`)**, ejecutando de forma segura el script principal (ej. `main.py` o similar) para recopilar evidencia empírica de salida estándar.
- **feat(critic):** Refactorizado `_stage_critic()` para realizar una evaluación objetiva real del diff de Git (`git status --porcelain`) y la salida empírica del ejecutable principal en lugar de devolver texto genérico estático.
- **fix(runtime):** **Interrupción Inmediata de Cancelación/Pausa (0.015s)**: Propagación de `cancel_event` y `pause_event` dentro de `event_aware_runner` lanzando `InterruptedError` inmediatamente antes y después de llamadas LLM/Herramientas, e interrupción instantánea del bucle de la máquina de estados.
- **feat(recovery):** **Reanudación Dual de Sesión (SQLite WAL + JSON)**: Fallback automático a los checkpoints de SQLite en `resume_session()` garantizando que la reanudación reconstruya `user_goal`, `replans_count`, `failed_verification` y `current_state` incluso tras cierres inesperados de la aplicación.

---

## [6.10.0] - 2026-08-28

### Added
- **feat(architecture):** Habilitada autorecuperación autónoma `DIAGNOSE -> REPLAN -> EXECUTE` para tareas de **Nivel 3 (Feature Standard)** ante fallos de verificación.
- **feat(ui):** Renderizado determinista y formateo explícito en el reporte final de verificación para `NOT_REQUIRED` (`⚪ NOT_REQUIRED (Sin directiva de pruebas requerida)`).
- **test(qa):** Creado módulo `tests/test_tdd_recovery_loop.py` validando el ciclo TDD completo (`FAIL -> DIAGNOSE -> REPLAN -> FIX -> PASS`). Suite total con **106/106 pruebas unitarias pasadas al 100%**.

---

## [6.9.0] - 2026-08-28

### Added
- **feat(llm):** Incorporado **timeout duro de 120s (`request_timeout=120`)** a `LiteLLMModel` en llamadas a Ollama para prevenir cuelgues indefinidos.
- **feat(verifier):** Añadido filtrado inteligente de directivas negativas ("No añadas tests", "sin pruebas") para asegurar la devolución de `NOT_REQUIRED`.
- **feat(verifier):** Inclusión automática de `self.workspace_dir` en `PYTHONPATH` para ejecución correcta de `unittest` en proyectos aislados.
- **test(qa):** Suite de **5 Pruebas de Benchmark** ejecutadas y validadas con 100% de éxito.

---

## [6.8.0] - 2026-08-28

### Added
- **feat(verifier):** Semántica estricta de verificación de 4 estados (`PASS`, `FAIL`, `NOT_RUN`, `NOT_REQUIRED`). Tareas sin pruebas unitarias requeridas ahora devuelven `NOT_REQUIRED` en lugar de marcar falsos fallos en las métricas.
- **feat(telemetry):** Eventos de observabilidad granulares en el runtime: `STATE_ENTERED`, `STATE_EXITED`, `LLM_CALL_STARTED` y `LLM_CALL_COMPLETED` con timestamps precisos.
- **fix(architecture):** Diagnóstico de `hola_codeagent` confirmando la existencia del directorio en el workspace persistente.
- **test(qa):** Suite completa de 105 pruebas unitarias e integración aprobadas al 100%.

---

## [6.7.0] - 2026-08-28

### Added
- **feat(security):** Sistema de **Autorización Humana (HITL - Human-In-The-Loop)** para comandos de consola sensibles (`pip install`, `npm install`, `git push`, etc.).
- **feat(ui):** Tarjeta interactiva `.approval-card` en la interfaz de chat con botones **"✅ Aprobar / Autorizar"** y **"❌ Rechazar / Denegar"**.
- **feat(api):** Endpoint REST `POST /api/terminal/approve` para registrar pre-aprobación y autorización dinámica de comandos.
- **test(qa):** Módulo `tests/test_terminal_hitl_approval.py` alcanzando **105/105 pruebas unitarias e integración pasadas al 100%**.

---

## [6.6.0] - 2026-08-28

### Added
- **feat(runtime):** Deshabilitado el Stdin interactivo (`stdin=subprocess.DEVNULL`) en `ejecutar_comando_terminal` para prevenir cuelgues indefinidos en comandos que soliciten teclado.
- **feat(ui):** Integrado botón **"⏹️ Cancelar Tarea"** con `AbortController` en la tarjeta en vivo de progreso del chat.
- **feat(ui):** Alerta de tiempo transcurrido en vivo (`⚠️ Tarea ejecutándose por más de 60s...`) para visibilidad inmediata del usuario.
- **test(qa):** Módulo `tests/test_task_timeout_safeguard.py` con **102/102 pruebas unitarias aprobadas al 100%**.

---

## [6.5.0] - 2026-08-28

### Added
- **feat(ui):** Integradas **Tarjetas de Terminal (`.terminal-card`)** en el flujo de chat para renderizar comandos ejecutados, código de salida y stdout/stderr.
- **feat(ui):** Cada tarjeta de terminal incluye un botón dedicado **"📋 Copiar Comando"** para copiar comandos de consola con un clic.
- **feat(tools):** Buffer de eventos de tareas de terminal (`TERMINAL_TASKS_BUFFER`) en `tools.py` integrado con el endpoint `/api/agent/chat`.

---

## [6.4.0] - 2026-08-28

### Added
- **feat(ui):** Eliminado el bloque estático de texto simulado/falso (`Worked for 110s...`) al inicio del chat.
- **feat(ui):** Persistencia automática del historial de chat mediante `localStorage` para evitar la pérdida de mensajes al refrescar la página (F5).
- **feat(ui):** Botón dedicado **"🗑️ Limpiar Historial de Chat"** en la barra superior para borrar intencionalmente la conversación cuando el usuario lo desee.

---

## [6.3.0] - 2026-08-28

### Added
- **feat(verification):** Verificación tri-estado basada en evidencia (`PASS`, `FAIL`, `NOT_RUN`). Elimina los falsos positivos donde repositorios vacíos o sin tests reportaban sintaxis o pruebas pasadas.
- **feat(architecture):** Aislamiento estricto de `TaskContext.project_root` mediante rutas absolutas (`os.path.abspath`) ancladas determinísticamente al workspace de cada tarea.
- **feat(ui):** Formato evidencial y transparente de resultados agénticos (`CodeAgent — Task Result`), eliminando titulares de marketing innecesarios.
- **test(qa):** Módulo `tests/test_verifier_evidence.py` alcanzando **100/100 pruebas unitarias aprobadas al 100%**.

---

## [6.2.0] - 2026-08-28

### Added
- **feat(ui):** Habilitada la selección de texto libre con mouse (`user-select: text !important`) en el historial de chat, respuestas del asistente y bloques de código.
- **feat(ui):** Botón **"📋 Copiar Respuesta"** integrado en cada respuesta del agente para copiar con un clic al portapapeles con confirmación visual ("✅ ¡Copiado!").

---

## [6.0.0] - 2026-08-28

### Added
- **feat(architecture):** Motor de Runtime Autónomo Desacoplado (`CodeAgentRuntime`) en `runtime/runtime.py` con métodos `start_task()`, `get_task()`, `pause_task()`, `resume_task()`, `cancel_task()` y `get_events()`.
- **feat(storage):** Almacenamiento Persistente Local SQLite (`storage/database.py`) en modo WAL con tablas `tasks`, `checkpoints`, `events` (Event Sourcing) y `metrics`.
- **feat(events):** Bus de Eventos Persistente (`runtime/event_bus.py`) que registra la línea de tiempo completa de eventos agénticos y los emite a suscriptores.
- **feat(api):** Endpoints REST `/api/tasks`, `/api/tasks/<id>`, `/api/tasks/<id>/events`, `/api/tasks/<id>/resume` para reconexión instantánea post-recarga de UI (F5).
- **test(qa):** Suite `tests/test_runtime_storage.py` alcanzando **94/94 pruebas pasadas al 100%**.

---

## [5.3.0] - 2026-08-27

### Added
- **feat(ide):** Menú File interactivo y atajos de teclado (`Ctrl+N`, `Ctrl+O`, `Ctrl+S`, `Ctrl+Shift+S`, `Ctrl+W`, `Ctrl+Q`) en la UI Claude/Desktop.
- **feat(ide):** Soporte para personalización de nombre y extensión en `Nuevo Archivo` y renombrado en vivo (✏️) en el árbol Explorer.
- **feat(os-interop):** Integración con diálogos nativos del Explorador de Windows mediante PowerShell Forms Bridge (`DesktopIDEApi`) e inputs nativos HTML5.
- **refactor(quality):** Escritura atómica de archivos (`_atomic_write_file`) con eliminación garantizada de temporales en caso de fallo de E/S.
- **test(qa):** Resiliencia ante JSON corrupto en `JSONSessionRepository.load_session` y suite `tests/test_qa_edge_cases.py` alcanzando `91/91` pruebas aprobadas (100% OK).

---

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
