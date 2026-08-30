# Graph Report - CodeAgent  (2026-08-30)

## Corpus Check
- 158 files · ~90,781 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2032 nodes · 2876 edges · 177 communities (145 shown, 32 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 343 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e5d63ad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Canonical Architecture Analysis — CodeAgent v6.1
- LocalCodeProxyHandler
- An�lisis de Violaciones del SDD Contract System
- CodeAgentRuntime
- Canonical Enforcement Audit (Phase C2.5)
- Changelog
- 💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated)
- ejecutar_comando_terminal
- mis_agentes_inteligentes/tools
- mis_agentes_inteligentes.tools
- .run
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
- AgentStateMachineController
- TestSmokeSystem
- ADR-001: Selección de smolagents como Motor ReAct
- ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo
- ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM
- integrator.py
- get_model
- mis_agentes_inteligentes/rag_tools
- TestSDDConformance
- graphify.js
- rules/graphify.md
- workflows/graphify.md
- agent_pipeline.py
- __init__.py
- start_hub.sh
- [2.2.0] - 2026-07-25
- 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)
- TaskContract
- DatabaseManager
- Correctness Properties
- [2.3.0] - 2026-08-04
- [2.4.0] - 2026-08-26
- INV-001 — Pipeline Authority
- [2.2.1] - 2026-07-26
- get_db_manager
- [2.5.0] - 2026-08-26
- Design Document: CodeAgent SDD Contract
- Components and Interfaces
- [3.5.0] - 2026-08-27
- [4.0.0] - 2026-08-27
- [4.3.0] - 2026-08-27
- [5.3.0] - 2026-08-27
- VerificationEngine
- Workflow State Machines
- [6.5.0] - 2026-08-28
- [6.6.0] - 2026-08-28
- [6.7.0] - 2026-08-28
- [6.8.0] - 2026-08-28
- SDDIntegrator
- Algorithmic Pseudocode
- Error Handling
- Implementation Plan: CodeAgent SDD Contract
- Data Models
- Example Usage
- EvidenceLogger
- 📊 MAPA DE FLUJOS DE PERSISTENCIA ACTUALES
- EventBus
- Dependencies
- [6.11.0] - 2026-08-28
- [6.2.0] - 2026-08-28
- Testing Strategy
- Security Considerations
- INV-002 — TaskContract Authority
- Diagnosis
- Audit Results by Requirement
- UIManager
- PERSISTENCE CANONICALIZATION REPORT — Phase C3.1
- TestServerLifecycle
- Task
- TaskRouter
- ToolPolicyEnforcer
- .handle_sdd_health
- .build_contract
- test_e2e_real_desktop_lifecycle.py
- tools.py
- TestTaskContractCanonical
- INV-003 — Cross-Task Isolation
- ExecutionLevel
- INV-004 — Intent Preservation
- TestDesktopPipelineVisualization
- Repository Hygiene Report — Phase C1 (Safe Repository Hygiene)
- Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`)
- BenchmarkMetricsCollector
- Change Impact Analysis — SDD Governance Telemetry Endpoint
- _atomic_write_file
- INV-005 — Failure Containment
- TestRegressionSuite
- SPEC-009 — SDD Governance Telemetry Endpoint
- TestAgents
- SPEC-010 — Dynamic Feature Governance Automation
- Change Impact Analysis — Feature Governance Automation
- _ContractWrapper
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
- main.py
- SDD Audits & Certifications Registry
- SDD Change Impact Analysis Framework
- SDD Specifications & Invariant Hierarchy
- SDD Bi-Directional Traceability Matrix
- TestPytestVerifierResolution
- TestSessionManager
- SPEC-009/README.md
- sdd_check.py
- Legacy Retirement Report - Phase C3.2
- Feature Runtime Evidence — SPEC-011
- CodeAgentBenchmarkSuite
- Migration Report: Legacy Orchestrator Verification (`orquestador_agente.py`)
- GraphContextEngine
- SPEC-011/README.md
- Migration Report: RAG Legacy Migration (`rag_tools.py` → `graph_context.py`)
- Change Impact Analysis — AST Subgraph Context Retrieval & Impact Engine (SPEC-013)
- SPEC-012 — Desktop Real-Time Pipeline EventSource Visualization
- Change Impact Analysis — Desktop Real-Time Pipeline EventSource Visualization (SPEC-012)
- mis_agentes_inteligentes.rag_tools
- Feature Runtime Evidence — SPEC-012
- localcode_server.py
- ejecutar_agentes
- SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG)
- Feature Runtime Evidence — SPEC-013
- Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`)
- get_terminal_tasks_buffer
- SPEC-012/README.md
- Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView)
- set_active_workspace
- SPEC-013/README.md
- ThreadedTCPServer
- JSONSessionRepository
- session_manager.py
- test_localcode_server.py
- BaseSessionRepository
- TestDiagnoseRootCauseAndVersion
- Task Contract Compatibility Matrix
- TestAgentStateMachineController
- load_session
- TestRuntimeAndStorage
- TestTaskTimeoutSafeguardAndCancellation
- TestQAEdgeCasesAndNegativeScenarios
- TestVerifierEvidenceAndWorkspaceIsolation
- test_local_model_provider.py
- [6.9.0] - 2026-08-28
- claude_code_cli.py
- [6.4.0] - 2026-08-28

