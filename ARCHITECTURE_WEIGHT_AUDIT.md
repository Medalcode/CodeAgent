# Deep Architecture & Complexity Weight Audit — CodeAgent v6.1 (SDD Certified)

## Executive Summary

Este documento presenta una auditoría de arquitectura profunda y análisis de complejidad accidental del proyecto **CodeAgent**. 

CodeAgent ha evolucionado a través de múltiples iteraciones mayores (v1.0 CLI básico → v3.5 Desktop → v4.0 State Machine → v5.0 SDD Certification → v6.1 Local-Only Architecture & AST Subgraph RAG). Si bien esta evolución ha introducido un riguroso sistema de **Gobernanza SDD (Spec-Driven Development)** con 8 invariantes (`INV-001` a `INV-008`) y 5 especificaciones activas (`SPEC-009` a `SPEC-013`), el crecimiento incremental ha dejado un peso de **complejidad accidental significativo**, artefactos de runtime persistidos en el repositorio, duplicación de responsabilidades y módulos "God Object".

### Diagnóstico Cuantitativo del Repositorio
- **Archivos totales en código fuente**: ~140 archivos (excluyendo entornos virtuales `.venv`).
- **Módulos con alto riesgo (God Modules)**: 5 archivos concentran >4,000 líneas de código y hasta 10 responsabilidades mezcladas cada uno (`agent_pipeline.py`, `localcode_server.py`, `tools.py`, `sdd_check.py`, `desktop_app.py`).
- **Artefactos de runtime en Git**: 1 base de datos SQLite de 12.8 MB (`codeagent_desktop.db`), 40+ archivos temporales (`tmp*`), bases de datos auxiliares (`MisEventos.db`), reportes JSON masivos (`metrics_benchmarks.json`) y decenas de archivos de sesión JSON (`sesiones/*.json`).
- **Higiene de entornos**: Existe un entorno virtual secundario anidado (`mis_agentes_inteligentes/venv`) que duplica paquetes masivos (PyTorch, SciPy, Pandas, LiteLLM) dentro del directorio de código fuente del proyecto.
- **Abstracciones Huérfanas / Paralelas**: Redefinición del enum `TaskType` y dataclasses `TaskContract` en `agent_pipeline.py` en paralelo a `sdd_contract/`, mientras la clase `SDDIntegrator` (`sdd_contract/integrator.py`) permanece desacoplada sin importarse en el pipeline principal.

### Principio Rector
**NO se modificará ni eliminará código durante esta fase.** El objetivo de esta auditoría es proporcionar el mapa definitivo para preservar al 100% las garantías del sistema SDD (contratos, invariantes, trazabilidad y verificabilidad) mientras se elimina el peso muerto accidental acumulado.

---

## Current Architecture Map

El sistema se organiza en 5 capas conceptuales principales:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. ENTRY POINTS & DESKTOP RUNNERS                                                      │
│    - desktop_app.py (PyWebView Desktop IDE Runner & Process Lifecycle Manager)        │
│    - Iniciar_OpenCode.bat / Lanzar_CodeAgent_Desktop.bat (Windows Launch Scripts)      │
│    - orquestador_agente.py (Legacy Supervisor Script)                                  │
│    - mis_agentes_inteligentes/main.py (CLI Runner) & app.py (Streamlit UI)             │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. HTTP & PRESENTATION LAYER                                                           │
│    - mis_agentes_inteligentes/localcode_server.py (Multi-threaded HTTP/TCP Server)    │
│    - mis_agentes_inteligentes/localcode_claude_ui.html (Frontend JetBrains IDE HTML)   │
│    - localcode_claude_ui.html (Root duplicate HTML)                                    │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. SDD GOVERNANCE & CONTRACT ENFORCEMENT                                               │
│    - sdd_contract/ (task_router, task_contract, tool_policy, ui_manager,               │
│                       evidence_logger, verification_engine, replanner, task_types)    │
│    - scripts/sdd_check.py (Automated Verification CLI & Traceability Engine)           │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. AGENT PIPELINE & INTELLIGENCE CORE                                                  │
│    - mis_agentes_inteligentes/agent_pipeline.py (AgentStateMachineController & Stages) │
│    - mis_agentes_inteligentes/agents.py (smolagents & LiteLLM Model Integration)       │
│    - mis_agentes_inteligentes/graph_context.py (Graphify AST Subgraph RAG - SPEC-013)  │
│    - mis_agentes_inteligentes/tools.py (System, Terminal & GitHub Tools + HITL)       │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. STORAGE, EVENT SOURCING & RUNTIME STATE                                             │
│    - mis_agentes_inteligentes/storage/database.py (DatabaseManager / SQLite WAL)      │
│    - mis_agentes_inteligentes/runtime/event_bus.py (EventBus & Event Sourcing)       │
│    - mis_agentes_inteligentes/session_manager.py (Legacy JSON Sessions)               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Essential Complexity

