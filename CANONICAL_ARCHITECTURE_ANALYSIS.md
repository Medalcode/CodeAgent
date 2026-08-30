# Canonical Architecture Analysis — CodeAgent v6.1

## Executive Summary

El objetivo de esta fase (**Phase B: Canonicalization Analysis**) es resolver de forma definitiva las arquitecturas paralelas, duplicados históricos y abstracciones redundantes acumuladas en **CodeAgent**. 

A lo largo de sus iteraciones (CLI → Streamlit → State Machine → SDD Governance → Desktop IDE), el proyecto incorporó múltiples soluciones para la misma responsabilidad sin retirar sistemáticamente las versiones anteriores. 

Esta auditoría establece la regla fundamental:
> **ONE RESPONSIBILITY → ONE CANONICAL IMPLEMENTATION**

Este documento define la implementación canónica y oficial para cada responsabilidad del sistema, sirviendo como el plano obligatorio antes de realizar cualquier modificación, eliminación o refactorización de código en fases posteriores.

---

## Canonical Component Matrix

| Responsabilidad | Implementaciones Actuales | Implementación Canónica | Implementaciones Legacy / Redundantes | Estrategia de Migración |
| :--- | :--- | :--- | :--- | :--- |
| **Clasificación y Contratos de Tareas** | - `sdd_contract/task_types.py`<br>- `sdd_contract/task_contract.py`<br>- `agent_pipeline.py` (inline `TaskType`) | `sdd_contract/task_types.py` & `task_contract.py` | `TaskType` y `TaskContract` duplicados en `agent_pipeline.py` | Reemplazar definiciones inline en `agent_pipeline.py` con importaciones directas desde `sdd_contract`. |
| **RAG / Context Retrieval** | - `graph_context.py` (Graphify AST)<br>- `rag_tools.py` (ChromaDB + BM25) | `mis_agentes_inteligentes/graph_context.py` (`SPEC-013`) | `mis_agentes_inteligentes/rag_tools.py` | Deprecar `rag_tools.py`. Eliminar dependencia de ChromaDB/BM25. |
| **Persistencia de Sesiones y Tareas** | - `storage/database.py` (SQLite WAL)<br>- `session_manager.py` (JSON `sesiones/`) | `mis_agentes_inteligentes/storage/database.py` | `session_manager.py` y archivos `.json` en `sesiones/` | Unificar persistencia en `DatabaseManager`. Retener `session_manager.py` solo para Export/Import Markdown. |
| **Interfaz de Usuario Principal** | - `desktop_app.py` (PyWebView)<br>- `localcode_server.py` + HTML UI<br>- `app.py` (Streamlit)<br>- `claude_code_cli.py` | `desktop_app.py` + `localcode_server.py` + `localcode_claude_ui.html` | `app.py` (Streamlit Web App legacy) | Declarar PyWebView Desktop como UI Canónica. Marcar Streamlit (`app.py`) como Legacy. |
| **Fachada Integradora SDD** | - `sdd_contract/integrator.py`<br>- Invocaciones directas en `agent_pipeline.py` | `sdd_contract/integrator.py` (`SDDIntegrator`) | Invocaciones dispersas / instanciaciones duplicadas en pipeline | Conectar `agent_pipeline.py` a `SDDIntegrator` como fachada unificada de gobernanza. |
| **Entry Point del Sistema** | - `desktop_app.py`<br>- `main.py`<br>- `app.py`<br>- `orquestador_agente.py`<br>- `.bat` scripts | `desktop_app.py` (Desktop IDE Runner) | `orquestador_agente.py`, `app.py` | `desktop_app.py` es el Entry Point Canónico. `main.py` es Entry Point CLI Secundario. |
| **Event Sourcing y Telemetría** | - `runtime/event_bus.py`<br>- Registros dispersos | `mis_agentes_inteligentes/runtime/event_bus.py` | Logs dispares en archivos de texto sueltos | Canalizar todos los eventos de pipeline mediante `EventBus` persistido en SQLite. |
| **Frontend HTML/JS** | - `mis_agentes_inteligentes/localcode_claude_ui.html`<br>- `localcode_claude_ui.html` (Raíz) | `mis_agentes_inteligentes/localcode_claude_ui.html` | `localcode_claude_ui.html` en la raíz del proyecto | Eliminar copia duplicada en la raíz del proyecto. |

---

## Task Contract Analysis

### Estado Actual
Actualmente coexisten dos definiciones de tipos y contratos de tareas:

