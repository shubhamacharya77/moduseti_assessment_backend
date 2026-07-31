import io
from typing import Any
import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from database.chroma import store_chunks
from services.csv_service import (
    calculate_sales_metrics,
    clean_and_process_sales_csv,
    persist_sales_data_to_db,
)
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


@router.post("/sales", status_code=status.HTTP_200_OK)
async def upload_sales(
    file: UploadFile = File(..., description="Sales CSV dataset file (e.g. sales_transactions.csv)")
) -> dict[str, Any]:
    """Uploads a Sales CSV file, normalizes records, calculates KPIs, and persists to PostgreSQL."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .csv files are supported."
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded Sales CSV file is empty."
        )

    try:
        raw_df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not parse CSV file: {str(e)}"
        )

    # 1. Clean and process raw sales DataFrame
    clean_df, report = clean_and_process_sales_csv(raw_df)
    if clean_df.empty:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded CSV file contains no valid sales rows."
        )

    # 2. Calculate quantitative sales metrics
    metrics = calculate_sales_metrics(clean_df)

    # 3. Persist transactions & metrics to database via SQLModel
    batch_id = persist_sales_data_to_db(clean_df, metrics)

    return {
        "status": "success",
        "filename": file.filename,
        "batch_id": batch_id,
        "rows_received": report.get("total_rows_received", 0),
        "rows_processed": report.get("processed_rows", 0),
        "skipped_rows": report.get("skipped_rows", 0),
        "summary_metrics": {
            "total_revenue": metrics.get("total_revenue", 0.0),
            "total_profit": metrics.get("total_profit", 0.0),
            "profit_margin_pct": metrics.get("profit_margin_pct", 0.0),
            "top_category": metrics.get("top_category", "None"),
            "top_region": metrics.get("top_region", "None"),
        },
        "message": "Sales dataset successfully parsed, cleaned, and persisted into database."
    }
