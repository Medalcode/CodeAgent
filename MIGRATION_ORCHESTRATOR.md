# Migration Report: Legacy Orchestrator Verification (`orquestador_agente.py`)

## Before
- **Componente Anterior**: `orquestador_agente.py` (Script supervisor independiente de v1.0 en la raíz del proyecto).
- **Problema**: `orquestador_agente.py` fue escrito como un script experimental inicial para probar modelos Ollama mediante inyección directa de prompts y generación de parches sobre archivos locales, sin pasar por la máquina de estados ReAct ni la gobernanza SDD (`INV-001`).

## Canonical Component
- **Componente Canónico**: `mis_agentes_inteligentes/agent_pipeline.py` (`AgentStateMachineController`) y `mis_agentes_inteligentes/benchmark_suite.py`.
- **Ventaja**: Ejecución segura gobernada por `TaskContract` y máquina de estados acotada (`INIT`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DIAGNOSE`, `REPLAN`), respaldada por la suite estandarizada de 5 benchmarks reproducibles (`benchmark_suite.py`).

## Consumers Migrated
- Ningún módulo de producción, test o batch script activo importa ni invoca `orquestador_agente.py`.

## Compatibility
- `orquestador_agente.py` emite una advertencia de deprecación formal (`DeprecationWarning`) si es ejecutado manualmente.

## Tests
- `python scripts/sdd_check.py`: PASS.
- `python -m pytest`: PASS (192 tests pasados).

## SDD Validation
- `python scripts/sdd_check.py`: **RESULT: PASS**.
- Invariante `INV-001` (Pipeline Authority): **100% TRACEABLE**.

## Deprecation Status
- **Estado**: **DEPRECATED / ARCHIVE_CANDIDATE**.
- `orquestador_agente.py` está listo para ser retirado o archivado en `docs/archive/` en la Fase C3/D.

## Rollback
- Revertir la advertencia en `orquestador_agente.py` mediante `git checkout`.