1. **Implementación Canónica (`sdd_contract/`)**:
   - `sdd_contract/task_types.py`: Define `TaskType` con 4 valores (`CHAT`, `ACTION`, `FEATURE`, `RECOVERY`) y la dataclass `TaskClassification`.
   - `sdd_contract/task_contract.py`: Define la interfaz abstracta `TaskContract` y sus 4 especializaciones (`ChatTaskContract`, `ActionTaskContract`, `FeatureTaskContract`, `RecoveryTaskContract`).
   - `sdd_contract/task_router.py`: Autoridad SDD que realiza la clasificación heurística y determinista del prompt.

2. **Implementación Incompleta y Duplicada (`agent_pipeline.py`)**:
   - Líneas 88-102 de `agent_pipeline.py`: Re-define `class TaskType(Enum)` con solo 3 valores (`CHAT`, `ACTION`, `FEATURE` — omitiendo `RECOVERY`).
   - Re-define `class TaskContract` como una dataclass con atributos heterogéneos (`execution_level`, `requires_code_verification`, `requires_tests`, `tools_allowed`, `files_allowed`).

### Diagnóstico de Incompatibilidad
- `agent_pipeline.py` delega la clasificación a `TaskRouter` mediante `ComplexityRiskEvaluator.classify_with_router(user_goal)`, el cual retorna la cadena `.value` (ej. `'CHAT'`), pero luego instancia su propia clase interna `TaskContract`.
- Esto rompe el principio de autoría única de SDD y genera divergencia si se añaden nuevos tipos de contrato (como `RECOVERY`).

### Decisión de Canonización
- **CANONICAL IMPLEMENTATION**: `sdd_contract/task_types.py` y `sdd_contract/task_contract.py`.
- **LEGACY IMPLEMENTATION**: La redefinición inline de `TaskType` y `TaskContract` en `agent_pipeline.py`.
- **MIGRATION PATH**: 
  1. Importar `TaskType` y los contratos desde `sdd_contract` dentro de `agent_pipeline.py`.
  2. Eliminar las definiciones de clase redundantes en `agent_pipeline.py`.
  3. Asegurar que `agent_pipeline.py` soporte la variante `RECOVERY` en la máquina de estados.
- **RIESGO**: BAJO. Los valores de string de los enums son idénticos.
- **PRUEBAS NECESARIAS**: `test_task_router_negations.py`, `test_sdd_conformance.py`.

---

## RAG Architecture Decision

### Análisis Comparativo

| Criterio | `rag_tools.py` (Legacy) | `graph_context.py` (`SPEC-013` Canónico) |
| :--- | :--- | :--- |
| **Tecnología Base** | ChromaDB (Vector DB) + BM25 Léxico | Graphify AST Graph (`graphify-out/graph.json`) |
| **Tipo de Extraición** | Chunking de texto plano por similitud vectorial | Subgrafo AST (1-hop / 2-hop) de llamados y clases |
| **Dependencias Heavy** | `chromadb`, `sentence_transformers` | Estándar de Python (`json`, `pathlib`, `re`) |
| **Precisión Arquitectónica** | Baja (fragmentos aislados sin jerarquía) | Muy Alta (relaciones directas invocador-invocado) |
| **Uso en Pipeline Actual** | Solo referenciado en `main.py` y `test_rag_tools.py` | Invocado directamente en `agent_pipeline.py` (`_stage_explorer`) |

### Preguntas Clave de Auditoría
1. **¿`graph_context.py` reemplaza completamente a `rag_tools.py`?**
   - **SÍ**. `graph_context.py` proporciona contexto contextualizado estructuralmente por AST, superando el RAG basado en similitud de texto sin contexto sintáctico.
2. **¿Existe alguna funcionalidad que se perdería al retirar `rag_tools.py`?**
   - **NO**. La búsqueda léxica BM25 en `rag_tools.py` es redundante frente a las herramientas de lectura directa (`tools.py`) y la búsqueda exacta por nodos AST en `graph_context.py`.
3. **¿`rag_tools.py` sigue siendo utilizado en producción?**
   - **NO**. `agent_pipeline.py` utiliza exclusivamente `GraphContextEngine` (`SPEC-013`). `rag_tools.py` solo persiste por compatibilidad con el runner CLI `main.py` antiguo.

### Decisión de Canonización
- **CANONICAL**: `mis_agentes_inteligentes/graph_context.py` (Cumple `SPEC-013`).
- **DEPRECATED**: `mis_agentes_inteligentes/rag_tools.py`.
- **REMOVE_CANDIDATE**: `rag_tools.py` y sus tests asociados (`test_rag_tools.py`) en la Fase C de limpieza.

