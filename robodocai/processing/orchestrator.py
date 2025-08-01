import uuid
import time
from pathlib import Path

# Importaciones para la gestión de la base de datos
from db.database import SessionLocal
from db import repository

def process_document(doc_id: uuid.UUID, file_path: str):
    """
    Procesa un documento en segundo plano, actualizando su estado en la base de datos.

    Args:
        doc_id (uuid.UUID): El ID del documento a procesar.
        file_path (str): La ruta al archivo temporal.
    """
    print(f"[+] Starting processing for document: {doc_id}")
    
    # Crear una sesión de base de datos dedicada para esta tarea.
    db = SessionLocal()
    try:
        # 1. Actualizar el estado a "processing"
        repository.update_document_status(db=db, document_id=doc_id, new_status="processing")
        print(f"[+] Document {doc_id} status updated to 'processing'")

        # 2. Simular un trabajo de larga duración (ej: llamado a un LLM)
        time.sleep(10)

        # 3. Actualizar el estado a "completed"
        repository.update_document_status(db=db, document_id=doc_id, new_status="completed")
        print(f"[+] Document {doc_id} status updated to 'completed'")

        print(f"[+] Finished processing for document: {doc_id}")

    finally:
        # 4. Asegurarse de que la sesión de la base de datos se cierre siempre.
        db.close()
        print(f"[+] Database session closed for task {doc_id}")

    # 5. Limpiar el archivo temporal después del procesamiento.
    try:
        Path(file_path).unlink()
        print(f"[+] Cleaned up temporary file: {file_path}")
    except OSError as e:
        print(f"[-] Error cleaning up file {file_path}: {e}")