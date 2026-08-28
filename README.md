# 💻 CodeAgent (v6.6 Enterprise)

> **Un entorno local y extensible para construir y supervisar agentes de código autónomos.**

CodeAgent es una plataforma de ingeniería de software asistida por IA local inspirada en **Google Antigravity** y **GitHub Copilot Workspace**. Está diseñada para ejecutar agentes autónomos sobre repositorios de código locales y remotos con soporte para modelos locales (**Ollama qwen2.5-coder:14b**) y modelos en la nube (OpenAI, Gemini, Anthropic, Groq).

---

## 🏗️ Arquitectura del Sistema (5 Capas Principales)

```
              ┌────────────────────────────────────────────────────────┐
              │                     LOCALCODE IDE                      │
              │         Interfaz Web 3-Paneles estilo Antigravity     │
              └───────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
              ┌────────────────────────────────────────────────────────┐
              │             LOCALCODE PROXY SERVER & REST API          │
              └───────────────────────────┬────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                             PIPELINE MULTI-ROL CODEAGENT V3.0                               │
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
│ 🛡️ DIFFERENTIATOR: Supervisor Agent con Benchmarks y diagnóstico de fallos                   │
│ 🧠 INTELLIGENCE: Grafo AST Graphify + Memoria de 3 Capas (Factual, Decisión, Trabajo)       │
│ ⚙️ EXECUTION: Sandboxing PermissionLevel + Terminal Shell + Git / GitHub REST             │
│ 🧩 EXTENSIBILITY: Subagentes dinámicos .md + Multi-Proveedor LiteLLM (Ollama/Cloud)        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## ✨ Características Principales (v3.0 Enterprise)

- **🔄 Multi-Proveedor Dinámico:** Cambia al vuelo entre modelos locales (Ollama) y proveedores Cloud (OpenAI, Anthropic, Google Gemini, Groq) unificados a través de **LiteLLM**.
- **🧠 Orquestación con smolagents:** Utiliza el framework moderno `smolagents` de HuggingFace. A diferencia de agentes antiguos basados en JSON (ReAct), nuestro `CodeAgent` interactúa escribiendo código Python real para orquestar herramientas complejas, lo que lo hace infalible incluso con modelos pequeños de 7B/8B.
- **💾 Sesiones Persistentes:** Las conversaciones se guardan en el disco duro automáticamente. Puedes crear nuevas sesiones, renombrarlas, alternar entre ellas o borrarlas.
- **🌟 Enrutador Swarm Automático:** Selecciona el modo "Auto", y un clasificador ruteará tu petición al agente y conjunto de herramientas adecuados automáticamente.
- **🧬 Subagentes Dinámicos:** Soporta la importación dinámica de subagentes desde la comunidad. Simplemente arrastra un archivo `.md` (con YAML frontmatter) a la carpeta `subagents/` y la interfaz lo asimilará como un nuevo agente nativo.
- **⚡ Alto Rendimiento en UI:** Implementación de `@st.cache_data` para el parseo de sesiones JSON, logrando una interfaz gráfica responsiva que no bloquea el hilo principal al cargar el historial.
- **👀 Observabilidad Total:** Integración transparente sin silenciar flujos en el *backend*, lo que permite monitorear toda la Cadena de Pensamientos (CoT) y llamadas a herramientas del agente en la terminal de forma nativa.
- **🌐 Integración con Graphify:** Conocimiento estructural del código mediante un knowledge graph de AST. Compatible con asistentes como Claude, Cursor y OpenCode para exploraciones más inteligentes.
### 🚀 Proactividad Agéntica, Observabilidad y Calidad de Código (v2.5.0)
- **Streaming Paso a Paso (`ActionStep`):** Ejecución reactiva con `stream=True` notificando pensamientos, llamadas a herramientas y observaciones en tiempo real.
- **Auto-Detección de Raíz de Proyecto (`_detectar_raiz_proyecto`):** Resolución automática de la raíz real del repositorio (`CodeAgent/`) buscando `.git`, `AGENTS.md` o `graphify-out/`.
- **Inyección Automática de Reglas (`AGENTS.md` y `.agents/rules`):** Inclusión transparente de guías de arquitectura y señales explícitas sobre el grafo `graphify` para el agente.
- **Expansión de Contexto Ollama (`num_ctx=8192+`):** Gestión optimizada de memoria VRAM reduciendo la pérdida de atención en modelos de 7B/14B.
- **Sandboxing por Allowlist (`STRICT_SANDBOX`):** Restricción de ejecutables permitidos en la terminal (`ALLOWED_COMMANDS`).
- **Verificación Sintáctica AST Post-Edición:** Análisis inmediato con `ast.parse` tras escrituras en archivos Python.
- **Suite de Pruebas Extendido (57/57 pasadas):** Creación de `tests/test_e2e_suite.py` y cobertura de 5 niveles (Unit, Integration, E2E, Smoke, Regression).

### 🛡️ Últimas Mejoras de Fiabilidad, Calidad Técnica y QA (v2.3.0)
- **Refactorización de Rutas Absolutas:** Anclamiento de `SESSIONS_DIR` en `session_manager.py` y `DB_DIR` en `rag_tools.py` al directorio raíz del módulo (`BASE_DIR`).
- **Optimización por Caché (`mtime`):** Implementación de caché basada en modificación de archivos para la lectura de subagentes en disco (`load_subagents_from_disk()`).
- **Manejo Seguro de Recursos (Context Manager):** Refactorización de `consultar_db` usando `with sqlite3.connect(...)` para asegurar el cierre de conexiones SQLite.
- **Limpieza de Importaciones y Code Smells:** Promoción de importaciones internas (`difflib`, `shlex`, `traceback`, `logging`) al encabezado principal de los archivos y eliminación de silenciamientos de excepciones en favor de `logging.warning`.
- **Extensión de Pruebas Automatizadas (41/41 tests pasados):** Adición de `tests/test_regression.py` y `tests/test_integration_pipeline.py` alcanzando 41 pruebas unitarias, de integración y regresión con 100% de éxito.

### 🛡️ Últimas Mejoras de Fiabilidad, Seguridad y UX (v2.2.1)
- **Eliminación de Riesgo de Shell Injection (`ejecutar_comando_terminal`):** Tokenización segura con `shlex.split` y `shell=False` para comandos directos, junto con sanitización de tuberías y operadores de consola.
- **Corrección de Lanzador en Windows (`Iniciar_OpenCode.bat`):** Reescritura a sintaxis batch 100% lineal sin bloques parentéticos ambiguos, selección de Python 3.10/3.11 estable e instalación con `--prefer-binary`.
- **Preservación de Sintaxis Markdown:** Compresión inteligente de respuestas largas en el historial (`_truncar_markdown`) cerrando automáticamente bloques de código ```` ``` ```` incompletos.
- **Enrutamiento Swarm Ampliado:** Inclusión de subagentes dinámicos (`subagents/*.md`) en la puntuación ponderada de `route_prompt`.
- **Suite de Pruebas Automatizada (34/34 tests pasados):** Extensión de la suite `unittest` alcanzando 34 pruebas unitarias, de integración y smoke tests con 100% de efectividad.
- **Pipeline de CI/CD (GitHub Actions):** Integración de workflow automatizado `.github/workflows/ci.yml` para linting (`ruff`), testing y validación de contenedores Docker.