---

## Session Persistence Decision

### Análisis de Mecanismos Actuales

1. **Archivos JSON (`session_manager.py` / `sesiones/*.json`)**:
   - Mecanismo heredado de v2.0 (Streamlit UI).
   - Guarda el historial de mensajes de chat como un diccionario JSON por sesión en disco.
   - Carece de transacciones thread-safe, no soporta checkpoints de tareas ni event sourcing.

2. **SQLite Database (`storage/database.py` / `DatabaseManager`)**:
   - Mecanismo canónico introducido en v5.0 / v6.0.
   - Almacena en `codeagent_desktop.db` con soporte WAL (Write-Ahead Logging):
     - Tabla `tasks`: Estado de cada tarea, prompt, tipo, iteraciones y resultado.
     - Tabla `checkpoints`: Checkpoints serializados del estado del agente para pausas/reanudación.
     - Tabla `events`: Event Sourcing continuo para streaming SSE en tiempo real.

### Arquitectura Objetivo de Persistencia

```
                   ┌──────────────────────────────────────────────┐
                   │          CodeAgent Core Pipeline             │
                   └──────────────────────┬───────────────────────┘
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │    CANONICAL STORAGE: DatabaseManager        │
                   │    (SQLite WAL: codeagent_desktop.db)        │
                   │                                              │
                   │  - tasks (Task LifeCycle & Metadata)         │
                   │  - checkpoints (State Recovery & Resume)     │
                   │  - events (Real-Time SSE Event Sourcing)     │
                   └──────────────────────┬───────────────────────┘
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │        EXPORT / IMPORT UTILITY LAYER         │
                   │  - Conversion to Markdown / User Downloads   │
                   └──────────────────────────────────────────────┘
```

### Decisión de Canonización
- **CANONICAL STORAGE**: `mis_agentes_inteligentes/storage/database.py` (`DatabaseManager` sobre SQLite).
- **LEGACY STORAGE**: `session_manager.py` guardando archivos `.json` sueltos en `sesiones/`.
- **DESTINO DE ARCHIVOS JSON**:
  - Descontinuar la creación de archivos JSON individuales por sesión en runtime.
  - Reutilizar `session_manager.py` únicamente como formateador utilitario para exportar sesiones de la base de datos a documentos Markdown.

---

## Interface Architecture Decision

### Clasificación de Interfaces

| Interface | Clasificación | Propósito | Estado |
| :--- | :--- | :--- | :--- |
| `desktop_app.py` | **PRIMARY USER INTERFACE** | Aplicación de escritorio nativa independiente (PyWebView) con integración de Ollama y backend local. | **CANÓNICA** |
| `localcode_server.py` | **PRIMARY BACKEND SERVICE** | Servidor TCP/HTTP multihilo que entrega endpoints REST, eventos SSE y la UI frontend. | **CANÓNICA** |
| `localcode_claude_ui.html` | **PRIMARY FRONTEND UI** | SPA en HTML/JS con diseño IDE JetBrains Mono, visualización de pipeline SSE y chat. | **CANÓNICA** |
| `mis_agentes_inteligentes/main.py` | **SECONDARY / CLI** | Runner en consola de comandos para entornos headless o automatizaciones sin GUI. | **MANTENER** |
| `claude_code_cli.py` | **EXPERIMENTAL** | REPL interactivo en terminal simulando la interfaz de Claude Code CLI. | **EXPERIMENTAL** |
| `app.py` | **LEGACY UI** | Interfaz Web de 3 paneles basada en Streamlit. | **DEPRECADA** |

### Preguntas Clave de Auditoría
1. **¿Cuál es el producto principal?**
   - **CodeAgent Desktop IDE** (`desktop_app.py` + `localcode_server.py` + `localcode_claude_ui.html`).
2. **¿Qué interfaces deben mantenerse?**
   - La interfaz Desktop nativa y el runner de consola `main.py` para integración CLI.
3. **¿Qué interfaces solo existen por evolución histórica?**
   - `app.py` (Streamlit) fue la UI temporal en v2.0 antes de construir el servidor nativo HTTP y la ventana PyWebView en v3.5/v5.0.

---

## SDD Integration Decision

### Análisis de `sdd_contract/integrator.py`

