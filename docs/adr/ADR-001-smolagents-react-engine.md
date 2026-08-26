# ADR-001: Selección de smolagents como Motor ReAct

- **Estado:** Aprobado
- **Fecha:** 2026-08-04
- **Autores:** Staff Architect & Engineering Team

## Contexto
El sistema requiere un motor agéntico liviano y flexible capaz de ejecutar bucles de razonamiento ReAct (Thought -> Action -> Observation) sobre modelos locales (vía Ollama) y modelos Cloud.

## Decisión
Se seleccionó la librería `smolagents` de HuggingFace sobre alternativas pesadas como LangChain/AutoGPT.

## Consecuencias
- **Positivas:**
  - Código fuente minimalista y fácilmente auditable.
  - Cero sobrecarga de abstracciones innecesarias.
  - Decoradores `@tool` simples y declarativos.
- **Negativas:**
  - Requiere manejo explícito de compatibilidad con `litellm` en versiones específicas de Pydantic v2.
