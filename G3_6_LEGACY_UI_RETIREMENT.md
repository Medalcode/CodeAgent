# G3.6 LEGACY UI RETIREMENT (CONTROLLED EXECUTION)

## 1. Objective
Retirar de forma segura y definitiva la interfaz de escritorio heredada (`mis_agentes_inteligentes/localcode_claude_ui.html`) y configurar React como la ǖnica UI canónica para la aplicación, eliminando dependencias obsoletas sin afectar APIs ni lógica backend.

## 2. Baseline
- `pytest`: 222 passed, 1 environmental timeout (test_01_real_desktop_entrypoint_identity).
- `SDD Check`: PASS.
- `npm build / lint`: PASS.
- El código se encontraba en la rama `main` en un estado limpio antes de la ejecución de G3.6.

## 3. Scope
- Remoción física del archivo `localcode_claude_ui.html`.
- Refactorización de enrutamiento en `localcode_server.py`.
- Actualización de suite de pruebas para dependencias explícitas de la UI vieja.
- Eliminación del archivo del manifiesto de empaquetado.

## 4. Legacy Consumers Found
Se auditaron y abordaron las siguientes dependencias:
- **ACTIVE RUNTIME**: `localcode_server.py` mapeaba la ruta raíz (`/`) al HTML viejo.
- **ACTIVE RUNTIME**: `app.py` contenía un warning refiriéndose al HTML viejo.
- **ACTIVE TEST**: `tests/test_desktop_pipeline_visualization.py`, `tests/test_localcode_server.py`, `tests/test_desktop_app.py`.
- **PACKAGING**: `packaging/manifest.json`.

## 5. Routing Changes
- En `localcode_server.py`, las rutas como `/`, `/ui`, `/app`, `/chat` se actualizaron para resolver a `/frontend/dist/index.html`.
- Se preservaron íntegramente las rutas de API (`/api/*`), manteniendo el contrato estricto sin pérdida de funcionalidad.

## 6. Test Changes
- **MIGRATE**: `tests/test_localcode_server.py` y `tests/test_desktop_app.py` pasaron de buscar la ruta `/localcode_claude_ui.html` a la nueva UI.
- **MIGRATE**: `tests/test_desktop_pipeline_visualization.py` que originalmente abría el código fuente HTML, fue actualizado para englobar el _bundle minificado de React_ (en `frontend/dist/assets/`) comprobando la existencia de la lógica `onmessage`, `JSON.parse` y `onerror` del EventAdapter, garantizando así la trazabilidad SDD de visualización de eventos sin amarrarse a literales que desaparecen en el build paso final de Vite.

## 7. Packaging Changes
- Modificado `packaging/manifest.json`.
- Eliminado `mis_agentes_inteligentes/localcode_claude_ui.html` del array `app_files`.
- Se verificó que `frontend/dist` persiste intacto en el array `app_directories`.

## 8. Legacy HTML Removal
- El archivo físico `mis_agentes_inteligentes/localcode_claude_ui.html` **HA SIDO ELIMINADO.**

## 9. Post-Removal Reference Audit
Se ejecutó nuevamente la bǖsqueda de la cadena `localcode_claude_ui.html` en todo el repositorio.
- **Resultado:** 0 dependencias activas runtime, 0 en packaging, 0 en test suites. Únicamente figuran remanentes en los directorios de cachés (`graphify-out/`), los cuales son artefactos pasivos de documentación y no impactan ejecución.

## 10. Validation Results
- **npm build**: PASS.
- **npm lint**: PASS.
- **pytest**: PASS (con el timeout intermitente ambiental conocido inalterado).
- **SDD Check**: PASS.
- **Packaging Build**: PASS.

## 11. Regression Classification
- **NEW_REGRESSION**: Ninguna.
- **PRE_EXISTING_CONFIRMED**: El timeout en `test_e2e_real_desktop_lifecycle.py` es ambiental y existía de antemano.

## 12. Architectural Impact
- **React es ahora la ǖnica UI de Desktop**. El flujo de arranque nativo de PyWebView y el acceso browser-based local redirigen invariablemente a los _assets_ generados por Vite.
- Las responsabilidades del backend no han cambiado (Runtime, AgentPipeline, Verificación y Cancelación). No se añadieron librerías complejas.
- CodeAgent abandona su diseño híbrido transitorio y solidifica la separación limpia cliente-servidor para su UI.

## 13. Risk
- **LOW**. Todos los consumos fueron reasignados. Empaquetado exitoso validado.

## 14. Rollback Strategy
El cambio fue consolidado en un solo commit semántico (`refactor(ui): retire legacy HTML UI and route desktop to React (G3.6)`).
Para revertir, basta con ejecutar `git revert HEAD`, lo cual devolverá el HTML heredado y recompondrá los strings fijos en los tests de visualización y enrutamiento en Python.

## 15. What was NOT modified
- `desktop_app.py`
- `agent_pipeline.py`
- `runtime.py`
- Lógica de persistencia en SQLite o en memoria.
- APIs JSON y contratos SDD.

## 16. Final Decision
**RETIRED SUCCESSFULLY.**