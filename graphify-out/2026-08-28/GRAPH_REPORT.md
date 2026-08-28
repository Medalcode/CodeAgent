# Graph Report - CodeAgent  (2026-08-28)

## Corpus Check
- 66 files · ~42,135 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 688 nodes · 1036 edges · 47 communities (39 shown, 8 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 223 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `211bab43`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_manager.py
- LocalCodeProxyHandler
- TestRegressionSuite
- DatabaseManager
- main.py
- Changelog
- 💻 CodeAgent (v5.3 Enterprise)
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
- DesktopIDEApi
- BenchmarkMetricsCollector
- tools.py
- mis_agentes_inteligentes/agents
- mis_agentes_inteligentes.agents
- _atomic_write_file
- TestSmokeSystem
- ADR-001: Selección de smolagents como Motor ReAct
- ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo
- ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM
- TestSessionManager
- mis_agentes_inteligentes/main
- mis_agentes_inteligentes/rag_tools
- CodeAgentBenchmarkSuite
- graphify.js
- rules/graphify.md
- workflows/graphify.md
- config.py
- __init__.py
- start_hub.sh
- mis_agentes_inteligentes.rag_tools
- 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)

## God Nodes (most connected - your core abstractions)
1. `AgentStateMachineController` - 29 edges
2. `LocalCodeProxyHandler` - 24 edges
3. `DatabaseManager` - 21 edges
4. `tool()` - 19 edges
5. `CodeAgentRuntime` - 18 edges
6. `TestTools` - 18 edges
7. `JSONSessionRepository` - 17 edges
8. `escribir_archivo_local()` - 15 edges
9. `DesktopIDEApi` - 13 edges
10. `EventBus` - 13 edges

## Surprising Connections (you probably didn't know these)
- `TestDiagnoseRootCauseAndVersion` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestDiagnoseRootCauseAndVersion` --uses--> `AgentStateMachineController`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestAgentStateMachineController` --uses--> `BenchmarkMetricsCollector`  [INFERRED]
  tests/test_state_machine.py → mis_agentes_inteligentes/benchmark_metrics.py
- `TestStateCheckpointing` --uses--> `JSONSessionRepository`  [INFERRED]
  tests/test_state_checkpointing.py → mis_agentes_inteligentes/session_manager.py
- `TestTools` --uses--> `PermissionLevel`  [INFERRED]
  tests/test_tools.py → mis_agentes_inteligentes/tools.py

## Import Cycles
- None detected.

## Communities (47 total, 8 thin omitted)

