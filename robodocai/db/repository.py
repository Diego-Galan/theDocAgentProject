from uuid import UUID
from sqlalchemy.orm import Session
from . import models

def create_document(db: Session, source_filename: str) -> models.Document:
    """
    Crea un nuevo registro de documento en la base de datos.

    Args:
        db: La sesión de la base de datos.
        source_filename: El nombre del archivo original.

    Returns:
        El objeto Document recién creado.
    """
    db_document = models.Document(source_filename=source_filename)
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
