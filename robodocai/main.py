from fastapi import FastAPI, Depends, UploadFile, status, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path
import shutil

from db import database, models, repository
from db.database import get_db
from processing import orchestrator

# Crea las tablas de la base de datos si no existen.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="RoboDocAI API")


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

    Args:
        file (UploadFile): El archivo a subir.
        tasks (BackgroundTasks): Gestor de tareas en segundo plano de FastAPI.
        db (Session, optional): La sesión de la base de datos inyectada.

    Returns:
        dict: Un diccionario con un mensaje, el ID del documento y el nombre del archivo.
    """
    # 1. Crear el registro en la base de datos para obtener un ID único.
    new_document = repository.create_document(db=db, source_filename=file.filename)
    doc_id = new_document.id

    # 2. Definir y crear el directorio para archivos temporales.
    temp_dir = Path("temp_uploads")
    temp_dir.mkdir(exist_ok=True)

    # 3. Construir la ruta del archivo temporal usando el ID del documento.
    file_extension = Path(file.filename).suffix
    temp_file_path = temp_dir / f"{doc_id}{file_extension}"

    # 4. Guardar el archivo subido en la ruta temporal.
    with temp_file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. Agendar la tarea de procesamiento en segundo plano.
    tasks.add_task(orchestrator.process_document, doc_id=doc_id, file_path=str(temp_file_path))

    # 6. Devolver la respuesta inmediata al cliente.
    return {
        "message": "Document uploaded successfully and is scheduled for processing.",
        "id": str(doc_id),
        "source_filename": new_document.source_filename,
    }
