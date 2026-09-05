# G3.0 DESKTOP UI MODERNIZATION AUDIT

## 1. Objective
Auditar críticamente la UI Desktop actual de CodeAgent y determinar si existe justificación arquitectónica y de producto para reemplazar o modernizar la interfaz actual, definiendo la tecnología más adecuada sin suposiciones previas.

## 2. Current Architecture
La arquitectura funcional estabilizada después de G2.5 es:

`	ext
Desktop
   |
   v
PyWebView (desktop_app.py)
   |
   v
localcode_claude_ui.html
   |
   +-- Task API (POST /api/tasks)
   +-- SSE / Events (/api/events)
   +-- Cancellation
   +-- Workspace
   +-- Native PyWebView APIs
            |
            v
      localcode_server.py
            |
            v
          runtime.py
            |
            v
       AgentPipeline
            |
            v
      Verification
`

## 3. Current UI Audit
localcode_claude_ui.html es un archivo masivo de más de 2200 líneas que concentra la presentación (HTML/CSS) y la lógica (JavaScript).

*   **Visual Design**: A pesar de usar estilos en línea y clases manuales, ofrece una interfaz razonablemente estética con temas oscuros, resaltado de sintaxis básico, y badges de estado. Sin embargo, su responsive behavior es limitado, carece de accesibilidad completa (a11y) y algunos estados (ej. loaders, botones deshabilitados) se manipulan forzando opacidades directamente en el DOM.
*   **Interaction Design**: Permite flujo de chat, selección de workspace, apertura de archivos y aprobación de comandos. El feedback de carga es básico y el manejo de historial es artesanal.
*   **Technical UI Complexity**: Extremadamente alta para un archivo único. Maneja variables de estado globales (messages, iles, ctiveFile), listeners anidados, peticiones HTTP (fetch y SSE) y manipulaciones directas del DOM (document.getElementById(...)). Hay mucha lógica mezclada con presentación y una carencia total de componentes reutilizables.

## 4. Verified Problems
*   **Monolito Frontend**: El HTML supera las 2200 líneas.
*   **Estado Mutado Directamente**: El DOM se manipula a mano, provocando inconsistencias si una llamada falla silenciosamente.
*   **Lógica de Resiliencia Frágil**: Manejar la reconexión de Server-Sent Events o fallos de red en Vanilla JS monolítico sin un framework reactivo es propenso a race conditions y memory leaks.

## 5. UX Problems
*   **Escalabilidad Visual**: Incorporar nuevas features complejas (ej. visualización avanzada del AST, comparación de diffs) será cada vez más difícil.
*   **Refresco Manual**: Los estados (como la lista de archivos) a veces requieren recargas manuales o polling primitivo.

## 6. Maintainability Problems
*   **Testing Frontend Inexistente**: Al carecer de bundler (vite, webpack) o estructura (Node.js/package.json), no hay tests unitarios para la UI (como Jest/Vitest) ni linting (ESLint).
*   **Deuda Técnica Creciente**: Cualquier cambio menor en la UI requiere bucear en miles de líneas y asegurar que ninguna manipulación imperativa de DOM se rompa.

## 7. UI Responsibility Boundary
El boundary debe ser estricto para evitar acoplamiento:

*   **FRONTEND**: Presentation, UI state (chat, pestañas), visualización del progreso (SSE listeners), interacciones del usuario, renderizado de errores, formateo de sintaxis.
*   **BACKEND**: Task lifecycle, Workspace management, AST extraction, SQLite persistence, Execution (AgentPipeline/Verification), Cancellation semantics, File I/O (salvo diálogos nativos gestionados por el shell del OS).

El frontend **NUNCA** debe conocer los detalles del Task Contract, AgentPipeline, ni realizar I/O intensivo del OS directamente sin pasar por el Server o el Shell.

## 8. Current Frontend API
La interfaz actual se basa en endpoints estables del servidor local:

| Capability | Current API | Canonical | Frontend Dependency |
| :--- | :--- | :--- | :--- |
| Task creation | POST /api/agent/chat -> untime | Yes | HTTP Fetch |
| Task status / Events | GET /api/pipeline/events | Yes | EventSource (SSE) |
| Cancellation | POST /api/tasks/<id>/cancel | Yes | HTTP Fetch |
| Workspace | POST /api/workspace/open-folder | Yes | HTTP Fetch / PyWebView Native |
| Files (Read/Write) | POST /api/fs/save | Yes | HTTP Fetch / PyWebView Native |
| Health Check | GET /api/health | Yes | HTTP Fetch |

## 9. Technology Evaluation
A continuación, evaluamos diferentes opciones sin asumir la adopción ciega de un framework popular:

*   **Option A - Keep HTML/JS**: Sin costo de migración, pero mantenibilidad crítica y UX bloqueada.
*   **Option B - React + TypeScript**: Ecosistema gigante, librerías listas para chat (ej. shadcn, react-markdown). Alta mantenibilidad, testing sólido.
*   **Option C - Vue + TypeScript**: Muy rápido de aprender, curvo suave, excelente tooling con Vite. Ecosistema algo menor que React.
*   **Option D - Svelte/SvelteKit**: Rendimiento puro, sin Virtual DOM. Extremadamente ligero, pero menor ecosistema de componentes out-of-the-box comparado con React.
*   **Option E - Tauri + React**: Backend Rust + Frontend Web. Descartado, ya que CodeAgent es inherentemente un backend Python intensivo. Requeriría un sidecar Python muy complejo y empaquetado doble.
*   **Option F - Electron + React**: Requiere Node.js embebido. Pesado, alto consumo de memoria, empaquetado complejo. No aporta ventajas reales sobre PyWebView dado que Python ya maneja el servidor local.

