# Migration Report: Task Contract Migration (`agent_pipeline.py` → `sdd_contract/task_types.py` & `task_contract.py`)

## Before
- **Componente Anterior**: Definición inline duplicada de `TaskType(Enum)` (omitiendo `RECOVERY`) y `TaskContract(dataclass)` en `mis_agentes_inteligentes/agent_pipeline.py`.
- **Problema**: Inconsistencia con el sistema de gobernanza SDD en `sdd_contract/`. Si `sdd_contract/task_types.py` añadía un nuevo tipo de tarea (como `RECOVERY`), la definición local en `agent_pipeline.py` divergía y no lo soportaba.

## Canonical Component
- **Componente Canónico**: `sdd_contract/task_types.py` (`TaskType` Enum) y `sdd_contract/task_contract.py` (`TaskContract` ABC con subclases `ChatTaskContract`, `ActionTaskContract`, `FeatureTaskContract`, `RecoveryTaskContract`).
- **Ventaja**: Autoridad única e inmutable de tipos de contrato SDD con 4 especializaciones de gobernanza.

## Consumers Migrated
- `mis_agentes_inteligentes/agent_pipeline.py`: Se eliminó la redefinición local de `TaskType` y se reemplazó por la importación canónica `from sdd_contract.task_types import TaskType`.
- Se incorporaron propiedades de compatibilidad (`requires_code_verification`, `requires_tests`, `requires_execution`, `tools_allowed`, `files_allowed`) en `sdd_contract/task_contract.py`.

## Compatibility
- `TASK_CONTRACT_COMPATIBILITY_MATRIX.md` documenta la equivalencia completa entre los métodos abstractos de `sdd_contract` y las propiedades de acceso del pipeline.

## Tests
- `tests/test_task_router_negations.py`: PASS.
- `tests/test_sdd_conformance.py`: PASS.
- `tests/test_cross_task_telemetry_isolation.py`: PASS.

## SDD Validation
- `python scripts/sdd_check.py`: **RESULT: PASS**.
- Invariante `INV-002` (TaskContract Authority): **100% TRACEABLE**.

## Deprecation Status
- **Estado**: **CANONICALIZED**.
- La redefinición local fue removida y `sdd_contract` es la Autoridad Única.

## Rollback
- Revertir la importación en `agent_pipeline.py` y `sdd_contract/task_contract.py` mediante `git checkout`.