La complejidad esencial abarca los requerimientos y mecanismos strictly necesarios para preservar el comportamiento autónomo, determinista y seguro de CodeAgent:

1. **Determinismo y Máquina de Estados (INIT -> EXPLORE -> EXECUTE -> VERIFY -> REPLAN / DIAGNOSE)**:
   - Necesario para evitar bucles infinitos no controlados del LLM y garantizar que cada cambio pase por etapas de análisis AST, edición acotada y verificación explícita.
2. **Sistema de Contratos SDD y Clasificación de Tareas (`TaskRouter`)**:
   - Clasificación determinista del prompt en `CHAT`, `ACTION`, `FEATURE` y `RECOVERY`. Crucial para aplicar restricciones de herramientas e impedir ejecuciones de código innecesarias (Fast-Path `CHAT`).
3. **Restricción de Herramientas (`ToolPolicyEnforcer`) e Invariantes de Aislamiento**:
   - Garantizar que tareas `CHAT` no tengan acceso a herramientas de modificación (`INV-006`), que las modificaciones requieran verificación (`INV-007`) y que cada sesión mantenga aislamiento de espacio de trabajo (`INV-003`).
4. **Seguridad Lifecycle Desktop e Instancia Única de UI (`UIManager` / `INV-008`)**:
   - Prevenir colisiones de puertos TCP, múltiples ventanas de escritorio interfiriendo con el mismo espacio de trabajo o procesos huérfanos de Ollama/Backend.
5. **Recuperación Ante Fallos Basada en Evidencia (`EvidenceLogger` / `VerificationEngine` / `Replanner`)**:
   - Registrar pruebas objetivas de fallos sintácticos (`ast.parse`) y de ejecución de pruebas (`pytest`), permitiendo diagnósticos precisos en lugar de re-intentos a ciegas del LLM.
6. **AST Subgraph Context Retrieval (`SPEC-013` / `graph_context.py`)**:
   - Extracción acotada de contexto (1-hop / 2-hop) basada en la topología de código Graphify para alimentar al LLM con la menor cantidad posible de tokens sin perder dependencias cruzadas.

---

## Accidental Complexity

La complejidad accidental corresponde a elementos añadidos por crecimiento desordenado, iteraciones pasadas o falta de higiene en la estructura:

1. **Entorno Virtual Anidado (`mis_agentes_inteligentes/venv`)**:
   - Un directorio entero de entorno virtual de Python dentro del paquete fuente `mis_agentes_inteligentes/`. Contiene gigabytes de binarios (`torch_cpu.dll` de 305 MB, `pyarrow.dll`, `scipy`, etc.). Surgió porque `Iniciar_OpenCode.bat` crea `venv` ahí si no detecta `.venv` en la raíz.
2. **Persistencia de Bases de Datos SQLite en Git**:
   - `mis_agentes_inteligentes/codeagent_desktop.db` (12.8 MB) y sus archivos `-shm` / `-wal` están commiteados en el repositorio, al igual que `MisEventos.db` en la raíz y en el subdirectorio.
3. **Residuos de Ejecución Temporales (`tmp*` y `sesiones/*.json`)**:
   - Más de 40 archivos de texto temporales creados por la herramienta de edición y pruebas (`tmpctg4en8x`, `tmpb82g9jmk`, etc.) no son limpiados tras la ejecución y quedan en disco.
   - Decenas de archivos JSON en `mis_agentes_inteligentes/sesiones/` pertenecientes a ejecuciones pasadas.
