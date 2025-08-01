from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from core.config import settings

# 1. Motor de la Base de Datos (Engine)
# Se crea una única instancia de Engine para toda la aplicación.
# Se lee la URL de la base de datos desde nuestra configuración centralizada.
# `connect_args` es específico para SQLite para prevenir errores en entornos de múltiples hilos.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
)

# 2. Fábrica de Sesiones (Session Factory)
# SessionLocal es una fábrica. Cuando la llamemos, nos dará una nueva sesión de base de datos.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Clase Base para Modelos
# Nuestros modelos de ORM (como la clase Document) heredarán de esta clase.
Base = declarative_base()

# 4. Función de Dependencia para Sesiones
def get_db():
    """
    Dependencia de FastAPI que gestiona el ciclo de vida de la sesión de la base de datos.
    - Crea una nueva sesión para cada petición.
    - Provee la sesión a la ruta.
    - Cierra la sesión de forma segura al finalizar, incluso si hay errores.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()