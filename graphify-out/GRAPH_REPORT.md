# Graph Report - CodeAgent  (2026-08-28)

## Corpus Check
- 74 files · ~59,323 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 859 nodes · 1262 edges · 83 communities (61 shown, 22 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 262 edges (avg confidence: 0.82)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9a12ae36`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_manager.py
- LocalCodeProxyHandler
- set_active_workspace
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
- Requirements
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
- _atomic_write_file
- TestSmokeSystem
- ADR-001: Selección de smolagents como Motor ReAct
- ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo
- ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM
- tools.py
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
- TestAgents
- DatabaseManager
- Correctness Properties
- [2.3.0] - 2026-08-04
- [2.4.0] - 2026-08-26
- TestRuntimeRecoveryAndPauseSemantics
- [2.2.1] - 2026-07-26
- database.py
- [2.5.0] - 2026-08-26
- Design Document: CodeAgent SDD Contract
- Components and Interfaces
- [3.5.0] - 2026-08-27
- [4.0.0] - 2026-08-27
- [4.3.0] - 2026-08-27
- [5.3.0] - 2026-08-27
- TestTDDRecoveryLoop
- Workflow State Machines
- [6.5.0] - 2026-08-28
- [6.6.0] - 2026-08-28
- [6.7.0] - 2026-08-28
- [6.8.0] - 2026-08-28
- [6.9.0] - 2026-08-28
- Algorithmic Pseudocode
- Error Handling
- Implementation Plan: CodeAgent SDD Contract
- Data Models
- Example Usage
- .publish
- TestVerifierEvidenceAndWorkspaceIsolation
- mis_agentes_inteligentes/main
- Dependencies
- [6.11.0] - 2026-08-28
- [6.2.0] - 2026-08-28
- Testing Strategy
- Security Considerations
- [6.3.0] - 2026-08-28

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

## Communities (83 total, 22 thin omitted)

### Community 0 - "session_manager.py"
Cohesion: 0.06
Nodes (14): ABC, BaseSessionRepository, create_new_session(), export_session_to_markdown(), init_sessions_dir(), JSONSessionRepository, load_session(), Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio). (+6 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.08
Nodes (14): _inc_metric(), LocalCodeProxyHandler, main(), _ps_file_dialog(), _ps_folder_dialog(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., _safe_print() (+6 more)

### Community 2 - "set_active_workspace"
Cohesion: 0.22
Nodes (5): get_active_workspace(), Establece el directorio del espacio de trabajo activo de forma thread-safe para…, Devuelve el espacio de trabajo activo de forma thread-safe., set_active_workspace(), TestWorkspaceIsolation

### Community 3 - "CodeAgentRuntime"
Cohesion: 0.13
Nodes (10): CodeAgentRuntime, Any, Motor de ejecución autónomo desacoplado para CodeAgent v6.1. Gestión semántica…, Obtiene la información de la tarea, su estado actual y el último checkpoint., Lista las tareas recientes guardadas en SQLite., Pausa una tarea activa sin marcarla como cancelada., Reanuda una tarea pausada desde su último checkpoint en SQLite., Cancela definitivamente una tarea. (+2 more)

### Community 4 - "main.py"
Cohesion: 0.05
Nodes (27): graphify, _guardar_sesion_actual(), Guarda los datos de la sesión activa en disco., Comprime texto y asegura la validez de los bloques de código markdown., _truncar_markdown(), main(), print_banner(), _construir_contexto_workspace() (+19 more)

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
Nodes (32): AgentStateMachineController, ComplexityRiskEvaluator, ExecutionLevel, _get_phase_cognitive_directive(), Any, Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Evaluador determinista de complejidad, alcance e impacto en workspace. (+24 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.15
Nodes (10): _detectar_raiz_proyecto(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido…, Lee el contenido de un archivo local en tu disco duro para poder analizar su…, Rastrea e informa la ejecución de herramientas al colector de métricas. (+2 more)

### Community 12 - "mis_agentes_inteligentes.main"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes.main, mis_agentes_inteligentes.main.get_herramientas, mis_agentes_inteligentes.main._construir_contexto_workspace, mis_agentes_inteligentes.main.ejecutar_agentes

### Community 13 - "orquestador_agente.py"
Cohesion: 0.24
Nodes (14): aplicar(), backup_archivos_trabajo(), diagnosticar(), gen_script(), generar_fix(), main(), probar(), Guarda backups de archivos que los benchmarks pueden modificar. (+6 more)

### Community 14 - "Requirements"
Cohesion: 0.07
Nodes (28): Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria (+20 more)

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
Cohesion: 0.15
Nodes (9): editar_archivo_search_replace(), ejecutar_comando_terminal(), escribir_archivo_local(), Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para…, Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para…, Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip…, IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.…, _verificar_sintaxis_post_edicion() (+1 more)

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

### Community 26 - "_atomic_write_file"
Cohesion: 0.16
Nodes (8): _atomic_write_file(), check_tool_permission(), PermissionLevel, Enum, Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, Niveles de autorización para la ejecución segura de herramientas agénticas., Valida si el permiso actual autoriza la ejecución de la herramienta., TestTechnicalQualityRefactor

### Community 28 - "ADR-001: Selección de smolagents como Motor ReAct"
Cohesion: 0.40
Nodes (4): ADR-001: Selección de smolagents como Motor ReAct, Consecuencias, Contexto, Decisión

### Community 29 - "ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo"
Cohesion: 0.40
Nodes (4): ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo, Consecuencias, Contexto, Decisión

### Community 30 - "ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM"
Cohesion: 0.40
Nodes (4): ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM, Consecuencias, Contexto, Decisión

### Community 31 - "tools.py"
Cohesion: 0.25
Nodes (5): clear_terminal_tasks_buffer(), is_command_approved(), is_sensitive_command(), pre_approve_command(), TestTerminalHITLApproval

### Community 32 - "EventBus"
Cohesion: 0.15
Nodes (7): EventBus, get_event_bus(), Bus de eventos persistente con patrón Observador (Event Sourcing)., Registra un callback de escucha de eventos en tiempo real., Elimina un callback de escucha., get_db_manager(), TestRuntimeAndStorage

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

### Community 47 - "TestAgents"
Cohesion: 0.13
Nodes (13): crear_agente(), _detectar_modelo_local(), get_available_agents(), get_model(), load_subagents_from_disk(), Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML…, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos). (+5 more)

### Community 48 - "DatabaseManager"
Cohesion: 0.29
Nodes (4): Connection, DatabaseManager, Any, Gestor de almacenamiento persistente SQLite multihilo seguro para CodeAgent…

### Community 49 - "Correctness Properties"
Cohesion: 0.22
Nodes (9): Correctness Properties, Property 1: Task Classification Uniqueness, Property 2: CHAT Task Isolation, Property 3: ACTION Task Bounded Execution, Property 4: FEATURE Task Workflow Compliance, Property 5: UI Instance Uniqueness, Property 6: Evidence-Based Diagnosis, Property 7: Verification State Exhaustiveness (+1 more)

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

### Community 56 - "Design Document: CodeAgent SDD Contract"
Cohesion: 0.25
Nodes (7): Architecture, Component Responsibilities, Design Document: CodeAgent SDD Contract, Optimization Strategies, Overview, Performance Considerations, Performance Requirements

### Community 57 - "Components and Interfaces"
Cohesion: 0.25
Nodes (8): Components and Interfaces, Evidence Logger Interface, Replanner Interface, Task Contract Interface, Task Router Interface, Tool Policy Enforcer Interface, UI Manager Interface, Verification Engine Interface

### Community 58 - "[3.5.0] - 2026-08-27"
Cohesion: 0.67
Nodes (3): [3.5.0] - 2026-08-27, Added, Fixed

### Community 63 - "Workflow State Machines"
Cohesion: 0.29
Nodes (7): ACTION Task State Machine, CHAT Task State Machine, FEATURE Task State Machine, High-Level Design, RECOVERY Task State Machine, Task Classification System, Workflow State Machines

### Community 69 - "Algorithmic Pseudocode"
Cohesion: 0.33
Nodes (6): Algorithmic Pseudocode, Main Task Execution Algorithm, Task Classification Algorithm, Tool Policy Enforcement Algorithm, UI Manager Algorithm, Verification Algorithm

### Community 70 - "Error Handling"
Cohesion: 0.33
Nodes (6): Error Handling, Error Scenario 1: Classification Ambiguity, Error Scenario 2: UI Instance Limit Exceeded, Error Scenario 3: Evidence Not Available for Diagnosis, Error Scenario 4: Maximum Iterations Exceeded, Error Scenario 5: Tool Policy Violation

### Community 71 - "Implementation Plan: CodeAgent SDD Contract"
Cohesion: 0.33
Nodes (5): Implementation Plan: CodeAgent SDD Contract, Notes, Overview, Task Dependency Graph, Tasks

### Community 72 - "Data Models"
Cohesion: 0.40
Nodes (5): Data Models, Diagnosis Data Model, Plan Data Model, Task Data Model, Verification Criterion Data Model

### Community 73 - "Example Usage"
Cohesion: 0.40
Nodes (5): Example Usage, Feature Task Execution Example, Task Classification Example, Tool Policy Enforcement Example, UI Management Example

### Community 74 - ".publish"
Cohesion: 0.40
Nodes (3): Any, Persiste el evento en SQLite y notifica a todos los suscriptores activos., Obtiene la corriente de eventos guardados para reconstruir el estado visual en…

### Community 76 - "mis_agentes_inteligentes/main"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/main, main.get_herramientas, main._construir_contexto_workspace, main.ejecutar_agentes

### Community 77 - "Dependencies"
Cohesion: 0.50
Nodes (4): Dependencies, External Dependencies, Internal Dependencies, Version Compatibility

### Community 80 - "Testing Strategy"
Cohesion: 0.50
Nodes (4): Integration Testing Approach, Property-Based Testing Approach, Testing Strategy, Unit Testing Approach

### Community 81 - "Security Considerations"
Cohesion: 0.50
Nodes (4): Security Considerations, Security Controls, Security Requirements, Threat Model

## Knowledge Gaps
- **136 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+131 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `session_manager.py`, `CodeAgentBenchmarkSuite`, `CodeAgentRuntime`, `TestVerifierEvidenceAndWorkspaceIsolation`, `TestRuntimeRecoveryAndPauseSemantics`, `BenchmarkMetricsCollector`, `TestTDDRecoveryLoop`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `CodeAgentRuntime` connect `CodeAgentRuntime` to `EventBus`, `LocalCodeProxyHandler`, `AgentStateMachineController`, `TestVerifierEvidenceAndWorkspaceIsolation`, `DatabaseManager`, `TestRuntimeRecoveryAndPauseSemantics`, `database.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `ejecutar_agentes()` connect `main.py` to `TestAgents`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `AgentStateMachineController` (e.g. with `CodeAgentBenchmarkSuite` and `.__init__()`) actually correct?**
  _`AgentStateMachineController` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `DatabaseManager` (e.g. with `Event` and `EventBus`) actually correct?**
  _`DatabaseManager` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestE2ESystemSuite` and `TestLocalCodeServer`) actually correct?**
  _`LocalCodeProxyHandler` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `CodeAgentRuntime` (e.g. with `AgentStateMachineController` and `EventBus`) actually correct?**
  _`CodeAgentRuntime` has 11 INFERRED edges - model-reasoned connections that need verification._