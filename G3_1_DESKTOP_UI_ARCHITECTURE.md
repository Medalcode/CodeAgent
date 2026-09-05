# G3.1 DESKTOP UI ARCHITECTURE DESIGN

## 1. Objective
Diseñar la arquitectura técnica de la nueva Desktop UI de CodeAgent basada en React, TypeScript y Vite, orquestada por PyWebView. Esta arquitectura proporcionará el plano técnico verificable para permitir la migración sin comprometer los Invariantes Arquitectónicos (SDD), la semántica de Execution ni la de Verification en el backend de Python.

## 2. Evidence (Verified Facts)
Durante el análisis de código en vivo del estado G2.5, se comprobó lo siguiente:
*   El backend ya gestiona el ciclo asíncrono y los SSE events a través del CodeAgentRuntime (untime.py).
*   Los endpoints principales que consume la UI actual son:
    *   POST /api/agent/chat: Crea una tarea (permite instanciar proveedor y modelo) delegándola de forma segura a untime.start_task(agent_runner=_runner). La llamada bloquea en un hilo interno gestionado por ThreadingMixIn usando un 	hreading.Event, retornando JSON en caso de éxito, error o cancelación (HTTP 200 o HTTP 500 si se cancela).
    *   POST /api/tasks/<task_id>/cancel: Emite el flag de cancelación asíncrono a nivel de threading, interrumpiendo AgentPipeline de manera cooperativa.
    *   GET /api/pipeline/events: Emite SSE events (TASK_CREATED, STATE_CHANGED, TOOL_CALL, LLM_CALL_COMPLETED, TASK_COMPLETED, TASK_FAILED, TASK_CANCELLED).
    *   POST /api/workspace/open-folder: Abre el diálogo nativo (o fallback) y notifica al IDE del nuevo workspace.
*   Existe POST /api/tasks como endpoint canónico secundario, pero carece de la parametrización dinámica del Runner, la cual asume configuración por defecto de 	ools.py.

## 3. API Inconsistency Findings
**Conflicto:** POST /api/tasks vs POST /api/agent/chat.
**Resolución:**
*   POST /api/agent/chat es el contrato verdaderamente utilizado por la UI porque es el **único** capaz de instanciar y configurar explícitamente el _runner de Python (pasando provider y modelo) antes de inyectarlo en untime.py.
*   POST /api/tasks es un fallback headless usado para testing o automatización externa.
*   **Decisión Arquitectónica para la Nueva UI:** La nueva UI de React debe usar POST /api/agent/chat para iniciar la conversación/tarea, preservando la compatibilidad absoluta y el proxy model/provider, sin obligar a rediseñar el backend.

## 4. Frontend / Backend Boundary

### FRONTEND (React)
*   **Presentación y Componentes:** Renderizado de Markdown, resaltado de sintaxis, árbol de archivos, diálogos, scroll, temas visuales, inputs de usuario.
*   **Estado Transitorio de Cliente:** Formularios, dropdowns abiertos, visibilidad del sidebar, preferencias visuales, control de peticiones en vuelo (AbortController, Loading Spinners).
*   **Manejo de Eventos (Event Adapter):** Escuchar el EventSource, mutar el estado transitorio del proceso y transformarlo en timeline visual.

### BACKEND (Python)
*   **Autoridad de Ejecución:** Orquestación (AgentPipeline), verificación AST (Verification Engine).
*   **Task State Authority:** Persistencia SQLite (untime_db.py), checkpointing.
*   **Semántica de Cancelación:** Control de concurrencia de hilos (	hreading.Event), aborto de llamadas LLM y preservación de aislamiento.
*   **Filesystem & SDD:** Reglas del SDD y validación de workspaces de forma segura.

El Frontend **NO** duplica el ciclo de vida, **NO** asume cuándo una tarea terminó hasta no recibir TASK_COMPLETED (o el return de HTTP), y **NO** interroga el AST directamente sin pasar por una herramienta proxy.

## 5. Client State vs Server State
*   **Client State (Zustand o React Context):**
    *   isWorkspaceModalOpen: boolean
    *   sidebarExpanded: boolean
    *   currentInput: string
    *   selectedModel: string
    *   uiTheme: 'light' | 'dark'
