# Análisis de Violaciones del SDD Contract System

## Resumen Ejecutivo

**Estado:** ?? CRÍTICO - 4 violaciones identificadas en `agent_pipeline.py`

**Archivos afectados:** 
- `mis_agentes_inteligentes/agent_pipeline.py`

---

## Violación 1: CHAT Task Violates Contract (Requirement 2)

### Contrato CHAT (Requirement 2):
```
FOR A CHAT task, THE CodeAgent SHALL:
- NOT access the filesystem
- NOT execute terminal commands  
- NOT trigger verification steps
- NOT perform replanning
- return exactly one response and mark the task as DONE
```

### Comportamiento Observado:
```
CHAT task ? 213s ? 5 steps ? PLAN ? EXPLORE ? EXECUTE ? VERIFY ? DIAGNOSE ? REPLAN ×2
```

### Violaciones Identificadas:

#### 1.1 Clasificación Incorrecta (Requirement 1)
**Ubicación:** `ComplexityRiskEvaluator.evaluate()` line ~115

```python
# agent_pipeline.py line ~115
if is_explicit_chat or is_query or (not has_mutation and len(goal_lower.split()) <= 12):
    return ExecutionLevel.LEVEL_1_CHAT
```

**Problema:** El prompt "Responde únicamente con OK" DEBE clasificarse como CHAT, pero:
- El check `len(goal_lower.split()) <= 12` puede incluir prompts que NO son CHAT
- Falta check explícito para "responde únicamente", "sin herramientas", etc.

#### 1.2 Fallback a LEVEL_3_FEATURE (Requirement 1)
**Ubicación:** `ComplexityRiskEvaluator.evaluate()` line ~128

```python
# agent_pipeline.py line ~128
return ExecutionLevel.LEVEL_3_FEATURE
```

**Problema:** Si el prompt no matchea CHAT, ACTION o LEVEL_4, cae en LEVEL_3_FEATURE por defecto.

#### 1.3?? CHAT Fast Path (Requirement 2)
**Ubicación:** `AgentStateMachineController.run()` line ~276

```python
# agent_pipeline.py line ~276
active_level = level or self.infer_execution_level(user_goal)
current_state = start_state or (State.PLAN if active_level in (ExecutionLevel.LEVEL_3_FEATURE, ExecutionLevel.LEVEL_4_FULL) else State.EXECUTE)

# Fast path for LEVEL_1_CHAT
if active_level == ExecutionLevel.LEVEL_1_CHAT:
    # ... returns immediately
```

**Problema:** El fast path SÍ existe, pero `infer_execution_level()` puede no regresar LEVEL_1_CHAT correctamente.

#### 1.4 Verificación ejecutada para CHAT (Requirement 2)
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~458

```python
# agent_pipeline.py line ~458
def _stage_verifier(self, user_goal: str = "") -> dict[str, Any]:
    """Comprueba sintaxis AST, linter Ruff y suite de pruebas enfocado únicamente en los archivos del contrato de la tarea actual (Task-Scoped)."""
    # ... escanea 60 archivos .py
    # ... ejecuta tests sobre 28 archivos
    # ... ejecuta Ruff
    # ... ejecuta programa
```

**Problema:** `_stage_verifier()` siempre ejecuta:
- AST check sobre todos los archivos
- Ruff check
- Tests unittest
- Program execution

Esto viola el contrato CHAT que dice "NOT trigger verification steps".

#### 1.5 Replanning ejecutado para CHAT (Requirement 2)
**Ubicación:** `AgentStateMachineController.run()` line ~360

```python
# agent_pipeline.py line ~360
elif current_state == State.VERIFY:
    verification_res = self._stage_verifier(user_goal)
    if verification_res["success"]:
        current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE
    else:
        if active_level in (ExecutionLevel.LEVEL_3_FEATURE, ExecutionLevel.LEVEL_4_FULL) and replans_count < self.max_replans:
            current_state = State.DIAGNOSE
        else:
            current_state = State.CRITIC if active_level == ExecutionLevel.LEVEL_4_FULL else State.DONE
```

**Problema:** Si verification falla para LEVEL_1_CHAT, el código:
1. No entra en DIAGNOSE (correcto)
2. Pero sí ejecuta `_stage_verifier()` (INCORRECTO - viola Requirement 2)

---

## Violación 2: ACTION Task Violates Contract (Requirement 3)

### Contrato ACTION (Requirement 3):
```
FOR AN ACTION task, THE CodeAgent SHALL:
- use only the tools necessary to complete the task
- verify only what was explicitly requested
- perform zero replans if succeeds on first attempt
- NOT access tools outside the task scope
```

### Comportamiento Observado:
```
ACTION task ? python test_action.py executed 3 times ? 2 replans ? Ruff FAIL ? VERIFICATION_FAILED
```

### Violaciones Identificadas:

#### 2.1 Verificación ejecutada para ACTION sin solicitud explícita (Requirement 3)
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~520

