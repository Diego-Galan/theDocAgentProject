import uuid
import enum
from sqlalchemy import Column, String, JSON, DateTime, func, Text, Uuid, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base

class DocumentType(enum.Enum):
    FACTURA_COMERCIAL = "Factura Comercial"
    LISTA_EMPAQUE = "Packing List"
    CONOCIMIENTO_EMBARQUE = "Bill of Lading o Guía Aérea (Air Waybill)"
    CERTIFICADO_ORIGEN = "Certificado de Origen"
    PERMISOS_CERTIFICACIONES_ESPECIALES = "Permisos y Certificaciones Especiales"
    SEGURO_CARGA = "Certificado de Seguro de Carga"
    VISTOS_BUENOS = "Vistos Buenos o Documentos de Aprobación"
    CARTA_PORTE = "Carta de Porte Terrestre (CMR)"
    OTRO = "Otro, a menudo RUT"

class Shipment(Base):
    """
    Representa un "expediente" o "envío" que agrupa varios documentos.
    Permite gestionar el ciclo de vida de una operación de comercio exterior completa.
    """
    __tablename__ = "shipments"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)  # Para futura multi-tenencia
    name = Column(String, nullable=False, comment="Nombre descriptivo del expediente, ej: Importación Café Enero")
    status = Column(String, nullable=False, default="collecting_documents")
    consolidated_data = Column(JSON, nullable=True, comment="Datos consolidados de todos los documentos del expediente")
    dua_payload = Column(JSON, nullable=True, comment="Payload para la DUA, generado a partir de los datos consolidados")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    # Relación uno-a-muchos: Un envío tiene muchos documentos.
    documents = relationship("Document", back_populates="shipment", cascade="all, delete-orphan")


class Document(Base):
    """
    Representa un documento individual (factura, packing list, etc.)
    que pertenece a un Shipment.
    """
    __tablename__ = "documents"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    
    # Clave foránea que vincula el documento a un envío.
    shipment_id = Column(Uuid, ForeignKey("shipments.id"), nullable=False)

    source_filename = Column(String, nullable=False)
    
    # Nuevo campo para el tipo de documento usando el Enum
    document_type = Column(Enum(DocumentType), nullable=False, comment="Tipo de documento (e.g., FACTURA_COMERCIAL)")
    
    status = Column(String, nullable=False, default="received")
    structured_data = Column(JSON, nullable=True)
    raw_text_content = Column(Text, nullable=True)
    pre_flight_check_results = Column(JSON, nullable=True)
    classification_data = Column(JSON, nullable=True)
    supervisor_verdict = Column(JSON, nullable=True)
    error_log = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    # Relación muchos-a-uno: Muchos documentos pertenecen a un envío.
    shipment = relationship("Shipment", back_populates="documents")