import uuid
from pathlib import Path
import shutil
from fastapi import FastAPI, Depends, UploadFile, status, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
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

# --- Esquemas Pydantic (Modelos de Datos para la API) ---
# Esta es la versión robusta del esquema de respuesta.
class DocumentResponse(BaseModel):
    # Tratamos el ID como un string en la respuesta para máxima compatibilidad.
    id: str
    source_filename: str
    status: str
    raw_text_content: str | None = None
    # Aceptamos los campos JSON como diccionarios estándar de Python.
    structured_data: dict | None = None
    classification_data: dict | None = None
    pre_flight_check_results: dict | None = None
    supervisor_verdict: dict | None = None
    error_log: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True # Permite que Pydantic lea los datos desde un objeto SQLAlchemy.

# --- Endpoints de la API ---

@app.get("/", tags=["Health Check"])
async def root():
    """Endpoint de verificación de estado."""
    return {"message": "RoboDocAI API is running."}


@app.post("/upload/", status_code=status.HTTP_201_CREATED, tags=["Documents"])
async def upload_document(
    file: UploadFile, 
    tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Sube un documento, lo guarda temporalmente y agenda su procesamiento en segundo plano.
    """
    new_document = repository.create_document(db=db, source_filename=file.filename)
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

    return {
        "message": "Document uploaded successfully and is scheduled for processing.",
        "id": str(doc_id),
        "source_filename": new_document.source_filename,
    }


@app.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document_results(document_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Recupera el estado y los resultados completos de un documento procesado.
    """
    print(f"[+] Fetching results for document: {document_id}")
    db_document = repository.get_document_by_id(db=db, document_id=document_id)

    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Convertimos el ID a string manualmente antes de devolverlo
    response_data = db_document.__dict__
    response_data['id'] = str(db_document.id)
    
    return response_data
