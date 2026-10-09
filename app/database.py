from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./taskmanager.db"

# Create SQLAlchemy engine for SQLite database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy 2.0 models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and ensures proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
