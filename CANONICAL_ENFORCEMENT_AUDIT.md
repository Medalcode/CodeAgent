# Canonical Enforcement Audit (Phase C2.5)

## Executive Summary

Este informe evalúa la **adherencia real en runtime** de las decisiones de arquitectura canónica establecidas durante las Fases B y C2 de CodeAgent.

El objetivo principal es detectar **Canonicalization Drift** (divergencia donde la documentación o los principios declaran un componente como Canónico, pero el runtime aún prioriza o mantiene caminos legacy como primera opción).

### Conclusión Principal
La arquitectura canónica definida en la Fase B gobierna la mayoría de los flujos principales (RAG, UI, Entry Points). Sin embargo, se identificaron **dos hallazgos críticos de Canonicalization Drift en runtime**:
1. **Persistencia de Sesiones**: `AgentStateMachineController.resume_session()` y `_persist_state_checkpoint()` en `agent_pipeline.py` continúan consultando y escribiendo en archivos JSON (`session_manager.py`) **antes** de consultar SQLite (`storage/database.py`).
2. **Autoridad de Contratos de Tarea**: `ComplexityRiskEvaluator.build_contract()` en `agent_pipeline.py` todavía instancia una `@dataclass TaskContract` local en lugar de delegar en las subclases canónicas de `sdd_contract/task_contract.py`.

---

## Canonical Decisions Matrix

| Decisión | Autoridad Esperada (Phase B) | Autoridad Real en Runtime | Drift Detectado | Severidad |
| :--- | :--- | :--- | :--- | :--- |
| **Task Contract Authority** | `sdd_contract/task_contract.py` | `sdd_contract/task_types.py` (Tipos) + `agent_pipeline.py` (Dataclass local) | **SÍ** (`agent_pipeline.py` construye dataclass local) | **MEDIA** |
| **RAG Authority** | `graph_context.py` (SPEC-013) | `graph_context.py` | **NO** (`rag_tools` completamente desconectado) | **NINGUNA** |
| **Session Persistence Authority** | `storage/database.py` (SQLite WAL) | `session_manager.py` (JSON) ➔ `database.py` (SQLite) | **SÍ** (JSON se consulta y guarda primero) | **ALTA** |
| **UI Authority** | PyWebView Desktop (`desktop_app.py`) | PyWebView Desktop (`desktop_app.py`) | **NO** (Launchers actualizados a `desktop_app.py`) | **NINGUNA** |
| **Entry Point Authority** | `desktop_app.py` + `localcode_server.py` | `desktop_app.py` + `localcode_server.py` | **NO** (Batch scripts y Docker apuntan a Desktop) | **NINGUNA** |

---

## Task Contract Authority

### Análisis de Adherencia
- `sdd_contract/task_types.py` es la autoridad única para el enum `TaskType` (`CHAT`, `ACTION`, `FEATURE`, `RECOVERY`).
- En `sdd_contract/task_contract.py` residen las subclases de contrato (`ChatTaskContract`, `ActionTaskContract`, `FeatureTaskContract`, `RecoveryTaskContract`).

### Drift Identificado
- `agent_pipeline.py` re-declara una `@dataclass class TaskContract` local (líneas 91-99) e instanciarla en `ComplexityRiskEvaluator.build_contract()` (líneas 156-170).
- Aunque `sdd_contract/task_contract.py` posee la interfaz abstracta oficial, el engine de ejecución `AgentPipeline` utiliza la estructura local de dataclass.

---

## RAG Authority

### Análisis de Adherencia
- `mis_agentes_inteligentes/graph_context.py` es la **ÚNICA** autoridad de recuperación de contexto RAG en el pipeline (`SPEC-013`).
- `rag_tools.py` (ChromaDB + BM25) fue completamente removido de `main.py` y `TOOLS_MAP`.
- Ningún módulo de producción ni script invoca ni importa `rag_tools.py`.

### Drift Identificado
- **Ninguno**. `graph_context.py` gobierna el 100% de las consultas contextuales AST.

---

## Session Persistence Authority

### Análisis de Adherencia
- `mis_agentes_inteligentes/storage/database.py` (`DatabaseManager` SQLite WAL) es la infraestructura canónica de almacenamiento.

### Drift Identificado (**CRÍTICO**)
1. En `agent_pipeline.py` (líneas 504-515), el método `resume_session()` ejecuta:
   ```python
   from session_manager import load_session
   data = load_session(session_id)
   if not checkpoint and self._db_manager:
       chk_db = self._db_manager.get_latest_checkpoint(session_id)
   ```
   *Efecto*: JSON es consultado como primera opción, dejando a SQLite como un fallback secundario.
2. En `agent_pipeline.py` (líneas 228-249), `_persist_state_checkpoint()` guarda primero en JSON via `save_session(session_id, data)` y posteriormente sincroniza con SQLite.

