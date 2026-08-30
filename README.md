# 💻 CodeAgent (v6.2 SDD Certified & Canonical Architecture Migrated)

> **Un entorno local, robusto y extensible para construir, supervisar y gobernar agentes de código autónomos bajo certificación de invariantes SDD y arquitectura canónica unificada.**

CodeAgent es una plataforma de ingeniería de software asistida por IA local inspirada en **Google Antigravity** y **GitHub Copilot Workspace**. Está diseñada para ejecutar agentes autónomos sobre repositorios de código locales y remotos con soporte primario para modelos locales (**Ollama `qwen2.5-coder:14b`**, `llama3`, `deepseek`) y proveedores Cloud (OpenAI, Gemini, Anthropic, Groq).

---

## 🏗️ Arquitectura del Sistema (5 Capas Principales & Gobernanza SDD)

```
              ┌────────────────────────────────────────────────────────┐
              │                LOCALCODE DESKTOP & UI                  │
              │         Interfaz PyWebView + SSE Real-Time Visualizer  │
              └───────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │             LOCALCODE PROXY SERVER & REST API          │
              │         (SSE Streams, TaskRouter, HITL Approval)       │
              └───────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          PIPELINE MULTI-ROL CODEAGENT (AGENTPIPELINE)                       │
│                                                                                             │
│  🧠 PLANNER  ──►  🔍 EXPLORER  ──►  🔨 EXECUTOR  ──►  🧪 VERIFIER  ──►  👨‍⚖️ CRITIC           │
│  (Checklist)     (Graphify AST)   (Search/Replace)   (Sintaxis+Tests)  (Evaluación)       │
└─────────────────────────────────────────┬───────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            CAPAS ARQUITECTÓNICAS DEL SISTEMA                                │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎯 CORE: Engine autónomo smolagents con Re-planificación dinámica (planning_interval=2)    │
│ 🛡️ SDD GOVERNANCE: Invariantes Certificados (INV-001 a INV-008) y TaskContract Authority    │
│ 🧠 INTELLIGENCE: RAG sobre Subgrafos AST Graphify (SPEC-013) + Memoria de 3 Capas            │
│ ⚙️ EXECUTION: Sandboxing PermissionLevel + Terminal HITL + Git / GitHub REST                │
│ 🧩 EXTENSIBILITY: Subagentes dinámicos .md + Multi-Proveedor LiteLLM (Ollama/Cloud)        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 Auditorías y Migraciones Arquitectónicas (Phases A, B, C1 & C2)

CodeAgent cuenta con una suite completa de informes de auditoría, gobernanza y migraciones canónicas:

* **[ARCHITECTURE_WEIGHT_AUDIT.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/ARCHITECTURE_WEIGHT_AUDIT.md)**: Auditoría profunda de complejidad esencial vs. accidental, hotspots de dependencias y evaluación de módulos God Object.
* **[CANONICAL_ARCHITECTURE_ANALYSIS.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/CANONICAL_ARCHITECTURE_ANALYSIS.md)**: Matriz de canonización de responsabilidades (*ONE RESPONSIBILITY → ONE CANONICAL IMPLEMENTATION*), delimitación de componentes canónicos vs. legacy y roadmap de migración.
* **[REPOSITORY_HYGIENE_REPORT.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/REPOSITORY_HYGIENE_REPORT.md)**: Informe de desintoxicación y reducción de peso físico (**reducción del 98.7% de peso en disco**, pasando de 1.49 GB a 18.5 MB sin modificar comportamiento).

### 🚀 Informes de Migración Canónica (Phase C2)
1. **[MIGRATION_RAG.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/MIGRATION_RAG.md)**: Migración de `rag_tools.py` (ChromaDB) a `graph_context.py` (AST Subgraph RAG - SPEC-013).
2. **[MIGRATION_UI.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/MIGRATION_UI.md)**: Deprecación de `app.py` (Streamlit) en favor de `desktop_app.py` (PyWebView Desktop IDE).
3. **[MIGRATION_ORCHESTRATOR.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/MIGRATION_ORCHESTRATOR.md)**: Deprecación de `orquestador_agente.py` v1.0 en favor de `AgentStateMachineController` y `benchmark_suite.py`.
4. **[MIGRATION_SESSION.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/MIGRATION_SESSION.md)**: Transición de persistencia JSON suelta (`session_manager.py`) a `DatabaseManager` (SQLite WAL).
5. **[TASK_CONTRACT_COMPATIBILITY_MATRIX.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/TASK_CONTRACT_COMPATIBILITY_MATRIX.md)** & **[MIGRATION_CONTRACTS.md](file:///c:/Users/Jonatthan/Documents/Github/CodeAgent/MIGRATION_CONTRACTS.md)**: Unificación de `TaskContract` y `TaskType` bajo `sdd_contract/`.

---

## 🛡️ Sistema de Gobernanza SDD y Certificación de Invariantes

CodeAgent opera bajo un framework estricto de **Software-Driven Development (SDD)** respaldado por el script de verificación automatizada `python scripts/sdd_check.py` y una matriz formal de **8 Invariantes Certificados**:

| Invariante | Nombre | Garantía Principal |
| :--- | :--- | :--- |
| **INV-001** | **Pipeline Authority** | Toda ejecución de agente en producción pasa obligatoriamente por la máquina de estados `AgentPipeline`. |
| **INV-002** | **TaskContract Authority** | Los límites de gobernanza del `TaskContract` son inmutables y strictly aplicados en runtime. |
| **INV-003** | **Cross-Task Isolation** | Peticiones consecutivas reinician buffers de telemetría y llamadas a herramientas para evitar contaminación. |
| **INV-004** | **Intent Preservation** | Las restricciones negativas en el `TaskRouter` restringen únicamente herramientas prohibidas sin anular la intención general. |
| **INV-005** | **Failure Containment** | Las excepciones internas del pipeline devuelven respuestas de error seguras sin by-passear el contrato. |
| **INV-006** | **Tool Isolation** | Cuando `tools_allowed=False`, el agente no posee acceso a herramientas de modificación del workspace. |
| **INV-007** | **Conditional Verification** | Consultas conversacionales Fast-Path (CHAT) omiten la fase de verificación subprocess (`NOT_REQUIRED`). |
| **INV-008** | **Desktop Lifecycle Safety** | Instancias concurrentes mantienen PIDs/puertos independientes y socket cleanup mediante monitor nativo de procesos huérfanos. |

### CLI de Verificación SDD (`scripts/sdd_check.py`)
```bash
python scripts/sdd_check.py
```
Garantiza trazabilidad 100% entre especificaciones (`specs/features/` y `specs/invariants/`), código fuente, tests unitarios y evidencias de certificación.

---

## ✨ Características Principales

### 🧠 Local-Only & Ollama-First (SPEC-013)
- **Ejecución 100% Local:** Optimizado para funcionar sin conexiones externas obligatorias utilizando modelos Ollama de alta eficiencia (`qwen2.5-coder:14b`, `llama3`).
- **AST Subgraph Retrieval & RAG (`graph_context.py`):** Recuperación semántica contextual de subgrafos AST utilizando `graphify` para inyectar relaciones entre clases y funciones en el prompt del agente con mínimo consumo de tokens.

### 📡 Visualización de Pipeline en Tiempo Real y SSE (SPEC-011 / SPEC-012)
- **Server-Sent Events (SSE):** Transmisión de estados en tiempo real a través del servidor REST (`localcode_server.py`).
- **Desktop UI Interactiva:** Visualización paso a paso de cada fase del pipeline agéntico (`INIT`, `PLANNER`, `EXPLORER`, `EXECUTOR`, `VERIFIER`, `CRITIC`), junto con tarjetas de ejecución de terminal, botones para copiar comandos y autorización humana HITL (Human-In-The-Loop) para operaciones sensibles (`pip`, `git push`, etc.).

### 🔄 Multi-Proveedor Dinámico & smolagents
- **Orquestación con smolagents:** `CodeAgent` interactúa escribiendo código Python real para orquestar herramientas complejas, evitando fallos comunes de formateo JSON en modelos locales de 7B/14B.
- **Conector Universal LiteLLM:** Intercambio transparente entre Ollama local y proveedores Cloud (OpenAI, Anthropic, Gemini, Groq).

### 🤖 Subagentes Dinámicos y Mercado de Skills
- **Carga de Subagentes `.md`:** Ingesta automática de subagentes definidos en Markdown con YAML frontmatter en la carpeta `subagents/`.
- **Skills Integradas:** Soporte nativo para TDD, edición por Diffs, consultas a bases de datos SQLite en modo solo lectura, búsquedas en GitHub y automatización Git.

---

## 🚀 Instalación y Ejecución

### Opción 1: Lanzador Directo en Windows (Recomendado)
Haz doble clic en **`Lanzar_CodeAgent_Desktop.bat`** o **`Iniciar_OpenCode.bat`**.
El script se encargará automáticamente de:
1. Validar/crear el entorno virtual `.venv`.
2. Instalar dependencias requeridas.
3. Iniciar el servidor local y abrir la interfaz Desktop.

### Opción 2: Ejecución Manual

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el servidor backend LocalCode
python mis_agentes_inteligentes/localcode_server.py
```