4. **Duplicación de Archivos de Interfaz Gráfica (HTML)**:
   - `localcode_claude_ui.html` (60 KB, 1694 líneas) en la raíz del proyecto es casi idéntico a `mis_agentes_inteligentes/localcode_claude_ui.html` (58 KB, 1646 líneas).
5. **Redefinición Paralela de Abstracciones SDD**:
   - `mis_agentes_inteligentes/agent_pipeline.py` re-define su propia versión de `TaskType(Enum)` y `TaskContract(dataclass)` en lugar de importar y utilizar las abstracciones canónicas definidas en `sdd_contract/task_types.py` y `sdd_contract/task_contract.py`.
6. **Abstracción Huérfana `SDDIntegrator`**:
   - `sdd_contract/integrator.py` define una fachada (`SDDIntegrator`) diseñada para conectar todos los servicios SDD. Sin embargo, ningún módulo principal (`agent_pipeline.py`, `localcode_server.py`, `desktop_app.py`) la instancia ni la importa.
7. **Coexistencia de Dos Sistemas de RAG**:
   - `mis_agentes_inteligentes/rag_tools.py` (basado en ChromaDB + BM25) coexiste con `graph_context.py` (basado en AST Graphify / SPEC-013). `rag_tools.py` representa un enfoque anterior que genera costo de mantenimiento superfluo.
8. **Scripts de Supervisión y UI Obsoletos**:
   - `orquestador_agente.py` (script raíz de 495 líneas para supervisar modelos Ollama directamente) y `app.py` (interfaz Streamlit legacy) compiten conceptualmente con `desktop_app.py` y `localcode_server.py`.

---

## SDD Components That Must Be Preserved

Los siguientes componentes forman el núcleo de gobernanza SDD y **BAJO NINGUNA CIRCUNSTANCIA deben eliminarse ni alterarse funcionalmente**:

1. **`sdd_contract/task_router.py`**: Autoridad central determinista para clasificar prompts en `CHAT`, `ACTION`, `FEATURE` y `RECOVERY`. Preserva `INV-002`.
2. **`sdd_contract/tool_policy.py`**: Motor de aplicación de políticas de herramientas permitidas/bloqueadas por tipo de tarea. Preserva `INV-006`.
3. **`sdd_contract/ui_manager.py`**: Controlador de política de instancia única de interfaz de usuario. Preserva `INV-008`.
4. **`sdd_contract/evidence_logger.py`**: Colector y formateador de evidencia de fallos y replanificación. Preserva `INV-004` e `INV-005`.
5. **`sdd_contract/verification_engine.py`**: Evaluador de criterios formales de verificación de código y pruebas. Preserva `INV-007`.
6. **`sdd_contract/replanner.py`**: Generador de planes de reparación basados strictly en diagnóstico empírico.
7. **`scripts/sdd_check.py`**: CLI de auditoría automatizada que valida la trazabilidad (`specs/traceability.md`), existencia de invariantes (`INV-001`..`INV-008`) y especificaciones (`SPEC-009`..`SPEC-013`). Preserva la verificabilidad del pipeline.
8. **`specs/` y `audits/`**: Directivas formales de especificación, matrices de trazabilidad y reportes de certificación que constituyen la evidencia estática de gobernanza.

---

## Candidate Components for Simplification

Componentes que pueden simplificarse, consolidarse o unificarse **sin romper contratos ni invariantes**:

1. **Consolidación de `TaskType` y `TaskContract`**:
   - Eliminar las definiciones duplicadas de `TaskType` y `TaskContract` en `agent_pipeline.py`.
   - Hacer que `agent_pipeline.py` importe directamente los tipos desde `sdd_contract.task_types` y `sdd_contract.task_contract`.
2. **Unificación o Eliminación de `SDDIntegrator` (`sdd_contract/integrator.py`)**:
   - Si `agent_pipeline.py` ya interactúa directamente con `TaskRouter` y `VerificationEngine`, la fachada `SDDIntegrator` de 124 líneas en `integrator.py` es redundante y puede integrarse directamente o removerse si no aporta valor estructural.
