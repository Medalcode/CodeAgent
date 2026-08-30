# SPEC-012 — Desktop Real-Time Pipeline EventSource Visualization

## Intent
Conectar la interfaz de usuario Desktop (`desktop_app.py`) al flujo de eventos Server-Sent Events en tiempo real (`GET /api/pipeline/events?task_id=XYZ`) de `SPEC-011`. Reemplazar el temporizador artificial estático (`secCount % 3 === 0`) con un componente visual reactivo que renderice en vivo las transiciones de la máquina de estados del `AgentPipeline` (`INIT`, `PLAN`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DIAGNOSE`, `REPLAN`, `CRITIC`, `DONE`) y las herramientas en ejecución.

## Preconditions
- El servidor backend `localcode_server.py` y la ruta SSE `GET /api/pipeline/events` (`SPEC-011`) se encuentran operativos.
- La interfaz Desktop `desktop_app.py` inicia una petición de chat con un `task_id` correlacionado.

## Postconditions
- La interfaz de usuario establece una conexión `EventSource` hacia `/api/pipeline/events?task_id=XYZ` durante la ejecución de la tarea.
- Al recibir eventos SSE `STATE_ENTERED` o `STATE_CHANGED`, el stepper de fases actualiza en vivo el indicador de estado activo (`PLAN`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DONE`).
- Al recibir eventos SSE `TOOL_EXECUTED`, la interfaz muestra una tarjeta informativa con el nombre de la herramienta en ejecución.
- Al recibir `TASK_COMPLETED`, `TASK_FAILED` o finalizar la llamada de chat HTTP, la conexión `EventSource` invoca `.close()` limpiamente.
- Si la conexión SSE falla o no está disponible, la interfaz degrada elegantemente hacia la respuesta final del agente sin interrumpir la ejecución.

## Invariants
- **INV-001** (Pipeline Authority): La visualización en el cliente es estrictamente de solo lectura y no altera la autoridad de ejecución de `AgentPipeline`.
- **INV-008** (Desktop Lifecycle Safety): El cliente SSE destruye sus conexiones en el evento `close()` o al cerrar la ventana del navegador Desktop.

## Failure Behavior
- Ante un error de red o socket cerrado en `EventSource`, la UI captura la excepción, cierra la conexión y permite que la respuesta final del `fetch('/api/agent/chat')` se renderice normalmente.

## Observability
- Registra en la consola del cliente la traza `[CodeAgent UI] Connected to SSE pipeline stream for task_id: XYZ` y `[CodeAgent UI] Closed SSE pipeline stream`.

## Testability
- Demostrable mediante la suite `tests/test_desktop_pipeline_visualization.py` que verifica la presencia del contrato de conexión SSE en la UI, el parseo de eventos reales, la correlación de `task_id`, el cleanup de recursos y la eliminación del progreso falso.

## Traceability
- Source File: `desktop_app.py`, `mis_agentes_inteligentes/localcode_server.py`, `mis_agentes_inteligentes/agent_pipeline.py`
- Test File: `tests/test_desktop_pipeline_visualization.py`
- Change Impact: `change/change-feature-desktop-pipeline-visualization.md`
- Evidence File: `audits/features/SPEC-012/runtime-evidence.md`
- Invariants: `INV-001`, `INV-008`