- **Estado Actual**:
  - `SDDIntegrator` implementa un patrón Facade que encapsula `TaskRouter`, `VerificationEngine`, `Replanner`, `UIManager`, `ToolPolicyEnforcer` y `EvidenceLogger`.
  - Ningún módulo de código actual (`agent_pipeline.py`, `localcode_server.py`, `desktop_app.py`) importa ni instancia `SDDIntegrator`.
  - `agent_pipeline.py` realiza llamadas dispersas e instanciaciones directas a los componentes individuales de `sdd_contract/`.

- **Diagnóstico Arquitectónico**:
  - `SDDIntegrator` representa una frontera arquitectónica limpia y necesaria para evitar que el pipeline conozca los detalles internos de cada subsistema de gobernanza.
  - La falta de adopción en `agent_pipeline.py` se debe a que el pipeline creció de forma monolítica.

### Decisión de Canonización
- **CLASIFICACIÓN**: `INTEGRATE` / `SIMPLIFY`.
- **ACCION**: 
  - Preservar `sdd_contract/integrator.py`.
  - Refactorizar `AgentStateMachineController` en `agent_pipeline.py` para delegar la gestión de contratos, verificación de políticas y registro de evidencia a la fachada `SDDIntegrator`.
  - Esto simplificará drásticamente la complejidad interna de `agent_pipeline.py`.

---

## Entry Point Decision

### Entry Point Matrix

| Entry Point | Purpose | Active Users | Dependencies | Status |
| :--- | :--- | :--- | :--- | :--- |
| `desktop_app.py` | Desktop IDE Runner (PyWebView + Backend + Ollama) | Usuarios Finales Desktop | `pywebview`, `localcode_server.py`, `urllib` | **CANONICAL ENTRY POINT** |
| `localcode_server.py` | Server HTTP/REST/SSE Backend | Desktop App / Navegadores Web | `agent_pipeline.py`, `http.server`, `database.py` | **CANONICAL BACKEND** |
| `Lanzar_CodeAgent_Desktop.bat` | Launcher directo para usuarios Windows | Usuarios Desktop Windows | `desktop_app.py`, `.venv` | **CANONICAL LAUNCHER** |
| `mis_agentes_inteligentes/main.py` | Execution Runner por terminal | Desarrolladores / CI | `agent_pipeline.py`, `agents.py` | **COMPATIBILITY CLI** |
| `Iniciar_OpenCode.bat` | Launcher interactivo con selector de 3 opciones | Usuarios Legacy | `desktop_app.py`, `app.py`, `claude_code_cli.py` | **COMPATIBILITY LAUNCHER** |
| `mis_agentes_inteligentes/claude_code_cli.py` | REPL interactivo de terminal | Desarrolladores / Pruebas | `agent_pipeline.py` | **DEVELOPMENT / EXPERIMENTAL** |
| `mis_agentes_inteligentes/app.py` | Web App Streamlit | Usuarios v2.x Legacy | `streamlit`, `session_manager.py` | **LEGACY** |
| `orquestador_agente.py` | Supervisor directo de modelos Ollama | Pruebas históricas de prompts | `urllib`, `json` | **HISTORICAL** |

### Decisión de Canonización
- **CANONICAL ENTRY POINT**: `desktop_app.py` (Ejecución Desktop) y `localcode_server.py` (Backend).
- **COMPATIBILITY ENTRY POINTS**: `Lanzar_CodeAgent_Desktop.bat` y `mis_agentes_inteligentes/main.py`.
- **LEGACY / RETIREMENT**: `orquestador_agente.py` y `app.py` se transfieren a componentes candidatos para archivo o remoción.

---

## Runtime Source of Truth

Tabla oficial de **Single Source of Truth** para cada tipo de estado del sistema:

