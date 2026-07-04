# Graph Report - D:\Github\CodeAgent  (2026-07-12)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 87 nodes · 108 edges · 22 communities (6 shown, 16 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `main()` - 8 edges
2. `ejecutar_agentes()` - 6 edges
3. `init_sessions_dir()` - 5 edges
4. `load_subagents_from_disk()` - 4 edges
5. `crear_agente()` - 4 edges
6. `init_chroma()` - 4 edges
7. `get_model()` - 3 edges
8. `get_available_agents()` - 3 edges
9. `route_prompt()` - 3 edges
10. `get_herramientas()` - 3 edges

## Surprising Connections (you probably didn't know these)
- `ejecutar_agentes()` --calls--> `get_model()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py
- `ejecutar_agentes()` --calls--> `route_prompt()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py
- `ejecutar_agentes()` --calls--> `crear_agente()`  [INFERRED]
  mis_agentes_inteligentes/main.py → mis_agentes_inteligentes/agents.py

## Import Cycles
- None detected.

## Communities (22 total, 16 thin omitted)

### Community 0 - "agents.py"
Cohesion: 0.15
Nodes (15): crear_agente(), get_available_agents(), get_model(), load_subagents_from_disk(), Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter, Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido., Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos)., Enrutador automático por palabras clave. (+7 more)

### Community 1 - "orquestador_agente.py"
Cohesion: 0.24
Nodes (14): aplicar(), backup_archivos_trabajo(), diagnosticar(), gen_script(), generar_fix(), main(), probar(), Guarda backups de archivos que los benchmarks pueden modificar. (+6 more)

### Community 2 - "init_chroma"
Cohesion: 0.38
Nodes (6): indexar_directorio_local(), init_chroma(), preguntar_a_repositorio(), Inicializa la base de datos ChromaDB y el modelo de embeddings., Escanea todos los archivos de código en un directorio local, los parte en pedazo, Realiza una búsqueda semántica sobre los repositorios previamente indexados para

### Community 3 - "session_manager.py"
Cohesion: 0.52
Nodes (5): create_new_session(), init_sessions_dir(), list_sessions(), load_session(), save_session()

### Community 4 - "tools.py"
Cohesion: 0.40
Nodes (4): buscar_en_internet(), guardar_reporte(), Realiza una búsqueda en internet usando Google para obtener información actualiz, Archiva el análisis para memoria a largo plazo.          Args:         analis

## Knowledge Gaps
- **1 isolated node(s):** `start_hub.sh script`
  These have ≤1 connection - possible missing edges or undocumented components.
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Are the 3 inferred relationships involving `ejecutar_agentes()` (e.g. with `crear_agente()` and `get_model()`) actually correct?**
  _`ejecutar_agentes()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Instancia dinámicamente el modelo LiteLLMModel según el proveedor elegido.`, `Lee todos los archivos .md en la carpeta subagents/ y parsea su YAML frontmatter`, `Devuelve la lista completa de agentes disponibles (Fijos + Dinámicos).` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `agents.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._