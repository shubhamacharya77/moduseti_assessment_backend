# AI Transformation Strategy Intelligence Platform — Architecture & System Structure

## 🏗️ How Is It Built?
The platform uses a **Layered Service Architecture** with strict isolation between deterministic data retrieval/analytics tools and the LLM reasoning engine.

---

## 1. Layer Responsibilities

- **`backend/api/`**: Only HTTP routes and request/response validation.
- **`backend/services/`**: Business logic, data transformations, PDF chunking, and Pandas calculations.
- **`backend/tools/`**: Fact retrieval (Chroma vector search, Pandas SQL queries, Research benchmarks).
- **`backend/agents/`**: LLM reasoning engine (Groq) and Supervisor graph (LangGraph).
- **`backend/database/`**: Database persistence (PostgreSQL engine, Chroma client, Supabase client).
- **`backend/models/`**: Pydantic schemas and SQLAlchemy ORM models.
- **`backend/prompts/`**: System prompt templates.

---

## 2. Layered Architecture Diagram

```
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                             APPLICATION LAYER                               │
 │             [ FastAPI Routing ]   [ Request / Payload Validation ]          │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │ Orchestrates Execution
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │                              SUPERVISOR LAYER                               │
 │             (LangGraph State Supervisor - Intent Routing & Tool Dispatch)   │
 ├──────────────┬───────────────────────┼──────────────────────┬───────────────┤
 │              │                       │                      │               │
 │  ┌───────────▼──────────┐  ┌─────────▼────────────┐  ┌───────▼───────────┐ │ ┌──────────▼─────────┐
 │  │ Knowledge Tool (RAG) │  │ Sales Analytics Tool │  │ Customer Analytics│ │ │   Research Tool    │
 │  │    (Chroma Vector)   │  │    (Pandas / SQL)    │  │    (Pandas / SQL) │ │ │(External Benchmarks│
 │  └───────────┬──────────┘  └─────────┬────────────┘  └───────┬───────────┘ │ └──────────┬──────────┘
 │              │                       │                      │               │            │
 └──────────────┴───────────────────────┼──────────────────────┴───────────────┴────────────┘
                                        │ Raw Tool Outputs
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │                             EVIDENCE COLLECTOR                              │
 │          Aggregates & structures tool outputs into unified Evidence Package │
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │ Unified Evidence Package
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │                        STRATEGIC INTELLIGENCE ENGINE                        │
 │  (Groq LLM - The ONLY component allowed to execute LLM Reasoning & Synthesis)│
 └──────────────────────────────────────┬──────────────────────────────────────┘
                                        │
 ┌──────────────────────────────────────▼──────────────────────────────────────┐
 │                                STORAGE LAYER                                │
 │ [ Supabase File Storage ]    [ PostgreSQL (Structured) ]    [ Chroma Vector ]│
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flows

### Upload PDF Flow
```
Upload PDF ──► Chunk ──► Embedding ──► Chroma DB
```

### Upload CSV Flow
```
Upload CSV ──► Validation ──► Pandas Math ──► PostgreSQL
```

### Execution & Strategy Flow (Dashboard / Chat)
```
Dashboard Request ──► Supervisor ──► Tools ──► Evidence ──► LLM ──► JSON Response
```

---

## 4. Layer Contracts & Schemas

### Evidence Collector Output Schema (`EvidencePackage`)
Normalizes all tool outputs into a single Pydantic `EvidencePackage`:
```json
{
  "source": "Sales Analytics Tool",
  "category": "Quantitative Metric",
  "title": "Quarterly Revenue Decline",
  "details": { "total_revenue": 1250000, "growth_rate_pct": -14.2 },
  "confidence": "High (100% Deterministic Python Calculation)"
}
```

### Strategic Intelligence Engine Output Schema (`StrategicResponse`)
Receives `Question` + `EvidencePackage` and outputs structured strategic JSON:
```json
{
  "strategic_issues": ["Issue description..."],
  "evidence": ["Citations mapping back to Evidence Package"],
  "business_impact": "Financial/Operational impact...",
  "recommendation": "Phased strategic play...",
  "priority": "High (Immediate Quick-Win)",
  "expected_outcome": "Estimated ROI / Performance gain..."
}
```

---

## 5. Backend Technology Stack

- **Framework**: FastAPI (Async Python REST API)
- **Orchestration**: LangGraph (Stateful multi-actor agent graph)
- **AI Framework**: LangChain (Vector store adapters & tool wrappers)
- **LLM Engine**: Groq API (Sub-second inference)
- **Analytics**: Pandas (Dataframe math & trend analysis)
- **Relational Storage**: PostgreSQL (SQLAlchemy / asyncpg)
- **Vector Storage**: Chroma DB (Persistent vector collection)
- **File Storage**: Supabase Storage
