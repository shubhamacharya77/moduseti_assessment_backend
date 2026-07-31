import os
from typing import Any
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")


def get_chroma_client() -> chromadb.PersistentClient:
    """Initializes and returns a persistent Chroma DB client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_or_create_collection(collection_name: str = "enterprise_documents") -> Any:
    """Retrieves or creates a target vector collection in Chroma DB."""
    client = get_chroma_client()
    return client.get_or_create_collection(name=collection_name)
