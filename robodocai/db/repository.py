from uuid import UUID
from sqlalchemy.orm import Session
from . import models

def create_shipment(db: Session, user_id: str, name: str) -> models.Shipment:
    """
    Crea un nuevo registro de expediente (Shipment) en la base de datos.

    Args:
        db: La sesión de la base de datos.
        user_id: El ID del usuario asociado al expediente.
        name: El nombre descriptivo del expediente.

    Returns:
        El objeto Shipment recién creado.
    """
    db_shipment = models.Shipment(user_id=user_id, name=name)
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment

def create_document(db: Session, shipment_id: UUID, source_filename: str, document_type: models.DocumentType) -> models.Document:
    """
    Crea un nuevo registro de documento en la base de datos, asociado a un Shipment.

    Args:
        db: La sesión de la base de datos.
        shipment_id: El UUID del Shipment al que pertenece el documento.
        source_filename: El nombre del archivo original.
        document_type: El tipo de documento (usando el Enum DocumentType).

    Returns:
        El objeto Document recién creado.
    """
    db_document = models.Document(
        shipment_id=shipment_id,
        source_filename=source_filename,
        document_type=document_type
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document_by_id(db: Session, document_id: UUID) -> models.Document | None:
    """
    Recupera un documento por su UUID.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a recuperar.

    Returns:
        El objeto Document si se encuentra, de lo contrario None.
    """
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def update_document_status(db: Session, document_id: UUID, new_status: str) -> models.Document | None:
    """
    Actualiza el estado de un documento existente.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        new_status: El nuevo estado a establecer.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.status = new_status
        db.commit()
        db.refresh(db_document)
    return db_document

def update_pre_flight_check_results(db: Session, document_id: UUID, data: dict) -> models.Document | None:
    """
    Guarda los resultados de las comprobaciones previas (JSON) en un registro de documento.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        data: Un diccionario con los resultados de las comprobaciones.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.pre_flight_check_results = data
        db.commit()
        db.refresh(db_document)
    return db_document


def update_document_content(db: Session, document_id: UUID, text_content: str) -> models.Document | None:
    """
    Actualiza el campo de contenido de texto crudo de un documento.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        text_content: El contenido de texto extraído para guardar.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.raw_text_content = text_content
        db.commit()
        db.refresh(db_document)
    return db_document

def update_document_structured_data(db: Session, document_id: UUID, data: dict) -> models.Document | None:
    """
    Guarda los datos estructurados (JSON) en un registro de documento existente.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        data: Un diccionario con los datos estructurados a guardar.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.structured_data = data
        db.commit()
        db.refresh(db_document)
    return db_document

def update_document_classification_data(db: Session, document_id: UUID, data: dict) -> models.Document | None:
    """
    Guarda los datos de clasificación (JSON) en un registro de documento existente.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        data: Un diccionario con los datos de clasificación a guardar.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.classification_data = data
        db.commit()
        db.refresh(db_document)
    return db_document

def update_supervisor_verdict(db: Session, document_id: UUID, data: dict) -> models.Document | None:
    """
    Guarda el veredicto del supervisor (JSON) en un registro de documento existente.

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento a actualizar.
        data: Un diccionario con el veredicto del supervisor a guardar.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.supervisor_verdict = data
        db.commit()
        db.refresh(db_document)
    return db_document


def log_document_failure(db: Session, document_id: UUID, error_message: str) -> models.Document | None:
    """
    Registra un fallo de procesamiento para un documento específico.

    Esta función actualiza el estado del documento a 'error' y guarda
    un mensaje de error detallado en el campo `error_log`..

    Args:
        db: La sesión de la base de datos.
        document_id: El UUID del documento que falló.
        error_message: El mensaje de error que se va a registrar.

    Returns:
        El objeto Document actualizado si se encuentra, de lo contrario None.
    """
    db_document = get_document_by_id(db, document_id)
    if db_document:
        db_document.status = "error"
        db_document.error_log = error_message
        db.commit()
        db.refresh(db_document)
    return db_document