# G3.6.1 POST-RETIREMENT INTEGRITY CORRECTION

## 1. Objective
Corregir los efectos secundarios no intencionados introducidos durante el retiro de la Legacy UI (G3.6), restaurando la codificación original UTF-8 en código y tests y eliminando cambios que se salieron del alcance de la tarea, sin comprometer el objetivo original de G3.6 (hacer de React la única UI canónica).

## 2. Baseline
- **Parent Commit previo a la corrupción:** `49ce827` (Fin de G3.4 Iteration 3)
- **G3.6 Commits observados:** `2308f92` (Ejecución G3.6) y `c4ed5a2` (Reporte)
- **Tests baseline:** 222 passed, 1 environmental timeout. SDD PASS.
- **Build baseline:** npm build PASS.

## 3. Evidence
- La modificación con PowerShell `Set-Content` de `mis_agentes_inteligentes/localcode_server.py`, `mis_agentes_inteligentes/app.py` y los archivos en `tests/` (`test_localcode_server.py`, `test_desktop_app.py`, `test_desktop_pipeline_visualization.py`) corrompió la codificación (introdujo BOM UTF-8 y mojibake). Esto causó que `pytest` interpretara los literales de pruebas como `'Prompt vac\ufffdo'` y provocara falsos positivos de aserción.
- El archivo `mis_agentes_inteligentes/benchmark_report_v42.md` fue accidentalmente añadido en el commit original de G3.6 mediante una adición genérica de directorios (`git add mis_agentes_inteligentes/`).

## 4. Corrections
- Restauración vía `git checkout 49ce827 --` de `app.py`, `localcode_server.py` y los archivos de `tests/`.
- Re-aplicación de los enrutamientos intencionales hacia `/frontend/dist/index.html` usando un script nativo en Python (`open(..., encoding='utf-8')`) garantizando preservación binaria idéntica de caracteres acentuados.
- Restauración de `benchmark_report_v42.md` a su estado original (deshaciendo su inclusión indeseada).

## 5. Preserved G3.6 Changes
- `mis_agentes_inteligentes/localcode_claude_ui.html` sigue estrictamente eliminado.
- React sigue siendo la **Canonical Desktop UI**.
- `desktop_app.py` y `localcode_server.py` siguen apuntando a `frontend/dist/index.html`.
- Todas las rutas `/api/*` operan sin cambios.
- El empaquetado persiste sin el HTML heredado y conserva `frontend/dist`.
- Las aserciones sobre `EventAdapter` en `test_desktop_pipeline_visualization.py` están intactas y validadas con encoding limpio.

## 6. Unrelated Changes
- `mis_agentes_inteligentes/benchmark_report_v42.md` regresó a su estado histórico original en el árbol de trabajo y fue commiteado en reversa dentro del commit correctivo para sanear la historia.

## 7. Validation
- **npm build:** PASS
- **npm lint:** PASS (mismas advertencias baseline).
- **pytest:** PASS (misma métrica baseline con resolución de la regresión post-corrupción).
- **SDD Check:** PASS.
- **Packaging:** Construcción con `build_package.py` PASS.

## 8. Regression Classification
- **NEW_REGRESSION:** 0
- **PRE_EXISTING_CONFIRMED:** 1 (`test_01_real_desktop_entrypoint_identity` / `test_02_two_real_desktops_isolation_and_chat` - timeout intermitente ambiental comprobado históricamente).
- **ENVIRONMENTAL:** 0.
- **UNRELATED:** 0

## 9. Architectural Impact
Ningún cambio estructural. React preserva su estado canónico ganado en G3.6, habiéndose únicamente sanitizado la superficie textual de Python y removido ruido del histórico, estabilizando pytest ante problemas de IO encodings.

## 10. Risk
- **LOW.** La corrección fue una restauración pura a nivel texto sin cambios lógicos.

## 11. Rollback
La corrección está aislada en los commits de la serie `fix(ui): correct post-retirement encoding...` y `fix(test): ...`. Para deshacerlo (reintroduciendo la corrupción), bastaría usar `git revert`.

## 12. What Was NOT Modified
- `agent_pipeline.py`
- `runtime.py`
- Lógica de persistencia en SQLite.
- Contratos de tareas o EventBus.
- Código React (`frontend/`).
- Infraestructura de empaquetado.

## 13. Final Decision
`G3.6.1 CLOSED — G3.6 VERIFIED`