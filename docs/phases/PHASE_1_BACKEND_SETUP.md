# Phase 1 Specification: Backend Setup

## 🎯 End Goal
Establish a production-ready, modular FastAPI backend skeleton in `backend/` with virtual environment configuration, dependency management, environment variable loading, database connection clients (PostgreSQL, Chroma DB, Supabase), core Pydantic contracts, and an operational health check endpoint.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 1.1: Directory Hierarchy Initialization
Create the following directory layout under `backend/`:
```
backend/
 ├── api/           # Router modules (upload, dashboard, chat, health)
 ├── agents/        # LangGraph supervisor & Groq strategy engine
 │    ├── supervisor/
 │    └── strategy/
 ├── tools/         # Independent fact-retrieval tools
 │    ├── knowledge/
 │    ├── sales/
 │    ├── customer/
 │    ├── research/
 │    └── evidence/
 ├── services/      # Ingestion & data processing services
 ├── database/      # PostgreSQL, Chroma, Supabase client modules
 ├── models/        # Pydantic schemas & ORM models
 └── prompts/       # System prompt templates
```

### Sub-Phase 1.2: Dependencies & Environment Setup
- File: `backend/requirements.txt`
  - Core dependencies: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `langgraph`, `langchain`, `langchain-groq`, `groq`, `pandas`, `chromadb`, `psycopg2-binary`, `sqlalchemy`, `python-dotenv`, `sentence-transformers`, `pypdf`.
- File: `backend/.env.example`
  - `GROQ_API_KEY`
  - `POSTGRES_DB_URL`
  - `CHROMA_PERSIST_DIR`
  - `SUPABASE_URL` & `SUPABASE_KEY`

### Sub-Phase 1.3: Storage & Database Client Modules
- File: `backend/database/postgres.py`: SQLAlchemy engine setup, session generator, base model.
- File: `backend/database/chroma.py`: Persistent ChromaDB client initialization and collection management.
- File: `backend/database/supabase.py`: Supabase object storage client wrapper for raw PDF/CSV file storage.

### Sub-Phase 1.4: Core Pydantic Contracts
- File: `backend/models/evidence.py`:
  - `EvidenceItem`: Schema `{ source: str, category: str, title: str, details: dict | str, confidence: str }`
  - `EvidencePackage`: Schema `{ question: str, items: list[EvidenceItem] }`
- File: `backend/models/strategy.py`:
  - `StrategicIssue`: Detailed problem description
  - `StrategicResponse`: Schema `{ strategic_issues: list[str], evidence: list[str], business_impact: str, recommendation: str, priority: str, expected_outcome: str }`

### Sub-Phase 1.5: FastAPI Application & Health Route
- File: `main.py`:
  - Initialize FastAPI app instance.
  - Enable CORS middleware for frontend communication.
  - Expose `/api/health` endpoint returning `{"status": "healthy", "service": "MODUS AI Platform"}`.

---

## 🔍 Verification Criteria
1. `requirements.txt` installs cleanly.
2. Database client modules load without errors.
3. `uvicorn main:app` starts without errors.
4. Calling `GET http://localhost:8000/api/health` returns HTTP 200 `{"status": "healthy"}`.
