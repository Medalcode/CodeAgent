# Graph Report - CodeAgent  (2026-08-28)

## Corpus Check
- 71 files · ~50,604 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 755 nodes · 1156 edges · 71 communities (49 shown, 22 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8dda4a1b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_manager.py
- LocalCodeProxyHandler
- TestVerifierEvidenceAndWorkspaceIsolation
- CodeAgentRuntime
- main.py
- Changelog
- 💻 CodeAgent (v6.11 Enterprise)
- tool
- mis_agentes_inteligentes/tools
- mis_agentes_inteligentes.tools
- AgentStateMachineController
- _detectar_raiz_proyecto
- mis_agentes_inteligentes.main
- orquestador_agente.py
- rag_tools.py
- CodeAgent
- Test-Driven Development
- orquestador_agente
- TestTools
- mis_agentes_inteligentes/session_manager
- mis_agentes_inteligentes.session_manager
- desktop_app.py
- BenchmarkMetricsCollector
- _make_github_request
- mis_agentes_inteligentes/agents
- mis_agentes_inteligentes.agents
- tools.py
- TestSmokeSystem
- ADR-001: Selección de smolagents como Motor ReAct
- ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo
- ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM
- ejecutar_comando_terminal
- EventBus
- mis_agentes_inteligentes/rag_tools
- CodeAgentBenchmarkSuite
- graphify.js
- rules/graphify.md
- workflows/graphify.md
- config.py
- __init__.py
- start_hub.sh
- [2.2.0] - 2026-07-25
- 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)
- TestRuntimeAndStorage
- DatabaseManager
- [2.3.0] - 2026-08-04
- [2.4.0] - 2026-08-26
- TestRuntimeRecoveryAndPauseSemantics
- [2.2.1] - 2026-07-26
- database.py
- [2.5.0] - 2026-08-26
- mis_agentes_inteligentes.rag_tools
- [3.5.0] - 2026-08-27
- [4.0.0] - 2026-08-27
- [4.3.0] - 2026-08-27
- [5.3.0] - 2026-08-27
- TestAgents
- [6.3.0] - 2026-08-28
- [6.5.0] - 2026-08-28
- [6.6.0] - 2026-08-28
- [6.7.0] - 2026-08-28
- [6.8.0] - 2026-08-28
- [6.9.0] - 2026-08-28
- app.py
- ejecutar_agentes
- [6.11.0] - 2026-08-28
- [6.2.0] - 2026-08-28

