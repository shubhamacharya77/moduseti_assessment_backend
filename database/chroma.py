import os
from typing import Any
from dotenv import load_dotenv
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from langchain_core.documents import Document

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBEDDING_MODEL_NAME = "google/embeddinggemma-300m"


def get_chroma_client() -> chromadb.PersistentClient:
    """Initializes and returns a persistent Chroma DB client."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_embedding_function() -> embedding_functions.SentenceTransformerEmbeddingFunction:
    """Returns the SentenceTransformer embedding function using google/embeddinggemma-300m."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )


def get_or_create_collection(
    collection_name: str = "enterprise_documents"
) -> Any:
    """Retrieves or creates a target vector collection in Chroma DB with Gemma embeddings."""
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )


def store_chunks(
    chunks: list[Document],
    collection_name: str = "enterprise_documents"
) -> int:
    """Stores a list of chunked LangChain Documents into the persistent Chroma collection.

    Args:
        chunks: List of chunked LangChain Document objects.
        collection_name: Target vector collection name.

    Returns:
        Number of chunk vectors stored.
    """
    if not chunks:
        return 0

    collection = get_or_create_collection(collection_name=collection_name)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for idx, chunk in enumerate(chunks):
        chunk_id = chunk.metadata.get("chunk_id", f"chunk_{idx}")
        ids.append(chunk_id)
        documents.append(chunk.page_content)
        metadatas.append(dict(chunk.metadata))

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)


def search_chunks(
    query_text: str,
    n_results: int = 4,
    collection_name: str = "enterprise_documents"
) -> list[dict[str, Any]]:
    """Performs semantic similarity search against stored vector chunks in Chroma DB.

    Args:
        query_text: Natural language search query string.
        n_results: Maximum number of relevant chunks to return.
        collection_name: Target vector collection name.

    Returns:
        List of matching document chunk dictionaries with text, metadata, and distances.
    """
    collection = get_or_create_collection(collection_name=collection_name)

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )

    matches: list[dict[str, Any]] = []
    if not results or "documents" not in results or not results["documents"]:
        return matches

    docs_list = results["documents"][0]
    metas_list = results.get("metadatas", [[]])[0]
    ids_list = results.get("ids", [[]])[0]
    distances_list = results.get("distances", [[]])[0] if "distances" in results and results["distances"] else []

    for idx in range(len(docs_list)):
        match_item = {
            "id": ids_list[idx] if idx < len(ids_list) else f"match_{idx}",
            "text": docs_list[idx],
            "metadata": metas_list[idx] if idx < len(metas_list) else {},
            "distance": distances_list[idx] if idx < len(distances_list) else None
        }
        matches.append(match_item)

    return matches