3. **Depreciación de `mis_agentes_inteligentes/rag_tools.py`**:
   - Reemplazar completamente cualquier uso remanente de ChromaDB/BM25 RAG por la solución canónica de AST Subgraph RAG (`graph_context.py` / `SPEC-013`).
4. **Unificación de Persistencia de Sesiones**:
   - Eliminar la dependencia de archivos JSON sueltos en `session_manager.py` / `sesiones/` y consolidar todo el estado de sesión y checkpointing en `DatabaseManager` (`storage/database.py`).
5. **Eliminación de UI y Frontend Duplicados**:
   - Mantener una única copia canónica de `localcode_claude_ui.html` dentro de `mis_agentes_inteligentes/` y eliminar la copia duplicada en la raíz del proyecto.
6. **Consolidación de Script de Supervisión Legacy (`orquestador_agente.py`)**:
   - Mover la lógica útil de evaluación/benchmarking de `orquestador_agente.py` a `benchmark_suite.py` y marcar el script raíz como deprecado.

---

## Large / High-Risk Modules

A continuación se detallan los 5 módulos más voluminosos y complejos del proyecto:

| Módulo | Líneas | Resps. Actuales | Dependencias Clave | Dependientes Clave | Riesgo Modif. | Prioridad Refactor |
| :--- | :---: | :---: | :--- | :--- | :---: | :---: |
| `mis_agentes_inteligentes/agent_pipeline.py` | 933 | ~10 | `agents`, `tools`, `graph_context`, `event_bus`, `database`, `sdd_contract` | `localcode_server.py`, `runtime.py`, `app.py`, `test_*.py` | **MUY ALTO** | **P1** |
| `mis_agentes_inteligentes/localcode_server.py` | 941 | ~10 | `agent_pipeline`, `http.server`, `threading`, `urllib`, `version` | `desktop_app.py`, `test_localcode_server.py`, `test_e2e_*.py` | **ALTO** | **P1** |
| `mis_agentes_inteligentes/tools.py` | 736 | ~10 | `subprocess`, `os`, `ast`, `requests`, `git` | `agent_pipeline.py`, `agents.py`, `test_tools.py` | **ALTO** | **P2** |
| `scripts/sdd_check.py` | 613 | ~6 | `ast`, `re`, `pathlib`, `argparse` | Workflow CI, `test_sdd_checker_engine.py` | **MEDIO** | **P3** |
| `desktop_app.py` | 455 | ~7 | `pywebview`, `subprocess`, `socket`, `ctypes`, `localcode_server` | Batch scripts, `test_desktop_app.py`, `test_e2e_*.py` | **MEDIO** | **P2** |

### Análisis Detallado de Responsabilidades por Módulo

#### 1. `mis_agentes_inteligentes/agent_pipeline.py`
- **Responsabilidad Actual**: Controlador orquestador central de la Máquina de Estados agéntica.
- **Mezcla de Responsabilidades**:
  1. Definición local de tipos `TaskType`, `TaskContract`, `State`.
  2. Generación de directivas cognitivas por fase (`_get_phase_cognitive_directive`).
  3. Evaluación de complejidad y riesgo (`ComplexityRiskEvaluator`).
  4. Extracción de contexto AST Graphify (`_stage_explorer`).
  5. Invocación y ejecución de herramientas ReAct (`_stage_executor`).
  6. Ejecución de verificadores sintácticos y de pruebas (`_stage_verifier`).
  7. Diagnóstico de causa raíz (`_stage_diagnoser`).
  8. Replanteamiento de estrategia (`_stage_replanner`).
  9. Control central del loop, persistencia y eventos (`AgentStateMachineController`).
  10. Registro y cálculo de métricas de benchmark.
- **Estrategia de División Recomendada**:
  Separar en un sub-paquete `mis_agentes_inteligentes/pipeline/` conteniendo:
  - `state_machine.py` (Solo el orquestador `AgentStateMachineController`).
  - `directives.py` (Generador de prompts/directivas cognitivas).
  - `evaluator.py` (Evaluación de complejidad y routing).
  - `stages/` (`explorer.py`, `executor.py`, `verifier.py`, `diagnoser.py`, `replanner.py`).

