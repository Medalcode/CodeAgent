# Graph Report - CodeAgent  (2026-08-30)

## Corpus Check
- 149 files · ~80,383 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1907 nodes · 2666 edges · 159 communities (128 shown, 31 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 322 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1f1ac7c3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Canonical Architecture Analysis — CodeAgent v6.1
- LocalCodeProxyHandler
- An�lisis de Violaciones del SDD Contract System
- .get_task
- Canonical Enforcement Audit (Phase C2.5)
- Changelog
- 💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated)
- tools.py
- mis_agentes_inteligentes/tools
- mis_agentes_inteligentes.tools
- AgentStateMachineController
- _detectar_raiz_proyecto
- Deep Architecture & Complexity Weight Audit — CodeAgent v6.1 (SDD Certified)
- orquestador_agente.py
- Requirements
- CodeAgent
- Test-Driven Development
- orquestador_agente
- TestTools
- mis_agentes_inteligentes/session_manager
- mis_agentes_inteligentes.session_manager
- desktop_app.py
- .publish
- consultar_github
- mis_agentes_inteligentes/agents
- mis_agentes_inteligentes.agents
- TestSmokeSystem
- ADR-001: Selección de smolagents como Motor ReAct
- ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo
- ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM
- ejecutar_comando_terminal
- get_model
- mis_agentes_inteligentes/rag_tools
- TestSDDConformance
- graphify.js
- rules/graphify.md
- workflows/graphify.md
- __init__.py
- start_hub.sh
- [2.2.0] - 2026-07-25
- 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)
- TaskContract
- ._get_connection
- Correctness Properties
- [2.3.0] - 2026-08-04
- [2.4.0] - 2026-08-26
- INV-001 — Pipeline Authority
- [2.2.1] - 2026-07-26
- event_bus.py
- [2.5.0] - 2026-08-26
- Design Document: CodeAgent SDD Contract
- Components and Interfaces
- [3.5.0] - 2026-08-27
- [4.0.0] - 2026-08-27
- [4.3.0] - 2026-08-27
- [5.3.0] - 2026-08-27
- SDDIntegrator
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
- EvidenceLogger
- TestSSEEndpoint
- Dependencies
- [6.11.0] - 2026-08-28
- [6.2.0] - 2026-08-28
- Testing Strategy
- Security Considerations
- INV-002 — TaskContract Authority
- Diagnosis
- Audit Results by Requirement
- UIManager
- integrator.py
- TaskRouter
- ToolType
- agent_pipeline.py
- test_e2e_real_desktop_lifecycle.py
- tool
- DesktopIDEApi
- INV-003 — Cross-Task Isolation
- check_ollama_running
- INV-004 — Intent Preservation
- TestDesktopPipelineVisualization
- Repository Hygiene Report — Phase C1 (Safe Repository Hygiene)
- Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`)
- BenchmarkMetricsCollector
- Change Impact Analysis — SDD Governance Telemetry Endpoint
- Event
- INV-005 — Failure Containment
- TestRegressionSuite
- SPEC-009 — SDD Governance Telemetry Endpoint
- ejecutar_agentes
- SPEC-010 — Dynamic Feature Governance Automation
- Change Impact Analysis — Feature Governance Automation
- version.py
- Feature Runtime Evidence — SPEC-009
- INV-006 — Tool Isolation
- INV-007 — Conditional Verification
- INV-008 — Desktop Lifecycle Safety
- SPEC-011 — Real-Time Pipeline State & Event Streaming (SSE)
- Feature Runtime Evidence — SPEC-010
- Change Impact Analysis — Real-Time Pipeline State & Event Streaming (SSE)
- SDD Change Impact Analysis Declaration
- SDD Certification Report — Release v5.0.0
- SDD Certification Report — Release [vX.Y.Z]
- TestRuntimeRecoveryAndPauseSemantics
- Runtime Audit Evidence — Release v5.0.0
- Certification Environment Metadata — Release v5.0.0
- SDD Audits & Certifications Registry
- SDD Change Impact Analysis Framework
- SDD Specifications & Invariant Hierarchy
- SDD Bi-Directional Traceability Matrix
- TestPytestVerifierResolution
- TestSessionManager
- SPEC-009/README.md
- sdd_check.py
- Feature Runtime Evidence — SPEC-011
- preguntar_a_repositorio
- Migration Report: Legacy Orchestrator Verification (`orquestador_agente.py`)
- GraphContextEngine
- SPEC-011/README.md
- Migration Report: RAG Legacy Migration (`rag_tools.py` → `graph_context.py`)
- Change Impact Analysis — AST Subgraph Context Retrieval & Impact Engine (SPEC-013)
- SPEC-012 — Desktop Real-Time Pipeline EventSource Visualization
- Change Impact Analysis — Desktop Real-Time Pipeline EventSource Visualization (SPEC-012)
- mis_agentes_inteligentes.rag_tools
- Feature Runtime Evidence — SPEC-012
- SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG)
- Feature Runtime Evidence — SPEC-013
- Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`)
- get_event_bus
- SPEC-012/README.md
- Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView)
- set_active_workspace
- SPEC-013/README.md
- JSONSessionRepository
- session_manager.py
- .to_dict
- BaseSessionRepository
- TestDiagnoseRootCauseAndVersion
- Task Contract Compatibility Matrix
- TestStateCheckpointing
- DatabaseManager
- .open_folder_dialog
- TestQAEdgeCasesAndNegativeScenarios
- .open_file_dialog
- [6.3.0] - 2026-08-28

