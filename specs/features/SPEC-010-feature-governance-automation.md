# SPEC-010 — Dynamic Feature Governance Automation

## Intent
Evolucionar la herramienta CLI `scripts/sdd_check.py` desde un validador limitado a los 8 invariantes fijos (`INV-001..008`) hacia una plataforma dinámica de gobernanza SDD capaz de descubrir, parsear y validar cualquier especificación de característica (`specs/features/SPEC-*.md`) e invariante (`specs/invariants/INV-*.md`), sus contratos estructurales, enlaces de trazabilidad, archivos de análisis de cambio y artefactos de evidencia dedicados.

## Preconditions
- El repositorio contiene un directorio `specs/invariants/` con archivos `INV-*.md`.
- El repositorio contiene un directorio `specs/features/` con archivos `SPEC-*.md`.
- El archivo `specs/traceability.md` define las tablas de trazabilidad para Invariantes y Características.

## Postconditions
- La ejecución `python scripts/sdd_check.py` descubre automáticamente todas las especificaciones `INV-*.md` y `SPEC-*.md`.
- Para cada especificación `SPEC-*.md`, la herramienta valida:
  1. Presencia de las 8 secciones obligatorias (`## Intent`, `## Preconditions`, `## Postconditions`, `## Invariants`, `## Failure Behavior`, `## Observability`, `## Testability`, `## Traceability`).
  2. Presencia de fila estructurada en `specs/traceability.md`.
  3. Existencia de los archivos de código fuente especificados.
  4. Existencia de los archivos de prueba unitaria y símbolos de prueba.
  5. Existencia del archivo de análisis de impacto de cambios (`change/change-*.md`).
  6. Existencia del archivo de evidencia de características (`audits/features/SPEC-*/` o `audits/certifications/`).
- La ejecución `python scripts/sdd_check.py --test-adversarial` valida 13 casos adversariales aislados (Casos A a M) sobre un directorio temporal sin invocar funciones helper acopladas.

## Invariants
- **INV-001** (Pipeline Authority): La gobernanza valida que las especificaciones no evadan el control del pipeline.
- **INV-005** (Failure Containment): Errores de sintaxis o formato en especificaciones producen un estado `FAIL` claro sin crashes no controlados del checker.
- **INV-007** (Conditional Verification): Mantiene compatibilidad backward con la suite de 8 invariantes.

## Failure Behavior
- Si alguna SPEC falta, carece de secciones obligatorias, o apunta a fuentes/tests/evidencias inexistentes, `sdd_check.py` emite un error explícito especificando el ID y retorna código de salida `1`.

## Observability
- Imprime tablas resumen claras demarcando `INVARIANT CHECK` y `FEATURE CHECK` con veredicto final `PASS` o `FAIL`.

## Testability
- Demostrable mediante `tests/test_sdd_checker_engine.py` (suite unittest aislada) y `python scripts/sdd_check.py --test-adversarial`.

## Traceability
- Source File: `scripts/sdd_check.py`
- Test File: `tests/test_sdd_checker_engine.py`
- Change Impact: `change/change-feature-governance-automation.md`
- Evidence File: `audits/features/SPEC-010/runtime-evidence.md`
- Invariants: `INV-001`, `INV-005`, `INV-007`