## 10. Framework Comparison

| Option | UX | Maintainability | Integration | Migration Risk | Complexity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HTML | Low | Very Poor | Native | Zero | High (Debt) |
| React | High | Excellent | API | Medium | Medium |
| Vue | High | Excellent | API | Medium | Medium |
| Svelte | High | Excellent | API | Medium | Medium |

## 11. Desktop Shell Comparison

| Shell | Backend Language | Binary Size | Memory Footprint | Packaging Complexity | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| PyWebView | Python | Small (uses OS Webview) | Low | Low (PyInstaller) | **KEEP** |
| Electron | Node.js | Massive | High | High | DO NOT USE |
| Tauri | Rust | Very Small | Very Low | High (Rust+Python bindings) | DO NOT USE |

## 12. Migration Strategy
**Migración Incremental Segura:**
El servidor localcode_server.py ya es una API REST/SSE agnóstica.
1. Se crea un proyecto Frontend (ej. rontend/) con Vite + React/Vue.
2. Durante el desarrollo, la app Frontend consume http://localhost:<port> donde corre el backend en modo developer.
3. Se implementa paridad funcional uno a uno (Chat, Markdown, SSE, File Tree).
4. El proceso de empaquetado (PyInstaller) se ajusta para construir el frontend (generando archivos estáticos en dist/) y el servidor Python simplemente los sirve.
5. PyWebView carga el index.html compilado.
6. Se retira localcode_claude_ui.html legacy.

## 13. Risk Assessment
*   **Riesgo de Arquitectura**: **LOW**. La arquitectura subyacente (Backend Python + API + Web UI) no cambia en absoluto. Solo se reemplaza el "cliente" (VanillaJS -> React/Vue).
*   **Riesgo de Integración**: **LOW**. El localcode_server.py no necesita enterarse de qué framework web se usa.
*   **Riesgo de Empaquetado**: **MEDIUM**. Requerirá Node.js solo en tiempo de compilación (CI/CD) para hacer 
pm run build, y PyInstaller deberá apuntar a los assets generados.

## 14. Testing Strategy
*   **Unit**: Vitest o Jest para componentes y reducers de estado.
*   **Integration**: MSW (Mock Service Worker) para simular la API REST de Python y eventos SSE en el frontend.
*   **Desktop/Regression**: Mantener pytest y sdd_check.py para asegurar que el backend permanece inmutable. Pruebas End-to-End con Playwright/Selenium si fuera necesario.

## 15. Candidates

### Candidate 1: Incremental React SPA + PyWebView
*   **Problem Solved**: Mantenibilidad UI, escalabilidad de componentes.
*   **Architecture**: Vite + React + TypeScript consumiendo REST/SSE de CodeAgent. Empaquetado con PyWebView sirviendo estáticos.
*   **Benefits**: TypeScript, Componentes, ReactMarkdown, Zustand (estado).
*   **Costs**: Añade Node/NPM como dependencia de desarrollo.
*   **Risks**: Ajuste del script de PyInstaller.
*   **Action**: **DO NOW**.

### Candidate 2: Incremental Svelte SPA + PyWebView
*   **Problem Solved**: Mantenibilidad UI sin Virtual DOM.
*   **Architecture**: Vite + Svelte.
*   **Benefits**: Más ligero que React.
*   **Costs/Risks**: Ecosistema de componentes Markdown/Code-Mirror algo más pequeño que React.
*   **Action**: **DEFER** (React provee mejor tooling pre-construido para IDEs y Markdown).

### Candidate 3: Tauri o Electron Rewrite
*   **Problem Solved**: N/A (Busca solucionar algo que PyWebView ya hace bien).
*   **Benefits**: Ninguno aplicable que compense perder Python como "First-Class Citizen".
*   **Action**: **DO NOT DO**.

## 16. What We Should NOT Do
*   **NO** reescribir el backend.
*   **NO** refactorizar AgentPipeline.
*   **NO** migrar a Tauri o Electron.
*   **NO** crear una nueva capa de API (Graphql, tRPC) innecesaria. El REST/SSE actual funciona perfectamente.
*   **NO** duplicar el ciclo de vida de tareas en Node.js.
*   **NO** modificar Verification Engine.
*   **NO** intentar modernizar añadiendo features (Ej. Auth); mantener Feature Parity estricto en V1.

## 17. Recommendation
Se recomienda **React + TypeScript + Vite**, manteniendo **PyWebView** como shell y localcode_server.py como Backend inmutable. 
*   **¿Por qué React?** Es el estándar de la industria, el ecosistema para componentes complejos (Editor de código tipo Monaco, Markdown parsing avanzado, Árboles virtuales) es maduro y robusto.
*   **¿Por qué PyWebView?** Porque CodeAgent es Python puro. Separar el Frontend compilado como estáticos dentro del binario Python (PyInstaller) es la forma más mantenible de distribuir la app, manteniendo tamaño pequeño.

## 18. Decision
**G3.0 JUSTIFIED — PROCEED TO UI ARCHITECTURE DESIGN**

## 19. What Was NOT Modified
Absolutamente **NINGUN** archivo de código, dependencia, ni script fue modificado durante esta fase. Es estrictamente un documento de auditoría.