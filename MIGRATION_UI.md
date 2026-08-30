# Migration Report: Legacy UI Deprecation (`app.py` Streamlit → `desktop_app.py` PyWebView)

## Before
- **Componente Anterior**: `mis_agentes_inteligentes/app.py` (Interfaz Web Streamlit 3-Paneles de v2.0).
- **Problema**: Streamlit imponía recargas completas de script (`st.rerun()`), imposibilitaba el streaming directo de Server-Sent Events (SSE) en tiempo real, bloqueaba la integración de ventanas nativas Desktop y requería dependencias pesadas de terceros.

## Canonical Component
- **Componente Canónico**: `desktop_app.py` + `mis_agentes_inteligentes/localcode_server.py` + `mis_agentes_inteligentes/localcode_claude_ui.html`.
- **Ventaja**: Ejecución nativa multihilo sin dependencias pesadas, servidor HTTP embebido, soporte nativo SSE en tiempo real (`SPEC-011` / `SPEC-012`), gestión de ciclo de vida de procesos (`INV-008`).

## Consumers Migrated
1. `Iniciar_OpenCode.bat`: Se actualizó la opción por defecto (Opción 1) para lanzar `desktop_app.py` (CodeAgent Desktop IDE Canónico).
2. `mis_agentes_inteligentes/app.py`: Mantiene la emisión explícita de `DeprecationWarning`.

## Compatibility
- `app.py` se conserva en el repositorio durante la Fase C2 para usuarios que aún requieran la interfaz legacy de Streamlit.
- `Iniciar_OpenCode.bat` mantiene la Opción 3 para lanzar Streamlit en modo legacy.

## Tests
- `tests/test_desktop_app.py`: PASS.
- `tests/test_e2e_real_desktop_lifecycle.py`: PASS.
- `tests/test_regression.py`: PASS (captura correctamente el DeprecationWarning de `app.py`).

## SDD Validation
- `python scripts/sdd_check.py`: **RESULT: PASS**.
- Invariante `INV-008` (Desktop Lifecycle Safety): **100% TRACEABLE**.

## Deprecation Status
- **Estado**: **DEPRECATED**.
- `app.py` se retirará en la Fase C3/D.

## Rollback
- Revertir la selección por defecto en `Iniciar_OpenCode.bat` mediante `git checkout`.
