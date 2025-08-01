import uuid
import time
from pathlib import Path

def process_document(doc_id: uuid.UUID, file_path: str):
    """
    Simula el procesamiento de un documento.

    Args:
        doc_id (uuid.UUID): El ID del documento a procesar.
        file_path (str): La ruta al archivo temporal.
    """
    print(f"[+] Starting processing for document: {doc_id}")
    
    # Simula un trabajo de larga duración (ej: llamado a un LLM)
    time.sleep(10)
    
    print(f"[+] Finished processing for document: {doc_id}")
    
    # Limpia el archivo temporal después del procesamiento.
    try:
        Path(file_path).unlink()
        print(f"[+] Cleaned up temporary file: {file_path}")
    except OSError as e:
        print(f"[-] Error cleaning up file {file_path}: {e}")