### Community 0 - "session_manager.py"
Cohesion: 0.06
Nodes (17): ABC, _guardar_sesion_actual(), Guarda los datos de la sesión activa en disco., Comprime texto y asegura la validez de los bloques de código markdown., _truncar_markdown(), BaseSessionRepository, create_new_session(), export_session_to_markdown() (+9 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.07
Nodes (15): _inc_metric(), LocalCodeProxyHandler, main(), _ps_file_dialog(), _ps_folder_dialog(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., _safe_print() (+7 more)

### Community 2 - "TestRegressionSuite"
Cohesion: 0.20
Nodes (5): git_diff(), git_status(), Muestra el estado del repositorio Git (archivos modificados, untracked, etc).…, Muestra los cambios no commiteados en el repositorio. Args: ruta_repo: Ruta del…, TestRegressionSuite

### Community 3 - "DatabaseManager"
Cohesion: 0.06
Nodes (27): Connection, Event, EventBus, get_event_bus(), Any, Bus de eventos persistente con patrón Observador (Event Sourcing)., Registra un callback de escucha de eventos en tiempo real., Elimina un callback de escucha. (+19 more)

### Community 4 - "main.py"
Cohesion: 0.06
Nodes (26): graphify, crear_agente(), _detectar_modelo_local(), get_available_agents(), get_model(), load_subagents_from_disk(), Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML… (+18 more)

### Community 5 - "Changelog"
Cohesion: 0.06
Nodes (30): [2.2.0] - 2026-07-25, [2.2.1] - 2026-07-26, [2.3.0] - 2026-08-04, [2.4.0] - 2026-08-26, [2.5.0] - 2026-08-26, [3.5.0] - 2026-08-27, [4.0.0] - 2026-08-27, [4.2.0] - 2026-08-27 (+22 more)

### Community 6 - "💻 CodeAgent (v5.3 Enterprise)"
Cohesion: 0.10
Nodes (19): Arquitectura, 🏗️ Arquitectura del Sistema (5 Capas Principales), Benchmarks (3 niveles), ✨ Características Principales (v3.0 Enterprise), 💻 CodeAgent (v5.3 Enterprise), 🚀 Instalación y Ejecución, Knowledge Graph, Opción 1: Arranque Rápido (Recomendado para Windows) (+11 more)

### Community 7 - "tool"
Cohesion: 0.13
Nodes (13): tool(), buscar_en_internet(), consultar_db(), git_add(), git_commit(), git_push(), guardar_reporte(), Realiza una búsqueda en internet usando Google para obtener información… (+5 more)

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - "AgentStateMachineController"
Cohesion: 0.05
Nodes (28): AgentStateMachineController, ComplexityRiskEvaluator, ExecutionLevel, _get_phase_cognitive_directive(), Any, Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Persiste el estado activo de la Máquina de Estados en la sesión JSON. (+20 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.12
Nodes (12): _detectar_raiz_proyecto(), get_active_workspace(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Rastrea e informa la ejecución de herramientas al colector de métricas., Devuelve el espacio de trabajo activo de forma thread-safe., Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,… (+4 more)

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
Cohesion: 0.22
Nodes (9): CodeAgent, mis_agentes_inteligentes/setup_db, setup_db.create_dummy_db, mis_agentes_inteligentes.app, mis_agentes_inteligentes.app.get_sessions_list, mis_agentes_inteligentes.setup_db, mis_agentes_inteligentes.setup_db.create_dummy_db, mis_agentes_inteligentes/app (+1 more)

### Community 16 - "Test-Driven Development"
Cohesion: 0.15
Nodes (10): Designing for Mockability, When to Mock, Anti-patterns, Rules of the loop, Seams — where tests go, Test-Driven Development, What a good test is, Bad Tests (+2 more)

### Community 17 - "orquestador_agente"
Cohesion: 0.17
Nodes (12): orquestador_agente.validar_sintaxis, orquestador_agente.aplicar, orquestador_agente.restaurar_agents, orquestador_agente.main, orquestador_agente, orquestador_agente.supervisor, orquestador_agente.backup_archivos_trabajo, orquestador_agente.restaurar_archivos_trabajo (+4 more)

### Community 18 - "TestTools"
Cohesion: 0.16
Nodes (9): editar_archivo_search_replace(), ejecutar_comando_terminal(), escribir_archivo_local(), Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para…, Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para…, Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip…, IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.…, _verificar_sintaxis_post_edicion() (+1 more)

### Community 19 - "mis_agentes_inteligentes/session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes/session_manager, session_manager.init_sessions_dir, session_manager.create_new_session, session_manager.list_sessions, session_manager.load_session, session_manager.save_session, session_manager.delete_session, session_manager.rename_session (+1 more)

### Community 20 - "mis_agentes_inteligentes.session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes.session_manager, mis_agentes_inteligentes.session_manager.init_sessions_dir, mis_agentes_inteligentes.session_manager.create_new_session, mis_agentes_inteligentes.session_manager.list_sessions, mis_agentes_inteligentes.session_manager.load_session, mis_agentes_inteligentes.session_manager.save_session, mis_agentes_inteligentes.session_manager.delete_session, mis_agentes_inteligentes.session_manager.rename_session (+1 more)

### Community 21 - "DesktopIDEApi"
Cohesion: 0.08
Nodes (22): check_ollama_running(), check_server_running(), DesktopIDEApi, launch_ollama_bg(), launch_server_bg(), main(), _ps_file_dialog(), _ps_folder_dialog() (+14 more)

### Community 22 - "BenchmarkMetricsCollector"
Cohesion: 0.26
Nodes (7): BenchmarkMetricsCollector, Any, Registra la ejecución real de una herramienta por el agente., Calcula los KPIs cuantitativos agregados con datos reales., Genera un reporte formateado en Markdown con los KPIs cuantitativos., Colector y repositorio persistente de métricas cuantitativas agénticas., Registra el resultado de un ciclo de ejecución de la Máquina de Estados.

### Community 23 - "tools.py"
Cohesion: 0.21
Nodes (12): consultar_github(), leer_archivo_github(), leer_repositorio_github(), _make_github_request(), Helper centralizado para llamadas HTTP autenticadas a la API de GitHub., Usa esta herramienta cuando el usuario te proporcione un token de Github para…, Usa esta herramienta para analizar a fondo uno o VARIOS repositorios. Debes…, Lee el contenido de un archivo específico de un repositorio de GitHub. Pasa el… (+4 more)

### Community 24 - "mis_agentes_inteligentes/agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes/agents, agents.get_model, agents.load_subagents_from_disk, agents.get_available_agents, agents.route_prompt, agents.crear_agente

### Community 25 - "mis_agentes_inteligentes.agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes.agents, mis_agentes_inteligentes.agents.get_model, mis_agentes_inteligentes.agents.load_subagents_from_disk, mis_agentes_inteligentes.agents.get_available_agents, mis_agentes_inteligentes.agents.route_prompt, mis_agentes_inteligentes.agents.crear_agente

### Community 26 - "_atomic_write_file"
Cohesion: 0.15
Nodes (8): _atomic_write_file(), check_tool_permission(), PermissionLevel, Enum, Niveles de autorización para la ejecución segura de herramientas agénticas., Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, Valida si el permiso actual autoriza la ejecución de la herramienta., TestTechnicalQualityRefactor

### Community 28 - "ADR-001: Selección de smolagents como Motor ReAct"
Cohesion: 0.40
Nodes (4): ADR-001: Selección de smolagents como Motor ReAct, Consecuencias, Contexto, Decisión

### Community 29 - "ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo"
Cohesion: 0.40
Nodes (4): ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo, Consecuencias, Contexto, Decisión

### Community 30 - "ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM"
Cohesion: 0.40
Nodes (4): ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM, Consecuencias, Contexto, Decisión

### Community 32 - "mis_agentes_inteligentes/main"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/main, main.get_herramientas, main._construir_contexto_workspace, main.ejecutar_agentes

### Community 33 - "mis_agentes_inteligentes/rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/rag_tools, rag_tools.init_chroma, rag_tools.indexar_directorio_local, rag_tools.preguntar_a_repositorio

### Community 34 - "CodeAgentBenchmarkSuite"
Cohesion: 0.17
Nodes (7): CodeAgentBenchmarkSuite, Any, CodeAgent v4.2 Reproducible Benchmark Suite Suite estandarizada de 5 tareas…, Exporta el reporte de benchmark en formato Markdown en…, Ejecutor automatizado de la Suite de 5 Benchmarks Reales de Ingeniería., Ejecuta la suite completa de 5 tareas y compila el informe comparativo., TestCodeAgentBenchmarkSuite

### Community 45 - "mis_agentes_inteligentes.rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes.rag_tools, mis_agentes_inteligentes.rag_tools.init_chroma, mis_agentes_inteligentes.rag_tools.indexar_directorio_local, mis_agentes_inteligentes.rag_tools.preguntar_a_repositorio

### Community 46 - "🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)"
Cohesion: 0.50
Nodes (3): 📈 KPIs Globales Acumulados, 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise), 📊 Resultados por Tarea de Ingeniería

## Knowledge Gaps
- **56 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `session_manager.py`, `CodeAgentBenchmarkSuite`, `DatabaseManager`?**
  _High betweenness centrality (0.138) - this node is a cross-community bridge._
- **Why does `CodeAgentRuntime` connect `DatabaseManager` to `LocalCodeProxyHandler`, `AgentStateMachineController`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `set_active_workspace()` connect `LocalCodeProxyHandler` to `_detectar_raiz_proyecto`, `DesktopIDEApi`, `tools.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `AgentStateMachineController` (e.g. with `CodeAgentBenchmarkSuite` and `.__init__()`) actually correct?**
  _`AgentStateMachineController` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestE2ESystemSuite` and `TestLocalCodeServer`) actually correct?**
  _`LocalCodeProxyHandler` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `DatabaseManager` (e.g. with `Event` and `EventBus`) actually correct?**
  _`DatabaseManager` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `CodeAgentRuntime` (e.g. with `AgentStateMachineController` and `EventBus`) actually correct?**
  _`CodeAgentRuntime` has 5 INFERRED edges - model-reasoned connections that need verification._