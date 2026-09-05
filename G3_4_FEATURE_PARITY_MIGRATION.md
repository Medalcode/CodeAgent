# G3.4 FEATURE PARITY MIGRATION (ITERATION 1)

## Objective
Migrar las características base del App Shell y el Workspace Tree (G3.4.1 y G3.4.2) a la nueva UI de React, estableciendo paridad funcional con la versión heredada, sin modificar la estructura o los endpoints del backend en Python.

## Baseline
- **Git Commit:** 070e794 feat(ui): implement G3.2-G3.3 React frontend foundation and packaging
- **Tests:** 223 passed (0 fallos).
- **SDD:** PASS.

## Legacy Inventory & Parity Matrix (Current Scope)
| Legacy Feature            | Implemented | React Equivalent           | Contract | Risk | Status |
| ------------------------- | ----------- | -------------------------- | -------- | ---- | ------ |
| **App Shell**             | Yes         | App.tsx layout           | None     | LOW  | MIGRATED |
| **Workspace Tree**        | Yes         | <WorkspaceTree />        | GET /api/workspace/tree | LOW  | MIGRATED |
| **Native Folder Picker**  | Yes         | window.pywebview.api     | PyWebView API | LOW  | MIGRATED |
| **Task Input**            | Yes (G3.3)  | App.tsx Input Area       | POST /api/agent/chat | LOW  | MIGRATED |
| **Task Submission**       | Yes (G3.3)  | piClient.ts             | POST /api/agent/chat | LOW  | MIGRATED |
| **SSE Event Timeline**    | Yes (G3.3)  | <EventTimeline /> logic  | GET /api/pipeline/events | LOW  | MIGRATED |
| **Cancellation**          | Yes (G3.3)  | piClient.ts             | POST /api/tasks/<id>/cancel | LOW | MIGRATED |

## Evidence
1. **Workspace Tree Migration:** Se implementó WorkspaceTree.tsx que consume el endpoint GET /api/workspace/tree. Renderiza de forma jerárquica los archivos parseando sus rutas relativas de manera exactamente equivalente a la UI heredada. 
2. **Native API integration:** El botón "Open Folder" ahora evalúa en tiempo de ejecución si existe window.pywebview.api. De ser así, invoca el picker nativo open_folder_dialog(), al igual que el comportamiento original de la Legacy UI.
3. **App Shell:** Se re-estructuró App.tsx usando un layout moderno y limpio con un Sidebar lateral fijo (Workspace) y un Main Content responsivo (Header, Timeline y área de Input). Todo con CSS plano y sin frameworks de UI (ej. Tailwind) para respetar las directivas de arquitectura mínima.

## Changes
- rontend/src/api/apiClient.ts: Añadido tipo WorkspaceFile, WorkspaceTreeResponse y función getWorkspaceTree().
- rontend/src/components/WorkspaceTree.tsx [NEW]: Componente para desplegar la estructura de directorios y llamar a la API pywebview nativa.
- rontend/src/App.tsx: Actualizado para incluir <WorkspaceTree /> en un sidebar y mejorar el layout (App Shell).

## Non-Changes
- **Backend:** NO se modificó ningún endpoint ni archivo en mis_agentes_inteligentes/. El contrato de la API existente fue 100% suficiente.
- **State Management:** NO se introdujo Redux ni Zustand. Todo se resolvió con useState y encapsulamiento local en el árbol de componentes.

## Architecture Impact
- **React Client:** Capaz de consumir correctamente el contexto de archivos locales y visualizarlo usando una jerarquía calculada a partir de los JSON lineales que emite Python.
- **Backend/Runtime:** Cero impacto.

## Risk
- **PyWebView context scoping [LOW]:** El objeto global de pywebview inyectado podría estar ausente durante el hot-reload en vite (desarrollo web normal). El código ya previene esto al envolver la llamada y manejar el caso donde no existe el contenedor nativo.

## Testing
- Compilación de 
pm run build exitosa.
- **Pytest:** Regresión ejecutada pre-construcción con cero fallos (223 passed).
- **SDD Check:** PASS.
- El empaquetado de Desktop fue regenerado satisfactoriamente.

## Rollback
- Continuar usando localcode_claude_ui.html, el cual sigue sirviéndose nativamente por el backend sin haber sido desmantelado ni deprecado. 

## Decision
**ACCEPTED** (Iteración 1). Listo para la iteración 2 u otra revisión según se considere.