## God Nodes (most connected - your core abstractions)
1. `AgentStateMachineController` - 65 edges
2. `LocalCodeProxyHandler` - 38 edges
3. `ExecutionLevel` - 33 edges
4. `SDDIntegrator` - 32 edges
5. `TestSDDConformance` - 31 edges
6. `DatabaseManager` - 27 edges
7. `TaskRouter` - 27 edges
8. `ComplexityRiskEvaluator` - 24 edges
9. `CodeAgentRuntime` - 24 edges
10. `ChatTaskContract` - 24 edges

## Surprising Connections (you probably didn't know these)
- `_ContractWrapper` --uses--> `ActionTaskContract`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_contract.py
- `_ContractWrapper` --uses--> `ChatTaskContract`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_contract.py
- `_ContractWrapper` --uses--> `FeatureTaskContract`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_contract.py
- `_ContractWrapper` --uses--> `TaskRouter`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_router.py
- `_ContractWrapper` --uses--> `TaskType`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_types.py

## Import Cycles
- None detected.

## Communities (177 total, 32 thin omitted)

### Community 0 - "Canonical Architecture Analysis — CodeAgent v6.1"
Cohesion: 0.06
Nodes (30): Análisis Comparativo, Análisis de Mecanismos Actuales, Análisis de `sdd_contract/integrator.py`, Arquitectura Objetivo de Persistencia, Canonical Architecture Analysis — CodeAgent v6.1, Canonical Component Matrix, Clasificación de Interfaces, Components to Archive (+22 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.18
Nodes (4): _inc_metric(), LocalCodeProxyHandler, Maneja el streaming HTTP Server-Sent Events en GET /api/pipeline/events., Verifica si el servicio Ollama local está activo en el endpoint configurado.

### Community 2 - "An�lisis de Violaciones del SDD Contract System"
Cohesion: 0.05
Nodes (36): 1.1 Clasificaci�n Incorrecta (Requirement 1), 1.2 Fallback a LEVEL_3_FEATURE (Requirement 1), 1.3?? CHAT Fast Path (Requirement 2), 1.4 Verificaci�n ejecutada para CHAT (Requirement 2), 1.5 Replanning ejecutado para CHAT (Requirement 2), 2.1 Verificaci�n ejecutada para ACTION sin solicitud expl�cita (Requirement 3), 2.2 Ejecuci�n repetida del programa (Requirement 3), 2.3 Ruff FAIL hace fallar ACTION aunque no sea parte del contrato (Requirement 3) (+28 more)

### Community 3 - "CodeAgentRuntime"
Cohesion: 0.13
Nodes (12): Event, Registra un callback de escucha de eventos en tiempo real., CodeAgentRuntime, Any, Motor de ejecución autónomo desacoplado para CodeAgent v6.1. Gestión semántica…, Obtiene la información de la tarea, su estado actual y el último checkpoint., Lista las tareas recientes guardadas en SQLite., Pausa una tarea activa sin marcarla como cancelada. (+4 more)

### Community 4 - "Canonical Enforcement Audit (Phase C2.5)"
Cohesion: 0.08
Nodes (24): Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Análisis de Adherencia, Canonical Decisions Matrix, Canonical Enforcement Audit (Phase C2.5), Canonicalization Drift Findings (+16 more)

### Community 5 - "Changelog"
Cohesion: 0.20
Nodes (9): [4.2.0] - 2026-08-27, [6.0.0] - 2026-08-28, [6.10.0] - 2026-08-28, [6.3.0] - 2026-08-28, Added, Added, Added, Added (+1 more)

### Community 6 - "💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated)"
Cohesion: 0.11
Nodes (17): 🏗️ Arquitectura del Sistema (5 Capas Principales & Gobernanza SDD), 📐 Auditorías y Migraciones Arquitectónicas (Phases A, B, C1 & C2), ✨ Características Principales, CLI de Verificación SDD (`scripts/sdd_check.py`), 💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated), 🚀 Informes de Migración Canónica y Auditoría de Cumplimiento (Phases C2 & C2.5), 🚀 Instalación y Ejecución, 🌐 Knowledge Graph (`graphify-out/`) (+9 more)

