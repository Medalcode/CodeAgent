# Graph Report - CodeAgent  (2026-07-12)

## Corpus Check
- 19 files · ~9,981 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 116 nodes · 132 edges · 31 communities (12 shown, 19 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `760f9a01`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- agents.py
- orquestador_agente.py
- init_chroma
- session_manager.py
- tools.py
- start_hub.sh
- consultar_db
- consultar_github
- editar_archivo_search_replace
- ejecutar_comando_terminal
- escribir_archivo_local
- git_add
- git_commit
- git_diff
- git_push
- git_status
- leer_archivo_github
- leer_archivo_local
- leer_repositorio_github
- listar_directorio_local
- obtener_contexto_workspace
- main.py
- 💻 OpenCode Hub (CodeAgent)
- graphify.js
- graphify.md
- graphify.md

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `ejecutar_agentes()` - 7 edges
3. `init_sessions_dir()` - 5 edges
4. `💻 OpenCode Hub (CodeAgent)` - 5 edges
5. `load_subagents_from_disk()` - 4 edges
6. `crear_agente()` - 4 edges
7. `init_chroma()` - 4 edges
8. `load_session()` - 4 edges
9. `save_session()` - 4 edges
10. `rename_session()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `ejecutar_agentes()` --calls--> `get_model()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py
- `ejecutar_agentes()` --calls--> `route_prompt()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py
- `ejecutar_agentes()` --calls--> `crear_agente()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py

## Import Cycles
- None detected.

## Communities (31 total, 19 thin omitted)

### Community 0 - "agents.py"
Cohesion: 0.22
Nodes (10): crear_agente(), get_available_agents(), get_model(), load_subagents_from_disk(), Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter, Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)., Enrutador automático mejorado con scoring ponderado., Crea el CodeAgent de smolagents.     FIX: system_prompt ahora se pasa correctame (+2 more)

### Community 1 - "orquestador_agente.py"
Cohesion: 0.24
Nodes (14): aplicar(), backup_archivos_trabajo(), diagnosticar(), gen_script(), generar_fix(), main(), probar(), Guarda backups de archivos que los benchmarks pueden modificar. (+6 more)

### Community 2 - "init_chroma"
Cohesion: 0.38
Nodes (6): indexar_directorio_local(), init_chroma(), preguntar_a_repositorio(), Inicializa la base de datos ChromaDB y el modelo de embeddings., Escanea todos los archivos de código en un directorio local y los indexa en Chro, Realiza una búsqueda semántica sobre los archivos previamente indexados con inde

### Community 3 - "session_manager.py"
Cohesion: 0.29
Nodes (11): create_new_session(), delete_session(), export_session_to_markdown(), init_sessions_dir(), list_sessions(), load_session(), BUG 5 FIX: protegido contra session_id None o inválido., Renombra una sesión existente. (+3 more)

### Community 4 - "tools.py"
Cohesion: 0.40
Nodes (4): buscar_en_internet(), guardar_reporte(), Realiza una búsqueda en internet usando Google para obtener información actualiz, Archiva el análisis para memoria a largo plazo.          Args:         analis

### Community 22 - "main.py"
Cohesion: 0.21
Nodes (8): graphify, _construir_contexto_workspace(), ejecutar_agentes(), get_herramientas(), Pipeline de agentes con smolagents de HuggingFace. El LLM usa CodeAgent para gen, Convierte los nombres del UI en la lista de funciones @tool., Genera un bloque de contexto del workspace actual para inyectar en el system_pro, Pipeline principal usando smolagents.     FIX: el historial ya no se manda como

### Community 23 - "💻 OpenCode Hub (CodeAgent)"
Cohesion: 0.22
Nodes (8): Arquitectura, Benchmarks (3 niveles), ✨ Características Principales (Fases 1 a 6), 🚀 Instalación y Ejecución, 💻 OpenCode Hub (CodeAgent), 🧪 Orquestador Supervisor-Agente, 🛠️ Tecnologías Utilizadas, Uso

## Knowledge Gaps
- **10 isolated node(s):** `start_hub.sh script`, `graphify`, `Workflow: graphify`, `graphify`, `✨ Características Principales (Fases 1 a 6)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ejecutar_agentes()` connect `main.py` to `agents.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `crear_agente()` connect `agents.py` to `main.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `get_model()` connect `agents.py` to `main.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `ejecutar_agentes()` (e.g. with `crear_agente()` and `get_model()`) actually correct?**
  _`ejecutar_agentes()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `IMPORTANT: keep the reminder string free of backticks and $(...) constructs.`, `Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido.`, `Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._