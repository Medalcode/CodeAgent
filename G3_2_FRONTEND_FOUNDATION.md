# G3.2 FRONTEND FOUNDATION

## 1. Objective
Implementar la fundación técnica del nuevo frontend Desktop de CodeAgent utilizando React, TypeScript y Vite, demostrando que puede comunicarse bidireccionalmente con el backend Python existente (API REST y SSE) sin alterar la arquitectura base ni introducir Node.js en producción.

## 2. Baseline
*   Antes de los cambios, se ejecutó scripts/sdd_check.py y pytest.
*   **Fix Crítico:** Durante el baseline se identificó y reparó un *race condition* originado en la fase anterior (G2.5) en localcode_server.py. Si la tarea se completaba instantáneamente, el evento TASK_COMPLETED se emitía antes de que el servidor se suscribiera al event_bus, lo que provocaba un *timeout* en 	est_e2e_real_desktop_lifecycle.py. Se ajustó la suscripción para que preceda al untime.start_task(...), solventando el bug.

## 3. Files Added / Modified
*   **Agregados:**
    *   rontend/ (Scaffolding Vite React-TS)
    *   rontend/src/types/index.ts (Contratos tipados del dominio: TaskStatus, SSEEvent, ChatResponse).
    *   rontend/src/api/apiClient.ts (Cliente fetch para /api/agent/chat y /api/tasks/<id>/cancel).
    *   rontend/src/events/EventAdapter.ts (Clase wrapper para EventSource que normaliza SSE y emite callbacks seguros).
    *   rontend/src/App.tsx (Componente funcional de prueba integrado con el EventAdapter y el Client).
    *   rontend/vite.config.ts (Configurado para enrutar el proxy de desarrollo a http://localhost:8000 y servir base relativa).
*   **Modificados:**
    *   mis_agentes_inteligentes/localcode_server.py (Fix de carrera, sin alterar interfaces).
    *   mis_agentes_inteligentes/localcode_claude_ui.html (Agregado enlace de fallback: "Try React UI (Beta)").

## 4. Dependencies Added
Únicamente dependencias de desarrollo y empaquetado en package.json (Vite, React, React-DOM, TypeScript). Node/npm existe **sólo** como cadena de compilación.

## 5. Architecture Implemented
`	ext
React (App.tsx)
 ├──> apiClient.ts (Fetch POST)
 └──> EventAdapter.ts (EventSource)
       └──> Backend (localcode_server.py -> CodeAgentRuntime -> EventBus)
`
Se respetó la separación. React no conoce los detalles de SQLite ni del AST de Python.

## 6. API Integration
El frontend realiza llamadas POST a piClient.startChat(prompt, taskId). Utiliza promesas asíncronas para manejar el éxito y extraer posibles errores HTTP, reflejándolos en la UI mínima.

## 7. SSE Integration
Se implementó EventSource apuntando a /api/pipeline/events?task_id=.... Escucha la conexión y transforma los strings de JSON en la interfaz TS tipada SSEEvent.

## 8. EventAdapter
El EventAdapter se diseñó para separar completamente la red de React. En App.tsx, usamos una referencia useRef para mantener la conexión persistente, y callbacks que mutan el estado visual status y la lista de eventos recibidos (events).

## 9. Cancellation Integration
El piClient.cancelTask interactúa con el endpoint de cancel, disparando el cancel_event de los hilos de Python. El EventAdapter captura entonces el TASK_CANCELLED emitido asíncronamente por el Backend. 

## 10. Legacy Coexistence
La interfaz antigua localcode_claude_ui.html sigue siendo cargada nativamente por desktop_app.py. A través de un link flotante incorporado, los usuarios o desarrolladores pueden navegar a /frontend/dist/index.html servido por SimpleHTTPRequestHandler temporalmente para propósitos de prueba, comprobando que ambas coexisten sin destruirse.

## 11. Development Mode

pm run dev expone el servidor local de Vite haciendo proxy a localhost:8000/api. Se elude el problema de CORS naturalmente porque a los ojos de la app web, el backend y el frontend comparten origen (localhost:5173).

## 12. Production Build
El comando 
pm run build transpila y minimiza los TS/TSX a HTML, JS, CSS puros en rontend/dist/. Estos activos estáticos carecen de referencias de servidor Node.

## 13. PyWebView Integration
A través del enlace agregado a la UI legacy, PyWebView demostró ser perfectamente capaz de renderizar los activos estáticos de Vite (index.html y bundles .js) sirviéndose desde el directorio rontend/dist.

## 14. Testing
Se ha probado la ejecución del smoke test del empaquetado:
- Build de Node limpio (
pm run build).
- Desacoplamiento (el backend sigue respondiendo).

## 15. Regression Comparison
Se comparó pytest -q contra la falla detectada.
El error E2E provocado por un timeout anterior fue RESUELTO. La ejecución de Python es **PRE-EXISTING_FIXED**. La regresión de UI es nula.

## 16. SDD Result
python scripts/sdd_check.py arroja PASS, garantizando que los Invariantes Arquitectónicos se preservan inalterados.

## 17. Packaging Result
Se validó la generación de activos estáticos del frontend. Aún no se acopló a PyInstaller para no romper la distribución actual, dejando esta tarea para G3.3.

## 18. Risks
- **Riesgo Visual:** La interfaz fundacional carece de diseño, resaltado Markdown y árbol de directorios.
- **Riesgo Proxy PyInstaller:** En G3.3 habrá que modificar PyInstaller para incluir recursivamente los assets del frontend (dist/assets).

## 19. Rollback
Para desactivar esta fase, sencillamente borrar la carpeta rontend/ y el botón introducido en localcode_claude_ui.html. 

## 20. What Was NOT Changed
NO SE MODIFICÓ:
* AgentPipeline
* Runtime
* SQLite
* Verification
* SDD
* APIs

## 21. NEXT PHASE
Se recomienda continuar a:
**G3.3 — Feature-Parity Migration**