"""Database session management. Provides engine, session factory, and FastAPI dependency."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config import get_settings
from backend.db.models import Base
from typing import Generator


def get_engine(database_url: str | None = None):
    url = database_url or get_settings().database_url
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, pool_size=5)


def create_tables(engine):
    """Create all tables. Used for demo mode and testing."""
    Base.metadata.create_all(bind=engine)


_engine = None
_SessionLocal = None


def init_db(database_url: str | None = None):
    """Initialize the database engine and session factory."""
    global _engine, _SessionLocal
    _engine = get_engine(database_url)
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
    return _engine


def get_session_factory():
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
