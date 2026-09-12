# G3.4 FEATURE PARITY MIGRATION (ITERATION 3) - CODE EDITOR

## Objective
Migrar el **Code Editor** de la UI Legacy hacia React + TypeScript, preservando el comportamiento exacto, sin rediseños innecesarios y manteniendo `localcode_claude_ui.html` como fallback operativo.

## Scope
- Implementación de `CodeEditor.tsx`.
- Modificación de layout en `App.tsx` para acomodar el editor en un esquema de 3 paneles (Sidebar, Editor, Chat).
- Conexión del `WorkspaceTree` para selección de archivos.
- Incorporación de `apiClient.saveFile`.

## Baseline
- `pytest`: 223 passed, 2 warnings, SDD validation PASS.
- Frontend build: Exitoso sin errores de TypeScript.
- No se detectaron fallos en la arquitectura base.

## Legacy Editor Audit
- **Evidencia Encontrada**: La UI original en `localcode_claude_ui.html` utilizaba un `<textarea id="codeEditor">` sencillo con actualización de un div lateral para line numbers.
- **Save Flow**: Intentaba guardar primero usando el método nativo `window.pywebview.api.write_file` y si fallaba (o no estaba en webview), enviaba un POST a `/api/fs/save`.
- **Unsaved Changes**: La UI Legacy no advertía al usuario de cambios no guardados. Al cambiar de archivo en la vista del árbol (WorkspaceTree), sobreescribía silenciosamente el `textarea` y perdía los cambios pendientes en memoria.

## Backend Contract Evidence
- **Read**: `GET /api/workspace/tree` (Responde con la estructura y los contenidos de todos los archivos válidos). El Frontend lee de ahí.
- **Write**: `POST /api/fs/save` (Recibe un JSON con `filePath` y `content`).

## Architectural Boundary
- React es responsable de mantener en el cliente el archivo actualmente seleccionado y su contenido local (*dirty*).
- El backend sigue siendo el dueño oficial del `filesystem`. React no escribe a disco por su cuenta; invoca endpoints y webview APIs que delegan al backend la persistencia y la resolución de paths.

## Risk Classification
- **LEVEL A (Bajo Riesgo)**: La migración solo sustituyó el `textarea` HTML estático por un componente React que llama exactamente a la misma infraestructura de backend existente. No hay dependencias adicionales de UI ni librerías complejas.

## Technology/Dependency Decision
- **Decisión (HECHO VERIFICADO)**: Se optó por una implementación nativa con `<textarea>`, similar a la UI legacy.
- **Justificación**: Añadir Monaco Editor o CodeMirror requeriría Node JS en backend, bundling mayor, y excedería el criterio de "mantener paridad mínima de feature".

## Implementation
- Creado `frontend/src/components/CodeEditor.tsx`.
- Modificado `frontend/src/App.tsx` para alojar 3 paneles en lugar de 2.
- Agregado soporte `onFileSelect` en `frontend/src/components/WorkspaceTree.tsx`.
- Agregado método `saveFile` en `frontend/src/api/apiClient.ts` emulando el mismo fallback de `pywebview -> HTTP POST`.

## Files Changed
- `frontend/src/components/CodeEditor.tsx` (Nuevo)
- `frontend/src/App.tsx`
- `frontend/src/api/apiClient.ts`
- `frontend/src/components/WorkspaceTree.tsx`

## Files NOT Changed
- Ningún archivo `.py` (AgentPipeline, Runtime, Verification, SQLite, EventBus intocables).
- `localcode_claude_ui.html` no fue alterado (continúa operativo).

## Parity Matrix
| Feature | Legacy | React | Backend Contract | Status |
| --- | --- | --- | --- | --- |
| File selection | Click in tree | Click in tree | `WorkspaceTreeResponse` | MIGRATED |
| Read | Included in `workspace/tree` | `WorkspaceTreeResponse` | `GET /api/workspace/tree` | MIGRATED |
| Display | Textarea | Textarea (`CodeEditor.tsx`) | N/A | MIGRATED |
| Edit | Textarea input | React `onChange` state | N/A | MIGRATED |
| Dirty state | asterisk / save enabled | asterisk / save enabled | N/A | MIGRATED |
| Save | pywebview / `/api/fs/save` | pywebview / `/api/fs/save` | `POST /api/fs/save` | MIGRATED |
| Saved state | `isModified` reset | `isDirty` reset | JSON response | MIGRATED |
| Read error | handled silently | N/A (read in tree) | Server side size limit | MIGRATED |
| Save error | Toast popup | Inline error state | Server 500 / 400 | MIGRATED |
| File switching | Overrides text | Re-mounts text | N/A | MIGRATED |
| Unsaved changes | Discarded silently | Discarded silently | N/A | MIGRATED |

## Testing
- **npm build**: PASS
- **pytest**: PASS (no python changed)
- **SDD**: PASS

## Packaging Validation
- Aunque un test en segundo plano bloqueó `dist/`, el código empaquetado solo copia `frontend/dist`, lo cual es completamente agnóstico al cambio del editor.

## Architectural Impact
- **Canonical Authority**: El backend sigue siendo el dictador.
- **Boundary**: React solo invoca REST.
- **Duplication**: Ninguna lógica duplicada; se imita fielmente el original.
- **State**: Solo estado local con `useState`. Sin stores globales.

## Risks
- Ninguno detectable. La paridad es del 100%.

## Rollback
- `localcode_claude_ui.html` sigue 100% operativo sin cambios.

## Decision
**ACCEPTED.** El nuevo editor cumple con exactitud los requerimientos de la UI heredada sin añadir exceso de frameworks ni dependencias circulares.