---

## UI Authority

### Análisis de Adherencia
- **CodeAgent Desktop IDE** (`desktop_app.py` + `localcode_server.py` + `localcode_claude_ui.html`) es la interfaz de usuario principal.
- `Iniciar_OpenCode.bat` fue actualizado para lanzar `desktop_app.py` por defecto (Opción 1).
- `Lanzar_CodeAgent_Desktop.bat` ejecuta `desktop_app.py`.

### Clasificación de Interfaces
- **PRIMARY**: `desktop_app.py` + `localcode_server.py` + `localcode_claude_ui.html`
- **SECONDARY**: `claude_code_cli.py` / `main.py` (CLI en Terminal)
- **LEGACY**: `mis_agentes_inteligentes/app.py` (Streamlit UI v2.0)

---

## Entry Point Authority

### Análisis de Adherencia
- `desktop_app.py` (PyWebView Desktop IDE Runner) y `localcode_server.py` (Backend REST/SSE) son los Entry Points canónicos oficializados.
- Se eliminaron las ambigüedades en la documentación y scripts bat.

---

## Compatibility API Audit

Evaluación de las 5 propiedades de compatibilidad agregadas a `sdd_contract/task_contract.py`:

| Propiedad | Tipo | Consumidores Activos | Necesidad Futura | Plan de Eliminación |
| :--- | :--- | :--- | :--- | :--- |
| `requires_code_verification` | `COMPATIBILITY_API` | `agent_pipeline.py` | Media | Reemplazar por `contract.can_verify()` |
| `requires_tests` | `COMPATIBILITY_API` | `agent_pipeline.py` | Media | Reemplazar por chequeo de `ToolType.TEST_RUNNER` |
| `requires_execution` | `COMPATIBILITY_API` | `agent_pipeline.py` | Media | Reemplazar por `contract.get_max_iterations() > 1` |
| `tools_allowed` | `COMPATIBILITY_API` | `agent_pipeline.py` (`INV-006`) | Alta | Reemplazar por `len(contract.get_allowed_tools()) > 0` |
| `files_allowed` | `COMPATIBILITY_API` | `agent_pipeline.py` | Media | Reemplazar por `ToolType.FILESYSTEM in contract.get_allowed_tools()` |

---

## Canonicalization Drift Findings

1. **[DRIFT-01] Prioridad Invertida en Persistencia de Checkpoints**: `resume_session()` y `_persist_state_checkpoint()` priorizan I/O de archivos JSON en lugar de `DatabaseManager`.
2. **[DRIFT-02] Instanciación Local de Dataclass TaskContract**: `ComplexityRiskEvaluator` crea instancias de la dataclass local en lugar de invocar `sdd_contract.task_contract.get_contract(task_type)`.

---

## Required Corrections

### Safe Corrections (Recomendadas para Fase C3)
1. Invertir el orden de búsqueda en `resume_session()`: Consultar `DatabaseManager.get_latest_checkpoint()` como fuente primaria, y usar JSON `load_session()` únicamente como fallback legacy.
2. Hacer opcional la persistencia JSON en `_persist_state_checkpoint()`, asegurando que `DatabaseManager.save_checkpoint()` sea la operación primaria.
3. Actualizar `ComplexityRiskEvaluator.build_contract()` para retornar directamente instancias del contrato canónico (`ChatTaskContract`, `ActionTaskContract`, `FeatureTaskContract`).

### High Risk Corrections (Diferir a Refactor Mayor)
- Eliminación física total de `session_manager.py` o de la dataclass local hasta haber completado la migración completa de tests de integración.

---

## Removal Readiness

Clasificación final del estado de cada componente legacy del sistema:

| Componente | Archivo | Estado de Remoción | Justificación |
| :--- | :--- | :--- | :--- |
| **RAG Legacy** | `mis_agentes_inteligentes/rag_tools.py` | **REMOVAL_READY** | Zero referencias en runtime activo; `DeprecationWarning` activo. |
| **Orquestador Legacy** | `orquestador_agente.py` | **REMOVAL_READY** | Script aislado v1.0 sin consumidores; `DeprecationWarning` activo. |
| **Streamlit UI** | `mis_agentes_inteligentes/app.py` | **DEPRECATED / COMPATIBILITY_ONLY** | Mantenido únicamente para usuarios que ejecuten opción 3 legacy. |
| **JSON Sessions** | `mis_agentes_inteligentes/session_manager.py` | **ACTIVE_LEGACY** | Aún consultado por `agent_pipeline.py`. Requiere corrección de prioridad. |
| **Integrador SDD** | `sdd_contract/integrator.py` | **COMPATIBILITY_ONLY** | Fachada sin acoplamiento activo en el pipeline. |

---
*Fin del informe de auditoría de gobernanza canónica.*