### 🛡️ Últimas Mejoras de Fiabilidad, Seguridad y UX (v2.2)
- **Seguridad SQL Estricta (`consultar_db`):** Validación en capa Python para restringir ejecuciones exclusivamente a consultas `SELECT`, `PRAGMA` y `EXPLAIN`.
- **Eliminación de Duplicación (DRY Context & GitHub API):** Reutilización de `obtener_contexto_workspace` en `main.py` y creación de `_make_github_request` para llamadas HTTP autenticadas centralizadas.
- **Edición por Diff Segura (`editar_archivo_search_replace`):** Verificación de coincidencias múltiples para evitar reemplazos ambiguos accidentales.
- **Resiliencia en Carga de Sesiones:** Reemplazo de silencio de excepciones por logging de diagnósticos en `session_manager.py`.
- **Suite de Pruebas Extendido:** Adición de `test_session_manager.py` y ampliación de `test_tools.py` y `test_agents.py` cubriendo CRUD de sesiones, seguridad y utilidades.
- **Estructuración como Paquete Python:** Adición de `__init__.py` en `mis_agentes_inteligentes/`.

### 🛡️ Últimas Mejoras de Fiabilidad y UX (v2.1)
- **Refactorización de Rutas:** Se resolvieron dependencias de `cwd` problemáticas para la base de datos `MisEventos.db` y el archivo de log.
- **Principio DRY en GitHub API:** Consolidación de la lógica repetitiva de obtención del nombre real de repositorios.
- **Optimización en `get_model`:** Simplificación de validaciones redundantes de API Keys.
- **Suite de Pruebas Unitarias (TDD):** Nuevas pruebas automatizadas con `unittest` para los módulos clave (`tools.py` y `agents.py`).

### 🛡️ Últimas Mejoras de Fiabilidad y UX (v2.0)
- **Roles Estrictos:** Inyección correcta de `system_prompt` en el `CodeAgent` para asegurar que el agente asuma el rol seleccionado.
- **Contexto de Workspace:** El agente ahora es consciente del directorio de trabajo actual y su estructura antes de responder.
- **Enrutador Inteligente:** Nuevo enrutador automático con *scoring ponderado* (evalúa palabras clave y su peso) para elegir el mejor agente según el prompt.
- **Gestión de Sesiones Robusta:** Caché invalidada en tiempo real para mantener la UI sincronizada, historial separado del system prompt para evitar alucinaciones en modelos de 7B, y capacidad para exportar sesiones a Markdown.
- **Soporte `.env`:** Carga automática de variables de entorno para mayor seguridad de las API Keys (con plantilla `.env.example`).
- **Nuevos Comandos UI:** Slash commands integrados (`/help`, `/status`, `/clear`, `/export`) directamente en el chat.
- **Terminal Segura:** Directorio de trabajo (`cwd`) garantizado por comando, timeout ampliado a 60s, y blacklist fortalecida.

