# ADR-002: Proxy HTTP Multihilo Ligero Basado en http.server Nativo

- **Estado:** Aprobado
- **Fecha:** 2026-08-05
- **Autores:** Staff Architect & DevOps Team

## Contexto
Se requiere un servidor proxy local para atender peticiones REST de la interfaz web JetBrains Mono Theme (`localcode_claude_ui.html`) y reenviar llamadas al socket local de Ollama.

## Decisión
Se implementó `ThreadedTCPServer` y `LocalCodeProxyHandler` sobre `http.server.SimpleHTTPRequestHandler` de la librería estándar de Python.

## Consecuencias
- **Positivas:**
  - Cero dependencias externas adicionales instaladas en el sistema host.
  - Inicio instantáneo (<50ms) y huella de memoria mínima (<15MB RAM).
  - Soporte de concurrencia multihilo sin bloquear el loop de eventos.
- **Negativas:**
  - Para asincronía basada en WebSockets se requerirá una capa liviana sobre `asyncio`/`websockets` en futuras iteraciones.
