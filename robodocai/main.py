from fastapi import FastAPI, Depends, UploadFile, status
from sqlalchemy.orm import Session

from db import database, models, repository
from db.database import get_db

# Crea las tablas de la base de datos si no existen.
# Esto es útil para el desarrollo, pero para producción se podría usar Alembic.
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="RoboDocAI API")


@app.get("/", tags=["Health Check"])
async def root():
    """Endpoint de verificación de estado."""
    return {"message": "RoboDocAI API is running."}


@app.post("/upload/", status_code=status.HTTP_201_CREATED, tags=["Documents"])
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    """
    Sube un documento, crea un registro en la base de datos y devuelve su ID.

    Args:
        file (UploadFile): El archivo a subir.
        db (Session, optional): La sesión de la base de datos inyectada por FastAPI. Defaults to Depends(get_db).

    Returns:
        dict: Un diccionario con un mensaje, el ID del documento y el nombre del archivo.
    """
    # Llama a la función del repositorio para persistir el nuevo documento.
    # Usamos file.filename para obtener el nombre del archivo original.
    new_document = repository.create_document(db=db, source_filename=file.filename)

    return {
        "message": "Document uploaded successfully and is pending processing.",
        "id": str(new_document.id),
        "source_filename": new_document.source_filename,
    }