```python
# agent_pipeline.py line ~520
has_neg = any(neg in user_goal_lower for neg in (
    "no añadas tests", "no test", "no tests", "sin tests", ...
))
user_requested_tests = not has_neg and any(k in user_goal_lower for k in ("test", "prueba", "unittest", "pytest", "cobertura", "assert"))
```

**Problema:** El check `user_requested_tests` evalúa si el prompt contiene "test" o "prueba". Pero el prompt es:
```
"Crea únicamente test_action.py con: print(\"ACTION_OK\") Ejecuta el archivo una sola vez. No ejecutes tests."
```

El prompt CONTIENE "test" en "test_action.py", por lo tanto:
- `user_requested_tests = True` (FALSO - es solo el nombre del archivo)
- Tests se ejecutan (INCORRECTO)

#### 2.2 Ejecución repetida del programa (Requirement 3)
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~560

```python
# agent_pipeline.py line ~560
target_script = None
if not has_exec_neg:
    if "main.py" in task_modified_files:
        target_script = "main.py"
    elif task_py_files:
        target_script = task_py_files[0]
    elif any(k in user_goal_lower for k in ("ejecuta", "corre", "run")):
        main_candidates = [f for f in task_modified_files if f.endswith(".py") and not _is_test_file(f)]
        if main_candidates:
            target_script = main_candidates[0]

if target_script:
    script_path = os.path.join(self.workspace_dir, target_script)
    if os.path.exists(script_path):
        # Ejecuta el programa
```

**Problema:** El prompt dice "Ejecuta el archivo una sola vez", pero:
1. `target_script = "test_action.py"` (porque está en `task_modified_files`)
2. El programa se ejecuta
3. Si falla verificación, REPLAN ocurre
4. EL MISMO PROGRAMA se ejecuta de nuevo (Violation: "execute exactly once")

#### 2.3 Ruff FAIL hace fallar ACTION aunque no sea parte del contrato (Requirement 3)
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~600

```python
# agent_pipeline.py line ~600
blocking_checks = []
if not ast_valid:
    blocking_checks.append(f"ast_errors: {ast_errors}")
if not ruff_passed:
    blocking_checks.append("ruff_failed")
if tests_status == "FAIL" or not tests_passed:
    blocking_checks.append("tests_failed")
if not program_passed:
    blocking_checks.append(f"program_failed ({target_script}): {program_output}")

success = (len(blocking_checks) == 0)
```

**Problema:** Ruff check forma parte de `blocking_checks`, lo que significa:
- Si Ruff FAIL ? `success = False`
- Si `success = False` ? REPLAN puede ocurrir (si LEVEL_3 o LEVEL_4)
- PERO el prompt dice "No ejecutes tests" (no menciona Ruff)
- Ruff NO es parte del contrato ACTION para este caso

#### 2.4 VERIFICATION_FAILED por fallo global del workspace (Requirement 3)
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~475

```python
# agent_pipeline.py line ~475
# 1. Escaneo de archivos Python en el workspace
all_py_files = []
for root, _, files in os.walk(self.workspace_dir):
    if any(ign in root for ign in ('.git', '.venv', 'venv', '__pycache__', 'node_modules', 'graphify-out')):
        continue
    for file in files:
        if file.endswith('.py'):
            all_py_files.append(os.path.join(root, file))
```

**Problema:** `_stage_verifier()` escanea TODO el workspace, no solo los archivos de la tarea:
- Escanea `mis_agentes_inteligentes/` (60 archivos)
- Escanea `tests/` (28 archivos)
- Si ALGÚN archivo tiene error ? VERIFICATION_FAILED
- PERO el contrato ACTION solo debe verificar LO QUE SE PIDIÓ

---

## Violación 3: NOT_REQUIRED never becomes FAIL

### Contrato VERIFICATION (Requirement 6):
```
FOR a task with verification results PASS + PASS + NOT_REQUIRED, 
THE CodeAgent SHALL mark it as SUCCESS
```

### Código Actual:
**Ubicación:** `AgentStateMachineController._stage_verifier()` line ~600

```python
# agent_pipeline.py line ~600
blocking_checks = []
if not ast_valid:
    blocking_checks.append(f"ast_errors: {ast_errors}")
if not ruff_passed:
    blocking_checks.append("ruff_failed")
if tests_status == "FAIL" or not tests_passed:
    blocking_checks.append("tests_failed")
if not program_passed:
    blocking_checks.append(f"program_failed ({target_script}): {program_output}")

success = (len(blocking_checks) == 0)
```

**Problema:** El código NO distingue entre:
- `NOT_REQUIRED` (excluido de success calculation)
- `FAIL` (incluido en success calculation)

El check es binario: o pasas o fallas. NO hay concepto de `NOT_REQUIRED`.

---

## Violación 4: REPLAN without evidence (Requirement 9)

### Contrato REPLAN (Requirement 9):
```
FOR THE DIAGNOSE phase, THE CodeAgent SHALL require evidence of failure before replanning
```

### Código Actual:
**Ubicación:** `AgentStateMachineController._stage_diagnose()` line ~430

