# Graph Report - CodeAgent  (2026-08-27)

## Corpus Check
- 51 files · ~25,281 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 516 nodes · 715 edges · 44 communities (36 shown, 8 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 167 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6a70c5e7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_manager.py
- LocalCodeProxyHandler
- TestAgents
- TestLocalCodeServer
- main.py
- Changelog
- 💻 CodeAgent (v4.0 Enterprise)
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
- mis_agentes_inteligentes/main
- mis_agentes_inteligentes/rag_tools
- graphify.js
- rules/graphify.md
- workflows/graphify.md
- config.py
- __init__.py
- start_hub.sh

## God Nodes (most connected - your core abstractions)
1. `LocalCodeProxyHandler` - 20 edges
2. `tool()` - 19 edges
3. `TestTools` - 18 edges
4. `AgentStateMachineController` - 13 edges
5. `TestLocalCodeServer` - 13 edges
6. `TestAgentStateMachineController` - 12 edges
7. `JSONSessionRepository` - 11 edges
8. `escribir_archivo_local()` - 11 edges
9. `BenchmarkMetricsCollector` - 10 edges
10. `ejecutar_agentes()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `TestAgentStateMachineController` --uses--> `BenchmarkMetricsCollector`  [INFERRED]
  tests/test_state_machine.py → mis_agentes_inteligentes/benchmark_metrics.py
- `TestE2ESystemSuite` --uses--> `LocalCodeProxyHandler`  [INFERRED]
  tests/test_e2e_suite.py → mis_agentes_inteligentes/localcode_server.py
- `TestLocalCodeServer` --uses--> `LocalCodeProxyHandler`  [INFERRED]
  tests/test_localcode_server.py → mis_agentes_inteligentes/localcode_server.py
- `TestTools` --uses--> `PermissionLevel`  [INFERRED]
  tests/test_tools.py → mis_agentes_inteligentes/tools.py
- `TestAgentStateMachineController` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_state_machine.py → mis_agentes_inteligentes/agent_pipeline.py

## Import Cycles
- None detected.

## Communities (44 total, 8 thin omitted)

### Community 0 - "session_manager.py"
Cohesion: 0.07
Nodes (12): ABC, BaseSessionRepository, create_new_session(), export_session_to_markdown(), init_sessions_dir(), JSONSessionRepository, load_session(), Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio). (+4 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.17
Nodes (5): _inc_metric(), LocalCodeProxyHandler, Establece el directorio del espacio de trabajo activo de forma thread-safe para…, set_active_workspace(), TestWorkspaceIsolation

### Community 2 - "TestAgents"
Cohesion: 0.13
Nodes (13): crear_agente(), _detectar_modelo_local(), get_available_agents(), get_model(), load_subagents_from_disk(), Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML…, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos). (+5 more)

### Community 3 - "TestLocalCodeServer"
Cohesion: 0.14
Nodes (7): main(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., _safe_print(), ThreadedTCPServer, TestE2ESystemSuite, TestLocalCodeServer

### Community 4 - "main.py"
Cohesion: 0.07
Nodes (18): graphify, _guardar_sesion_actual(), Guarda los datos de la sesión activa en disco., Comprime texto y asegura la validez de los bloques de código markdown., _truncar_markdown(), main(), print_banner(), _construir_contexto_workspace() (+10 more)

### Community 5 - "Changelog"
Cohesion: 0.08
Nodes (24): [2.2.0] - 2026-07-25, [2.2.1] - 2026-07-26, [2.3.0] - 2026-08-04, [2.4.0] - 2026-08-26, [2.5.0] - 2026-08-26, [3.5.0] - 2026-08-27, [4.0.0] - 2026-08-27, Added (+16 more)

### Community 6 - "💻 CodeAgent (v4.0 Enterprise)"
Cohesion: 0.10
Nodes (19): Arquitectura, 🏗️ Arquitectura del Sistema (5 Capas Principales), Benchmarks (3 niveles), ✨ Características Principales (v3.0 Enterprise), 💻 CodeAgent (v4.0 Enterprise), 🚀 Instalación y Ejecución, Knowledge Graph, Opción 1: Arranque Rápido (Recomendado para Windows) (+11 more)

### Community 7 - "tool"
Cohesion: 0.12
Nodes (15): tool(), buscar_en_internet(), consultar_db(), git_commit(), git_diff(), git_push(), git_status(), guardar_reporte() (+7 more)

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - "AgentStateMachineController"
Cohesion: 0.08
Nodes (17): AgentStateMachineController, ExecutionLevel, Any, Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Alias de compatibilidad hacia atrás para la versión v3.0., Genera un plan de acción estructurado., Consulta el Grafo AST Graphify en busca de contexto estructural. (+9 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.14
Nodes (10): _detectar_raiz_proyecto(), get_active_workspace(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Devuelve el espacio de trabajo activo de forma thread-safe., Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido… (+2 more)

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
Nodes (13): CodeAgent, mis_agentes_inteligentes/setup_db, setup_db.create_dummy_db, mis_agentes_inteligentes.app, mis_agentes_inteligentes.app.get_sessions_list, mis_agentes_inteligentes.rag_tools, mis_agentes_inteligentes.rag_tools.init_chroma, mis_agentes_inteligentes.rag_tools.indexar_directorio_local (+5 more)

### Community 16 - "Test-Driven Development"
Cohesion: 0.15
Nodes (10): Designing for Mockability, When to Mock, Anti-patterns, Rules of the loop, Seams — where tests go, Test-Driven Development, What a good test is, Bad Tests (+2 more)

### Community 17 - "orquestador_agente"
Cohesion: 0.17
Nodes (12): orquestador_agente.validar_sintaxis, orquestador_agente.aplicar, orquestador_agente.restaurar_agents, orquestador_agente.main, orquestador_agente, orquestador_agente.supervisor, orquestador_agente.backup_archivos_trabajo, orquestador_agente.restaurar_archivos_trabajo (+4 more)

### Community 18 - "TestTools"
Cohesion: 0.23
Nodes (7): editar_archivo_search_replace(), escribir_archivo_local(), Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para…, Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para…, IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.…, _verificar_sintaxis_post_edicion(), TestTools

### Community 19 - "mis_agentes_inteligentes/session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes/session_manager, session_manager.init_sessions_dir, session_manager.create_new_session, session_manager.list_sessions, session_manager.load_session, session_manager.save_session, session_manager.delete_session, session_manager.rename_session (+1 more)

### Community 20 - "mis_agentes_inteligentes.session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes.session_manager, mis_agentes_inteligentes.session_manager.init_sessions_dir, mis_agentes_inteligentes.session_manager.create_new_session, mis_agentes_inteligentes.session_manager.list_sessions, mis_agentes_inteligentes.session_manager.load_session, mis_agentes_inteligentes.session_manager.save_session, mis_agentes_inteligentes.session_manager.delete_session, mis_agentes_inteligentes.session_manager.rename_session (+1 more)

### Community 21 - "desktop_app.py"
Cohesion: 0.25
Nodes (10): check_ollama_running(), check_server_running(), launch_ollama_bg(), launch_server_bg(), main(), CodeAgent Desktop Runner (v3.5) Lanza CodeAgent y Ollama automáticamente en una…, Verifica si el servicio Ollama está activo en el puerto 11434., Inicia el servicio Ollama ('ollama serve') en segundo plano si no está activo. (+2 more)

### Community 22 - "BenchmarkMetricsCollector"
Cohesion: 0.35
Nodes (5): BenchmarkMetricsCollector, Any, Calcula los KPIs cuantitativos agregados., Colector y repositorio persistente de métricas cuantitativas agénticas., Registra el resultado de un ciclo de ejecución de la Máquina de Estados.

### Community 23 - "_make_github_request"
Cohesion: 0.18
Nodes (12): consultar_github(), leer_archivo_github(), leer_repositorio_github(), _make_github_request(), Usa esta herramienta cuando el usuario te proporcione un token de Github para…, Usa esta herramienta para analizar a fondo uno o VARIOS repositorios. Debes…, Lee el contenido de un archivo específico de un repositorio de GitHub. Pasa el…, Helper centralizado para llamadas HTTP autenticadas a la API de GitHub. (+4 more)

### Community 24 - "mis_agentes_inteligentes/agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes/agents, agents.get_model, agents.load_subagents_from_disk, agents.get_available_agents, agents.route_prompt, agents.crear_agente

### Community 25 - "mis_agentes_inteligentes.agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes.agents, mis_agentes_inteligentes.agents.get_model, mis_agentes_inteligentes.agents.load_subagents_from_disk, mis_agentes_inteligentes.agents.get_available_agents, mis_agentes_inteligentes.agents.route_prompt, mis_agentes_inteligentes.agents.crear_agente

### Community 26 - "tools.py"
Cohesion: 0.28
Nodes (7): check_tool_permission(), git_add(), PermissionLevel, Enum, Niveles de autorización para la ejecución segura de herramientas agénticas., Valida si el permiso actual autoriza la ejecución de la herramienta., Añade archivos al staging area de Git. Pasa los archivos separados por…

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

## Knowledge Gaps
- **51 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+46 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `set_active_workspace()` connect `LocalCodeProxyHandler` to `tools.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `ejecutar_agentes()` connect `main.py` to `TestAgents`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `LocalCodeProxyHandler` connect `LocalCodeProxyHandler` to `TestLocalCodeServer`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestE2ESystemSuite` and `TestLocalCodeServer`) actually correct?**
  _`LocalCodeProxyHandler` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `mis_agentes_inteligentes/tools` (e.g. with `CodeAgent` and `tools.consultar_db`) actually correct?**
  _`mis_agentes_inteligentes/tools` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `mis_agentes_inteligentes.tools` (e.g. with `CodeAgent` and `mis_agentes_inteligentes.tools.consultar_db`) actually correct?**
  _`mis_agentes_inteligentes.tools` has 18 INFERRED edges - model-reasoned connections that need verification._
- **What connects `start_hub.sh script`, `graphify`, `What a good test is` to the rest of the system?**
  _51 weakly-connected nodes found - possible documentation gaps or missing edges._