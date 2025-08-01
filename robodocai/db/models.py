import uuid
from sqlalchemy import Column, String, JSON, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from .database import Base

class Document(Base):
    """
    Representa un documento procesado en el sistema RoboDocAI.
    Cada fila es un único documento que ha sido subido para su procesamiento.
    """
    __tablename__ = "documents"

    # Clave primaria: Un identificador único universal (UUID) para cada documento.
    # Esto es preferible a un entero autoincremental por seguridad y para entornos distribuidos.
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # El nombre del archivo tal como fue subido por el usuario.
    # Ejemplo: "factura_proveedor_marzo.pdf"
    source_filename = Column(String, nullable=False)

    # El estado actual del documento dentro del flujo de trabajo de procesamiento.
    # Valores posibles: "received", "processing", "completed", "error", "needs_review".
    status = Column(String, nullable=False, default="received")

    # Un campo JSON para almacenar los datos estructurados extraídos por el LLM.
    # Ejemplo: {"invoice_id": "INV-123", "total_amount": 450.50, ...}
    structured_data = Column(JSON, nullable=True)

    # El contenido de texto crudo extraído del documento.
    # Se llena después de la fase de OCR o extracción de texto.
    raw_text_content = Column(Text, nullable=True)

    # Marcas de tiempo para auditoría, gestionadas automáticamente por la base de datos.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())