---

## 🧪 Suite de Pruebas y Control de Calidad

CodeAgent cuenta con una suite automatizada de **más de 190 pruebas unitarias, de integración, de ciclo de vida Desktop y de conformidad SDD** con 100% de tasa de aprobación.

```bash
# Ejecutar todas las pruebas del sistema
python -m pytest

# Ejecutar verificación de gobernanza estructural SDD
python scripts/sdd_check.py
```

---

## 🛠️ Tecnologías Utilizadas

- **[smolagents](https://huggingface.co/docs/smolagents/):** Engine de agentes basados en código Python de HuggingFace.
- **[LiteLLM](https://litellm.vercel.app/):** Puente multi-proveedor para Ollama, OpenAI, Anthropic y Gemini.
- **[Graphify](https://github.com/):** Motor de análisis AST y generación de grafos de conocimiento.
- **PyWebView & HTTP Server:** Interfaz Desktop nativa y servidor REST multihilo con streaming SSE.
- **SQLite / DatabaseManager:** Persistencia local de sesiones, checkpoints y event sourcing.

---

## 🌐 Knowledge Graph (`graphify-out/`)

El directorio `graphify-out/graph.json` contiene el grafo del AST del repositorio con más de 1,800 nodos y 2,600 relaciones entre componentes, permitiendo a los agentes explorar la arquitectura sin realizar lecturas masivas e ineficientes de archivos.