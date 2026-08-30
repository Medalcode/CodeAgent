# Migration Report: Session JSON Retirement (`session_manager.py` → `storage/database.py`)

## Before
- **Componente Anterior**: `mis_agentes_inteligentes/session_manager.py` (Guardado de archivos JSON individuales en `mis_agentes_inteligentes/sesiones/*.json`).
- **Problema**: Los archivos JSON sueltos carecían de transaccionalidad ACID, causaban bloqueos I/O no sincronizados bajo concurrencia y no soportaban event sourcing para streaming SSE.

## Canonical Component
- **Componente Canónico**: `mis_agentes_inteligentes/storage/database.py` (`DatabaseManager` sobre SQLite con WAL).
- **Ventaja**: Almacenamiento unificado y thread-safe de tareas (`tasks`), checkpoints de recuperación (`checkpoints`) y eventos de pipeline (`events`), compatible con multi-proceso y streaming en tiempo real.

## Consumers Migrated
- `AgentStateMachineController` (`agent_pipeline.py`) prioriza `DatabaseManager` para checkpoints de recuperabilidad y persistencia de tareas.
- `localcode_server.py` utiliza exclusivamente `DatabaseManager` y `EventBus` para peticiones REST y SSE.

## Compatibility
- `session_manager.py` se mantiene en el repositorio durante la Fase C2 como utilidad para exportar sesiones a Markdown o importar archivos legados.
- Se agregó `mis_agentes_inteligentes/sesiones/.gitkeep` para garantizar la existencia del directorio si algún módulo legacy requiere crear temporales.

## Tests
- `tests/test_session_manager.py`: PASS.
- `tests/test_runtime_storage.py`: PASS.
- `tests/test_state_checkpointing.py`: PASS.

## SDD Validation
- `python scripts/sdd_check.py`: **RESULT: PASS**.
- Invariante `INV-003` (Cross-Task Isolation): **100% TRACEABLE**.

## Deprecation Status
- **Estado**: **DEPRECATED**.
- El almacenamiento directo de JSONs en `sesiones/` está deprecado y sustituido por `DatabaseManager`.

## Rollback
- Revertir la advertencia en `session_manager.py` mediante `git checkout`.
