# SPEC-009 — SDD Governance Telemetry Endpoint

## Intent
Exponer un endpoint HTTP dedicado `GET /api/health/sdd` en el servidor backend `localcode_server.py` que proporcione métricas de gobernanza SDD en tiempo real (versión certificada, commit certificado, estado del proceso padre y autoridad del pipeline) para monitores de salud y la UI Desktop.

## Preconditions
- El servidor proxy backend `localcode_server.py` está iniciado y escuchando en su puerto TCP asignado.

## Postconditions
- La petición `GET /api/health/sdd` retorna un código de respuesta `200 OK` con Content-Type `application/json`.
- El cuerpo JSON contiene exactamente los campos:
  - `status`: `"OK"`
  - `sdd_version`: `"5.0.0"`
  - `certified_commit`: `"b0157240d41d3a81c0b3c68b94d2e3a46c90f874"`
  - `invariants_certified_count`: `8`
  - `parent_pid`: Entero PID del proceso padre.
  - `parent_alive`: Booleano indicando el estado del proceso padre.
  - `pipeline_authority_active`: `True`

## Invariants
- **INV-001** (Pipeline Authority): La ruta es de solo lectura y no ejecuta instancias de agente fuera de `AgentPipeline`.
- **INV-008** (Desktop Lifecycle Safety): La ruta consulta `_is_parent_alive()` de forma hilo-segura sin alterar la lógica de shutdown o monitoreo.

## Failure Behavior
- Si ocurre una excepción interna al consultar el estado del proceso padre, el endpoint retorna HTTP `200 OK` con `status: "DEGRADED"` y `parent_alive: False` en lugar de causar un crash 500 del servidor.

## Observability
- Las peticiones a `/api/health/sdd` se registran en los logs del servidor con la traza `[LocalCode Server] GET /api/health/sdd`.

## Testability
- Demostrable mediante test de integración usando `unittest.TestCase` y `urllib.request` / WSGI test client invocando el handler HTTP.

## Traceability
- Source File: `mis_agentes_inteligentes/localcode_server.py`
- Test File: `tests/test_sdd_health_endpoint.py`
- Change Impact: `change/change-feature-sdd-telemetry.md`
- Evidence File: `audits/features/SPEC-009/runtime-evidence.md`
- Invariants: `INV-001`, `INV-008`