## God Nodes (most connected - your core abstractions)
1. `AgentStateMachineController` - 44 edges
2. `LocalCodeProxyHandler` - 38 edges
3. `SDDIntegrator` - 32 edges
4. `TestSDDConformance` - 31 edges
5. `DatabaseManager` - 27 edges
6. `TaskRouter` - 25 edges
7. `ExecutionLevel` - 24 edges
8. `CodeAgentRuntime` - 24 edges
9. `Changelog` - 22 edges
10. `EventBus` - 21 edges

## Surprising Connections (you probably didn't know these)
- `ExecutionLevel` --uses--> `TaskRouter`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_router.py
- `ExecutionLevel` --uses--> `TaskType`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_types.py
- `TestDiagnoseRootCauseAndVersion` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestFeedbackLoopAndToolEvents` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_feedback_loop.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestRuntimeRecoveryAndPauseSemantics` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_runtime_recovery.py → mis_agentes_inteligentes/agent_pipeline.py

## Import Cycles
- None detected.

## Communities (159 total, 31 thin omitted)

### Community 0 - "Canonical Architecture Analysis — CodeAgent v6.1"
Cohesion: 0.06
Nodes (30): Análisis Comparativo, Análisis de Mecanismos Actuales, Análisis de `sdd_contract/integrator.py`, Arquitectura Objetivo de Persistencia, Canonical Architecture Analysis — CodeAgent v6.1, Canonical Component Matrix, Clasificación de Interfaces, Components to Archive (+22 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.05
Nodes (27): Módulo de Configuración Centralizado para CodeAgent Define variables de…, _get_process_creation_time(), get_sdd_health_dict(), _inc_metric(), _is_parent_alive(), LocalCodeProxyHandler, main(), _ps_file_dialog() (+19 more)

### Community 2 - "An�lisis de Violaciones del SDD Contract System"
Cohesion: 0.05
Nodes (36): 1.1 Clasificaci�n Incorrecta (Requirement 1), 1.2 Fallback a LEVEL_3_FEATURE (Requirement 1), 1.3?? CHAT Fast Path (Requirement 2), 1.4 Verificaci�n ejecutada para CHAT (Requirement 2), 1.5 Replanning ejecutado para CHAT (Requirement 2), 2.1 Verificaci�n ejecutada para ACTION sin solicitud expl�cita (Requirement 3), 2.2 Ejecuci�n repetida del programa (Requirement 3), 2.3 Ruff FAIL hace fallar ACTION aunque no sea parte del contrato (Requirement 3) (+28 more)

### Community 3 - ".get_task"
Cohesion: 0.15
Nodes (6): Any, Obtiene la información de la tarea, su estado actual y el último checkpoint., Lista las tareas recientes guardadas en SQLite., Pausa una tarea activa sin marcarla como cancelada., Reanuda una tarea pausada desde su último checkpoint en SQLite., Obtiene la lista de eventos desde un determinado ID.

### Community 4 - "Canonical Enforcement Audit (Phase C2.5)"
Cohesion: 0.08
Nodes (24): Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Canonical Decisions Matrix, Canonical Enforcement Audit (Phase C2.5), Canonicalization Drift Findings (+16 more)

### Community 5 - "Changelog"
Cohesion: 0.20
Nodes (9): [4.2.0] - 2026-08-27, [6.0.0] - 2026-08-28, [6.10.0] - 2026-08-28, [6.4.0] - 2026-08-28, Added, Added, Added, Added (+1 more)

### Community 6 - "💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated)"
Cohesion: 0.11
Nodes (17): 🏗️ Arquitectura del Sistema (5 Capas Principales & Gobernanza SDD), 📐 Auditorías y Migraciones Arquitectónicas (Phases A, B, C1 & C2), ✨ Características Principales, CLI de Verificación SDD (`scripts/sdd_check.py`), 💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated), 🚀 Informes de Migración Canónica (Phase C2), 🚀 Instalación y Ejecución, 🌐 Knowledge Graph (`graphify-out/`) (+9 more)