*   **Server State (Reflejado asíncronamente en UI vía SSE/Fetch):**
    *   	askLifecycle: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'CANCELLED' | 'FAILED'
    *   	askTimeline: Array de eventos recibidos por /api/pipeline/events
    *   workspaceFiles: Árbol de archivos proporcionado por el backend tras selección.

## 6. Frontend Architecture: API Client & Event Adapter
Se estructura una capa intermedia explícita para evitar mezclar lógica de red y componentes.

`	ext
frontend/src/api/
├── apiClient.ts      # Funciones asíncronas puras (fetch)
├── endpoints.ts      # startChat(), cancelTask(), fetchWorkspace()
└── EventAdapter.ts   # Envoltorio de EventSource
`
**EventAdapter** será una clase o hook (useTaskEvents(taskId)) encargado de transformar los payloads puros de SSE (ej. TOOL_EXECUTED) en acciones tipadas de estado en React (dispatch o mutación de Store), permitiendo reconexión automática y limpieza de listeners (close()) al desmontar.

## 7. Component Architecture
Basado en las responsabilidades estrictas, la estructura de React sugerida es:

`	ext
<App>
  ├── <Sidebar>
  │    ├── <WorkspaceTree>
  │    └── <TaskHistoryList>
  ├── <ChatContainer>
  │    ├── <MessageList> (Renderiza Markdown)
  │    ├── <EventTimeline> (Renderiza eventos SSE inline)
  │    └── <InputArea>
  └── <StatusBar>
`
*   WorkspaceTree: Visualiza los archivos del Backend; invoca piClient.openFolder() si está vacío.
*   EventTimeline: Componente "tonto" (dummy) que recibe la lista de eventos desde el Store global.
*   InputArea: Posee un estado local controlado; dispara startChat(), manejando bloqueos de carga (Loading) según el estado derivado del backend.

## 8. TypeScript Contracts (Type Safety)
Para garantizar integridad, se definirán *solamente* los tipos que React necesita conocer de la capa de comunicación (no los tipos internos de Python).

`	ypescript
export type TaskStatus = 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'CANCELLED' | 'FAILED';

export interface SSEEvent {
  event_type: 'TASK_CREATED' | 'STATE_CHANGED' | 'TOOL_CALL' | 'TASK_COMPLETED' | 'TASK_FAILED' | 'TASK_CANCELLED';
  task_id: string;
  payload: any;
}

export interface ChatResponse {
  success: boolean;
  respuesta?: string;
  terminal_tasks?: string[];
  error?: string;
}
`

## 9. Build Architecture & Packaging
La infraestructura Node/Vite **solo existirá en tiempo de compilación (Build Time)**. No se enviará Node al empaquetado Desktop.
1.  **Development Mode:** 
pm run dev inicia un servidor Vite en el puerto 5173. El servidor Vite hace proxy (server.proxy de ite.config.ts) de /api hacia localhost:8080 (donde corre localcode_server.py).
2.  **Production Mode:** 
pm run build transpila TypeScript a HTML/CSS/JS estático y lo inyecta en un subdirectorio dist/frontend.
3.  **Packaging (PyInstaller):** PyInstaller se configura para empacar dist/frontend como assets. localcode_server.py servirá el nuevo index.html estático en su ruta raíz.

## 10. Migration Strategy
1.  **Fase 1 (Frontend Foundation):** Inicializar Vite + React. Configurar tipados y API client.
2.  **Fase 2 (Feature Parity - Paralelo):** Implementar Sidebar, Árbol y Chat en React en paralelo al sistema viejo. Ambos coexistirán temporalmente (se puede servir UI antigua en /legacy).
3.  **Fase 3 (Cutover):** Una vez que los Tests Unitarios e Integration (E2E básico de red) aprueben la nueva UI, desktop_app.py apuntará al nuevo index.html.
4.  **Fase 4 (Retirement):** Se elimina localcode_claude_ui.html del repositorio.

