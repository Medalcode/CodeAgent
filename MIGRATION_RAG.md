# Migration Report: RAG Legacy Migration (`rag_tools.py` → `graph_context.py`)

## Before
- **Componente Anterior**: `mis_agentes_inteligentes/rag_tools.py` (ChromaDB + BM25 text chunk RAG).
- **Problema**: `rag_tools.py` requería la inicialización de bases de datos vectoriales pesadas (`chromadb`), dividía el código en fragmentos sin jerarquía sintáctica y consumía tokens excesivos sin conocimiento de la topología AST.

## Canonical Component
- **Componente Canónico**: `mis_agentes_inteligentes/graph_context.py` (Cumple `SPEC-013` AST Subgraph RAG).
- **Ventaja**: Extrae subgrafos acotados (1-hop / 2-hop) basados en el grafo de conocimiento Graphify (`graphify-out/graph.json`) determinista y sin costo de LLM para la extracción.

## Consumers Migrated
1. `mis_agentes_inteligentes/main.py`: Se removió `import rag_tools` y la opción `"Memoria RAG"` del mapa `TOOLS_MAP`.
2. `tests/test_main.py`: Se actualizó `test_get_herramientas_memoria_rag` para verificar que la opción RAG legacy ya no expone las herramientas de ChromaDB.

## Compatibility
- `mis_agentes_inteligentes/rag_tools.py` se conserva en el repositorio durante la Fase C2 con una advertencia formal de deprecación (`DeprecationWarning`) para evitar romper proyectos externos que aún pudieran importarlo.

## Tests
- `tests/test_main.py`: PASS.
- `tests/test_rag_tools.py`: PASS (verifica que la funcionalidad legacy sigue respondiendo si se importa directamente).

## SDD Validation
- `python scripts/sdd_check.py`: **RESULT: PASS**.
- Invariantes y especificaciones (`SPEC-013` AST Subgraph Retrieval): **100% TRACEABLE**.

## Deprecation Status
- **Estado**: **DEPRECATED**.
- `rag_tools.py` está listo para ser removido físicamente en la Fase C3/D.

## Rollback
- Restaurar `mis_agentes_inteligentes/main.py` y `tests/test_main.py` mediante `git checkout`.