### Community 7 - "tools.py"
Cohesion: 0.17
Nodes (8): _atomic_write_file(), check_tool_permission(), PermissionLevel, Enum, Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, Niveles de autorización para la ejecución segura de herramientas agénticas., Valida si el permiso actual autoriza la ejecución de la herramienta., TestTechnicalQualityRefactor

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - "AgentStateMachineController"
Cohesion: 0.09
Nodes (18): AgentStateMachineController, Any, Controlador determinista de estados, enrutador adaptativo y gestor de…, Determina el Nivel de Ejecución óptimo usando la evaluación de complejidad y…, Persiste el estado activo de la Máquina de Estados en la sesión JSON., Ejecuta el ciclo agéntico mediante la Máquina de Estados Determinista., Alias de compatibilidad hacia atrás para la versión v3.0., Reanuda la ejecución desde una sesión JSON o checkpoint de SQLite. (+10 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.15
Nodes (10): _detectar_raiz_proyecto(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido…, Lee el contenido de un archivo local en tu disco duro para poder analizar su…, Rastrea e informa la ejecución de herramientas al colector de métricas. (+2 more)

### Community 12 - "Deep Architecture & Complexity Weight Audit — CodeAgent v6.1 (SDD Certified)"
Cohesion: 0.10
Nodes (20): 1. `mis_agentes_inteligentes/agent_pipeline.py`, 2. `mis_agentes_inteligentes/localcode_server.py`, 3. `mis_agentes_inteligentes/tools.py`, Accidental Complexity, Análisis Detallado de Responsabilidades por Módulo, Candidate Components for Simplification, Current Architecture Map, Deep Architecture & Complexity Weight Audit — CodeAgent v6.1 (SDD Certified) (+12 more)

### Community 13 - "orquestador_agente.py"
Cohesion: 0.22
Nodes (15): aplicar(), backup_archivos_trabajo(), diagnosticar(), gen_script(), generar_fix(), main(), probar(), Supervisor local que consulta el endpoint v1/chat/completions de Ollama en… (+7 more)

### Community 14 - "Requirements"
Cohesion: 0.07
Nodes (28): Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria (+20 more)

### Community 15 - "CodeAgent"
Cohesion: 0.12
Nodes (17): CodeAgent, mis_agentes_inteligentes/main, main.get_herramientas, main._construir_contexto_workspace, main.ejecutar_agentes, mis_agentes_inteligentes/setup_db, setup_db.create_dummy_db, mis_agentes_inteligentes.app (+9 more)

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
Cohesion: 0.15
Nodes (19): find_free_port(), get_process_creation_time(), is_backend_compatible(), launch_ollama_bg(), launch_server_bg(), main(), CodeAgent Desktop Runner (v3.5) Lanza CodeAgent y Ollama automáticamente en una…, Verifica si en la URL dada responde un backend de CodeAgent retornando su… (+11 more)

### Community 22 - ".publish"
Cohesion: 0.40
Nodes (3): Any, Persiste el evento en SQLite y notifica a todos los suscriptores activos., Obtiene la corriente de eventos guardados para reconstruir el estado visual en…

### Community 23 - "consultar_github"
Cohesion: 0.20
Nodes (12): consultar_github(), leer_archivo_github(), leer_repositorio_github(), _make_github_request(), Helper centralizado para llamadas HTTP autenticadas a la API de GitHub., Usa esta herramienta cuando el usuario te proporcione un token de Github para…, Usa esta herramienta para analizar a fondo uno o VARIOS repositorios. Debes…, Lee el contenido de un archivo específico de un repositorio de GitHub. Pasa el… (+4 more)

### Community 24 - "mis_agentes_inteligentes/agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes/agents, agents.get_model, agents.load_subagents_from_disk, agents.get_available_agents, agents.route_prompt, agents.crear_agente

### Community 25 - "mis_agentes_inteligentes.agents"
Cohesion: 0.33
Nodes (6): mis_agentes_inteligentes.agents, mis_agentes_inteligentes.agents.get_model, mis_agentes_inteligentes.agents.load_subagents_from_disk, mis_agentes_inteligentes.agents.get_available_agents, mis_agentes_inteligentes.agents.route_prompt, mis_agentes_inteligentes.agents.crear_agente

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
Cohesion: 0.18
Nodes (6): ejecutar_comando_terminal(), is_command_approved(), is_sensitive_command(), pre_approve_command(), Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip…, TestTerminalHITLApproval

### Community 32 - "get_model"
Cohesion: 0.08
Nodes (19): get_model(), Instancia dinámicamente el modelo LiteLLMModel asegurando MODO LOCAL-ONLY…, patch, TEST 15 (No Exfiltración): Garantiza que el endpoint LLM resuelto apunta…, TEST 1: El proveedor predeterminado debe ser 'Ollama (Local)'., TEST 2: El modelo predeterminado debe ser 'qwen2.5-coder:14b'., TEST 3: La instanciación predeterminada de get_model() no requiere…, TEST 4: Un proveedor explícito 'OpenAI' debe ser RECHAZADO con ValueError. (+11 more)

### Community 33 - "mis_agentes_inteligentes/rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/rag_tools, rag_tools.init_chroma, rag_tools.indexar_directorio_local, rag_tools.preguntar_a_repositorio

### Community 34 - "TestSDDConformance"
Cohesion: 0.10
Nodes (4): ActionTaskContract, Contract for ACTION tasks - minimal tools, single operation., Garantiza que agent_pipeline y mis_agentes_inteligentes.agent_pipeline son el…, TestSDDConformance

### Community 45 - "[2.2.0] - 2026-07-25"
Cohesion: 0.50
Nodes (4): [2.2.0] - 2026-07-25, Added, Fixed, Refactored

### Community 46 - "🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)"
Cohesion: 0.50
Nodes (3): 📈 KPIs Globales Acumulados, 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise), 📊 Resultados por Tarea de Ingeniería

### Community 47 - "TaskContract"
Cohesion: 0.07
Nodes (18): Get the appropriate contract for a task type., ChatTaskContract, ABC, Task Contract implementations for SDD. Enforces behavioral boundaries per task…, Base interface for all task contracts., Contract for RECOVERY tasks - state restoration., Return True if verification is allowed for this task., Return True if replanning is allowed for this task. (+10 more)

### Community 49 - "Correctness Properties"
Cohesion: 0.22
Nodes (9): Correctness Properties, Property 1: Task Classification Uniqueness, Property 2: CHAT Task Isolation, Property 3: ACTION Task Bounded Execution, Property 4: FEATURE Task Workflow Compliance, Property 5: UI Instance Uniqueness, Property 6: Evidence-Based Diagnosis, Property 7: Verification State Exhaustiveness (+1 more)

### Community 50 - "[2.3.0] - 2026-08-04"
Cohesion: 0.50
Nodes (4): [2.3.0] - 2026-08-04, Added, Performance, Refactored

### Community 51 - "[2.4.0] - 2026-08-26"
Cohesion: 0.50
Nodes (4): [2.4.0] - 2026-08-26, Added, Fixed, Refactored

### Community 52 - "INV-001 — Pipeline Authority"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-001 — Pipeline Authority, Preconditions, Related Modules, Related Tests (+4 more)

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

### Community 62 - "SDDIntegrator"
Cohesion: 0.07
Nodes (25): Any, Ensure only one UI instance exists., Update existing UI instance., Get all evidence for a task., Integrates SDD contract enforcement into existing pipeline., Classify a prompt using the task router., Enforce tool policy for a task type., Create a new task with the appropriate contract. (+17 more)

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

### Community 74 - "EvidenceLogger"
Cohesion: 0.10
Nodes (16): Evidence, EvidenceLogger, EvidenceType, Enum, Evidence Logger for recording verification failures and diagnoses., Types of evidence that can be logged., Log a diagnosis with evidence. Args: task_id: ID of the task problem: The…, Log a replanning event with diagnosis. Args: task_id: ID of the task… (+8 more)

### Community 76 - "TestSSEEndpoint"
Cohesion: 0.14
Nodes (7): TEST-007 (INV-008): Verifica que la ruta SSE esté registrada en…, TEST-001: Verifica suscripción, publicación y des-suscripción en EventBus., TEST-002: Verifica que la emisión de eventos preserve los tipos y estructura…, TEST-004: Verifica que un cliente SSE desconectado elimine su listener del…, TEST-005: Verifica que múltiples suscriptores concurrentes reciban el evento de…, TEST-006: Verifica que la suscripción a eventos pueda filtrarse por task_id de…, TestSSEEndpoint

### Community 77 - "Dependencies"
Cohesion: 0.50
Nodes (4): Dependencies, External Dependencies, Internal Dependencies, Version Compatibility

### Community 80 - "Testing Strategy"
Cohesion: 0.50
Nodes (4): Integration Testing Approach, Property-Based Testing Approach, Testing Strategy, Unit Testing Approach

### Community 81 - "Security Considerations"
Cohesion: 0.50
Nodes (4): Security Considerations, Security Controls, Security Requirements, Threat Model

### Community 82 - "INV-002 — TaskContract Authority"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-002 — TaskContract Authority, Preconditions, Related Modules, Related Tests (+4 more)

### Community 83 - "Diagnosis"
Cohesion: 0.10
Nodes (17): Generate a new plan based on diagnosis., Determine if replanning should occur., Diagnosis, Plan, PlanStatus, PlanStep, Enum, Replanner with evidence-based triggers. (+9 more)

### Community 84 - "Audit Results by Requirement"
Cohesion: 0.08
Nodes (24): Audit Results by Requirement, Conclusion, Conformance Audit: SDD Contract System, Conformance Matrix, Executive Summary, IMMEDIATE (Blocker), MEDIUM TERM (High Priority), Parallel Architecture Risk (+16 more)

### Community 85 - "UIManager"
Cohesion: 0.10
Nodes (15): Enum, UI Manager for enforcing single-instance policy., Represents a UI instance., Convert to dictionary for serialization., Manages UI lifecycle with single-instance policy., Create a new UI instance. Args: session_id: The current session ID ui_type:…, Update an existing UI instance. Does NOT create new instances. Args:…, Mark the UI instance as closed. (+7 more)

### Community 88 - "integrator.py"
Cohesion: 0.13
Nodes (13): Integrator for SDD contract enforcement into existing agent_pipeline.py., Enum, Task data model for execution tracking., Status of task execution., Workflow phases for tasks., Represents a task being executed., Check if task can still replan., Mark task as verified with results. (+5 more)

### Community 89 - "TaskRouter"
Cohesion: 0.11
Nodes (22): Any, Task Router for classifying user prompts into task types., Normalize diacritics / accents from text while preserving original text., Apply decision rules to determine task type. Returns: The determined TaskType, Classifies incoming prompts into task types., Calculate confidence score for classification. Returns: Confidence score…, Generate human-readable reason for classification. Returns: Reason string…, Classify a user prompt into a task type. Args: prompt: The user's input prompt… (+14 more)

### Community 90 - "ToolType"
Cohesion: 0.10
Nodes (15): FeatureTaskContract, Return set of tools allowed for this task type., Contract for FEATURE tasks - full workflow., Tool categorization for policy enforcement., ToolType, Tool Policy Enforcer for controlling tool access by task type., Get all blocked tools for a task type., Policy defining allowed tools for a task type. (+7 more)

### Community 92 - "agent_pipeline.py"
Cohesion: 0.05
Nodes (31): ComplexityRiskEvaluator, ExecutionLevel, _get_phase_cognitive_directive(), Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Evaluador determinista de complejidad, alcance e impacto en workspace., Devuelve la directiva cognitiva acotada a la fase activa., State (+23 more)

### Community 93 - "test_e2e_real_desktop_lifecycle.py"
Cohesion: 0.22
Nodes (12): Popen, discover_desktop_backend(), get_health(), is_port_listening(), kill_process_tree(), skipUnless, Test E2E Real del ENTRYPOINT Real de CodeAgent Desktop (desktop_app.py).…, Test 1: Ejecuta desktop_app.py como proceso real y valida los metadatos de su… (+4 more)

### Community 94 - "tool"
Cohesion: 0.13
Nodes (13): tool(), buscar_en_internet(), consultar_db(), git_add(), git_commit(), git_push(), guardar_reporte(), Archiva el análisis para memoria a largo plazo. Args: analisis: El texto del… (+5 more)

### Community 95 - "DesktopIDEApi"
Cohesion: 0.14
Nodes (8): DesktopIDEApi, _ps_save_dialog(), API nativa expuesta al frontend de Javascript a través de PyWebView., Abre el diálogo nativo de Guardar Como para escribir contenido en disco., Guarda directamente el contenido del buffer en una ruta existente., Inicia una nueva ventana de la aplicación de escritorio (DESACTIVADA POR…, Finaliza el proceso de la ventana y la aplicación., TestDesktopIDEApi

### Community 96 - "INV-003 — Cross-Task Isolation"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-003 — Cross-Task Isolation, Preconditions, Related Modules, Related Tests (+4 more)

### Community 97 - "check_ollama_running"
Cohesion: 0.31
Nodes (6): check_ollama_running(), check_server_running(), Comprueba si un servidor backend compatible y propio responde en la URL de…, Verifica si el servicio Ollama está activo en el puerto 11434., patch, TestDesktopApp

### Community 98 - "INV-004 — Intent Preservation"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-004 — Intent Preservation, Preconditions, Related Modules, Related Tests (+4 more)

### Community 99 - "TestDesktopPipelineVisualization"
Cohesion: 0.14
Nodes (7): TEST-001: Verifica que localcode_claude_ui.html contenga las funciones de…, TEST-002: Verifica que la UI maneje eventos reales de STATE_ENTERED y…, TEST-003 (INV-008): Verifica que closePipelineSSE se invoque en el bloque…, TEST-004: Verifica la correlación end-to-end entre task_id en UI request,…, TEST-005: Verifica que el temporizador estático falso secCount % 3 === 0 haya…, TEST-006: Verifica que la UI maneje errores de EventSource sin interrumpir el…, TestDesktopPipelineVisualization

### Community 101 - "Repository Hygiene Report — Phase C1 (Safe Repository Hygiene)"
Cohesion: 0.14
Nodes (13): 1. Pruebas Unitarias e Integración (Pytest), 2. Verificación de Gobernanza SDD (`sdd_check.py`), 3. Smoke Test de Importaciones, Overview, Removed Duplicate Files, Removed Runtime Artifacts, Repository Hygiene Report — Phase C1 (Safe Repository Hygiene), Repository Size After (+5 more)

### Community 102 - "Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`), Rollback, SDD Validation (+1 more)

### Community 103 - "BenchmarkMetricsCollector"
Cohesion: 0.07
Nodes (16): BenchmarkMetricsCollector, Any, CodeAgent Benchmark & Quality Metrics Engine Registra, calcula y persiste…, Registra la ejecución real de una herramienta por el agente., Calcula los KPIs cuantitativos agregados con datos reales., Genera un reporte formateado en Markdown con los KPIs cuantitativos., Colector y repositorio persistente de métricas cuantitativas agénticas., Registra el resultado de un ciclo de ejecución de la Máquina de Estados. (+8 more)

### Community 104 - "Change Impact Analysis — SDD Governance Telemetry Endpoint"
Cohesion: 0.20
Nodes (9): Certification Impact, Change Impact Analysis — SDD Governance Telemetry Endpoint, Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests (+1 more)

### Community 105 - "Event"
Cohesion: 0.13
Nodes (11): handle_sse_events_dict(), Any, Serializa una instancia de Event o dict al formato Server-Sent Events (SSE)., Event, Registra un callback de escucha de eventos en tiempo real., Elimina un callback de escucha., Inicia una nueva tarea agéntica de forma asíncrona y la registra en SQLite., Unit & Integration Tests for Desktop Real-Time Pipeline EventSource… (+3 more)

### Community 106 - "INV-005 — Failure Containment"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-005 — Failure Containment, Preconditions, Related Modules, Related Tests (+4 more)

### Community 107 - "TestRegressionSuite"
Cohesion: 0.20
Nodes (5): git_diff(), git_status(), Muestra el estado del repositorio Git (archivos modificados, untracked, etc).…, Muestra los cambios no commiteados en el repositorio. Args: ruta_repo: Ruta del…, TestRegressionSuite

### Community 108 - "SPEC-009 — SDD Governance Telemetry Endpoint"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-009 — SDD Governance Telemetry Endpoint, Testability (+1 more)

### Community 109 - "ejecutar_agentes"
Cohesion: 0.05
Nodes (32): graphify, crear_agente(), _detectar_modelo_local(), get_available_agents(), load_subagents_from_disk(), Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML…, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)., Enrutador automático mejorado con scoring ponderado. (+24 more)

### Community 110 - "SPEC-010 — Dynamic Feature Governance Automation"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-010 — Dynamic Feature Governance Automation, Testability (+1 more)

### Community 111 - "Change Impact Analysis — Feature Governance Automation"
Cohesion: 0.25
Nodes (7): Change Impact Analysis — Feature Governance Automation, Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests

### Community 112 - "version.py"
Cohesion: 0.24
Nodes (7): Single source of truth for CodeAgent version., get_health(), is_port_listening(), skipUnless, Prueba E2E Real OS Lifecycle para Windows (Sin Mocks). Verifica que dos…, Ejecuta dos subprocesos Python reales de localcode_server.py simulando Desktop…, TestE2ERealLifecycle

### Community 113 - "Feature Runtime Evidence — SPEC-009"
Cohesion: 0.33
Nodes (5): 1. HTTP JSON Payload Verification, 2. Observability Log Trace (R4), 3. Automated Test Verification, Feature Runtime Evidence — SPEC-009, Summary

### Community 114 - "INV-006 — Tool Isolation"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-006 — Tool Isolation, Preconditions, Related Modules, Related Tests (+4 more)

### Community 115 - "INV-007 — Conditional Verification"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-007 — Conditional Verification, Preconditions, Related Modules, Related Tests (+4 more)

### Community 116 - "INV-008 — Desktop Lifecycle Safety"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-008 — Desktop Lifecycle Safety, Preconditions, Related Modules, Related Tests (+4 more)

### Community 117 - "SPEC-011 — Real-Time Pipeline State & Event Streaming (SSE)"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-011 — Real-Time Pipeline State & Event Streaming (SSE), Testability (+1 more)

### Community 118 - "Feature Runtime Evidence — SPEC-010"
Cohesion: 0.40
Nodes (4): 1. Dynamic Discovery Telemetry, 2. Decoupled Adversarial Self-Diagnostic Engine (13 Cases), Feature Runtime Evidence — SPEC-010, Summary

### Community 119 - "Change Impact Analysis — Real-Time Pipeline State & Event Streaming (SSE)"
Cohesion: 0.22
Nodes (8): Change Impact Analysis — Real-Time Pipeline State & Event Streaming (SSE), Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests, Required Runtime Evidence

### Community 120 - "SDD Change Impact Analysis Declaration"
Cohesion: 0.22
Nodes (8): Certification Impact, Change Title, Description, Modified Components, Potentially Affected Invariants, Required Regression Tests, Required Runtime Evidence, SDD Change Impact Analysis Declaration

### Community 121 - "SDD Certification Report — Release v5.0.0"
Cohesion: 0.29
Nodes (6): Certification Verdict, **CERTIFIED PASS**, Invariant Certification Matrix, Known Limitations Documented, Release Metadata, SDD Certification Report — Release v5.0.0

### Community 122 - "SDD Certification Report — Release [vX.Y.Z]"
Cohesion: 0.29
Nodes (6): Certification Verdict, **[CERTIFIED PASS / PASS WITH RESERVATIONS / FAIL]**, Invariant Certification Matrix, Known Limitations Documented, Release Metadata, SDD Certification Report — Release [vX.Y.Z]

### Community 124 - "Runtime Audit Evidence — Release v5.0.0"
Cohesion: 0.33
Nodes (5): 1. Fast-Path CHAT Execution Telemetry (`INV-001`, `INV-002`, `INV-006`, `INV-007`), 2. Multi-Request Cross-Task Isolation Telemetry (`INV-003`), 3. Desktop Concurrency & Lifecycle Telemetry (`INV-008`), Certified Commit, Runtime Audit Evidence — Release v5.0.0

### Community 125 - "Certification Environment Metadata — Release v5.0.0"
Cohesion: 0.40
Nodes (4): Certification Environment Metadata — Release v5.0.0, Key Dependencies, System Information, Verified Artifacts & Hash Context

### Community 127 - "SDD Audits & Certifications Registry"
Cohesion: 0.50
Nodes (3): Certification Status History, Directory Structure, SDD Audits & Certifications Registry

### Community 128 - "SDD Change Impact Analysis Framework"
Cohesion: 0.50
Nodes (3): Change Impact Analysis Workflow, SDD Change Impact Analysis Framework, When to Execute Impact Analysis

### Community 129 - "SDD Specifications & Invariant Hierarchy"
Cohesion: 0.29
Nodes (6): Automated SDD Verification CLI (`scripts/sdd_check.py`), Certified Invariants Overview, Directory Structure, SDD Specifications & Invariant Hierarchy, What `sdd_check.py` Does NOT Validate, What `sdd_check.py` Validates

### Community 130 - "SDD Bi-Directional Traceability Matrix"
Cohesion: 0.40
Nodes (4): 1. Invariant Traceability Matrix, 2. Feature Traceability Matrix, 3. Impact Analysis Lookup Guide, SDD Bi-Directional Traceability Matrix

### Community 131 - "TestPytestVerifierResolution"
Cohesion: 0.29
Nodes (3): Tests de resolución del verificador de pruebas con sys.executable -m pytest.…, Verifica que _stage_verifier use sys.executable -m pytest para descubrir y…, TestPytestVerifierResolution

### Community 134 - "sdd_check.py"
Cohesion: 0.11
Nodes (23): discover_features(), discover_invariants(), normalize_repo_path(), parse_traceability_table(), Descubre dinámicamente todos los archivos specs/invariants/INV-*.md. Retorna…, Descubre dinámicamente todos los archivos specs/features/SPEC-*.md. Retorna…, Valida la existencia real de un archivo y su rango de líneas si está…, Valida que los archivos de prueba y símbolos referenciados existan en disco. (+15 more)

### Community 136 - "Feature Runtime Evidence — SPEC-011"
Cohesion: 0.33
Nodes (5): 1. HTTP SSE Event Stream Telemetry, 2. Server Log Trace Evidence, 3. Automated Test Suite Execution, Feature Runtime Evidence — SPEC-011, Summary

### Community 137 - "preguntar_a_repositorio"
Cohesion: 0.21
Nodes (9): _bm25_score(), indexar_directorio_local(), init_chroma(), preguntar_a_repositorio(), Calcula una puntuación BM25 léxica simplificada basada en frecuencia de…, Realiza una búsqueda semántica sobre los archivos previamente indexados con…, Inicializa la base de datos ChromaDB y el modelo de embeddings., Escanea todos los archivos de código en un directorio local y los indexa en… (+1 more)

### Community 138 - "Migration Report: Legacy Orchestrator Verification (`orquestador_agente.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Legacy Orchestrator Verification (`orquestador_agente.py`), Rollback, SDD Validation (+1 more)

### Community 139 - "GraphContextEngine"
Cohesion: 0.05
Nodes (28): ContextBudgeter, ContextFormatter, GraphCacheManager, GraphContextEngine, Any, AST Subgraph Context Retrieval & Impact Engine (SPEC-013). Motor modular…, Extractor determinista de targets (archivos/símbolos) en 5 niveles sin LLM., Administrador de caché en memoria de graphify-out/graph.json basado en mtime. (+20 more)

### Community 141 - "Migration Report: RAG Legacy Migration (`rag_tools.py` → `graph_context.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: RAG Legacy Migration (`rag_tools.py` → `graph_context.py`), Rollback, SDD Validation (+1 more)

### Community 142 - "Change Impact Analysis — AST Subgraph Context Retrieval & Impact Engine (SPEC-013)"
Cohesion: 0.18
Nodes (10): Change Impact Analysis — AST Subgraph Context Retrieval & Impact Engine (SPEC-013), Current Production Files Modified in this Phase, Description, Feature Title, Invariants NOT Affected, Modified Production Files (Planned for Implementation Phase), Potentially Affected Invariants, Required Runtime Evidence (+2 more)

### Community 143 - "SPEC-012 — Desktop Real-Time Pipeline EventSource Visualization"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-012 — Desktop Real-Time Pipeline EventSource Visualization, Testability (+1 more)

### Community 144 - "Change Impact Analysis — Desktop Real-Time Pipeline EventSource Visualization (SPEC-012)"
Cohesion: 0.22
Nodes (8): Change Impact Analysis — Desktop Real-Time Pipeline EventSource Visualization (SPEC-012), Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests, Required Runtime Evidence

### Community 145 - "mis_agentes_inteligentes.rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes.rag_tools, mis_agentes_inteligentes.rag_tools.init_chroma, mis_agentes_inteligentes.rag_tools.indexar_directorio_local, mis_agentes_inteligentes.rag_tools.preguntar_a_repositorio

### Community 146 - "Feature Runtime Evidence — SPEC-012"
Cohesion: 0.33
Nodes (5): 1. Desktop UI JavaScript SSE Contract, 2. End-to-End Task-ID Correlation, 3. Automated Test Suite Execution, Feature Runtime Evidence — SPEC-012, Summary

### Community 149 - "SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG)"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG), Testability (+1 more)

### Community 150 - "Feature Runtime Evidence — SPEC-013"
Cohesion: 0.22
Nodes (8): 1. Pre-Implementation TDD RED Baseline Evidence, 2. Controlled TDD GREEN Implementation Evidence, 3. Full Regression Test Suite Evidence, 4. Performance Benchmarks, 5. SDD Governance Verification, 6. Invariant Preservation Summary, Feature Runtime Evidence — SPEC-013, Summary

### Community 151 - "Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`), Rollback, SDD Validation (+1 more)

### Community 152 - "get_event_bus"
Cohesion: 0.29
Nodes (3): get_event_bus(), Verifica la capacidad de autorecuperación TDD (FAIL -> DIAGNOSE -> REPLAN ->…, TestTDDRecoveryLoop

### Community 154 - "Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView), Rollback, SDD Validation (+1 more)

### Community 155 - "set_active_workspace"
Cohesion: 0.22
Nodes (5): get_active_workspace(), Establece el directorio del espacio de trabajo activo de forma thread-safe para…, Devuelve el espacio de trabajo activo de forma thread-safe., set_active_workspace(), TestWorkspaceIsolation

### Community 159 - "session_manager.py"
Cohesion: 0.29
Nodes (6): create_new_session(), export_session_to_markdown(), init_sessions_dir(), load_session(), rename_session(), save_session()

### Community 160 - ".to_dict"
Cohesion: 0.29
Nodes (5): Any, Convert to dictionary for serialization., Convert to dictionary for serialization., Result of task execution., TaskResult

### Community 161 - "BaseSessionRepository"
Cohesion: 0.25
Nodes (3): BaseSessionRepository, ABC, Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio).

### Community 163 - "Task Contract Compatibility Matrix"
Cohesion: 0.33
Nodes (5): Consumer Analysis, Detailed Comparison Table, Migration Architecture Plan, Purpose, Task Contract Compatibility Matrix

### Community 166 - "DatabaseManager"
Cohesion: 0.12
Nodes (11): EventBus, Bus de eventos persistente con patrón Observador (Event Sourcing)., CodeAgentRuntime, Motor de ejecución autónomo desacoplado para CodeAgent v6.1. Gestión semántica…, Cancela definitivamente una tarea., DatabaseManager, get_db_manager(), Gestor de almacenamiento persistente SQLite multihilo seguro para CodeAgent… (+3 more)

## Knowledge Gaps
- **516 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+511 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TaskRouter` connect `TaskRouter` to `TestSDDConformance`, `AgentStateMachineController`, `integrator.py`, `agent_pipeline.py`, `SDDIntegrator`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `TestDiagnoseRootCauseAndVersion`, `.get_task`, `TestSDDConformance`, `TestStateCheckpointing`, `DatabaseManager`, `BenchmarkMetricsCollector`, `Event`, `GraphContextEngine`, `get_event_bus`, `TaskRouter`, `TestRuntimeRecoveryAndPauseSemantics`, `agent_pipeline.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `ExecutionLevel` connect `agent_pipeline.py` to `TestDiagnoseRootCauseAndVersion`, `TestSDDConformance`, `TestStateCheckpointing`, `BenchmarkMetricsCollector`, `AgentStateMachineController`, `GraphContextEngine`, `TaskRouter`, `TestRuntimeRecoveryAndPauseSemantics`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `AgentStateMachineController` (e.g. with `GraphContextEngine` and `TaskRouter`) actually correct?**
  _`AgentStateMachineController` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestDesktopPipelineVisualization` and `TestE2ESystemSuite`) actually correct?**
  _`LocalCodeProxyHandler` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `SDDIntegrator` (e.g. with `EvidenceLogger` and `Diagnosis`) actually correct?**
  _`SDDIntegrator` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `TestSDDConformance` (e.g. with `AgentStateMachineController` and `ComplexityRiskEvaluator`) actually correct?**
  _`TestSDDConformance` has 10 INFERRED edges - model-reasoned connections that need verification._