```python
# agent_pipeline.py line ~430
def _stage_diagnose(self, verification_res: dict[str, Any], _user_goal: str) -> dict[str, Any]:
    """Genera un RootCauseReport estructurado aislando la causa raíz del fallo."""
    ast_errors = verification_res.get("ast_errors", [])
    err_str = ", ".join(str(e) for e in ast_errors) if ast_errors else "Fallo en suite de pruebas o linter"

    requires_reexploration = any(k in err_str.lower() for k in ("import", "module", "not found", "nameerror", "attributeerror"))
    return {
        "root_cause": err_str,
        "failed_assumption": "El código recién modificado cumplía la sintaxis y los contratos de los módulos.",
        "strategy_change": "...",
        "requires_reexploration": requires_reexploration,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
```

**Problema:** La función:
1. NO recibe evidencia concreta (solo `verification_res` dictionary)
2. Genera `root_cause` basado en `ast_errors` (que puede ser vacío)
3. NO requiere evidencia de failure antes de replan

**Además:** Requirement 9 dice "no replan after PASS", pero el código:
- Si verification pasa ? `success = True`
- Si `success = True` ? no entra en DIAGNOSE
- PERO si verification FALLA y luego se arregla, REPLAN puede ocurrir de nuevo

---

## Violación 5: UI Lifecycle (Requirement 10)

### Contrato UI (Requirement 10):
```
NO inference, tool execution, verification, or replanning SHALL create new UI instances
```

### Código Actual:
**Ubicación:** `desktop_app.py` (no en agent_pipeline.py, pero afecta)

**Problema:** No hay ninguna verificación en `agent_pipeline.py` que controle UI creation.
- `UIManager` existe en `sdd_contract/ui_manager.py`
- PERO `agent_pipeline.py` no lo usa
- `desktop_app.py` puede crear ventanas nuevas sin restricción

---

## Matriz de Violaciones

| Violación | Requirement | Componente | Estado | Severity |
|-----------|-------------|------------|--------|----------|
| CHAT classification | 1 | ComplexityRiskEvaluator | ? BROKEN | CRITICAL |
| CHAT verification | 2 | _stage_verifier() | ? BROKEN | CRITICAL |
| CHAT replanning | 2 | run() state machine | ?? PARTIAL | HIGH |
| ACTION classification | 3 | ComplexityRiskEvaluator | ? BROKEN | CRITICAL |
| ACTION verification | 3 | _stage_verifier() | ? BROKEN | CRITICAL |
| ACTION execution count | 3 | _stage_verifier() program exec | ? BROKEN | CRITICAL |
| ACTION Ruff check | 3 | _stage_verifier() blocking | ? BROKEN | CRITICAL |
| ACTION workspace scan | 3 | _stage_verifier() all files | ? BROKEN | CRITICAL |
| NOT_REQUIRED ? FAIL | 6 | _stage_verifier() success | ? BROKEN | CRITICAL |
| REPLAN without evidence | 9 | _stage_diagnose() | ? BROKEN | CRITICAL |
| UI lifecycle | 10 | AgentStateMachineController | ? MISSING | CRITICAL |
| Test file detection | 3 | _is_test_file() | ?? FLAWED | HIGH |

---

## Plan de Corrección

### Fase 1: Integrar TaskRouter (Requirement 1)
1. Import `TaskRouter` in `agent_pipeline.py`
2. Replace `ComplexityRiskEvaluator.evaluate()` with `TaskRouter.classify()`
3. Ensure CHAT tasks go through fast path

### Fase 2: Create Task-Scoped Verifier (Requirements 2, 3)
1. Create new method `_stage_verifier_task_scoped(contract)` 
2. Accept contract as parameter
3. Only verify what contract specifies
4. Return `VerificationResult` with PASS/FAIL/ERROR/NOT_REQUIRED

### Fase 3: Evidence Integration (Requirements 6, 7, 9)
1. Import `EvidenceLogger`
2. Log verification failures with evidence
3. Require evidence in `_stage_diagnose()`

### Fase 4: UI Manager Integration (Requirement 10)
1. Import `UIManager`
2. Wrap UI creation
3. Enforce single instance policy

### Fase 5: Test Suite (Requirements 2, 3)
1. Create acceptance test for CHAT
2. Create acceptance test for ACTION
3. Verify contract compliance

---

## Conclusión

**Total Violations:** 12  
**Critical:** 10  
**High:** 2  

**Root Cause:** `agent_pipeline.py` contains OLD verification logic that:
1. Does NOT use TaskContract for scoping
2. Does NOT distinguish NOT_REQUIRED from FAIL
3. Does NOT log evidence properly
4. Does NOT integrate TaskRouter
5. Does NOT control UI lifecycle

**Fix Strategy:** NOT rewrite, but INTEGRATE:
- Keep existing code structure
- Add SDD contract checks BEFORE verification
- Replace global workspace scan with task-scoped verification
- Integrate EvidenceLogger for all failures
- Use UIManager for UI creation

**Warning:** Do NOT run benchmarks until these fixes are applied. Current behavior violates SDD contract.
