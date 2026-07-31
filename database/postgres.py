import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Retrieve database URL from environment; fallback to local SQLite for development
DATABASE_URL = os.getenv("POSTGRES_DB_URL", "sqlite:///./local_modus_ai.db")

# SQLite requires check_same_thread=False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency injector yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
