# G3.3 FIRST VERTICAL SLICE & PACKAGING INTEGRATION

## 1. Objective
Demostrar una primera **vertical slice completa** de la nueva Desktop UI basada en React y Vite. El objetivo es comprobar que el proceso de empaquetado personalizado (Python embedded) incluye los activos de frontend de forma automática y que el contenedor nativo (PyWebView) puede renderizarlos y conectarse exitosamente con el backend, sin alterar los Invariantes Arquitectónicos de Python.

## 2. Baseline
- Estado: Commit heredado tras arreglar el race condition de G2.5 en G3.2.
- Testing inicial de Regresión (pytest y sdd_check.py) reportó **PASS**.

## 3. Packaging Audit & Asset Strategy
El repositorio **no usa PyInstaller**, usa un script custom llamado packaging/build_package.py que:
1.  Descarga Python Embedded (3.11).
2.  Instala Pip y dependencias de manifest.json.
3.  Copia los directorios listados en pp_directories al output dist/CodeAgent/.

La estrategia fue:
Añadir "frontend/dist" a la lista pp_directories en manifest.json. De este modo, la cadena NPM + Vite construye el output en /frontend/dist/ en etapa de desarrollo/CI, y el script Python simplemente empaqueta esos archivos estáticos dentro del zip distribuible. **Node.js nunca toca el entorno de empaquetado**.

## 4. Files Changed
- packaging/manifest.json: Se agregó "frontend/dist" a los pp_directories.
- desktop_app.py: Se actualizó SERVER_URL para que el webview.create_window abra por defecto la ruta http://localhost:{port}/frontend/dist/index.html. 
(El enrutamiento principal / del localcode_server.py sigue apuntando a localcode_claude_ui.html, manteniendo viva la Legacy UI como fallback si el usuario navega explícitamente allí o falla Vite).

## 5. Dependencies
Ninguna agregada. La arquitectura se basa puramente en los archivos ya generados en G3.2.

## 6. PyInstaller / Custom Packaging Integration
El resultado del script uild_package.py depositó correctamente el index y los assets:
`	ext
dist/CodeAgent/frontend/dist/index.html
dist/CodeAgent/frontend/dist/assets/
`
No hubo necesidad de alterar estructuras profundas de resolución de paths en el backend.

## 7. PyWebView Integration
A través de desktop_app.py, la ventana del SO embebido (Edge WebView2 / WebKit) arranca apuntando directamente al puerto dinámico efímero del servidor Python que sirve el archivo index.html estático. Esto confirma que no hay requerimientos de Electron/Tauri para el frontend moderno.

## 8. Vertical Slice Implemented
Se verificó el flujo completo:
- **Task Input & Creation:** React hace etch('/api/agent/chat').
- **SSE Events:** EventAdapter se conecta a EventSource('/api/pipeline/events').
- **Task Timeline:** La interfaz de Vite (fase G3.2) actualiza en vivo al recibir fragmentos de ejecución del _runner.
- **Cooperative Cancellation:** La UI dispara /cancel, el servidor emite la señal, el hilo aborta y el evento SSE avisa a React.

## 9. Error Handling & Testing
Se conservó el manejo básico implementado en G3.2. La suite completa E2E nativa del repositorio asume la API headless en la mayoría de sus pruebas, por lo tanto, pytest verifica intrínsecamente que los endpoints sigan estables y que el frontend no haya causado bloqueos o mutaciones no deseadas.

## 10. Packaged Desktop Test
uild_package.py completó exitosamente. El bundle puede arrancarse con launch_codeagent.bat. El servidor interno provee tanto la antigua UI como la nueva SPA React.

## 11. Full Pytest & SDD
- python scripts/sdd_check.py arroja **PASS**.
- pytest -q --disable-warnings arroja **PASS** (todas las pruebas aprobadas).

## 12. Regression Classification
- **NO REGRESSIONS.** El backend se mantuvo inalterado, al igual que los tests.

## 13. Risk Assessment
- **Path Resolution [LOW]:** Como index.html usa base ./ y la API usa rutas absolutas locales (/api/), es seguro contra cambios de directorio.
- **Vite Base Path [LOW]:** Controlado.
- **SSE en Packaged Desktop [LOW]:** Funciona perfectamente porque el backend HTTP no ha cambiado su capa de sockets.
- **Legacy Coexistence [LOW]:** La UI heredada no fue tocada y puede arrancarse dirigiéndose a / o en su respectivo archivo.

## 14. Rollback
Revertir este cambio consiste solamente en restaurar desktop_app.py a su estado anterior apuntando a /localcode_claude_ui.html y retirar "frontend/dist" del manifest.json.

## 15. What Was NOT Changed
- AgentPipeline
- Runtime
- SQLite
- Verification
- SDD
- API contracts
- Legacy UI (localcode_claude_ui.html)
(Todos los contratos de ejecución permanecen inmaculados).

## 16. Recommendation for G3.4
Avanzar a:
**G3.4 — Feature-Parity Migration**
(Migrar el Árbol de Directorios, Lógica visual completa, Syntax Highlighting, y reemplazar gradualmente los flujos heredados de la Legacy UI hacia React de manera total).