## 11. Feature Parity Matrix
| Feature | Legacy UI | React UI Goal | Complexity / Risk |
| :--- | :--- | :--- | :--- |
| Workspace Dialog & Fallback | SÍ | SÍ | Low |
| Chat Markdown Rendering | SÍ | SÍ (ReactMarkdown) | Low |
| SSE Streaming & Logs | SÍ | SÍ (EventAdapter) | Medium |
| Cooperative Cancellation | SÍ | SÍ | Low (API exist.) |
| Terminal Approvals | SÍ | SÍ | Medium |
| Archivos (Open/Save) | SÍ | DEFER (Simplificar/Omitir si no es IDE) | Medium |

## 12. Testing Architecture
*   **Unit Tests (Vitest):** Probar lógica pura del EventAdapter, asegurando que STATE_CHANGED transforma correctamente el store.
*   **Component Tests (React Testing Library):** Asegurar que <InputArea> desactiva botones durante status === 'RUNNING'.
*   **Integration (MSW):** Interceptar llamadas etch('/api/agent/chat') para probar que los reducers reaccionan a respuestas de error (ej. Cancelación por Timeout o Errores de Modelo).
*   **Regression (Backend):** Seguir obligando el uso de pytest y scripts/sdd_check.py para garantizar que la UI no rompa el Pipeline en el servidor Python.

## 13. Accessibility (A11y) Requirements
*   Uso de HTML Semántico en el Sidebar (<nav>, <ul>).
*   <form> nativo para el input del chat para permitir "Enter" submission naturalmente.
*   Atributos ria-live="polite" en el <EventTimeline> para leer actualizaciones asíncronas para screen-readers.
*   Atributo disabled nativo en el botón Enviar, prescindiendo del engañoso pointer-events: none por CSS actual.

## 14. Risk Assessment
*   **Frontend Risk [HIGH]:** Recrear un parser de eventos complejo y un renderizado de markdown fluido requiere librerías robustas y evitar Rerenders excesivos.
*   **Integration Risk [LOW]:** El servidor backend localcode_server.py no debe tocarse, pues su interfaz asíncrona ya está testeada y es sólida tras la reparación G2.5.
*   **Packaging Risk [MEDIUM]:** La dependencia transicional hacia Vite exige que el pipeline CI/CD o el flujo de Build manual realice primero un paso de 
pm install && npm run build antes de ejecutar PyInstaller. Esto modificará los documentos de Build existentes.

## 15. Rollback Strategy
Si durante la fase G3.2 o G3.3 se descubren bloqueadores nativos de compilación:
1. React se desarrolla en la carpeta rontend/.
2. Si falla críticamente, simplemente no se modifica el desktop_app.py (que seguirá apuntando a localcode_claude_ui.html).
3. El servidor Python sigue agnóstico a quién consume su API. El Rollback tiene un coste nulo para el backend.

## 16. SDD Check Validation
La arquitectura propuesta se adhiere 100% a los invariantes:
- **INV-001 (Pipeline Authority)**: La UI solo despacha requests; Python manda.
- **INV-006 (Tool Isolation)**: React no procesa ni ejecuta código, solo lo renderiza.
- **INV-008 (Desktop Lifecycle Safety)**: El uso de /api/tasks/<id>/cancel respeta la terminación cooperativa ThreadingMixIn.

## 17. Architectural Decision
La adopción de **React + TypeScript + Vite** sirviendo estáticos sobre **PyWebView** provee el equilibrio óptimo entre **Developer Experience**, **Mantenibilidad Frontend**, y **Aislamiento Funcional** sin corromper la autoridad del backend Python. La arquitectura cliente-servidor (REST + SSE) es asíncrona por defecto y completamente capaz de integrarse con React de manera profesional.

**SE ACEPTA LA ARQUITECTURA PROPUESTA.**

## 18. What Was NOT Modified
NO CODE CHANGES.
NO DEPENDENCY CHANGES.
NO API CHANGES.
NO BACKEND CHANGES.

## 19. NEXT PHASE
Se recomienda iniciar:
**G3.2 — Frontend Foundation / Implementation**
*(Desarrollo inicial de Vite+React manteniendo la UI antigua intacta).*