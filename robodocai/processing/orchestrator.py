import uuid
from pathlib import Path

# Importaciones para la gestión de la base de datos
from db.database import SessionLocal
from db import repository, models

# Importaciones de agentes
from agents.data_extractor import DataExtractorAgent
from agents.classification_agent import propose_tariff_classification
from agents.pre_flight_check_agent import run_pre_flight_checks
from agents.supervisor_agent import review_final_output


def process_document(doc_id: uuid.UUID, file_path: str):
    """
    Procesa un documento en segundo plano, ejecutando el pipeline completo de agentes.
    """
    print(f"[+] Starting processing for document: {doc_id}")
    
    db = SessionLocal()
    try:
        # 1. Actualizar estado a "processing"
        repository.update_document_status(db=db, document_id=doc_id, new_status="processing")
        print(f"[+] Document {doc_id} status updated to 'processing'")

        # Retrieve the document object to access its properties like document_type
        db_document = repository.get_document_by_id(db=db, document_id=doc_id)
        if not db_document:
            print(f"[-] CRITICAL: Document {doc_id} not found in DB. Aborting task.")
            repository.log_document_failure(db=db, document_id=doc_id, error_message="Document not found in DB during processing.")
            return

        # 2. Extraer datos estructurados usando el agente apropiado
        structured_data = None
        if db_document.document_type == models.DocumentType.FACTURA_COMERCIAL:
            print(f"[+] Documento identificado como {db_document.document_type.value}. Usando DataExtractorAgent...")
            extractor_agent = DataExtractorAgent()
            structured_data_model = extractor_agent.extract_from_commercial_invoice(file_path=file_path)
            if structured_data_model:
                # Convertir el modelo Pydantic a un dict para el resto del pipeline
                structured_data = structured_data_model.model_dump()
        else:
            # Lógica para otros tipos de documentos o para manejar tipos no soportados
            print(f"[-] Advertencia: No hay un agente de extracción definido para el tipo de documento: {db_document.document_type.value}")
            # Por ahora, podemos registrar un error o simplemente continuar sin datos estructurados.
            # Vamos a registrar un error para ser estrictos.
            repository.log_document_failure(
                db=db,
                document_id=doc_id,
                error_message=f"Tipo de documento '{db_document.document_type.value}' no soportado por ningún agente de extracción."
            )
            return # Detiene el procesamiento para este documento

        #Validar que la extracción fue exitosa antes de continuar
        if not structured_data:
            error_details = "El agente de extracción no pudo procesar el documento o no devolvió datos."
            full_error_message = f"Data Extraction Agent Error: {error_details}"
            print(f"[-] Error procesando documento {doc_id}: {full_error_message}")
            repository.log_document_failure(db=db, document_id=doc_id, error_message=full_error_message)
            return

        # 5. Guardar los datos estructurados en la base de datos
        repository.update_document_structured_data(db=db, document_id=doc_id, data=structured_data)
        print(f"[+] Structured data saved for document {doc_id}")

        # 6. Proponer clasificación arancelaria
        classification_result = propose_tariff_classification(structured_data=structured_data)
        if "error" in classification_result:
            error_details = classification_result.get("message", "No details provided.")
            full_error_message = f"Classification Agent Error: {error_details}"
            print(f"[-] Error processing document {doc_id}: {full_error_message}")
            repository.log_document_failure(db=db, document_id=doc_id, error_message=full_error_message)
            return
        
        # 7. Guardar el resultado de la clasificación
        repository.update_document_classification_data(db=db, document_id=doc_id, data=classification_result)
        print(f"[+] Classification data saved for document {doc_id}")

        # 8. Ejecutar Pre-Flight Checks de negocio
        pre_flight_results = run_pre_flight_checks(
            structured_data=structured_data,
            classification_data=classification_result,
            document_type=db_document.document_type # Passed document_type
        )
        repository.update_pre_flight_check_results(db=db, document_id=doc_id, data=pre_flight_results)
        print(f"[+] Pre-flight check results saved for document {doc_id}")
        
        if not pre_flight_results.get("checks_passed", True):
            print(f"[-] Document {doc_id} failed pre-flight checks. Sending for human review.")
            repository.update_document_status(db=db, document_id=doc_id, new_status="needs_review")
            return

        # 9. Supervisar el resultado final
        supervisor_verdict = review_final_output(structured_data=structured_data, classification_data=classification_result)
        repository.update_supervisor_verdict(db=db, document_id=doc_id, data=supervisor_verdict)
        print(f"[+] Supervisor verdict saved for document {doc_id}")

        # 10. Determinar el estado final basado en el veredicto del supervisor
        final_status = "completed"
        if supervisor_verdict.get("validation_status") != "approved":
            final_status = "needs_review"
        
        repository.update_document_status(db=db, document_id=doc_id, new_status=final_status)
        print(f"[+] Document {doc_id} status updated to '{final_status}'")

        print(f"[+] Finished processing for document {doc_id}")

    finally:
        db.close()
        print(f"[+] Database session closed for task {doc_id}")

    # Limpiar el archivo temporal
    try:
        Path(file_path).unlink()
        print(f"[+] Cleaned up temporary file: {file_path}")
    except OSError as e:
        print(f"[-] Error cleaning up file {file_path}: {e}")