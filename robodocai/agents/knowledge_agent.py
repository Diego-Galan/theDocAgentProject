import os
import faiss
import numpy as np
import pickle
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from typing import List

# --- Configuración de la Base de Conocimiento ---

# Directorio para almacenar los artefactos de la base de conocimiento
KB_DIR = os.path.join(os.path.dirname(__file__), '..', 'kb')
os.makedirs(KB_DIR, exist_ok=True)

# Archivos clave
ARANCEL_PDF_FILE = os.path.join(os.path.dirname(__file__), '..', 'arancel_aduanas.pdf')
INDEX_FILE = os.path.join(KB_DIR, 'faiss_index.bin')
CHUNKS_FILE = os.path.join(KB_DIR, 'text_chunks.pkl')

# Modelo de embedding
MODEL_NAME = 'all-MiniLM-L6-v2'


def _create_knowledge_base():
    """
    Crea y guarda una base de conocimiento vectorial a partir del PDF del arancel.
    
    Este proceso es intensivo y solo se ejecuta si no se encuentra un índice existente.
    """
    print("[+] (KnowledgeAgent) Base de conocimiento no encontrada. Creando una nueva...")

    # 1. Validar que el PDF exista
    if not os.path.exists(ARANCEL_PDF_FILE):
        raise FileNotFoundError(
            f"El archivo del arancel ('{os.path.basename(ARANCEL_PDF_FILE)}') no se encontró en el directorio principal. "
            "Por favor, añádelo para poder crear la base de conocimiento."
        )

    # 2. Leer texto del PDF
    print(f"[+] (KnowledgeAgent) Leyendo texto de '{os.path.basename(ARANCEL_PDF_FILE)}'...")
    reader = PdfReader(ARANCEL_PDF_FILE)
    full_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    # 3. Dividir texto en fragmentos (chunks)
    # Usamos párrafos como una forma simple de fragmentación.
    text_chunks = [chunk.strip() for chunk in full_text.split('\n\n') if chunk.strip()]
    print(f"[+] (KnowledgeAgent) El texto fue dividido en {len(text_chunks)} fragmentos.")

    # 4. Cargar modelo y generar embeddings
    print(f"[+] (KnowledgeAgent) Cargando el modelo de embedding '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    print("[+] (KnowledgeAgent) Generando embeddings para los fragmentos... (esto puede tardar)")
    embeddings = model.encode(text_chunks, show_progress_bar=True)

    # 5. Crear y guardar el índice FAISS
    print("[+] (KnowledgeAgent) Creando el índice FAISS...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_FILE)
    print(f"[+] (KnowledgeAgent) Índice FAISS guardado en '{INDEX_FILE}'")

    # 6. Guardar los fragmentos de texto
    with open(CHUNKS_FILE, 'wb') as f:
        pickle.dump(text_chunks, f)
    print(f"[+] (KnowledgeAgent) Fragmentos de texto guardados en '{CHUNKS_FILE}'")


def search_tariff_schedule(product_description: str, k: int = 5) -> List[str]:
    """
    Busca en el arancel de aduanas los fragmentos más relevantes para una descripción de producto.

    Args:
        product_description: La descripción del producto a buscar.
        k: El número de resultados a devolver.

    Returns:
        Una lista de cadenas de texto con los fragmentos más similares del arancel.
    """
    # 1. Verificar si la base de conocimiento existe, si no, crearla.
    if not os.path.exists(INDEX_FILE) or not os.path.exists(CHUNKS_FILE):
        _create_knowledge_base()

    # 2. Cargar los datos y el modelo
    print("[+] (KnowledgeAgent) Cargando la base de conocimiento existente...")
    index = faiss.read_index(INDEX_FILE)
    with open(CHUNKS_FILE, 'rb') as f:
        text_chunks = pickle.load(f)
    
    model = SentenceTransformer(MODEL_NAME)

    # 3. Vectorizar la consulta del usuario
    print(f"[+] (KnowledgeAgent) Buscando en el arancel para: '{product_description}'...")
    query_embedding = model.encode([product_description])

    # 4. Realizar la búsqueda en el índice FAISS
    distances, indices = index.search(query_embedding, k)

    # 5. Devolver los fragmentos de texto correspondientes
    results = [text_chunks[i] for i in indices[0]]
    print("[+] (KnowledgeAgent) Búsqueda completada con éxito.")
    
    return results