#### 2. `mis_agentes_inteligentes/localcode_server.py`
- **Responsabilidad Actual**: Servidor HTTP/TCP nativo y streamer SSE para la interfaz Desktop/Web.
- **Mezcla de Responsabilidades**:
  1. Handler HTTP multihilo (`LocalCodeProxyHandler`).
  2. Router de endpoints REST (`/api/prompt`, `/api/health`, etc.).
  3. Engine de streaming SSE Server-Sent Events (`/api/pipeline/events`).
  4. Servidor de archivos estáticos HTML/JS/CSS.
  5. Monitor de proceso padre (auto-terminación si el proceso Desktop muere).
  6. Diálogos GUI nativos mediante PowerShell en Windows (`_ps_file_dialog`).
  7. Lógica de impresión segura anti-UnicodeEncodeError en Windows.
  8. Servidor CLI runner (`main()`).
- **Estrategia de División Recomendada**:
  Separar en un sub-paquete `mis_agentes_inteligentes/server/`:
  - `handler.py` (Handler HTTP principal).
  - `routes.py` (Enrutamiento de API REST).
  - `sse.py` (Streaming de eventos SSE).
  - `static.py` (Servidor de archivos estáticos).
  - `process_monitor.py` (Monitoreo de proceso padre).

#### 3. `mis_agentes_inteligentes/tools.py`
- **Responsabilidad Actual**: Conjunto monolítico de herramientas del agente y sistema HITL.
- **Mezcla de Responsabilidades**:
  1. Herramientas I/O de archivos (`leer_archivo_local`, `escribir_archivo_local`, etc.).
  2. Ejecución terminal (`ejecutar_comando_terminal`).
  3. Verificación sintáctica post-edición (`_verificar_sintaxis_post_edicion`).
  4. Lógica de escritura atómica en disco (`_atomic_write_file`).
  5. Autodetector de raíz de proyecto (`_detectar_raiz_proyecto`).
  6. Contexto thread-safe de workspace activo (`set_active_workspace`).
  7. Sistema HITL de autorización de comandos terminales (`PermissionLevel`, etc.).
  8. Herramientas de integración con GitHub API.
  9. Archivador de análisis a memoria a largo plazo.
- **Estrategia de División Recomendada**:
  Separar en `mis_agentes_inteligentes/tools/`:
  - `file_tools.py` (Operaciones de archivos y edición).
  - `terminal_tools.py` (Ejecución terminal y permisos HITL).
  - `github_tools.py` (API de GitHub).
  - `workspace_context.py` (Gestión de workspace activo).

---

## Repository Hygiene Problems

Se identifican los siguientes problemas críticos de higiene de repositorio que deben corregirse en la fase de limpieza:

```
[DEBT-HYGIENE-01] Entorno virtual anidado en mis_agentes_inteligentes/venv (PyTorch/SciPy/Pandas)
[DEBT-HYGIENE-02] Base de datos SQLite activa de 12.8 MB commiteada: mis_agentes_inteligentes/codeagent_desktop.db
[DEBT-HYGIENE-03] Archivos WAL/SHM de SQLite commiteados en Git (*.db-wal, *.db-shm)
[DEBT-HYGIENE-04] Base de datos duplicada MisEventos.db en la raíz y dentro del paquete
[DEBT-HYGIENE-05] Más de 40 archivos de trabajo temporales (tmp*) abandonados en mis_agentes_inteligentes/
[DEBT-HYGIENE-06] Decenas de archivos de sesión JSON obsoletos en mis_agentes_inteligentes/sesiones/
[DEBT-HYGIENE-07] Archivo duplicado de UI Frontend: localcode_claude_ui.html en la raíz y en el paquete
[DEBT-HYGIENE-08] Archivos de dump de entorno virtual commiteados (root-venv.txt, nested-venv.txt)
[DEBT-HYGIENE-09] Ausencia de reglas exhaustivas en .gitignore para SQLite DBs, WAL, SHM y tmp*
```

---

## Dependency Hotspots

Puntos del sistema con alto acoplamiento de entrada/salida ("Hubs de Dependencia"):

