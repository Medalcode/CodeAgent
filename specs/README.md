# SDD Specifications & Invariant Hierarchy

This directory contains the formal Software-Driven Development (SDD) specifications and invariant definitions for CodeAgent.

## Directory Structure

```text
specs/
├── README.md
├── traceability.md
└── invariants/
    ├── INV-001-pipeline-authority.md
    ├── INV-002-task-contract-authority.md
    ├── INV-003-cross-task-isolation.md
    ├── INV-004-intent-preservation.md
    ├── INV-005-failure-containment.md
    ├── INV-006-tool-isolation.md
    ├── INV-007-conditional-verification.md
    └── INV-008-desktop-lifecycle-safety.md
```

## Certified Invariants Overview

| Invariant ID | Name | Core Guarantee |
| :--- | :--- | :--- |
| **INV-001** | Pipeline Authority | All production agent executions pass through `AgentPipeline` state machine. |
| **INV-002** | TaskContract Authority | TaskContract governance boundaries are strictly enforced and immutable. |
| **INV-003** | Cross-Task Isolation | Peticiones consecutivas inician con telemetría y buffers aislados. |
| **INV-004** | Intent Preservation | Negative constraints restrict only prohibited tools, keeping positive intent. |
| **INV-005** | Failure Containment | Pipeline internal exceptions trigger safe error responses, avoiding bypasses. |
| **INV-006** | Tool Isolation | `tools_allowed=False` removes all workspace tools from agent instance. |
| **INV-007** | Conditional Verification | Fast-Path CHAT omits verification phases (`NOT_REQUIRED`). |
| **INV-008** | Desktop Lifecycle Safety | Concurrent Desktops maintain independent ports/PIDs; parent monitor cleans orphans. |

## Automated SDD Verification CLI (`scripts/sdd_check.py`)

The automated SDD checker CLI performs structural traceability checks:

### What `sdd_check.py` Validates
1. **Existence Checks**: Confirms that `specs/traceability.md`, `audits/certifications/v5.0.0/certification.md`, and all 8 `INV-*.md` spec files exist on disk.
2. **Structural Table Parsing**: Parsea la tabla Markdown en `traceability.md` y valida que cada invariante contenga columnas estructuradas para Spec, Source, Tests y Evidence.
3. **Source Path & Line Range Validation**: Extrae y resuelve las rutas de código fuente. Verifica que los archivos existan físicamente en disco y que los rangos de líneas (`#L159-L160`) estén dentro de los límites válidos del archivo.
4. **Test File & Symbol Validation**: Verifica que cada archivo de prueba referenciado (`tests/test_*.py`) exista en disco y que los símbolos especificados (`test_func`) estén presentes.
5. **Evidence File Validation**: Verifica la existencia física del archivo de evidencia de certificación.
6. **Adversarial Self-Diagnostics**: Ejecuta `--test-adversarial` para verificar que los 7 casos de falso PASS (Casos A al G) sean detectados determinísticamente.

### What `sdd_check.py` Does NOT Validate
- Runtime E2E executions or LLM API calls (these are validated during Full Release Certification audits).

