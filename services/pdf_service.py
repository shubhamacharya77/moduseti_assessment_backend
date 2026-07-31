import fitz  # PyMuPDF
from typing import Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_documents_from_pdf(
    file_bytes: bytes,
    doc_name: str,
    doc_type: str
) -> list[Document]:
    """Extract page-level text from PDF bytes using PyMuPDF (fitz) into LangChain Documents.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.
        doc_name: Filename or document title.
        doc_type: Category ('company_profile' or 'hr_policy').

    Returns:
        List of page-level LangChain Document objects with doc metadata.
    """
    pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
    documents: list[Document] = []

    for index, page in enumerate(pdf_doc, start=1):
        extracted_text = page.get_text() or ""
        cleaned_text = extracted_text.strip()
        if not cleaned_text:
            continue

        metadata: dict[str, Any] = {
            "doc_name": doc_name,
            "doc_type": doc_type,
            "page": index,
        }
        documents.append(Document(page_content=cleaned_text, metadata=metadata))

    pdf_doc.close()
    return documents


def chunk_pdf_documents(
    documents: list[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> list[Document]:
    """Split a list of page-level LangChain Documents into recursive text chunks.

    Args:
        documents: List of page-level Document objects.
        chunk_size: Maximum character size per chunk.
        chunk_overlap: Overlapping character count between adjacent chunks.

    Returns:
        List of chunked LangChain Document objects with chunk_id in metadata.
    """
    if not documents:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = text_splitter.split_documents(documents)

    # Assign unique chunk_id to metadata for each chunk
    for idx, chunk in enumerate(chunks):
        doc_type = chunk.metadata.get("doc_type", "doc")
        page = chunk.metadata.get("page", 1)
        chunk.metadata["chunk_id"] = f"{doc_type}_p{page}_c{idx}"

    return chunks
