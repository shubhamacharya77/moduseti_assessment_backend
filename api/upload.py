from typing import Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from database.chroma import store_chunks
from services.pdf_service import chunk_pdf_documents, extract_documents_from_pdf

router = APIRouter()


@router.post("/pdf", status_code=status.HTTP_200_OK)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF document file (Company Profile or HR Policy)"),
    doc_type: str = Form(..., description="Document category ('company_profile' or 'hr_policy')")
) -> dict[str, Any]:
    """Uploads a PDF document, extracts pages, chunks text, and indexes embeddings in Chroma DB."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .pdf files are supported."
        )

    clean_doc_type = doc_type.strip().lower()
    if clean_doc_type not in ["company_profile", "hr_policy"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid doc_type. Must be either 'company_profile' or 'hr_policy'."
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty."
        )

    # 1. Extract page-level documents
    page_docs = extract_documents_from_pdf(
        file_bytes=file_bytes,
        doc_name=file.filename,
        doc_type=clean_doc_type
    )

    if not page_docs:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract readable text from the provided PDF."
        )

    # 2. Chunk documents recursively
    chunks = chunk_pdf_documents(page_docs)

    # 3. Store vector embeddings in ChromaDB
    chunks_stored = store_chunks(chunks)

    return {
        "status": "success",
        "doc_name": file.filename,
        "doc_type": clean_doc_type,
        "pages_extracted": len(page_docs),
        "chunks_processed": chunks_stored,
        "message": "Document successfully parsed, chunked, and indexed into vector store."
    }
