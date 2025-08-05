import uuid
from pathlib import Path

# Importaciones para la gestión de la base de datos
from db.database import SessionLocal
from db import repository

# Importaciones para el procesamiento de PDF
from pypdf import PdfReader

# Importaciones de agentes
from agents.data_extractor import extract_data_from_text
from agents.classification_agent import propose_tariff_classification

def process_document(doc_id: uuid.UUID, file_path: str):
    """
    Procesa un documento en segundo plano, extrayendo su texto, 
    obteniendo datos estructurados y actualizando su estado.

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

        # 4. Extraer datos estructurados del texto usando el agente
        structured_data = extract_data_from_text(text_content=extracted_text)

        # --- Manejo de Errores del Agente ---
        # Comprueba si el agente de extracción de datos devolvió un error.
        if "error" in structured_data:
            error_details = structured_data.get("message", "No details provided.")
            full_error_message = f"Agent Error: {error_details}"
            print(f"[-] Error processing document {doc_id}: {full_error_message}")
            
            # Usa la nueva función dedicada para registrar el fallo
            repository.log_document_failure(
                db=db, 
                document_id=doc_id, 
                error_message=full_error_message
            )
            # Detiene el procesamiento para este documento
            return

        # 5. Guardar los datos estructurados en la base de datos
        repository.update_document_structured_data(db=db, document_id=doc_id, data=structured_data)
        print(f"[+] Structured data saved for document {doc_id}")

        # 6. Proponer clasificación arancelaria
        classification_result = propose_tariff_classification(structured_data=structured_data)

        # --- Manejo de Errores del Agente de Clasificación ---
        if "error" in classification_result:
            error_details = classification_result.get("message", "No details provided.")
            full_error_message = f"Classification Agent Error: {error_details}"
            print(f"[-] Error processing document {doc_id}: {full_error_message}")
            
            repository.log_document_failure(
                db=db, 
                document_id=doc_id, 
                error_message=full_error_message
            )
            return
        
        # 7. Guardar el resultado de la clasificación
        repository.update_document_classification_data(db=db, document_id=doc_id, data=classification_result)
        print(f"[+] Classification data saved for document {doc_id}")

        # 8. Actualizar estado a "completed"
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