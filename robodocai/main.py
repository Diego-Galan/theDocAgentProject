import uuid
from pathlib import Path
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, status, BackgroundTasks, HTTPException, Form, File, APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_serializer
from datetime import datetime

from db import database, models, repository
from db.database import get_db
from processing import orchestrator

# Crea las tablas de la base de datos si no existen.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="RoboDocAI API",
    description="API para el procesamiento inteligente de documentos de comercio exterior."
)

# Initialize APIRouter
router = APIRouter()

# --- Esquemas Pydantic (Modelos de Datos para la API) ---
class DocumentResponse(BaseModel):
    id: str
    shipment_id: str
    source_filename: str
    status: str
    raw_text_content: str | None = None
    structured_data: dict | None = None
    classification_data: dict | None = None
    pre_flight_check_results: dict | None = None
    supervisor_verdict: dict | None = None
    error_log: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    document_type: models.DocumentType

    @field_serializer('id', 'shipment_id')
    def serialize_ids(self, value: uuid.UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True

class ShipmentCreate(BaseModel):
    name: str

class ShipmentResponse(BaseModel):
    id: str
    user_id: str | None = None
    name: str
    status: str
    consolidated_data: dict | None = None
    dua_payload: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None
    documents: List[DocumentResponse] = [] # List of associated documents

    @field_serializer('id')
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True

# --- Endpoints de la API ---

@app.get("/", tags=["Health Check"])
async def root():
    """Endpoint de verificación de estado."""
    return {"message": "RoboDocAI API is running."}

@router.post("/shipments/", response_model=ShipmentResponse, tags=["Shipments"])
async def create_new_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo expediente (Shipment) para agrupar documentos.
    """
    user_id = "test-user-01" # Hardcoded for now
    db_shipment = repository.create_shipment(db=db, user_id=user_id, name=shipment.name)
    response_data = ShipmentResponse.model_validate(db_shipment)
    return response_data

@router.get("/shipments/{shipment_id}", response_model=ShipmentResponse, tags=["Shipments"])
async def get_shipment_by_id(
    shipment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Recupera la información completa de un expediente (Shipment) por su ID,
    incluyendo todos los documentos asociados.
    """
    # Query the Shipment, and eager load its documents
    db_shipment = db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first()

    if db_shipment is None:
        raise HTTPException(status_code=404, detail=f"Shipment with ID {shipment_id} not found.")

    response_data = ShipmentResponse.model_validate(db_shipment)
    return response_data

@router.post("/shipments/{shipment_id}/documents/", status_code=status.HTTP_201_CREATED, response_model=DocumentResponse, tags=["Documents"])
async def upload_document_to_shipment(
    shipment_id: uuid.UUID, # Path parameter
    tasks: BackgroundTasks,
    document_type: models.DocumentType = Form(...), # Form data
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Sube un documento, lo asocia a un expediente existente y agenda su procesamiento.
    """
    db_shipment = db.query(models.Shipment).filter(models.Shipment.id == shipment_id).first()
    if not db_shipment:
        raise HTTPException(status_code=404, detail=f"Shipment with ID {shipment_id} not found.")

    new_document = repository.create_document(
        db=db,
        shipment_id=shipment_id,
        source_filename=file.filename,
        document_type=document_type
    )
    doc_id = new_document.id

    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    file_extension = Path(file.filename).suffix
    temp_file_path = temp_dir / f"{doc_id}{file_extension}"

    try:
        contents = file.file.read()
        with open(temp_file_path, 'wb') as f:
            f.write(contents)
        print(f"[+] File saved successfully to {temp_file_path}")
    except Exception as e:
        print(f"[-] Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Could not save uploaded file.")
    finally:
        file.file.close()

    tasks.add_task(orchestrator.process_document, doc_id=doc_id, file_path=str(temp_file_path))

    response_data = DocumentResponse.model_validate(new_document)
    return response_data

@app.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document_results(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Recupera el estado y los resultados completos de un documento procesado.
    """
    print(f"[+] Fetching results for document: {document_id}")
    db_document = repository.get_document_by_id(db=db, document_id=document_id)

    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    response_data = DocumentResponse.model_validate(db_document)
    return response_data

# Register the router with the main app
app.include_router(router)