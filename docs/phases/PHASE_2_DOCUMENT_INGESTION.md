# Phase 2 Specification: Document Ingestion & Knowledge RAG Tool

## 🎯 End Goal
Build an automated document processing pipeline that accepts Company Profile PDFs and HR Policy PDFs, extracts clean text, recursively chunks document content, generates vector embeddings, stores vectors into a persistent Chroma DB collection, and exposes an independent `KnowledgeTool` for targeted semantic retrieval.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 2.1: PDF Extraction & Text Chunking Service
- File: `backend/services/pdf_service.py`
- Functions:
  - `extract_text_from_pdf(file_bytes: bytes) -> str`: Uses `PyPDF` / `fitz` to extract full plain text from PDF pages.
  - `chunk_document_text(text: str, doc_name: str, doc_type: str) -> list[dict]`: Implements recursive character text splitting (chunk size: ~800 chars, chunk overlap: ~150 chars). Returns list of chunk dicts with metadata (`doc_name`, `doc_type`, `page_number`, `chunk_id`).

### Sub-Phase 2.2: Vector Storage & Embedding Pipeline
- File: `backend/database/chroma.py`
- Setup Chroma collection `enterprise_documents`.
- Embed text chunks using sentence-transformers/embedding model.
- Upsert embeddings, text chunks, and metadata into Chroma DB.

### Sub-Phase 2.3: Knowledge Tool Implementation
- File: `backend/tools/knowledge_tool.py`
- Class `KnowledgeTool(BaseTool)`:
  - Input: Query string or target topic.
  - Action: Performs similarity vector search against Chroma DB collection (`enterprise_documents`).
  - Output: Returns list of normalized `EvidenceItem` objects ONLY.
  - `EvidenceItem` format:
    - `source`: `"Knowledge Tool (" + doc_name + ")"`
    - `category`: `"Document Excerpt"`
    - `title`: Document section / header or topic title
    - `details`: `{"text_chunk": chunk_text, "doc_type": doc_type, "page": page_number}`
    - `confidence`: Similarity score string (e.g. `"Vector Match: 0.88"`)

### Sub-Phase 2.4: PDF Upload API Endpoint
- File: `backend/api/upload.py`
- Endpoint: `POST /api/upload/pdf`
  - Accepts multipart form data (PDF file + doc_type: `company_profile` | `hr_policy`).
  - Saves raw file to Supabase storage / local upload dir.
  - Triggers `PDFService` parsing, chunking, and Chroma ingestion.
  - Returns `{"status": "success", "chunks_processed": int, "doc_name": str}`.

---

## 🔍 Verification Criteria
1. Uploading a sample PDF via `POST /api/upload/pdf` yields `chunks_processed > 0`.
2. Chroma DB contains vectors tagged with doc metadata.
3. Invoking `KnowledgeTool.execute(query="HR compensation policy")` returns a list of valid `EvidenceItem` objects containing relevant policy text chunks.
4. The tool returns document chunks ONLY—no LLM reasoning or hallucinated commentary.
