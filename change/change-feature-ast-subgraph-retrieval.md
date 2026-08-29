# Change Impact Analysis — AST Subgraph Context Retrieval & Impact Engine (SPEC-013)

## Feature Title
AST Subgraph Context Retrieval & Impact Engine (`SPEC-013`)

## Description
Evolves the `_stage_explorer` phase in `mis_agentes_inteligentes/agent_pipeline.py` from an un-targeted global hub string generator into a Graphify-guided AST Context Retrieval System. Introduces a modular architecture (`GraphContextEngine` comprising `GraphCacheManager`, `TargetExtractor`, `SubgraphRetriever`, `ContextBudgeter`, and `ContextFormatter`) to extract target AST nodes and 1-hop / 2-hop neighborhoods (`callers`, `callees`, `imports`, `parent/container`) using a 5-level deterministic cascade (Exact File -> Exact Symbol -> Normalized Symbol -> Path Suffix -> Fuzzy Match).

## Target Modular Architecture
- `mis_agentes_inteligentes/graph_context.py` (New modular engine container: `GraphContextEngine`)
  - `GraphCacheManager`: Thread-safe in-memory graph cache indexed by file `mtime`.
  - `TargetExtractor`: Deterministic 5-level target symbol/file identification.
  - `SubgraphRetriever`: Adjacency traversal filtering `callers`, `callees`, `imports`, `contains`.
  - `ContextBudgeter`: Deterministic node priority queue pruning (P1 Target > P2 Callers/Callees > P3 Imports > P4 Container > P5 Siblings > P6 2-Hop) adhering to `max_tokens=1500`, `max_nodes=15`, `max_files=6`.
  - `ContextFormatter`: Structured Markdown context block formatter.
- `mis_agentes_inteligentes/agent_pipeline.py` (Consumer of `GraphContextEngine` in `_stage_explorer(user_goal)`)

## Modified Production Files (Planned for Implementation Phase)
- `mis_agentes_inteligentes/graph_context.py` [NEW]
- `mis_agentes_inteligentes/agent_pipeline.py` [MODIFY - Consumer]

## Current Production Files Modified in this Phase
- **ZERO** (Strict pre-implementation SDD phase)

## Potentially Affected Invariants
- [x] **INV-001** (Pipeline Authority)
  - *Justification*: `GraphContextEngine` operates strictly as a read-only deterministic context retrieval step within `_stage_explorer()`. It does not execute agents or alter pipeline state transitions.
- [x] **INV-004** (Intent Preservation)
  - *Justification*: Targeted AST subgraph retrieval enriches prompt context with actual caller/callee symbols specified in the user goal without relaxing `TaskContract` governance bounds.

## Invariants NOT Affected
- **INV-002** (TaskContract Authority): Contract rules and tool permissions remain immutable.
- **INV-003** (Cross-Task Isolation): Subgraph queries do not retain cross-task execution buffers.
- **INV-005** (Failure Containment): Graph errors trigger a graceful fallback without crashing pipeline.
- **INV-006** (Tool Isolation): Tool access policies are untouched.
- **INV-007** (Conditional Verification): Verification passes execute as defined.
- **INV-008** (Desktop Lifecycle Safety): In-memory cache uses file `mtime` without background threads or persistent sockets.

## Required Test Suites
- [x] `tests/test_graphify_context_retrieval.py` (New unit/integration suite for SPEC-013)
- [x] Full Test Suite (`python -m unittest discover -s tests`)

## Required Runtime Evidence
- Standalone feature evidence file `audits/features/SPEC-013/runtime-evidence.md` (To be generated post-implementation).
