# SPEC-011 — Real-Time Pipeline State & Event Streaming (SSE)

## Intent
Exponer un canal de comunicación unidireccional HTTP Server-Sent Events (SSE) en `GET /api/pipeline/events` en el servidor backend `localcode_server.py` que transmita eventos estructurados en tiempo real sobre las transiciones de estado del `AgentPipeline` (`INIT`, `PLAN`, `EXPLORE`, `EXECUTE`, `VERIFY`, `DIAGNOSE`, `REPLAN`, `CRITIC`, `DONE`) y telemetría de tareas hacia la UI Desktop.

## Preconditions
- El servidor proxy backend `localcode_server.py` está iniciado y escuchando en su puerto TCP asignado.
- El módulo `EventBus` (`mis_agentes_inteligentes/runtime/event_bus.py`) está disponible.

## Postconditions
- La petición `GET /api/pipeline/events` establece una conexión HTTP persistente con Content-Type `text/event-stream`.
- El handler emite periódicamente heartbeats (`: ping\n\n`) y transmite eventos formateados como `data: {"event_id": 1, "task_id": "...", "event_type": "STATE_ENTERED", "payload": {...}, "timestamp": 1234.56}\n\n`.
- Si se especifica el parámetro de consulta `?task_id=XYZ`, el canal SSE filtra y entrega únicamente los eventos correspondientes a la tarea `XYZ`.
- Al desconectarse el cliente HTTP o iniciarse el shutdown del servidor, el suscriptor se elimina de forma hilo-segura sin fugas de recursos.

## Invariants
- **INV-001** (Pipeline Authority): La ruta es de solo lectura y no ejecuta instancias de agente fuera de `AgentPipeline`.
- **INV-008** (Desktop Lifecycle Safety): El streaming SSE maneja `BrokenPipeError` y sockets cerrados permitiendo que `stop_server()` y el shutdown del proceso padre se completen limpiamente.

## Failure Behavior
- Si la conexión del cliente se interrumpe abruptamente o el socket falla durante `flush()`, el handler captura la excepción, invoca `event_bus.unsubscribe()` y finaliza la respuesta de forma limpia.

## Observability
- Las suscripciones y desconexiones SSE se registran en los logs del servidor con las trazas `[LocalCode Server] SSE Client subscribed to /api/pipeline/events` y `[LocalCode Server] SSE Client disconnected`.

## Testability
- Demostrable mediante la suite `tests/test_sse_endpoint.py` que verifica suscripción, publicación, filtrado por `task_id`, desconexión de clientes, compatibilidad con shutdown y formato `text/event-stream`.

## Traceability
- Source File: `mis_agentes_inteligentes/localcode_server.py`
- Test File: `tests/test_sse_endpoint.py`
- Change Impact: `change/change-feature-pipeline-sse-streaming.md`
- Evidence File: `audits/features/SPEC-011/runtime-evidence.md`
- Invariants: `INV-001`, `INV-008`
