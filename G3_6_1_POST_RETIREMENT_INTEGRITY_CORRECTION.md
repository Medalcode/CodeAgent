# G3.6.1 POST-RETIREMENT INTEGRITY CORRECTION

## 1. Objective
Corregir los efectos secundarios no intencionados introducidos durante el retiro de la Legacy UI (G3.6), restaurando la codificación original UTF-8 y eliminando cambios que se salieron del alcance de la tarea, sin comprometer el objetivo original de G3.6 (hacer de React la única UI canónica).

## 2. Baseline
- **Parent Commit previo a la corrupción:** `49ce827` (Fin de G3.4 Iteration 3)
- **G3.6 Commits observados:** `2308f92` (Ejecución G3.6) y `c4ed5a2` (Reporte)
- **Tests baseline:** 222 passed, 1 environmental timeout. SDD PASS.
- **Build baseline:** npm build PASS.

## 3. Evidence
- La modificación con PowerShell `Set-Content` de `mis_agentes_inteligentes/localcode_server.py` y `mis_agentes_inteligentes/app.py` corrompió la codificación (UTF-8 a Windows-1252/mojibake), alterando caracteres especiales como `❌` a `â Œ` o `ó` a `Ã³`.
- El archivo `mis_agentes_inteligentes/benchmark_report_v42.md` fue accidentalmente añadido en el commit original de G3.6 mediante una adición genérica de directorios (`git add mis_agentes_inteligentes/`), pese a no estar relacionado con el retiro del Legacy UI.

## 4. Corrections
- Restauración vía `git checkout 49ce827 --` de `app.py` y `localcode_server.py`.
- Re-aplicación de los enrutamientos intencionales hacia `/frontend/dist/index.html` usando un script en Python garantizando preservación `encoding='utf-8'`.
- Restauración de `benchmark_report_v42.md` a su estado original (deshaciendo su inclusión indeseada).

## 5. Preserved G3.6 Changes
- `mis_agentes_inteligentes/localcode_claude_ui.html` sigue estrictamente eliminado.
- React sigue siendo la **Canonical Desktop UI**.
- `desktop_app.py` y `localcode_server.py` siguen apuntando a `frontend/dist/index.html`.
- Todas las rutas `/api/*` operan sin cambios.
- El empaquetado persiste sin el HTML heredado y conserva `frontend/dist`.

## 6. Unrelated Changes
- `mis_agentes_inteligentes/benchmark_report_v42.md` regresó a su estado histórico original en el árbol de trabajo y fue commiteado en reversa dentro del commit correctivo para sanear la historia.

## 7. Validation
- **npm build:** PASS
- **npm lint:** PASS (mismas advertencias baseline).
- **pytest:** PASS (misma métrica baseline).
- **SDD Check:** PASS.
- **Packaging:** Construcción con `build_package.py` PASS, sin el HTML antiguo.

## 8. Regression Classification
- **NEW_REGRESSION:** 0
- **PRE_EXISTING_CONFIRMED:** 1 (`test_01_real_desktop_entrypoint_identity` / `test_02_two_real_desktops_isolation_and_chat` - timeout intermitente ambiental comprobado históricamente).
- **ENVIRONMENTAL:** 0 (Aparte del mencionado).
- **UNRELATED:** 0

## 9. Architectural Impact
Ningún cambio estructural. React preserva su estado canónico ganado en G3.6, habiéndose únicamente sanitizado la superficie textual de Python y removido ruido del histórico.

## 10. Risk
- **LOW.** La corrección fue una restauración pura a nivel texto sin cambios lógicos.

## 11. Rollback
La corrección está aislada en el commit `fix(ui): correct post-retirement encoding and scope drift`. Para deshacerlo (reintroduciendo la corrupción), bastaría un `git revert HEAD`.

## 12. What Was NOT Modified
- `agent_pipeline.py`
- `runtime.py`
- Lógica de persistencia en SQLite.
- Contratos de tareas o EventBus.
- Código React (`frontend/`).
- Infraestructura de empaquetado.

## 13. Final Decision
`G3.6.1 CLOSED — G3.6 VERIFIED`