# INV-006 — Tool Isolation

## Status
CERTIFIED

## Statement
Cuando `contract.tools_allowed == False` (para tareas `CHAT`), ninguna herramienta de workspace (filesystem, terminal integrada, Git, GitHub, Memoria RAG) debe estar presente en la lista de herramientas entregada a la instancia efectiva del agente smolagents.

## Scope
- `mis_agentes_inteligentes/main.py` (`get_herramientas`)
- `mis_agentes_inteligentes/agents.py` (`crear_agente`)

## Preconditions
- El contrato evaluado para el prompt determina `contract.tools_allowed == False`.

## Required Behavior
- `main.py` establece `herramientas = []` antes de invocar `crear_agente()`.
- La instancia `CodeAgent` de smolagents posee exactamente 0 herramientas externas de workspace (`len(workspace_tools_in_agent) == 0`).

## Forbidden Behavior
- Pasar la lista predeterminada `DEFAULT_AGENT_TOOLS` o agregar herramientas de disco/terminal a la instancia smolagents cuando el contrato prohíbe herramientas.

## Evidence
- Static: `herramientas = get_herramientas(selected_tools) if (not contract or contract.tools_allowed) else []` en `main.py#L129`.
- Tests: `tests/test_sdd_conformance.py`.
- Runtime: Inspección directa de `agente.tools` en runtime real de tareas CHAT.
- OS/Filesystem: N/A

## Related Tests
- `tests/test_sdd_conformance.py::TestSDDConformance::test_chat_contract_fast_path`

## Related Modules
- `mis_agentes_inteligentes/main.py`
- `mis_agentes_inteligentes/agents.py`

## Audit
- Audit Candidate: v5.0.0 Release Candidate Audit
- Audit Date: 2026-08-29
- Verdict: PASS

## Certification
- Certified Release: v5.0.0
- Commit SHA: `b0157240d41d3a81c0b3c68b94d2e3a46c90f874`
