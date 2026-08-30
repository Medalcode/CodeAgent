# Task Contract Compatibility Matrix

## Purpose
Este documento analiza en detalle la compatibilidad y diferencias entre la definición local `TaskContract` en `agent_pipeline.py` y la definición canónica `TaskContract` (ABC) en `sdd_contract/task_contract.py`, previo a cualquier sustitución de importación.

---

## Detailed Comparison Table

| Atributo / Método | `agent_pipeline.py` (Local Dataclass) | `sdd_contract/task_contract.py` (Canonical ABC) | Mapeo / Solución de Compatibilidad |
| :--- | :--- | :--- | :--- |
| **Tipo de Clase** | `@dataclass` concreta | `ABC` abstracta con 4 subclases | Agregar adapter/propiedades de conveniencia en `TaskContract` o extender la clase abstracta. |
| **Variantes `TaskType`** | `CHAT`, `ACTION`, `FEATURE` (Falta `RECOVERY`) | `CHAT`, `ACTION`, `FEATURE`, `RECOVERY` | `sdd_contract` incluye la variante `RECOVERY` completa. |
| **`task_type`** | Campo explícito `TaskType` | Método abstracto / Propiedad en subclase | Retornar `self.task_type` en las subclases de contrato. |
| **`requires_code_verification`** | Booleano directo (`bool`) | Método `can_verify() -> bool` | Mapear propiedad `@property def requires_code_verification(self) -> bool: return self.can_verify()`. |
| **`requires_tests`** | Booleano directo (`bool`) | Implícito en `can_verify()` | Mapear propiedad `@property def requires_tests(self) -> bool: return self.can_verify() and ToolType.TEST_RUNNER in self.get_allowed_tools()`. |
| **`requires_execution`** | Booleano directo (`bool`) | Implícito en `get_max_iterations()` | Mapear propiedad `@property def requires_execution(self) -> bool: return self.get_max_iterations() > 1`. |
| **`tools_allowed`** | Booleano directo (`bool`) | Conjunto `get_allowed_tools() -> set[ToolType]` | Mapear propiedad `@property def tools_allowed(self) -> bool: return len(self.get_allowed_tools()) > 1`. |
| **`files_allowed`** | Booleano directo (`bool`) | Implícito en `ToolType.FILESYSTEM` | Mapear propiedad `@property def files_allowed(self) -> bool: return ToolType.FILESYSTEM in self.get_allowed_tools()`. |
| **`execution_level`** | Campo enum `ExecutionLevel` | No presente directamente en `TaskContract` | Mapear propiedad `@property def execution_level(self) -> ExecutionLevel`. |
| **`get_max_iterations()`** | No presente | Método en contrato | Ventaja de `sdd_contract` (limita iteraciones dinámicamente per task). |

---

## Consumer Analysis

1. **`mis_agentes_inteligentes/agent_pipeline.py`**:
   - Lee `contract.requires_code_verification`, `contract.requires_execution`, `contract.tools_allowed`, `contract.files_allowed` y `contract.execution_level`.
2. **`sdd_contract/integrator.py`**:
   - Utiliza `sdd_contract/task_contract.py` invocando `get_contract(task_type)`.
3. **`tests/test_sdd_conformance.py`**:
   - Valida `ActionTaskContract` y `ChatTaskContract` importando desde `sdd_contract.task_contract`.

---

## Migration Architecture Plan

Para garantizar cero rupturas y compatibilidad 100%:
1. Añadir propiedades de compatibilidad (`requires_code_verification`, `requires_execution`, `tools_allowed`, `files_allowed`, `execution_level`) a la clase base `TaskContract` en `sdd_contract/task_contract.py`.
2. En `agent_pipeline.py`, reemplazar la redefinición local de `TaskType` y `TaskContract` por:
   ```python
   from sdd_contract.task_types import TaskType
   from sdd_contract.task_contract import (
       TaskContract,
       ChatTaskContract,
       ActionTaskContract,
       FeatureTaskContract,
       RecoveryTaskContract,
   )
   ```
3. Mantener el contrato `TaskContract` canónico como la **Autoridad Única Inviolable**.

---
*Fin de la matriz de compatibilidad de contratos.*
