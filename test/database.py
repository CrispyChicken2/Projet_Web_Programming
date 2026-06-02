from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///./cv_app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_database():
    """Cree les tables SQLite si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Fournit une session de base de donnees a une route FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