```
┌──────────────────────────────┬────────────────────────────────────────────────────────┐
│ Tipo de Estado               │ Source of Truth (Ubicación Canónica)                   │
├──────────────────────────────┼────────────────────────────────────────────────────────┤
│ Estado de Tareas (Task State)│ mis_agentes_inteligentes/codeagent_desktop.db (tasks) │
│ Estado de Sesiones (Sessions)│ mis_agentes_inteligentes/codeagent_desktop.db (sess)  │
│ Checkpoints de Recuperación  │ mis_agentes_inteligentes/codeagent_desktop.db (check) │
│ Eventos de Pipeline (Events) │ EventBus → SQLite (events) → HTTP SSE Stream          │
│ Subgrafo de Contexto (AST)   │ graphify-out/graph.json + GraphCacheManager           │
│ Métricas de Benchmarks       │ audits/benchmarks/results/ + BenchmarkMetricsCollector │
│ Configuración y Versión      │ mis_agentes_inteligentes/version.py & config.py        │
└──────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## Components to Deprecate

Componentes que permanecen en el repositorio pero se marcan oficialmente como **Deprecados** (no deben usarse para nuevo desarrollo):

1. `mis_agentes_inteligentes/rag_tools.py` (Reemplazado por AST Subgraph RAG `graph_context.py`).
2. `mis_agentes_inteligentes/app.py` (Reemplazado por PyWebView Desktop `desktop_app.py`).
3. `mis_agentes_inteligentes/session_manager.py` (Reemplazado por `DatabaseManager` para almacenamiento principal).
4. `orquestador_agente.py` (Reemplazado por `AgentStateMachineController` y `benchmark_suite.py`).

---

## Components to Archive

Archivos de documentación e historial que deben preservarse en `docs/archive/` o `audits/` como evidencia histórica pero fuera del flujo de trabajo principal:

1. `sdd_contract/CONFORMANCE_AUDIT.md` -> Mover a `audits/historical/`.
2. `sdd_contract/VIOLATION_ANALYSIS.md` -> Mover a `audits/historical/`.
3. `root-venv.txt` y `nested-venv.txt` -> Consolidar en documentación o remover.

---

## Components to Remove

Componentes identificados como **peso accidental puro o duplicados exactos** candidatos a remoción física en la Fase de Limpieza:

1. **`localcode_claude_ui.html` (en raíz)**: Duplicado exacto de `mis_agentes_inteligentes/localcode_claude_ui.html`.
2. **`mis_agentes_inteligentes/venv/`**: Entorno virtual secundario anidado de varios gigabytes.
3. **`mis_agentes_inteligentes/codeagent_desktop.db` (y archivos WAL/SHM)**: Bases de datos SQLite activas commiteadas por error en Git.
4. **`MisEventos.db`** (en raíz y en paquete): Bases de datos de eventos residuales.
5. **Archivos temporales `tmp*`** en `mis_agentes_inteligentes/`: Residuos de ejecuciones pasadas.
6. **Archivos JSON `sesiones/*.json`**: Residuos de sesiones pasadas.

---

## Migration Dependencies

Orden de dependencias de migración para evitar romper el sistema durante la simplificación:

```
ETAPA 1: Limpieza de Repositorio (Cero riesgo de código)
└── Eliminar venv anidado, DBs commiteadas, temporales y HTML duplicado de raíz.
    Actualizar .gitignore.

ETAPA 2: Canonización de Tipos y SDD Integration
├── Importar TaskType y TaskContract desde sdd_contract en agent_pipeline.py.
└── Conectar agent_pipeline.py a sdd_contract/integrator.py (SDDIntegrator).

ETAPA 3: Consolidación de RAG y Persistencia
├── Reemplazar referencias residuales de rag_tools.py por graph_context.py.
└── Redirigir la lectura/escritura de sesiones a DatabaseManager (SQLite).

ETAPA 4: Modularización de God Modules
├── Dividir agent_pipeline.py -> mis_agentes_inteligentes/pipeline/
├── Dividir localcode_server.py -> mis_agentes_inteligentes/server/
└── Dividir tools.py -> mis_agentes_inteligentes/tools/
```

---

## Risk Analysis

| Decisión de Canonización | Nivel de Riesgo | Posible Impacto | Plan de Mitigación |
| :--- | :---: | :--- | :--- |
| **Sustitución de `TaskType` local en `agent_pipeline.py`** | **BAJO** | Incompatibilidad de nombres de Enum. | Los valores string (`"CHAT"`, `"ACTION"`, `"FEATURE"`) son idénticos. Validar con `test_sdd_conformance.py`. |
| **Retiro de `rag_tools.py`** | **BAJO** | Fallo en `main.py` o `test_main.py` si aún llaman a `rag_tools`. | Actualizar `main.py` para usar `graph_context.py` antes de remover `rag_tools.py`. |
| **Consolidación de Sesiones en SQLite** | **MEDIO** | Pérdida de sesiones JSON pasadas en desarrollo local. | Crear un script de migración one-off si se desea importar sesiones JSON existentes a la tabla `sessions` de SQLite. |
| **Integración de `SDDIntegrator`** | **MEDIO** | Alteración en la secuencia de inicialización del pipeline. | Probar rigurosamente con `test_integration_pipeline.py` y `test_sdd_conformance.py`. |

---
*Fin del informe de análisis de canonización.*
