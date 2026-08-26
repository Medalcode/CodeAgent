import logging
import os

try:
    from smolagents import tool
except ImportError:
    def tool(func=None):
        if func is None:
            return lambda f: f
        return func

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    CHROMA_AVAILABLE = True
except ImportError:
    Chroma = None
    CHROMA_AVAILABLE = False

# Configuración del motor de Embeddings ligero (Corre en CPU y ocupa poca RAM)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")


def init_chroma():
    """Inicializa la base de datos ChromaDB y el modelo de embeddings."""
    if not CHROMA_AVAILABLE:
        return None, None
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings, collection_name="local_repos")
    return db, embeddings


_RAG_CACHE = {}


# BUG 6 FIX: @tool sin argumento posicional — smolagents >= 1.x no acepta @tool("nombre")
@tool
def indexar_directorio_local(ruta: str) -> str:
    """Escanea todos los archivos de código en un directorio local y los indexa en ChromaDB para búsquedas semánticas futuras.

    Args:
        ruta: Ruta al directorio a indexar.
    """
    global _RAG_CACHE
    _RAG_CACHE.clear()

    if not CHROMA_AVAILABLE:
        return "Error: Las librerías RAG no están instaladas (chromadb, langchain-community, sentence-transformers)."

    if not os.path.isdir(ruta):
        return f"Error: La ruta '{ruta}' no es un directorio válido."

    db, _ = init_chroma()
    if db is None:
        return "Error: No se pudo inicializar ChromaDB."

    archivos_procesados = 0
    textos = []
    metadatos = []

    # Extensiones de código válidas
    ext_validas = {'.py', '.js', '.ts', '.md', '.txt', '.html', '.css', '.json'}

    for root, dirs, files in os.walk(ruta):
        # Ignorar carpetas problemáticas
        dirs[:] = [d for d in dirs if d not in [
            'node_modules', 'venv', '.git', '__pycache__', '.venv', 'chroma_db', 'graphify-out'
        ]]

        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in ext_validas:
                ruta_completa = os.path.join(root, file)
                try:
                    with open(ruta_completa, encoding='utf-8') as f:
                        contenido = f.read()
                        textos.append(contenido)
                        metadatos.append({"source": ruta_completa})
                        archivos_procesados += 1
                except Exception as e:
                    logging.debug(f"Omite lectura del archivo {ruta_completa}: {e}")

    if not textos:
        return f"No se encontraron archivos de texto/código válidos en {ruta}."

    # Dividir los textos en fragmentos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(textos, metadatas=metadatos)

    # Añadir a ChromaDB
    db.add_documents(docs)

    return f"¡Éxito! Se indexaron {archivos_procesados} archivos ({len(docs)} fragmentos) de '{ruta}' en la memoria RAG."


def _bm25_score(query: str, text: str) -> float:
    """Calcula una puntuación BM25 léxica simplificada basada en frecuencia de términos de código."""
    terms = [t for t in query.lower().split() if len(t) > 2]
    if not terms:
        return 0.0
    text_lower = text.lower()
    score = 0.0
    for term in terms:
        count = text_lower.count(term)
        if count > 0:
            score += 1.0 + (count / (count + 1.5))
    return score


# BUG 6 FIX: ídem
@tool
def preguntar_a_repositorio(pregunta: str) -> str:
    """Realiza una búsqueda semántica sobre los archivos previamente indexados con indexar_directorio_local.

    Args:
        pregunta: Pregunta o búsqueda a realizar sobre el código indexado.
    """
    query_key = pregunta.strip().lower()
    if query_key in _RAG_CACHE:
        return _RAG_CACHE[query_key]

    if not CHROMA_AVAILABLE:
        return "Error: Las librerías RAG no están instaladas."

    db, _ = init_chroma()
    if db is None:
        return "Error: No se pudo inicializar ChromaDB."

    try:
        # Recuperar candidatos vectoriales y aplicar re-ranking híbrido léxico BM25
        candidatos = db.similarity_search(pregunta, k=8)

        if not candidatos:
            res_str = "No se encontró información relevante en la base de datos indexada."
            _RAG_CACHE[query_key] = res_str
            return res_str

        # Re-ordenar combinando similitud semántica con BM25 léxico
        candidatos.sort(key=lambda doc: _bm25_score(pregunta, doc.page_content), reverse=True)
        resultados = candidatos[:4]

        respuesta = "Fragmentos de código relevantes (Búsqueda Híbrida BM25 + Vectorial):\n\n"
        for i, res in enumerate(resultados, 1):
            source = res.metadata.get('source', 'Desconocido')
            respuesta += f"--- Resultado {i} (Archivo: {source}) ---\n{res.page_content}\n\n"

        _RAG_CACHE[query_key] = respuesta
        return respuesta
    except Exception as e:
        return f"Error al buscar en la memoria RAG: {e}"
