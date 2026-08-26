# ADR-003: Compatibilidad y Polyfill de Pydantic v2 con LiteLLM

- **Estado:** Aprobado
- **Fecha:** 2026-08-26
- **Autores:** Senior Staff Engineer & Core Team

## Contexto
En entornos Python 3.10 la importación de `litellm` desde `smolagents` generaba `PydanticUserError` por referencias hacia adelante no resueltas en `ChatCompletionReasoningSummaryTextBlock` al instanciar `Message`.

## Decisión
Inyectar el polyfill `litellm.types.utils.ChatCompletionReasoningSummaryTextBlock = Any` y ejecutar `.model_rebuild()` sobre `Message`, `Choices` y `ModelResponse` en `agents.py` antes del inicio de la ejecución del agente.

## Consecuencias
- **Positivas:**
  - Resuelve de forma determinista el fallo de instanciación sin requerir parches upstream.
  - Mantiene compatibilidad transparente tanto en entornos legacy Python 3.10 como en entornos unificados Python 3.11+.
