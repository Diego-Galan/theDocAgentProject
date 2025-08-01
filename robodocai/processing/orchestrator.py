import uuid
from pathlib import Path

# Importaciones para la gestión de la base de datos
from db.database import SessionLocal
from db import repository

# Importaciones para el procesamiento de PDF
from pypdf import PdfReader

def process_document(doc_id: uuid.UUID, file_path: str):
    """
    Procesa un documento en segundo plano, extrayendo su texto y actualizando su estado.

    Args:
        doc_id (uuid.UUID): El ID del documento a procesar.
        file_path (str): La ruta al archivo temporal.
    """
    print(f"[+] Starting processing for document: {doc_id}")
    
    db = SessionLocal()
    try:
        # 1. Actualizar estado a "processing"
        repository.update_document_status(db=db, document_id=doc_id, new_status="processing")
        print(f"[+] Document {doc_id} status updated to 'processing'")

        # 2. Extraer texto del PDF
        print(f"[+] Extracting text from {file_path}...")
        reader = PdfReader(file_path)
        extracted_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
        
        # 3. Guardar el texto extraído en la base de datos
        repository.update_document_content(db=db, document_id=doc_id, text_content=extracted_text)
        print(f"[+] Text extracted and saved for document {doc_id}")

        # 4. Actualizar estado a "completed"
        repository.update_document_status(db=db, document_id=doc_id, new_status="completed")
        print(f"[+] Document {doc_id} status updated to 'completed'")

        print(f"[+] Finished processing for document: {doc_id}")

    finally:
        db.close()
        print(f"[+] Database session closed for task {doc_id}")

    # Limpiar el archivo temporal
    try:
        Path(file_path).unlink()
        print(f"[+] Cleaned up temporary file: {file_path}")
    except OSError as e:
        print(f"[-] Error cleaning up file {file_path}: {e}")