```
                         ┌──────────────────────────┐
                         │   agent_pipeline.py      │ (HUB PRINCIPAL DE PIPELINE)
                         └────────────┬─────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│       tools.py       │  ┌  sdd_contract/*.py   │  │   graph_context.py   │
│  (System & File I/O) │  │ (Governance Rules)   │  │ (AST Subgraph RAG)   │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
            ▲                         ▲                         ▲
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      │
                         ┌────────────┴─────────────┐
                         │   localcode_server.py    │ (HUB HTTP & REST API)
                         └──────────────────────────┘
```

1. **`agent_pipeline.py` (Orchestration Hub)**:
   - Importa: `agents`, `tools`, `graph_context`, `runtime.event_bus`, `storage.database`, `sdd_contract.task_router`.
   - Es importado por: `localcode_server.py`, `runtime/runtime.py`, `app.py`, `main.py` y 15+ archivos de test.
2. **`localcode_server.py` (Network & UI Hub)**:
   - Importa: `agent_pipeline.py`, `version.py`, `urllib`, `http.server`, `threading`.
   - Es importado por: `desktop_app.py`, `test_localcode_server.py`, `test_e2e_real_desktop_lifecycle.py`.
3. **`tools.py` (Execution Authority Hub)**:
   - Importa: `os`, `subprocess`, `ast`, `requests`, `git`.
   - Es importado por: `agent_pipeline.py`, `agents.py`, `test_tools.py`.

---

## Duplicate or Overlapping Functionality

| Funcionalidad | Componente A (Canónico) | Componente B (Redundante / Legacy) | Diagnóstico |
| :--- | :--- | :--- | :--- |
| **Clasificación de Tareas** | `sdd_contract/task_router.py` | `ComplexityRiskEvaluator` (`agent_pipeline.py`) re-define routing | Duplicación parcial de reglas |
| **Definición de Contratos** | `sdd_contract/task_types.py` | `TaskType(Enum)` en `agent_pipeline.py` | Enum duplicado en 2 archivos |
| **Fachada SDD** | Implementación directa en `agent_pipeline.py` | `sdd_contract/integrator.py` (`SDDIntegrator`) | Fachada huérfana no utilizada |
| **Context Retrieval RAG** | `graph_context.py` (AST Graphify RAG) | `rag_tools.py` (ChromaDB + BM25 Text RAG) | `rag_tools.py` es legacy de v3.0 |
| **Gestión de Sesiones** | `storage/database.py` (SQLite Event Sourcing) | `session_manager.py` (Archivos JSON sueltos en `sesiones/`) | Dos motores de persistencia paralelos |
| **Supervisor Agéntico** | `agent_pipeline.py` (`AgentStateMachineController`) | `orquestador_agente.py` (Script supervisor directo) | Script raíz legacy |
| **Frontend UI HTML** | `mis_agentes_inteligentes/localcode_claude_ui.html` | `localcode_claude_ui.html` (en raíz del repo) | Duplicado idéntico de 60 KB |

---

## Refactoring Opportunities

Propuestas de refactorización estructural (para ser ejecutadas en fases posteriores con la aprobación del usuario):

1. **Fase 1: Higiene Estricta de Repositorio (Cero impacto en código)**
   - Agregar entradas exhaustivas a `.gitignore`: `*.db`, `*.db-wal`, `*.db-shm`, `tmp*`, `sesiones/`, `venv/`.
   - Eliminar de Git los binarios y temporales (`codeagent_desktop.db`, `MisEventos.db`, `tmp*`, `root-venv.txt`, `nested-venv.txt`).
   - Eliminar el entorno virtual secundario anidado `mis_agentes_inteligentes/venv`.
   - Eliminar el duplicado `localcode_claude_ui.html` de la raíz del proyecto.

2. **Fase 2: Unificación de Tipos y Fachadas SDD**
   - Eliminar la redefinición de `TaskType` y `TaskContract` en `agent_pipeline.py` y usar `sdd_contract.task_types`.
   - Decidir entre conectar `SDDIntegrator` (`integrator.py`) formalmente a `agent_pipeline.py` o remover el archivo huérfano.
   - Deprecar `rag_tools.py` (ChromaDB) y consolidar la lectura de contexto en `graph_context.py`.
   - Consolidar la gestión de sesiones en `DatabaseManager` (`storage/database.py`) y retirar `session_manager.py`.