## God Nodes (most connected - your core abstractions)
1. `AgentStateMachineController` - 37 edges
2. `DatabaseManager` - 27 edges
3. `LocalCodeProxyHandler` - 25 edges
4. `CodeAgentRuntime` - 24 edges
5. `Changelog` - 22 edges
6. `tool()` - 19 edges
7. `TestTools` - 18 edges
8. `JSONSessionRepository` - 17 edges
9. `EventBus` - 15 edges
10. `escribir_archivo_local()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `TestDiagnoseRootCauseAndVersion` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestRuntimeRecoveryAndPauseSemantics` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_runtime_recovery.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestAgentStateMachineController` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_state_machine.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestRuntimeRecoveryAndPauseSemantics` --uses--> `State`  [INFERRED]
  tests/test_runtime_recovery.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestDiagnoseRootCauseAndVersion` --uses--> `AgentStateMachineController`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py

## Import Cycles
- None detected.

## Communities (71 total, 22 thin omitted)

### Community 0 - "session_manager.py"
Cohesion: 0.06
Nodes (14): ABC, BaseSessionRepository, create_new_session(), export_session_to_markdown(), init_sessions_dir(), JSONSessionRepository, load_session(), Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio). (+6 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.07
Nodes (17): _inc_metric(), LocalCodeProxyHandler, main(), _ps_file_dialog(), _ps_folder_dialog(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., _safe_print() (+9 more)

### Community 3 - "CodeAgentRuntime"
Cohesion: 0.13
Nodes (10): CodeAgentRuntime, Any, Motor de ejecución autónomo desacoplado para CodeAgent v6.1. Gestión semántica…, Obtiene la información de la tarea, su estado actual y el último checkpoint., Lista las tareas recientes guardadas en SQLite., Pausa una tarea activa sin marcarla como cancelada., Reanuda una tarea pausada desde su último checkpoint en SQLite., Cancela definitivamente una tarea. (+2 more)

### Community 4 - "main.py"
Cohesion: 0.21
Nodes (6): _construir_contexto_workspace(), get_herramientas(), Pipeline de agentes con smolagents de HuggingFace. El LLM usa CodeAgent para…, Convierte los nombres del UI en la lista de funciones @tool., Genera un bloque de contexto del workspace actual para inyectar en el…, TestMainPipeline

### Community 5 - "Changelog"
Cohesion: 0.20
Nodes (9): [4.2.0] - 2026-08-27, [6.0.0] - 2026-08-28, [6.10.0] - 2026-08-28, [6.4.0] - 2026-08-28, Added, Added, Added, Added (+1 more)

### Community 6 - "💻 CodeAgent (v6.11 Enterprise)"
Cohesion: 0.10
Nodes (19): Arquitectura, 🏗️ Arquitectura del Sistema (5 Capas Principales), Benchmarks (3 niveles), ✨ Características Principales (v3.0 Enterprise), 💻 CodeAgent (v6.11 Enterprise), 🚀 Instalación y Ejecución, Knowledge Graph, Opción 1: Arranque Rápido (Recomendado para Windows) (+11 more)

### Community 7 - "tool"
Cohesion: 0.11
Nodes (17): tool(), buscar_en_internet(), consultar_db(), git_add(), git_commit(), git_diff(), git_push(), git_status() (+9 more)

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - "AgentStateMachineController"
Cohesion: 0.05
Nodes (32): AgentStateMachineController, ComplexityRiskEvaluator, ExecutionLevel, _get_phase_cognitive_directive(), Any, Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Controlador determinista de estados, enrutador adaptativo y gestor de… (+24 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.12
Nodes (12): _detectar_raiz_proyecto(), get_active_workspace(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Devuelve el espacio de trabajo activo de forma thread-safe., Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido… (+4 more)

### Community 12 - "mis_agentes_inteligentes.main"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes.main, mis_agentes_inteligentes.main.get_herramientas, mis_agentes_inteligentes.main._construir_contexto_workspace, mis_agentes_inteligentes.main.ejecutar_agentes

### Community 13 - "orquestador_agente.py"
Cohesion: 0.24
Nodes (14): aplicar(), backup_archivos_trabajo(), diagnosticar(), gen_script(), generar_fix(), main(), probar(), Guarda backups de archivos que los benchmarks pueden modificar. (+6 more)

### Community 14 - "rag_tools.py"
Cohesion: 0.21
Nodes (9): _bm25_score(), indexar_directorio_local(), init_chroma(), preguntar_a_repositorio(), Calcula una puntuación BM25 léxica simplificada basada en frecuencia de…, Realiza una búsqueda semántica sobre los archivos previamente indexados con…, Inicializa la base de datos ChromaDB y el modelo de embeddings., Escanea todos los archivos de código en un directorio local y los indexa en… (+1 more)

### Community 15 - "CodeAgent"
Cohesion: 0.15
Nodes (13): CodeAgent, mis_agentes_inteligentes/main, main.get_herramientas, main._construir_contexto_workspace, main.ejecutar_agentes, mis_agentes_inteligentes/setup_db, setup_db.create_dummy_db, mis_agentes_inteligentes.app (+5 more)

### Community 16 - "Test-Driven Development"
Cohesion: 0.15
Nodes (10): Designing for Mockability, When to Mock, Anti-patterns, Rules of the loop, Seams — where tests go, Test-Driven Development, What a good test is, Bad Tests (+2 more)

### Community 17 - "orquestador_agente"
Cohesion: 0.17
Nodes (12): orquestador_agente.validar_sintaxis, orquestador_agente.aplicar, orquestador_agente.restaurar_agents, orquestador_agente.main, orquestador_agente, orquestador_agente.supervisor, orquestador_agente.backup_archivos_trabajo, orquestador_agente.restaurar_archivos_trabajo (+4 more)

### Community 18 - "TestTools"
Cohesion: 0.24
Nodes (7): editar_archivo_search_replace(), escribir_archivo_local(), Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para…, Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para…, IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.…, _verificar_sintaxis_post_edicion(), TestTools

### Community 19 - "mis_agentes_inteligentes/session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes/session_manager, session_manager.init_sessions_dir, session_manager.create_new_session, session_manager.list_sessions, session_manager.load_session, session_manager.save_session, session_manager.delete_session, session_manager.rename_session (+1 more)

### Community 20 - "mis_agentes_inteligentes.session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes.session_manager, mis_agentes_inteligentes.session_manager.init_sessions_dir, mis_agentes_inteligentes.session_manager.create_new_session, mis_agentes_inteligentes.session_manager.list_sessions, mis_agentes_inteligentes.session_manager.load_session, mis_agentes_inteligentes.session_manager.save_session, mis_agentes_inteligentes.session_manager.delete_session, mis_agentes_inteligentes.session_manager.rename_session (+1 more)

### Community 21 - "desktop_app.py"
Cohesion: 0.08
Nodes (22): check_ollama_running(), check_server_running(), DesktopIDEApi, launch_ollama_bg(), launch_server_bg(), main(), _ps_file_dialog(), _ps_folder_dialog() (+14 more)

### Community 22 - "BenchmarkMetricsCollector"
Cohesion: 0.13
Nodes (8): BenchmarkMetricsCollector, Any, Registra la ejecución real de una herramienta por el agente., Calcula los KPIs cuantitativos agregados con datos reales., Genera un reporte formateado en Markdown con los KPIs cuantitativos., Colector y repositorio persistente de métricas cuantitativas agénticas., Registra el resultado de un ciclo de ejecución de la Máquina de Estados., TestAgentStateMachineController

### Community 23 - "_make_github_request"
Cohesion: 0.18
Nodes (12): consultar_github(), leer_archivo_github(), leer_repositorio_github(), _make_github_request(), Helper centralizado para llamadas HTTP autenticadas a la API de GitHub., Usa esta herramienta cuando el usuario te proporcione un token de Github para…, Usa esta herramienta para analizar a fondo uno o VARIOS repositorios. Debes…, Lee el contenido de un archivo específico de un repositorio de GitHub. Pasa el… (+4 more)

### Community 24 - "mis_agentes_inteligentes/agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes/agents, agents.get_model, agents.load_subagents_from_disk, agents.get_available_agents, agents.route_prompt, agents.crear_agente

### Community 25 - "mis_agentes_inteligentes.agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes.agents, mis_agentes_inteligentes.agents.get_model, mis_agentes_inteligentes.agents.load_subagents_from_disk, mis_agentes_inteligentes.agents.get_available_agents, mis_agentes_inteligentes.agents.route_prompt, mis_agentes_inteligentes.agents.crear_agente

### Community 26 - "tools.py"
Cohesion: 0.16
Nodes (9): _atomic_write_file(), check_tool_permission(), clear_terminal_tasks_buffer(), PermissionLevel, Enum, Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, Niveles de autorización para la ejecución segura de herramientas agénticas., Valida si el permiso actual autoriza la ejecución de la herramienta. (+1 more)

### Community 28 - "ADR-001: Selección de smolagents como Motor ReAct"
Cohesion: 0.40
Nodes (4): ADR-001: Selección de smolagents como Motor ReAct, Consecuencias, Contexto, Decisión

### Community 29 - "ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo"
Cohesion: 0.40
Nodes (4): ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo, Consecuencias, Contexto, Decisión

### Community 30 - "ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM"
Cohesion: 0.40
Nodes (4): ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM, Consecuencias, Contexto, Decisión

### Community 31 - "ejecutar_comando_terminal"
Cohesion: 0.19
Nodes (6): ejecutar_comando_terminal(), is_command_approved(), is_sensitive_command(), pre_approve_command(), Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip…, TestTerminalHITLApproval

### Community 32 - "EventBus"
Cohesion: 0.16
Nodes (9): EventBus, get_event_bus(), Any, Bus de eventos persistente con patrón Observador (Event Sourcing)., Persiste el evento en SQLite y notifica a todos los suscriptores activos., Obtiene la corriente de eventos guardados para reconstruir el estado visual en…, get_db_manager(), Verifica la capacidad de autorecuperación TDD (FAIL -> DIAGNOSE -> REPLAN ->… (+1 more)

### Community 33 - "mis_agentes_inteligentes/rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/rag_tools, rag_tools.init_chroma, rag_tools.indexar_directorio_local, rag_tools.preguntar_a_repositorio

### Community 34 - "CodeAgentBenchmarkSuite"
Cohesion: 0.17
Nodes (7): CodeAgentBenchmarkSuite, Any, CodeAgent v4.2 Reproducible Benchmark Suite Suite estandarizada de 5 tareas…, Exporta el reporte de benchmark en formato Markdown en…, Ejecutor automatizado de la Suite de 5 Benchmarks Reales de Ingeniería., Ejecuta la suite completa de 5 tareas y compila el informe comparativo., TestCodeAgentBenchmarkSuite

### Community 45 - "[2.2.0] - 2026-07-25"
Cohesion: 0.50
Nodes (4): [2.2.0] - 2026-07-25, Added, Fixed, Refactored

### Community 46 - "🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)"
Cohesion: 0.50
Nodes (3): 📈 KPIs Globales Acumulados, 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise), 📊 Resultados por Tarea de Ingeniería

### Community 48 - "DatabaseManager"
Cohesion: 0.29
Nodes (4): Connection, DatabaseManager, Any, Gestor de almacenamiento persistente SQLite multihilo seguro para CodeAgent…

### Community 50 - "[2.3.0] - 2026-08-04"
Cohesion: 0.50
Nodes (4): [2.3.0] - 2026-08-04, Added, Performance, Refactored

### Community 51 - "[2.4.0] - 2026-08-26"
Cohesion: 0.50
Nodes (4): [2.4.0] - 2026-08-26, Added, Fixed, Refactored

### Community 53 - "[2.2.1] - 2026-07-26"
Cohesion: 0.67
Nodes (3): [2.2.1] - 2026-07-26, Added, Fixed

### Community 55 - "[2.5.0] - 2026-08-26"
Cohesion: 0.67
Nodes (3): [2.5.0] - 2026-08-26, Added, Fixed

### Community 57 - "mis_agentes_inteligentes.rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes.rag_tools, mis_agentes_inteligentes.rag_tools.init_chroma, mis_agentes_inteligentes.rag_tools.indexar_directorio_local, mis_agentes_inteligentes.rag_tools.preguntar_a_repositorio

### Community 58 - "[3.5.0] - 2026-08-27"
Cohesion: 0.67
Nodes (3): [3.5.0] - 2026-08-27, Added, Fixed

### Community 62 - "TestAgents"
Cohesion: 0.16
Nodes (11): crear_agente(), _detectar_modelo_local(), get_available_agents(), load_subagents_from_disk(), Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML…, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)., Enrutador automático mejorado con scoring ponderado., Detecta si el modelo es local (Ollama) basándose en el model_id. (+3 more)

### Community 69 - "app.py"
Cohesion: 0.13
Nodes (6): graphify, _guardar_sesion_actual(), Guarda los datos de la sesión activa en disco., Comprime texto y asegura la validez de los bloques de código markdown., _truncar_markdown(), TestRegressionSuite

### Community 71 - "ejecutar_agentes"
Cohesion: 0.21
Nodes (8): get_model(), Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., main(), print_banner(), ejecutar_agentes(), Pipeline principal usando smolagents. FIX: el historial ya no se manda como…, patch, TestIntegrationPipeline

## Knowledge Gaps
- **67 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `session_manager.py`, `EventBus`, `CodeAgentBenchmarkSuite`, `CodeAgentRuntime`, `TestVerifierEvidenceAndWorkspaceIsolation`, `TestRuntimeRecoveryAndPauseSemantics`, `BenchmarkMetricsCollector`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `CodeAgentRuntime` connect `CodeAgentRuntime` to `EventBus`, `LocalCodeProxyHandler`, `TestVerifierEvidenceAndWorkspaceIsolation`, `AgentStateMachineController`, `TestRuntimeAndStorage`, `DatabaseManager`, `TestRuntimeRecoveryAndPauseSemantics`, `database.py`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `ejecutar_agentes()` connect `ejecutar_agentes` to `main.py`, `TestAgents`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `AgentStateMachineController` (e.g. with `CodeAgentBenchmarkSuite` and `.__init__()`) actually correct?**
  _`AgentStateMachineController` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `DatabaseManager` (e.g. with `Event` and `EventBus`) actually correct?**
  _`DatabaseManager` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestE2ESystemSuite` and `TestLocalCodeServer`) actually correct?**
  _`LocalCodeProxyHandler` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `CodeAgentRuntime` (e.g. with `AgentStateMachineController` and `EventBus`) actually correct?**
  _`CodeAgentRuntime` has 11 INFERRED edges - model-reasoned connections that need verification._