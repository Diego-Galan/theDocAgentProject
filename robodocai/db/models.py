import uuid
from sqlalchemy import Column, String, JSON, DateTime, func, Text, Uuid
from .database import Base

class Document(Base):
    """
    Representa un documento procesado en el sistema RoboDocAI.
    Cada fila es un único documento que ha sido subido para su procesamiento.
    """
    __tablename__ = "documents"

    # Clave primaria: Un identificador único universal (UUID) para cada documento.
    # Usamos el tipo genérico `Uuid` de SQLAlchemy para compatibilidad entre bases de datos.
    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # El nombre del archivo tal como fue subido por el usuario.
    source_filename = Column(String, nullable=False)

    # El estado actual del documento dentro del flujo de trabajo de procesamiento.
    status = Column(String, nullable=False, default="received")

    # Un campo JSON para almacenar los datos estructurados extraídos por el LLM.
    structured_data = Column(JSON, nullable=True)

    # El contenido de texto crudo extraído del documento.
    raw_text_content = Column(Text, nullable=True)

    # Un campo JSON para almacenar los resultados de las validaciones de negocio.
    pre_flight_check_results = Column(JSON, nullable=True)

    # Un campo JSON para almacenar el resultado del agente de clasificación arancelaria.
    classification_data = Column(JSON, nullable=True)

    # Un campo JSON para almacenar el veredicto del agente supervisor.
    supervisor_verdict = Column(JSON, nullable=True)

    # Campo para registrar cualquier mensaje de error durante el procesamiento.
    error_log = Column(Text, nullable=True)

    # Marcas de tiempo para auditoría, gestionadas automáticamente por la base de datos.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())
