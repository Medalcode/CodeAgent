# 💻 OpenCode Hub (CodeAgent)

Un Centro de Mando Avanzado para Agentes Inteligentes, construido con **Python, Streamlit y smolagents**. Este proyecto ha evolucionado de un simple script de consola a una plataforma completa estilo *OpenCode* o *OpenWebUI*, diseñada para interactuar con repositorios de código locales y remotos, gestionar tareas y proveer una arquitectura de orquestación de agentes robusta compatible con modelos locales (como Qwen y Llama) y en la nube.

## ✨ Características Principales (Fases 1 a 6)

- **🔄 Multi-Proveedor Dinámico:** Cambia al vuelo entre modelos locales (Ollama) y proveedores Cloud (OpenAI, Anthropic, Google Gemini, Groq) unificados a través de **LiteLLM**.
- **🧠 Orquestación con smolagents:** Utiliza el framework moderno `smolagents` de HuggingFace. A diferencia de agentes antiguos basados en JSON (ReAct), nuestro `CodeAgent` interactúa escribiendo código Python real para orquestar herramientas complejas, lo que lo hace infalible incluso con modelos pequeños de 7B/8B.
- **💾 Sesiones Persistentes:** Las conversaciones se guardan en el disco duro automáticamente. Puedes crear nuevas sesiones, renombrarlas, alternar entre ellas o borrarlas.
- **🌟 Enrutador Swarm Automático:** Selecciona el modo "Auto", y un clasificador ruteará tu petición al agente y conjunto de herramientas adecuados automáticamente.
- **🧬 Subagentes Dinámicos:** Soporta la importación dinámica de subagentes desde la comunidad. Simplemente arrastra un archivo `.md` (con YAML frontmatter) a la carpeta `subagents/` y la interfaz lo asimilará como un nuevo agente nativo.
- **⚡ Alto Rendimiento en UI:** Implementación de `@st.cache_data` para el parseo de sesiones JSON, logrando una interfaz gráfica responsiva que no bloquea el hilo principal al cargar el historial.
- **👀 Observabilidad Total:** Integración transparente sin silenciar flujos en el *backend*, lo que permite monitorear toda la Cadena de Pensamientos (CoT) y llamadas a herramientas del agente en la terminal de forma nativa.
- **🛠️ Configuración Desacoplada:** El LLM local (Ollama) ya no está fijo al localhost, permitiendo despliegues en clúster utilizando la variable de entorno `OLLAMA_API_BASE`.
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

1. Clona el repositorio e ingresa a la carpeta principal de la aplicación:
   ```bash
   cd mis_agentes_inteligentes
   ```
2. Activa el entorno virtual:
   ```bash
   source venv/bin/activate
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