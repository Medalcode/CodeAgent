# Graph Report - CodeAgent  (2026-08-28)

## Corpus Check
- 88 files · ~83,507 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1166 nodes · 1754 edges · 101 communities (76 shown, 25 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 307 edges (avg confidence: 0.78)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `264a7f85`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- session_manager.py
- LocalCodeProxyHandler
- An�lisis de Violaciones del SDD Contract System
- CodeAgentRuntime
- main.py
- Changelog
- 💻 CodeAgent (v6.11 Enterprise)
- tools.py
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
- is_sensitive_command
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
- ToolType
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
- VerificationEngine
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
- TestVerifierEvidenceAndWorkspaceIsolation
- mis_agentes_inteligentes/main
- Dependencies
- [6.11.0] - 2026-08-28
- [6.2.0] - 2026-08-28
- Testing Strategy
- Security Considerations
- [6.3.0] - 2026-08-28
- Diagnosis
- Audit Results by Requirement
- UIManager
- SDDIntegrator
- tool
- integrator.py
- TaskRouter
- ToolPolicyEnforcer
- TestFeedbackLoopAndToolEvents
- agent_pipeline.py
- TestSDDConformance
- TestRegressionSuite
- .to_dict
- TestRuntimeAndStorage
- TestStateCheckpointing
- TestTaskTimeoutSafeguardAndCancellation
- consultar_db

## God Nodes (most connected - your core abstractions)
1. `AgentStateMachineController` - 41 edges
2. `SDDIntegrator` - 32 edges
3. `DatabaseManager` - 27 edges
4. `LocalCodeProxyHandler` - 25 edges
5. `CodeAgentRuntime` - 24 edges
6. `TaskRouter` - 23 edges
7. `Changelog` - 22 edges
8. `ToolType` - 21 edges
9. `tool()` - 19 edges
10. `TestSDDConformance` - 18 edges

## Surprising Connections (you probably didn't know these)
- `ExecutionLevel` --uses--> `TaskRouter`  [INFERRED]
  mis_agentes_inteligentes/agent_pipeline.py → sdd_contract/task_router.py
- `TestDiagnoseRootCauseAndVersion` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_diagnose_root_cause.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestFeedbackLoopAndToolEvents` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_feedback_loop.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestRuntimeRecoveryAndPauseSemantics` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_runtime_recovery.py → mis_agentes_inteligentes/agent_pipeline.py
- `TestStateCheckpointing` --uses--> `ExecutionLevel`  [INFERRED]
  tests/test_state_checkpointing.py → mis_agentes_inteligentes/agent_pipeline.py

## Import Cycles
- None detected.

## Communities (101 total, 25 thin omitted)

### Community 0 - "session_manager.py"
Cohesion: 0.06
Nodes (14): BaseSessionRepository, create_new_session(), export_session_to_markdown(), init_sessions_dir(), JSONSessionRepository, load_session(), ABC, Interfaz abstracta para la gestión de sesiones de chat (Patrón Repositorio). (+6 more)

### Community 1 - "LocalCodeProxyHandler"
Cohesion: 0.07
Nodes (17): _inc_metric(), LocalCodeProxyHandler, main(), _ps_file_dialog(), _ps_folder_dialog(), Imprime texto de forma segura sin crash por UnicodeEncodeError en Windows…, Servidor TCP/HTTP multihilo no bloqueante para peticiones concurrentes., _safe_print() (+9 more)

### Community 2 - "An�lisis de Violaciones del SDD Contract System"
Cohesion: 0.05
Nodes (36): 1.1 Clasificaci�n Incorrecta (Requirement 1), 1.2 Fallback a LEVEL_3_FEATURE (Requirement 1), 1.3?? CHAT Fast Path (Requirement 2), 1.4 Verificaci�n ejecutada para CHAT (Requirement 2), 1.5 Replanning ejecutado para CHAT (Requirement 2), 2.1 Verificaci�n ejecutada para ACTION sin solicitud expl�cita (Requirement 3), 2.2 Ejecuci�n repetida del programa (Requirement 3), 2.3 Ruff FAIL hace fallar ACTION aunque no sea parte del contrato (Requirement 3) (+28 more)

### Community 3 - "CodeAgentRuntime"
Cohesion: 0.16
Nodes (9): CodeAgentRuntime, Any, Motor de ejecución autónomo desacoplado para CodeAgent v6.1. Gestión semántica…, Obtiene la información de la tarea, su estado actual y el último checkpoint., Lista las tareas recientes guardadas en SQLite., Pausa una tarea activa sin marcarla como cancelada., Reanuda una tarea pausada desde su último checkpoint en SQLite., Cancela definitivamente una tarea. (+1 more)

### Community 4 - "main.py"
Cohesion: 0.05
Nodes (30): graphify, crear_agente(), _detectar_modelo_local(), get_available_agents(), get_model(), load_subagents_from_disk(), Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML… (+22 more)

### Community 5 - "Changelog"
Cohesion: 0.20
Nodes (9): [4.2.0] - 2026-08-27, [6.0.0] - 2026-08-28, [6.10.0] - 2026-08-28, [6.4.0] - 2026-08-28, Added, Added, Added, Added (+1 more)

### Community 6 - "💻 CodeAgent (v6.11 Enterprise)"
Cohesion: 0.10
Nodes (19): Arquitectura, 🏗️ Arquitectura del Sistema (5 Capas Principales), Benchmarks (3 niveles), ✨ Características Principales (v3.0 Enterprise), 💻 CodeAgent (v6.11 Enterprise), 🚀 Instalación y Ejecución, Knowledge Graph, Opción 1: Arranque Rápido (Recomendado para Windows) (+11 more)

### Community 7 - "tools.py"
Cohesion: 0.13
Nodes (12): buscar_en_internet(), check_tool_permission(), clear_terminal_tasks_buffer(), git_add(), guardar_reporte(), PermissionLevel, Enum, Archiva el análisis para memoria a largo plazo. Args: analisis: El texto del… (+4 more)

### Community 8 - "mis_agentes_inteligentes/tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes/tools, tools.consultar_db, tools.guardar_reporte, tools.consultar_github, tools.leer_repositorio_github, tools.leer_archivo_github, tools.listar_directorio_local, tools.leer_archivo_local (+10 more)

### Community 9 - "mis_agentes_inteligentes.tools"
Cohesion: 0.11
Nodes (18): mis_agentes_inteligentes.tools, mis_agentes_inteligentes.tools.consultar_db, mis_agentes_inteligentes.tools.guardar_reporte, mis_agentes_inteligentes.tools.consultar_github, mis_agentes_inteligentes.tools.leer_repositorio_github, mis_agentes_inteligentes.tools.leer_archivo_github, mis_agentes_inteligentes.tools.listar_directorio_local, mis_agentes_inteligentes.tools.leer_archivo_local (+10 more)

### Community 10 - "AgentStateMachineController"
Cohesion: 0.10
Nodes (20): AgentStateMachineController, _get_phase_cognitive_directive(), Any, Controlador determinista de estados, enrutador adaptativo y gestor de…, Persiste el estado activo de la Máquina de Estados en la sesión JSON., Ejecuta el ciclo agéntico mediante la Máquina de Estados Determinista., Alias de compatibilidad hacia atrás para la versión v3.0., Reanuda la ejecución desde una sesión JSON o checkpoint de SQLite. (+12 more)

### Community 11 - "_detectar_raiz_proyecto"
Cohesion: 0.12
Nodes (12): _detectar_raiz_proyecto(), get_active_workspace(), leer_archivo_local(), listar_directorio_local(), obtener_contexto_workspace(), Devuelve el espacio de trabajo activo de forma thread-safe., Sube directorios hasta encontrar un marcador de raíz de repo (.git, AGENTS.md,…, Lista los archivos y carpetas de un directorio local y devuelve el contenido… (+4 more)

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
Cohesion: 0.16
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
Cohesion: 0.29
Nodes (3): _atomic_write_file(), Escribe un archivo de forma atómica con limpieza segura de temporales en caso…, TestTechnicalQualityRefactor

### Community 28 - "ADR-001: Selección de smolagents como Motor ReAct"
Cohesion: 0.40
Nodes (4): ADR-001: Selección de smolagents como Motor ReAct, Consecuencias, Contexto, Decisión

### Community 29 - "ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo"
Cohesion: 0.40
Nodes (4): ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo, Consecuencias, Contexto, Decisión

### Community 30 - "ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM"
Cohesion: 0.40
Nodes (4): ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM, Consecuencias, Contexto, Decisión

### Community 31 - "is_sensitive_command"
Cohesion: 0.29
Nodes (4): is_command_approved(), is_sensitive_command(), pre_approve_command(), TestTerminalHITLApproval

### Community 32 - "EventBus"
Cohesion: 0.15
Nodes (10): Event, EventBus, Any, Bus de eventos persistente con patrón Observador (Event Sourcing)., Registra un callback de escucha de eventos en tiempo real., Elimina un callback de escucha., Persiste el evento en SQLite y notifica a todos los suscriptores activos., Obtiene la corriente de eventos guardados para reconstruir el estado visual en… (+2 more)

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

### Community 47 - "ToolType"
Cohesion: 0.08
Nodes (18): Get the appropriate contract for a task type., ActionTaskContract, FeatureTaskContract, ABC, Task Contract implementations for SDD. Enforces behavioral boundaries per task…, Base interface for all task contracts., Return set of tools allowed for this task type., Return True if verification is allowed for this task. (+10 more)

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

### Community 62 - "VerificationEngine"
Cohesion: 0.10
Nodes (22): Enum, Core domain types for SDD Contract system., Task classification types., Verification result states., TaskType, VerificationState, Any, Verification Engine for validating task results against criteria. (+14 more)

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

### Community 83 - "Diagnosis"
Cohesion: 0.10
Nodes (17): Generate a new plan based on diagnosis., Determine if replanning should occur., Diagnosis, Plan, PlanStatus, PlanStep, Enum, Replanner with evidence-based triggers. (+9 more)

### Community 84 - "Audit Results by Requirement"
Cohesion: 0.08
Nodes (24): Audit Results by Requirement, Conclusion, Conformance Audit: SDD Contract System, Conformance Matrix, Executive Summary, IMMEDIATE (Blocker), MEDIUM TERM (High Priority), Parallel Architecture Risk (+16 more)

### Community 85 - "UIManager"
Cohesion: 0.10
Nodes (15): Enum, UI Manager for enforcing single-instance policy., Represents a UI instance., Convert to dictionary for serialization., Manages UI lifecycle with single-instance policy., Create a new UI instance. Args: session_id: The current session ID ui_type:…, Update an existing UI instance. Does NOT create new instances. Args:…, Mark the UI instance as closed. (+7 more)

### Community 86 - "SDDIntegrator"
Cohesion: 0.11
Nodes (14): Any, Ensure only one UI instance exists., Update existing UI instance., Get all evidence for a task., Integrates SDD contract enforcement into existing pipeline., Classify a prompt using the task router., Enforce tool policy for a task type., Create a new task with the appropriate contract. (+6 more)

### Community 87 - "tool"
Cohesion: 0.15
Nodes (14): _bm25_score(), indexar_directorio_local(), init_chroma(), preguntar_a_repositorio(), Calcula una puntuación BM25 léxica simplificada basada en frecuencia de…, Realiza una búsqueda semántica sobre los archivos previamente indexados con…, Inicializa la base de datos ChromaDB y el modelo de embeddings., Escanea todos los archivos de código en un directorio local y los indexa en… (+6 more)

### Community 88 - "integrator.py"
Cohesion: 0.13
Nodes (13): Integrator for SDD contract enforcement into existing agent_pipeline.py., Enum, Task data model for execution tracking., Status of task execution., Workflow phases for tasks., Represents a task being executed., Check if task can still replan., Mark task as verified with results. (+5 more)

### Community 89 - "TaskRouter"
Cohesion: 0.20
Nodes (10): Any, Task Router for classifying user prompts into task types., Classifies incoming prompts into task types., Apply decision rules to determine task type. Returns: The determined TaskType, Calculate confidence score for classification. Returns: Confidence score…, Generate human-readable reason for classification. Returns: Reason string…, Classify a user prompt into a task type. Args: prompt: The user's input prompt…, Extract classification indicators from prompt. Returns: Dictionary of indicator… (+2 more)

### Community 90 - "ToolPolicyEnforcer"
Cohesion: 0.13
Nodes (10): Tool Policy Enforcer for controlling tool access by task type., Get all blocked tools for a task type., Policy defining allowed tools for a task type., Enforce tool policy by filtering requested tools. Args: task_type: The task…, Controls tool access by task type., Initialize tool policies for each task type., Check if a tool is allowed for a task type. Args: task_type: The task type…, Get all allowed tools for a task type. (+2 more)

### Community 91 - "TestFeedbackLoopAndToolEvents"
Cohesion: 0.18
Nodes (6): ComplexityRiskEvaluator, Evaluador determinista de complejidad, alcance e impacto en workspace., Determina el Nivel de Ejecución óptimo usando la evaluación de complejidad y…, TaskContract, object, TestFeedbackLoopAndToolEvents

### Community 92 - "agent_pipeline.py"
Cohesion: 0.21
Nodes (6): ExecutionLevel, Enum, CodeAgent v4.0 Deterministic State Machine Controller & Adaptive Pipeline…, TaskType, CodeAgent Benchmark & Quality Metrics Engine Registra, calcula y persiste…, TestAgentPipeline

### Community 93 - "TestSDDConformance"
Cohesion: 0.17
Nodes (3): ChatTaskContract, Contract for CHAT tasks - conversational only., TestSDDConformance

### Community 94 - "TestRegressionSuite"
Cohesion: 0.20
Nodes (5): git_diff(), git_status(), Muestra el estado del repositorio Git (archivos modificados, untracked, etc).…, Muestra los cambios no commiteados en el repositorio. Args: ruta_repo: Ruta del…, TestRegressionSuite

### Community 95 - ".to_dict"
Cohesion: 0.29
Nodes (5): Any, Convert to dictionary for serialization., Convert to dictionary for serialization., Result of task execution., TaskResult

## Knowledge Gaps
- **183 isolated node(s):** `start_hub.sh script`, `graphify`, `What a good test is`, `Seams — where tests go`, `Anti-patterns` (+178 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentStateMachineController` connect `AgentStateMachineController` to `EventBus`, `session_manager.py`, `CodeAgentBenchmarkSuite`, `CodeAgentRuntime`, `TestStateCheckpointing`, `TestVerifierEvidenceAndWorkspaceIsolation`, `TestRuntimeRecoveryAndPauseSemantics`, `BenchmarkMetricsCollector`, `TaskRouter`, `TestFeedbackLoopAndToolEvents`, `agent_pipeline.py`, `TestSDDConformance`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `TaskRouter` connect `TaskRouter` to `AgentStateMachineController`, `SDDIntegrator`, `integrator.py`, `TestFeedbackLoopAndToolEvents`, `agent_pipeline.py`, `TestSDDConformance`, `VerificationEngine`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `CodeAgentRuntime` connect `CodeAgentRuntime` to `EventBus`, `LocalCodeProxyHandler`, `TestRuntimeAndStorage`, `TestTaskTimeoutSafeguardAndCancellation`, `AgentStateMachineController`, `TestVerifierEvidenceAndWorkspaceIsolation`, `DatabaseManager`, `TestRuntimeRecoveryAndPauseSemantics`, `database.py`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `AgentStateMachineController` (e.g. with `TaskRouter` and `CodeAgentBenchmarkSuite`) actually correct?**
  _`AgentStateMachineController` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `SDDIntegrator` (e.g. with `EvidenceLogger` and `Diagnosis`) actually correct?**
  _`SDDIntegrator` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `DatabaseManager` (e.g. with `Event` and `EventBus`) actually correct?**
  _`DatabaseManager` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `LocalCodeProxyHandler` (e.g. with `TestE2ESystemSuite` and `TestLocalCodeServer`) actually correct?**
  _`LocalCodeProxyHandler` has 2 INFERRED edges - model-reasoned connections that need verification._