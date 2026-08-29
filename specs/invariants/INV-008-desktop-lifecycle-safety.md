# INV-008 — Desktop Lifecycle Safety

## Status
CERTIFIED

## Statement
Instancias concurrentes de la aplicación Desktop deben mantener aislamiento total de procesos, puertos y recursos. El cierre de backend (`stop_server()`) debe ser estrictamente idempotente y la muerte abrupta del proceso padre no debe dejar procesos o puertos backend huérfanos.

## Scope
- `desktop_app.py`
- `mis_agentes_inteligentes/localcode_server.py`

## Preconditions
- Múltiples instancias Desktop se ejecutan en la misma máquina o la app Desktop finaliza de forma abrupta.

## Required Behavior
- Cada proceso Desktop asigna un puerto TCP dinámico propio (`find_free_port()`) y genera un `instance_id` UUID único.
- `is_backend_compatible()` valida `parent_pid`, `parent_creation_time` e `instance_id` para impedir que una instancia interfiera con el backend de otra.
- `stop_server()` utiliza `_STOPPING_LOCK` y es 100% idempotente ante invocaciones repetidas o multi-hilo.
- `localcode_server.py` ejecuta `_start_parent_monitor()` y auto-termina en $< 4$ segundos si el proceso padre muere de forma abrupta (`kill -9` / `TerminateProcess`).

## Forbidden Behavior
- Reutilizar destructivamente un backend perteneciente a otra instancia Desktop.
- Cerrar el backend de otra instancia durante el shutdown.
- Dejar procesos Python huérfanos escuchando en puertos TCP tras la muerte del proceso padre.

## Evidence
- Static: `is_backend_compatible()`, `_STOPPING_LOCK`, `_is_parent_alive()`.
- Tests: `tests/test_server_lifecycle.py`.
- Runtime: Auditoría adversarial de 6 escenarios de concurrencia y muerte abrupta en Windows.
- OS/Filesystem: Verificación de sockets TCP en OS y tabla de procesos Windows.

## Related Tests
- `tests/test_server_lifecycle.py::TestServerLifecycle::test_A_two_desktop_instances_do_not_share_backend`
- `tests/test_server_lifecycle.py::TestServerLifecycle::test_B_backend_ownership_requires_parent_identity`
- `tests/test_server_lifecycle.py::TestServerLifecycle::test_C_stop_server_is_idempotent`
- `tests/test_server_lifecycle.py::TestServerLifecycle::test_E_parent_pid_reuse_is_detected`

## Related Modules
- `desktop_app.py`
- `mis_agentes_inteligentes/localcode_server.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
