"""Conexión a SQLite vía SQLAlchemy. La DB vive junto a los otros archivos de api/."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "stock.db"

# check_same_thread=False hace falta para que FastAPI pueda usar la sesión
# en distintos threads (uvicorn workers). El archivo .db queda en api/stock.db.
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    """Dependency de FastAPI: abre/cierra una sesión por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