3. **Fase 3: Descomposición Modular de Módulos "God Object"**
   - Dividir `agent_pipeline.py` (933 líneas) en un paquete `pipeline/` bien estructurado con handlers de fase desacoplados.
   - Dividir `localcode_server.py` (941 líneas) en `server/` separando HTTP handler, SSE streaming y archivos estáticos.
   - Dividir `tools.py` (736 líneas) en `tools/` separando file tools, terminal tools y GitHub tools.

---

## Risk Matrix

Matriz de evaluación de riesgos para la refactorización futura de módulos clave:

| Módulo / Componente | Nivel de Riesgo | Posible Modo de Fallo | Impacto en Invariantes SDD | Mitigación Recomendada |
| :--- | :---: | :--- | :--- | :--- |
| **`agent_pipeline.py`** | **CRÍTICO** | Ruptura de la máquina de estados ReAct o desincronización de eventos. | `INV-001` (Pipeline Authority)<br>`INV-004` (Intent Preservation) | Mantener suite de pruebas en `test_sdd_conformance.py` y `test_state_machine.py` corriendo tras cada extracción. |
| **`localcode_server.py`** | **ALTO** | Fallos en el streaming SSE o desconexión del proceso Desktop. | `INV-008` (Desktop Lifecycle)<br>`SPEC-011` (SSE Streaming) | Ejecutar `test_e2e_real_desktop_lifecycle.py` y `test_sse_endpoint.py`. |
| **`sdd_contract/task_router.py`** | **ALTO** | Clasificación errónea de prompts (ej. clasificar ACTION como CHAT o viceversa). | `INV-002` (TaskContract Authority)<br>`INV-006` (Tool Isolation) | Ejecutar `test_task_router_negations.py` y `test_sdd_conformance.py`. |
| **`tools.py`** | **MEDIO** | Fallo de permisos HITL o error de sintaxis en `search_replace`. | `INV-006` (Tool Isolation) | Verificar con `test_tools.py` y `test_terminal_hitl_approval.py`. |
| **`graph_context.py`** | **MEDIO** | Fallo en la recuperación del subgrafo AST o invalidación de caché. | `SPEC-013` (AST Subgraph RAG) | Validar con `test_graphify_context_retrieval.py`. |

---

## Recommended Simplification Priorities

Se recomienda abordar la refactorización del proyecto en un plan de 4 etapas ordenadas por prioridad y nivel de riesgo:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 1: HIGIENE Y REMOCIÓN DE PESO MUERTO (Riesgo CERO)                              │
│ - Actualizar .gitignore.                                                               │
│ - Eliminar bases de datos SQLite commiteadas (codeagent_desktop.db, MisEventos.db).     │
│ - Eliminar entorno virtual anidado (mis_agentes_inteligentes/venv).                    │
│ - Limpiar temporales (tmp*) y duplicados de UI (localcode_claude_ui.html en raíz).     │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 2: UNIFICACIÓN DE INTEGRACIÓN Y CONTRATOS SDD (Riesgo BAJO)                      │
│ - Eliminar enums duplicados de TaskType en agent_pipeline.py.                           │
│ - Resolver abstracción huérfana sdd_contract/integrator.py.                            │
│ - Deprecar rag_tools.py y consolidar RAG en graph_context.py (SPEC-013).             │
│ - Consolidar sesiones en SQLite DatabaseManager.                                       │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 3: DESCOMPOSICIÓN DE GOD MODULES (Riesgo MEDIO-ALTO)                             │
│ - Refactorizar agent_pipeline.py en paquete modular mis_agentes_inteligentes/pipeline/ │
│ - Refactorizar localcode_server.py en paquete modular mis_agentes_inteligentes/server/ │
│ - Refactorizar tools.py en paquete modular mis_agentes_inteligentes/tools/             │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ETAPA 4: VERIFICACIÓN Y RE-CERTIFICACIÓN SDD (Riesgo BAJO)                             │
│ - Ejecutar suite de pruebas de regresión (python -m pytest).                           │
│ - Ejecutar script de verificación SDD (python scripts/sdd_check.py).                   │
│ - Actualizar grafo de conocimiento (graphify update .).                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---
*Fin del informe de auditoría.*
