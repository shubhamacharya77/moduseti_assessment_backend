from typing import Any
from database.chroma import search_chunks
from models.evidence import EvidenceItem


class KnowledgeTool:
    """Independent fact-retrieval tool querying ChromaDB vector store for document excerpts."""

    def __init__(self, collection_name: str = "enterprise_documents"):
        self.collection_name = collection_name

    def query(self, query_text: str, n_results: int = 4) -> list[EvidenceItem]:
        """Runs vector similarity search against Chroma DB and returns normalized EvidenceItem objects.

        Args:
            query_text: Executive question or target query string.
            n_results: Maximum number of document chunks to retrieve.

        Returns:
            List of normalized EvidenceItem objects.
        """
        raw_matches = search_chunks(
            query_text=query_text,
            n_results=n_results,
            collection_name=self.collection_name
        )

        evidence_items: list[EvidenceItem] = []

        for match in raw_matches:
            metadata = match.get("metadata", {})
            doc_name = metadata.get("doc_name", "Unknown Document")
            doc_type = metadata.get("doc_type", "document")
            page = metadata.get("page", 1)
            chunk_id = metadata.get("chunk_id", match.get("id", ""))
            distance = match.get("distance")

            confidence_str = (
                f"Vector Distance: {distance:.4f}"
                if distance is not None
                else "Vector Match"
            )

            item = EvidenceItem(
                source=f"Knowledge Tool ({doc_name})",
                category="Document Excerpt",
                title=f"Excerpt from {doc_name} (Page {page})",
                details={
                    "text_chunk": match.get("text", ""),
                    "doc_name": doc_name,
                    "doc_type": doc_type,
                    "page": page,
                    "chunk_id": chunk_id,
                },
                confidence=confidence_str,
            )
            evidence_items.append(item)

        return evidence_items