- **🤖 Agentes (Personas) Preconfigurados:** 
  - *Ingeniero de Software Local / Agente de Edición de Código:* Puede listar directorios, leer archivos, modificar código de forma segura y ejecutar comandos en tu PC.
  - *Analista de Código:* Lee repositorios de GitHub reales, descarga `README.md` y estructura de archivos para análisis. Detecta inteligentemente el nombre real del repositorio sin que el LLM tenga que adivinarlo.
  - *Asistente de Productividad:* Se conecta a bases de datos SQLite locales en **modo de solo lectura estricto** para gestionar datos y crear reportes sin riesgo de inyecciones destructivas.
- **🤖 Orquestador Supervisor-Agente:** Ciclo automático de mejora de prompts. Ejecuta 8 benchmarks en 3 niveles (baja, media, alta) sobre el agente local. Con API key (OpenAI/OpenRouter), un Supervisor GPT-4o-mini diagnostica fallos de ejecución y genera correcciones al system_prompt. Incluye backup/restore de archivos de trabajo entre iteraciones y validación de sintaxis antes de aplicar cambios.
- **🔌 Mercado de Skills (Tools):**
  - **Archivos Locales:** Lectura con truncamiento inteligente para no saturar la memoria (Context Window) del LLM, y un motor de edición basado en Diffs para modificaciones de código.
  - **Memoria RAG:** Indexación local de código fuente utilizando bases de datos vectoriales (Chroma) para búsquedas semánticas directas.
  - **Terminal Integrada:** Ejecución de comandos Bash con una capa de seguridad (Blacklist) que bloquea operaciones destructivas del sistema operativo. Manejo resiliente de strings (como rutas con espacios en `git add`) usando `shlex`.
  - **Búsqueda Web:** Permite buscar documentación o errores en internet (Google Search).
  - **Integración Git:** Status, Add, Commit, Diff y Push automatizados.

## 🧪 Orquestador Supervisor-Agente

El archivo `orquestador_agente.py` implementa un ciclo de evaluación y mejora para agentes locales.

### Benchmarks (3 niveles)

| Nivel | Descripción |
|-------|-------------|
| **baja** | Leer/escribir archivos, edición search/replace |
| **media** | Refactorizar funciones, escribir tests, depurar código |
| **alta** | Features multi-archivo, análisis completo de codebase, automatización |

### Uso

```bash
# Solo prueba (sin diagnóstico):
python3 orquestador_agente.py

# Con Supervisor activo (OpenAI/OpenRouter):
OPENAI_API_KEY="sk-..." python3 orquestador_agente.py

# Configurar proveedor y modelo:
API_BASE="https://openrouter.ai/api/v1" \
SUPERVISOR_MODEL="openai/gpt-4o-mini" \
MAX_ITERACIONES=3 \
python3 orquestador_agente.py
```

### Arquitectura

1. `probar()` → Ejecuta el agente en un subproceso limpio, extrae traza JSON con delimitadores únicos
2. `diagnosticar()` → GPT-4o-mini analiza herramientas usadas, pasos completados y calidad del resultado
3. `generar_fix()` → Genera search/replace sobre el system_prompt de `agents.py`
4. `aplicar()` → Valida sintaxis antes de escribir, con backup para rollback automático
5. `restaurar_archivos_trabajo()` → Restaura tools.py/main.py/session_manager.py entre benchmarks

## 🚀 Instalación y Ejecución

### Opción 1: Arranque Rápido (Recomendado para Windows)
Simplemente haz **doble clic en el archivo `Iniciar_OpenCode.bat`**. 
Este script se encargará automáticamente de:
- Detectar o crear el entorno virtual.
- Instalar todas las dependencias necesarias.
- Iniciar la aplicación y abrirla en tu navegador.

### Opción 2: Ejecución Manual
1. Clona el repositorio e ingresa a la carpeta principal de la aplicación:
   ```bash
   cd mis_agentes_inteligentes
   ```
2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate     # En Windows
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la interfaz gráfica con Streamlit:
   ```bash
   streamlit run app.py
   ```

## 🛠️ Tecnologías Utilizadas

- **[Streamlit](https://streamlit.io/):** Interfaz de usuario reactiva y gestión de estados.
- **[smolagents](https://huggingface.co/docs/smolagents/):** Orquestador nativo en Python para LLMs, altamente eficiente con modelos locales.
- **[LiteLLM](https://litellm.vercel.app/):** Traductor universal que permite conectar OpenAI, Anthropic, Gemini, Groq y Ollama usando el mismo código.
- **ChromaDB / HuggingFaceEmbeddings:** Para Memoria Semántica RAG.
- **APIs de GitHub:** Para extracción y análisis de repositorios en modalidad *Deep Dive*.

## Knowledge Graph

`graphify-out/graph.json` contiene **103 nodos y 102 aristas** del AST del proyecto, permitiendo a agentes AI comprender la arquitectura sin escanear archivos.

## Skills

- **tdd** (skills.sh) — patrones de testing para mantener y expandir la cobertura