### Community 7 - "ejecutar_comando_terminal"
Cohesion: 0.19
Nodes (6): ejecutar_comando_terminal(), is_command_approved(), is_sensitive_command(), pre_approve_command(), Ejecuta un comando en la terminal del sistema operativo (ej. pytest, ls, pip…, TestTerminalHITLApproval

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - ".run"
Cohesion: 0.11
Nodes (13): _get_phase_cognitive_directive(), Any, EvaluaciÃ³n crÃ­tica objetiva del diff, requisitos e integridad del workspace., Devuelve la directiva cognitiva acotada a la fase activa., Ejecuta el ciclo agÃ©ntico mediante la MÃ¡quina de Estados Determinista., Alias de compatibilidad hacia atrÃ¡s para la versiÃ³n v3.0., Reanuda la ejecuciÃ³n priorizando DatabaseManager/SQLite como Source of Truth.…, Genera un plan de acciÃ³n estructurado. (+5 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.17
Nodes (8): _detectar_raiz_proyecto(), get_active_workspace(), listar_directorio_local(), obtener_contexto_workspace(), Devuelve el espacio de trabajo activo de forma thread-safe., Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido…, Función de utilidad para el comando @workspace. Genera un resumen del entorno.

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
Cohesion: 0.17
Nodes (11): editar_archivo_search_replace(), escribir_archivo_local(), leer_archivo_local(), Lee el contenido de un archivo local en tu disco duro para poder analizar su…, Verifica automáticamente la sintaxis del archivo modificado (ej. ast.parse para…, Crea o sobreescribe un archivo local con el contenido proporcionado. Útil para…, Rastrea e informa la ejecución de herramientas al colector de métricas., IMPORTANTE: Úsala para modificar partes de un archivo SIN reescribirlo todo.… (+3 more)

### Community 19 - "mis_agentes_inteligentes/session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes/session_manager, session_manager.init_sessions_dir, session_manager.create_new_session, session_manager.list_sessions, session_manager.load_session, session_manager.save_session, session_manager.delete_session, session_manager.rename_session (+1 more)

### Community 20 - "mis_agentes_inteligentes.session_manager"
Cohesion: 0.22
Nodes (9): mis_agentes_inteligentes.session_manager, mis_agentes_inteligentes.session_manager.init_sessions_dir, mis_agentes_inteligentes.session_manager.create_new_session, mis_agentes_inteligentes.session_manager.list_sessions, mis_agentes_inteligentes.session_manager.load_session, mis_agentes_inteligentes.session_manager.save_session, mis_agentes_inteligentes.session_manager.delete_session, mis_agentes_inteligentes.session_manager.rename_session (+1 more)

### Community 21 - "desktop_app.py"
Cohesion: 0.05
Nodes (43): check_ollama_running(), check_server_running(), DesktopIDEApi, find_free_port(), get_process_creation_time(), is_backend_compatible(), launch_ollama_bg(), launch_server_bg() (+35 more)

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

### Community 26 - "AgentStateMachineController"
Cohesion: 0.09
Nodes (15): AgentStateMachineController, Controlador determinista de estados, enrutador adaptativo y gestor de…, TEST 3: JSON legacy se migra correctamente a SQLite en resume_session., TEST 4: _save_checkpoint escribe SQLite primero (Source of Truth)., TEST 5: Recovery/resume usa SQLite como Source of Truth., TEST 6: JSON corrupto no reemplaza SQLite válido., TEST 7: SQLite corrupto produce failure controlado (no inventa estado)., Tests para verificar la autoridad de persistencia canónica (C3.1). (+7 more)

### Community 28 - "ADR-001: Selección de smolagents como Motor ReAct"
Cohesion: 0.40
Nodes (4): ADR-001: Selección de smolagents como Motor ReAct, Consecuencias, Contexto, Decisión

### Community 29 - "ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo"
Cohesion: 0.40
Nodes (4): ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo, Consecuencias, Contexto, Decisión

### Community 30 - "ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM"
Cohesion: 0.40
Nodes (4): ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM, Consecuencias, Contexto, Decisión

### Community 31 - "integrator.py"
Cohesion: 0.08
Nodes (24): Integrator for SDD contract enforcement into existing agent_pipeline.py., ChatTaskContract, FeatureTaskContract, Task Contract implementations for SDD. Enforces behavioral boundaries per task…, Contract for RECOVERY tasks - state restoration., Contract for CHAT tasks - conversational only., Contract for FEATURE tasks - full workflow., RecoveryTaskContract (+16 more)

### Community 32 - "get_model"
Cohesion: 0.08
Nodes (19): get_model(), Instancia dinámicamente el modelo LiteLLMModel asegurando MODO LOCAL-ONLY…, patch, TEST 15 (No Exfiltración): Garantiza que el endpoint LLM resuelto apunta…, TEST 1: El proveedor predeterminado debe ser 'Ollama (Local)'., TEST 2: El modelo predeterminado debe ser 'qwen2.5-coder:14b'., TEST 3: La instanciación predeterminada de get_model() no requiere…, TEST 4: Un proveedor explícito 'OpenAI' debe ser RECHAZADO con ValueError. (+11 more)

### Community 33 - "mis_agentes_inteligentes/rag_tools"
Cohesion: 0.50
Nodes (4): mis_agentes_inteligentes/rag_tools, rag_tools.init_chroma, rag_tools.indexar_directorio_local, rag_tools.preguntar_a_repositorio

### Community 34 - "TestSDDConformance"
Cohesion: 0.10
Nodes (4): ActionTaskContract, Contract for ACTION tasks - minimal tools, single operation., Garantiza que agent_pipeline y mis_agentes_inteligentes.agent_pipeline son el…, TestSDDConformance

### Community 38 - "agent_pipeline.py"
Cohesion: 0.10
Nodes (8): ComplexityRiskEvaluator, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, Evaluador determinista de complejidad, alcance e impacto en workspace., CodeAgent Benchmark & Quality Metrics Engine Registra, calcula y persiste…, object, TestAgentPipeline, TestFeedbackLoopAndToolEvents, Tests de regresión de negaciones para TaskRouter y ComplexityRiskEvaluator.…

### Community 45 - "[2.2.0] - 2026-07-25"
Cohesion: 0.50
Nodes (4): [2.2.0] - 2026-07-25, Added, Fixed, Refactored

### Community 46 - "🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise)"
Cohesion: 0.50
Nodes (3): 📈 KPIs Globales Acumulados, 🧪 Reporte Oficial de Benchmark Reales CodeAgent (v4.2 Enterprise), 📊 Resultados por Tarea de Ingeniería

### Community 47 - "TaskContract"
Cohesion: 0.09
Nodes (12): ABC, Base interface for all task contracts., Return set of tools allowed for this task type., Return True if verification is allowed for this task., Return True if replanning is allowed for this task., Return maximum iterations for this task type., Compatibility property for pipeline verification check., Compatibility property for pipeline test requirement check. (+4 more)

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

### Community 52 - "INV-001 — Pipeline Authority"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-001 — Pipeline Authority, Preconditions, Related Modules, Related Tests (+4 more)

### Community 53 - "[2.2.1] - 2026-07-26"
Cohesion: 0.67
Nodes (3): [2.2.1] - 2026-07-26, Added, Fixed

### Community 54 - "get_db_manager"
Cohesion: 0.19
Nodes (6): Módulo de runtime autónomo y event bus para CodeAgent v6.0 Enterprise., get_runtime(), get_db_manager(), Módulo de almacenamiento persistente local SQLite para CodeAgent v6.0…, Verifica la capacidad de autorecuperación TDD (FAIL -> DIAGNOSE -> REPLAN ->…, TestTDDRecoveryLoop

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

### Community 62 - "VerificationEngine"
Cohesion: 0.13
Nodes (13): Any, Evaluate a single criterion against results. Args: criterion: The criterion to…, A single verification criterion., Get actual value from results for a criterion name., Analyze the difference between expected and actual., Gather evidence from all verification results. Args: criteria: List of…, Compute overall success based on criteria states. Args: criteria: List of…, Convert to dictionary for serialization. (+5 more)

### Community 63 - "Workflow State Machines"
Cohesion: 0.29
Nodes (7): ACTION Task State Machine, CHAT Task State Machine, FEATURE Task State Machine, High-Level Design, RECOVERY Task State Machine, Task Classification System, Workflow State Machines

### Community 68 - "SDDIntegrator"
Cohesion: 0.11
Nodes (14): Any, Ensure only one UI instance exists., Update existing UI instance., Get all evidence for a task., Integrates SDD contract enforcement into existing pipeline., Get the appropriate contract for a task type., Classify a prompt using the task router., Enforce tool policy for a task type. (+6 more)

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

### Community 75 - "📊 MAPA DE FLUJOS DE PERSISTENCIA ACTUALES"
Cohesion: 0.10
Nodes (19): 1. CHECKPOINT GUARDADO — `_save_checkpoint()` (agent_pipeline.py:213-275), 2. RESUME SESSION — `resume_session()` (agent_pipeline.py:496-554), 3. SESSION MANAGER API — Funciones públicas (session_manager.py:126-147), 4. LOCALCODE SERVER — Endpoints de sesión (localcode_server.py), 5. DESKTOP STARTUP — desktop_app.py, 6. SERVER STARTUP — localcode_server.py, 7. RUNTIME RECOVERY — Otros puntos de lectura/escritura, ✅ CRITERIOS DE ACEPTACIÓN POST-CAMBIO (+11 more)

### Community 76 - "EventBus"
Cohesion: 0.09
Nodes (13): Persiste el estado activo de la MÃ¡quina de Estados. Orden de autoridad…, EventBus, get_event_bus(), Bus de eventos persistente con patrón Observador (Event Sourcing)., Elimina un callback de escucha., Unit, Integration, Concurrency, and Lifecycle Tests for Real-Time SSE Endpoint…, TEST-007 (INV-008): Verifica que la ruta SSE esté registrada en…, TEST-001: Verifica suscripción, publicación y des-suscripción en EventBus. (+5 more)

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

### Community 86 - "PERSISTENCE CANONICALIZATION REPORT — Phase C3.1"
Cohesion: 0.11
Nodes (17): 5 Fallos Pre-existentes (NO regresión C3.1), 📝 ARCHIVOS MODIFICADOS, 📊 BASELINE (Pre-cambios), 🔧 CAMBIOS IMPLEMENTADOS, 🎯 CONCLUSIÓN, ✅ DEFINITION OF DONE — VERIFICADO, 🗂️ DEPENDENCIAS LEGACY RESTANTES (Post-C3.1), Flujos de Persistencia ANTES (PERSISTENCE_FLOW_BEFORE.md) (+9 more)

### Community 87 - "TestServerLifecycle"
Cohesion: 0.13
Nodes (8): Test G: Garantiza que el contrato del prompt CHAT permanece intacto con…, Test F: Desktop y backend obtienen la versión exactamente desde la misma fuente…, Test D: El puerto seleccionado por Desktop se asigna de forma explícita al…, Test B: Un backend con mismo workspace y versión pero distinto parent PID o…, Test C: Llamar a stop_server() múltiples veces es completamente seguro e…, Test E: Si el PID del proceso padre es reutilizado pero con diferente creation…, Test A: Dos instancias Desktop tienen instance_ids y puertos dedicados…, TestServerLifecycle

### Community 88 - "Task"
Cohesion: 0.09
Nodes (17): Any, Enum, Task data model for execution tracking., Convert to dictionary for serialization., Status of task execution., Workflow phases for tasks., Represents a task being executed., Check if task can still replan. (+9 more)

### Community 89 - "TaskRouter"
Cohesion: 0.18
Nodes (13): TaskContract, Any, Normalize diacritics / accents from text while preserving original text., Apply decision rules to determine task type. Returns: The determined TaskType, Classifies incoming prompts into task types., Calculate confidence score for classification. Returns: Confidence score…, Generate human-readable reason for classification. Returns: Reason string…, Classify a user prompt into a task type. Args: prompt: The user's input prompt… (+5 more)

### Community 90 - "ToolPolicyEnforcer"
Cohesion: 0.17
Nodes (7): Get all blocked tools for a task type., Enforce tool policy by filtering requested tools. Args: task_type: The task…, Controls tool access by task type., Initialize tool policies for each task type., Check if a tool is allowed for a task type. Args: task_type: The task type…, Get all allowed tools for a task type., ToolPolicyEnforcer

### Community 91 - ".handle_sdd_health"
Cohesion: 0.21
Nodes (7): get_sdd_health_dict(), Unit & Integration Tests for SDD Governance Telemetry Endpoint (GET…, UNIT: Verifica que get_sdd_health_dict() retorne las métricas exactas del…, UNIT: Verifica que si _is_parent_alive lanza una excepción, el dict degrade a…, INTEGRATION: Verifica que LocalCodeProxyHandler responde correctamente al…, INTEGRATION (R4): Verifica que handle_sdd_health emite la traza de log…, TestSDDHealthEndpoint

### Community 92 - ".build_contract"
Cohesion: 0.14
Nodes (9): Build a task contract using the canonical sdd_contract implementations., Comprueba el flujo real con 'Responde únicamente con OK.' y verifica las…, Caso A — CHAT: Directiva de conversación con prohibiciones primarias., Caso B — ACTION: Acción primaria con prohibiciones secundarias de verificadores., Caso C — ACTION: Mayúsculas y acentos con prohibición de linter/AST., Caso D — CHAT: Verbos mutacionales negados., Caso E — CHAT: Prohibición explícita de acción primaria., Prueba del prompt ACTION exacto del requerimiento 4. (+1 more)

### Community 93 - "test_e2e_real_desktop_lifecycle.py"
Cohesion: 0.22
Nodes (12): Popen, discover_desktop_backend(), get_health(), is_port_listening(), kill_process_tree(), skipUnless, Test E2E Real del ENTRYPOINT Real de CodeAgent Desktop (desktop_app.py).…, Test 1: Ejecuta desktop_app.py como proceso real y valida los metadatos de su… (+4 more)

### Community 94 - "tools.py"
Cohesion: 0.11
Nodes (18): buscar_en_internet(), clear_terminal_tasks_buffer(), consultar_db(), git_add(), git_commit(), git_diff(), git_push(), git_status() (+10 more)

### Community 95 - "TestTaskContractCanonical"
Cohesion: 0.10
Nodes (11): La evaluación de riesgo no debe perder información., Verifica que build_contract() use la autoridad canónica sdd_contract., TaskType debe importarse y usarse desde sdd_contract.task_types., Chat tasks deben retornar un wrapper sobre ChatTaskContract canónico., Action tasks deben retornar un wrapper sobre ActionTaskContract canónico., Feature tasks deben retornar un wrapper sobre FeatureTaskContract canónico., Propiedades de compatibilidad para tareas CHAT., Propiedades de compatibilidad para tareas ACTION. (+3 more)

### Community 96 - "INV-003 — Cross-Task Isolation"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-003 — Cross-Task Isolation, Preconditions, Related Modules, Related Tests (+4 more)

### Community 97 - "ExecutionLevel"
Cohesion: 0.12
Nodes (11): ExecutionLevel, Enum, Determina el Nivel de EjecuciÃ³n Ã³ptimo usando la evaluaciÃ³n de complejidad y…, State, Tests para semántica de fallos (STEP 7)., CASO A: SQLite disponible + sesión existe → SQLite., CASO B: SQLite disponible + sesión no existe + JSON existe → JSON → migrar →…, CASO C: SQLite disponible + ninguna sesión → sesión inexistente. (+3 more)

### Community 98 - "INV-004 — Intent Preservation"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-004 — Intent Preservation, Preconditions, Related Modules, Related Tests (+4 more)

### Community 99 - "TestDesktopPipelineVisualization"
Cohesion: 0.09
Nodes (13): handle_sse_events_dict(), Any, Serializa una instancia de Event o dict al formato Server-Sent Events (SSE)., Unit & Integration Tests for Desktop Real-Time Pipeline EventSource…, TEST-001: Verifica que localcode_claude_ui.html contenga las funciones de…, TEST-002: Verifica que la UI maneje eventos reales de STATE_ENTERED y…, TEST-003 (INV-008): Verifica que closePipelineSSE se invoque en el bloque…, TEST-004: Verifica la correlación end-to-end entre task_id en UI request,… (+5 more)

### Community 101 - "Repository Hygiene Report — Phase C1 (Safe Repository Hygiene)"
Cohesion: 0.14
Nodes (13): 1. Pruebas Unitarias e Integración (Pytest), 2. Verificación de Gobernanza SDD (`sdd_check.py`), 3. Smoke Test de Importaciones, Overview, Removed Duplicate Files, Removed Runtime Artifacts, Repository Hygiene Report — Phase C1 (Safe Repository Hygiene), Repository Size After (+5 more)

### Community 102 - "Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`), Rollback, SDD Validation (+1 more)

### Community 103 - "BenchmarkMetricsCollector"
Cohesion: 0.23
Nodes (7): BenchmarkMetricsCollector, Any, Registra la ejecución real de una herramienta por el agente., Calcula los KPIs cuantitativos agregados con datos reales., Genera un reporte formateado en Markdown con los KPIs cuantitativos., Colector y repositorio persistente de métricas cuantitativas agénticas., Registra el resultado de un ciclo de ejecución de la Máquina de Estados.

### Community 104 - "Change Impact Analysis — SDD Governance Telemetry Endpoint"
Cohesion: 0.20
Nodes (9): Certification Impact, Change Impact Analysis — SDD Governance Telemetry Endpoint, Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests (+1 more)

### Community 105 - "_atomic_write_file"
Cohesion: 0.18
Nodes (8): _atomic_write_file(), check_tool_permission(), PermissionLevel, Enum, Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, Niveles de autorización para la ejecución segura de herramientas agénticas., Valida si el permiso actual autoriza la ejecución de la herramienta., TestTechnicalQualityRefactor

### Community 106 - "INV-005 — Failure Containment"
Cohesion: 0.15
Nodes (12): Audit, Certification, Evidence, Forbidden Behavior, INV-005 — Failure Containment, Preconditions, Related Modules, Related Tests (+4 more)

### Community 108 - "SPEC-009 — SDD Governance Telemetry Endpoint"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-009 — SDD Governance Telemetry Endpoint, Testability (+1 more)

### Community 109 - "TestAgents"
Cohesion: 0.16
Nodes (11): crear_agente(), _detectar_modelo_local(), get_available_agents(), load_subagents_from_disk(), Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML…, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)., Enrutador automático mejorado con scoring ponderado., Detecta si el modelo es local (Ollama) basándose en el model_id. (+3 more)

### Community 110 - "SPEC-010 — Dynamic Feature Governance Automation"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-010 — Dynamic Feature Governance Automation, Testability (+1 more)

### Community 111 - "Change Impact Analysis — Feature Governance Automation"
Cohesion: 0.25
Nodes (7): Change Impact Analysis — Feature Governance Automation, Description, Feature Title, Invariants NOT Affected, Modified Components, Potentially Affected Invariants, Required Regression Tests

### Community 112 - "_ContractWrapper"
Cohesion: 0.20
Nodes (3): _ContractWrapper, Wrapper to provide canonical TaskContract instances with expected interface.…, Delegate attribute access to the canonical contract for any other properties.

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

### Community 126 - "main.py"
Cohesion: 0.16
Nodes (7): graphify, _construir_contexto_workspace(), get_herramientas(), Pipeline de agentes con smolagents de HuggingFace. El LLM usa CodeAgent para…, Convierte los nombres del UI en la lista de funciones @tool., Genera un bloque de contexto del workspace actual para inyectar en el…, TestMainPipeline

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

### Community 135 - "Legacy Retirement Report - Phase C3.2"
Cohesion: 0.14
Nodes (13): 1. `mis_agentes_inteligentes/rag_tools.py`, 2. `mis_agentes_inteligentes/orquestador_agente.py`, Before/After Summary, Compliance Verification, Components Preserved (Legacy Compatibility), Components Removed, Legacy Retirement Report - Phase C3.2, `mis_agentes_inteligentes/app.py` (+5 more)

### Community 136 - "Feature Runtime Evidence — SPEC-011"
Cohesion: 0.33
Nodes (5): 1. HTTP SSE Event Stream Telemetry, 2. Server Log Trace Evidence, 3. Automated Test Suite Execution, Feature Runtime Evidence — SPEC-011, Summary

### Community 137 - "CodeAgentBenchmarkSuite"
Cohesion: 0.18
Nodes (7): CodeAgentBenchmarkSuite, Any, CodeAgent v4.2 Reproducible Benchmark Suite Suite estandarizada de 5 tareas…, Exporta el reporte de benchmark en formato Markdown en…, Ejecutor automatizado de la Suite de 5 Benchmarks Reales de Ingeniería., Ejecuta la suite completa de 5 tareas y compila el informe comparativo., TestCodeAgentBenchmarkSuite

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

### Community 147 - "localcode_server.py"
Cohesion: 0.19
Nodes (9): _get_process_creation_time(), _is_parent_alive(), main(), _ps_file_dialog(), _ps_folder_dialog(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, _safe_print(), _start_parent_monitor() (+1 more)

### Community 148 - "ejecutar_agentes"
Cohesion: 0.21
Nodes (8): ejecutar_agentes(), Pipeline principal usando smolagents. FIX: el historial ya no se manda como…, patch, TestIntegrationPipeline, patch, Test de prevención de bypass para AgentPipeline en main.py. Verifica que si…, Garantiza que una excepción dentro de AgentPipeline.run_pipeline capture el…, TestPipelineBypassPrevention

### Community 149 - "SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG)"
Cohesion: 0.20
Nodes (9): Failure Behavior, Intent, Invariants, Observability, Postconditions, Preconditions, SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG), Testability (+1 more)

### Community 150 - "Feature Runtime Evidence — SPEC-013"
Cohesion: 0.22
Nodes (8): 1. Pre-Implementation TDD RED Baseline Evidence, 2. Controlled TDD GREEN Implementation Evidence, 3. Full Regression Test Suite Evidence, 4. Performance Benchmarks, 5. SDD Governance Verification, 6. Invariant Preservation Summary, Feature Runtime Evidence — SPEC-013, Summary

### Community 151 - "Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`), Rollback, SDD Validation (+1 more)

### Community 152 - "get_terminal_tasks_buffer"
Cohesion: 0.25
Nodes (5): get_terminal_tasks_buffer(), Any, Tests de aislamiento de telemetría entre ejecuciones consecutivas (Cross-Task…, Garantiza que la secuencia ACTION -> CHAT -> CHAT aísle completamente la…, TestCrossTaskTelemetryIsolation

### Community 154 - "Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView)"
Cohesion: 0.20
Nodes (9): Before, Canonical Component, Compatibility, Consumers Migrated, Deprecation Status, Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView), Rollback, SDD Validation (+1 more)

### Community 155 - "set_active_workspace"
Cohesion: 0.33
Nodes (3): Establece el directorio del espacio de trabajo activo de forma thread-safe para…, set_active_workspace(), TestWorkspaceIsolation

### Community 157 - "ThreadedTCPServer"
Cohesion: 0.24
Nodes (4): Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., ThreadedTCPServer, TestE2ESystemSuite, TestLocalCodeServer

### Community 158 - "JSONSessionRepository"
Cohesion: 0.24
Nodes (4): init_sessions_dir(), JSONSessionRepository, LEGACY: Inicializa directorio de sesiones JSON. Use DatabaseManager para…, Adaptador de persistencia basado en archivos JSON locales en disco.

### Community 159 - "session_manager.py"
Cohesion: 0.15
Nodes (10): _guardar_sesion_actual(), Guarda los datos de la sesión activa en disco., Comprime texto y asegura la validez de los bloques de código markdown., _truncar_markdown(), create_new_session(), delete_session(), list_sessions(), LEGACY SESSION COMPATIBILITY: Crea sesión JSON. DEPRECATED como autoridad… (+2 more)

### Community 160 - "test_localcode_server.py"
Cohesion: 0.39
Nodes (7): test_agent_chat_empty_prompt(), test_get_static_ui(), test_not_found_endpoint(), test_openapi_spec_endpoint(), test_prometheus_metrics_endpoint(), test_swagger_docs_endpoint(), test_workspace_tree_endpoint()

### Community 161 - "BaseSessionRepository"
Cohesion: 0.25
Nodes (3): BaseSessionRepository, ABC, Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio).

### Community 163 - "Task Contract Compatibility Matrix"
Cohesion: 0.33
Nodes (5): Consumer Analysis, Detailed Comparison Table, Migration Architecture Plan, Purpose, Task Contract Compatibility Matrix

### Community 165 - "load_session"
Cohesion: 0.25
Nodes (8): export_session_to_markdown(), load_session(), LEGACY SESSION COMPATIBILITY: Carga sesión JSON. DEPRECATED como autoridad…, LEGACY SESSION COMPATIBILITY: Guarda sesión JSON. DEPRECATED como autoridad…, LEGACY SESSION COMPATIBILITY: Renombra sesión JSON. DEPRECATED como autoridad…, LEGACY SESSION COMPATIBILITY: Exporta sesión JSON a Markdown. Función de…, rename_session(), save_session()

## Knowledge Gaps
- **553 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+548 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `ExecutionLevel`, `TestSDDConformance`, `CodeAgentRuntime`, `TestDiagnoseRootCauseAndVersion`, `TestAgentStateMachineController`, `agent_pipeline.py`, `CodeAgentBenchmarkSuite`, `.run`, `GraphContextEngine`, `EventBus`, `TestVerifierEvidenceAndWorkspaceIsolation`, `get_db_manager`, `TaskRouter`, `TestRuntimeRecoveryAndPauseSemantics`, `integrator.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `GraphContextEngine` connect `GraphContextEngine` to `ExecutionLevel`, `agent_pipeline.py`, `.run`, `_ContractWrapper`, `TaskRouter`, `AgentStateMachineController`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `ExecutionLevel` connect `ExecutionLevel` to `TestSDDConformance`, `TestDiagnoseRootCauseAndVersion`, `TestAgentStateMachineController`, `agent_pipeline.py`, `CodeAgentBenchmarkSuite`, `.run`, `GraphContextEngine`, `EventBus`, `_ContractWrapper`, `localcode_server.py`, `TestServerLifecycle`, `get_terminal_tasks_buffer`, `TaskRouter`, `AgentStateMachineController`, `TestRuntimeRecoveryAndPauseSemantics`, `.build_contract`, `TestTaskContractCanonical`, `integrator.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 29 inferred relationships involving `AgentStateMachineController` (e.g. with `GraphContextEngine` and `ActionTaskContract`) actually correct?**
  _`AgentStateMachineController` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestDesktopPipelineVisualization` and `TestE2ESystemSuite`) actually correct?**
  _`LocalCodeProxyHandler` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `ExecutionLevel` (e.g. with `GraphContextEngine` and `ActionTaskContract`) actually correct?**
  _`ExecutionLevel` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `SDDIntegrator` (e.g. with `EvidenceLogger` and `Diagnosis`) actually correct?**
  _`SDDIntegrator` has 19 INFERRED edges - model-reasoned connections that need verification._