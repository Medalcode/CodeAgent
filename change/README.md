# SDD Change Impact Analysis Framework

This directory contains guidelines and templates for assessing the impact of proposed codebase changes on certified SDD Invariants prior to implementation.

## Change Impact Analysis Workflow

```text
PROPOSED CHANGE
      ↓
IMPACT ANALYSIS (Check specs/traceability.md)
      ↓
IDENTIFY AFFECTED INVARIANTS (INV-001 .. INV-008)
      ↓
DETERMINE REGRESSION TEST SUITE
      ↓
IMPLEMENT CHANGE
      ↓
RUN FAST SDD CHECK (scripts/sdd_check.py)
      ↓
FULL RE-CERTIFICATION (If required)
```

## When to Execute Impact Analysis
Any pull request or commit that modifies:
- `mis_agentes_inteligentes/main.py`
- `mis_agentes_inteligentes/agent_pipeline.py`
- `desktop_app.py`
- `mis_agentes_inteligentes/localcode_server.py`
- `sdd_contract/`
- `mis_agentes_inteligentes/tools.py`
