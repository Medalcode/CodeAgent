# SPEC-013 — AST Subgraph Context Retrieval & Impact Engine (Graphify Subgraph RAG)

## Intent
Evolucionar el método `_stage_explorer` de `AgentPipeline` mediante un motor modular `GraphContextEngine` (`mis_agentes_inteligentes/graph_context.py`) que sustituya la inyección estática de hubs globales por la extracción determinista y acotada del subgrafo AST de 1 y 2 saltos (nodos objetivo, invocadores directos, funciones llamadas e importaciones) desde `graphify-out/graph.json` según el objetivo del usuario (`user_goal`).

## Preconditions
- El pipeline agéntico ejecuta una tarea con nivel de ejecución `LEVEL_2_ACTION`, `LEVEL_3_FEATURE` o `LEVEL_4_FULL`.
- El motor `GraphContextEngine` cuenta con acceso al archivo de grafo `graphify-out/graph.json` o a su caché en memoria.

## Postconditions
- `TargetExtractor` identifica los archivos y símbolos objetivo usando una cascada determinista de 5 niveles (Exact File -> Exact Symbol -> Normalized Symbol -> Path Suffix -> Fuzzy Match -> Workspace Fallback) sin invocar modelos LLM.
- `SubgraphRetriever` extrae los nodos adyacentes respetando la profundidad requerida (`depth=1` por defecto; `depth=2` únicamente para tareas `REFACTOR` y `DEBUG`).
- `ContextBudgeter` aplica poda determinista por orden de prioridad (P1 Target > P2 Callers/Callees > P3 Imports > P4 Container > P5 Siblings > P6 2-Hop) respetando el límite dominante `max_tokens=1500` (estimado vía `len(text) // 4`), `max_nodes=15` y `max_files=6`.
- `ContextFormatter` genera un bloque estructurado Markdown explicable con las rutas y anclas de línea de los símbolos incluidos.
- Ante ausencia, corrupción o error de `graph.json`, el sistema realiza un fallback observable a los archivos del workspace activos sin bloquear `AgentPipeline`.

## Invariants
- **INV-001** (Pipeline Authority): La recuperación de subgrafos es un componente determinista de contexto dentro de `AgentPipeline` y no altera la autoridad de ejecución ni ejecuta herramientas directamente.
- **INV-004** (Intent Preservation): El contexto enriquecido respeta la meta original del usuario sin relajar el contrato de la tarea.

## Failure Behavior
- Ante cualquier excepción de lectura de disco, parseo JSON, corruptud del grafo o símbolo no encontrado, `GraphContextEngine` emite un log estructurado `[Graphify RAG] status=fallback reason=...` y retorna una respuesta de fallback limpia sin interrumpir el pipeline.

## Observability
- Emisión de log estructurado de servidor: `[Graphify RAG] status=success target='<symbol>' nodes=N edges=M files=K tokens=T`.
- Log de fallback: `[Graphify RAG] status=fallback reason=<graph_file_missing|target_not_found|corrupt_graph>`.

## Testability
- Demostrable mediante la suite `tests/test_graphify_context_retrieval.py` que verifica la cascada determinista de extracción, el recorrido 1-hop/2-hop, la ordenación por prioridad, el presupuesto de 1500 tokens, la invalidación de caché por `mtime` y los fallbacks de seguridad.

## Traceability
- Source File: `mis_agentes_inteligentes/agent_pipeline.py`, `mis_agentes_inteligentes/graph_context.py`
- Test File: `tests/test_graphify_context_retrieval.py`
- Change Impact: `change/change-feature-ast-subgraph-retrieval.md`
- Evidence File: `audits/features/SPEC-013/runtime-evidence.md`
- Invariants: `INV-001`, `INV-004`
