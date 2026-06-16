import os
try:
    import chromadb
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from smolagents import tool
except ImportError:
    Chroma = None

# Configuración del motor de Embeddings ligero (Corre en CPU y ocupa poca RAM)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DB_DIR = "./chroma_db"

def init_chroma():
    """Inicializa la base de datos ChromaDB y el modelo de embeddings."""
    if Chroma is None:
        return None, None
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings, collection_name="local_repos")
    return db, embeddings

@tool("Indexar Directorio Local (RAG)")
def indexar_directorio_local(ruta: str):
    """Escanea todos los archivos de código en un directorio local, los parte en pedazos y los indexa en la base de datos vectorial ChromaDB para futuras búsquedas semánticas."""
    if Chroma is None:
        return "Error: Las librerías RAG no están instaladas (chromadb, langchain-chroma, sentence-transformers)."
        
    if not os.path.isdir(ruta):
        return f"Error: La ruta {ruta} no es un directorio válido."
        
    db, embeddings = init_chroma()
    
    archivos_procesados = 0
    textos = []
    metadatos = []
    
    # Extensiones de código válidas
    ext_validas = {'.py', '.js', '.ts', '.md', '.txt', '.html', '.css', '.json'}
    
    for root, dirs, files in os.walk(ruta):
        # Ignorar carpetas problemáticas
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', '__pycache__', '.venv']]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in ext_validas:
                ruta_completa = os.path.join(root, file)
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        textos.append(contenido)
                        metadatos.append({"source": ruta_completa})
                        archivos_procesados += 1
                except Exception:
                    pass # Ignorar archivos binarios o que no se puedan leer
                    
    if not textos:
        return f"No se encontraron archivos de texto/código válidos en {ruta}."
        
    # Dividir los textos en fragmentos (chunks)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents(textos, metadatas=metadatos)
    
    # Añadir a ChromaDB
    db.add_documents(docs)
    
    return f"¡Éxito! Se indexaron {archivos_procesados} archivos ({len(docs)} fragmentos) del directorio {ruta} en la memoria RAG."

@tool("Preguntar a Base de Conocimiento Local (RAG)")
def preguntar_a_repositorio(pregunta: str):
    """Realiza una búsqueda semántica sobre los repositorios previamente indexados para encontrar la respuesta en el código."""
    if Chroma is None:
        return "Error: Las librerías RAG no están instaladas."
        
    db, _ = init_chroma()
    
    try:
        # Recuperar los 4 fragmentos más relevantes
        resultados = db.similarity_search(pregunta, k=4)
        
        if not resultados:
            return "No se encontró información relevante en la base de datos indexada."
            
        respuesta = "Fragmentos de código relevantes encontrados en la memoria local:\n\n"
        for i, res in enumerate(resultados, 1):
            source = res.metadata.get('source', 'Desconocido')
            respuesta += f"--- Resultado {i} (Archivo: {source}) ---\n{res.page_content}\n\n"
            
        return respuesta
    except Exception as e:
        return f"Error al buscar en la memoria RAG: {e}"
