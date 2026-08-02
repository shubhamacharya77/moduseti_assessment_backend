import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_DB_URL")
if not DATABASE_URL:
    raise ValueError("POSTGRES_DB_URL environment variable is not set.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """Dependency injector yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
