# MODUS Enterprise AI: Transformation Strategy Intelligence Platform 🚀

[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js%2016%20%7C%20React%20%7C%20TypeScript-000000.svg)](https://nextjs.org/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Groq%20Llama%203.3%2070B%20%7C%20LangChain-FF4500.svg)](https://groq.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20ChromaDB-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, evidence-grounded **AI Strategy Intelligence Platform** built for executive leadership, C-suite decision makers, and strategy consultants. MODUS connects structured corporate databases (sales transactions, customer churn, revenue trends) with unstructured enterprise documentation (HR policies, operating handbooks, compliance manuals) to generate 100% deterministic, evidence-backed strategic recommendations.

---

## 📌 Table of Contents
- [1. Project Overview](#1-project-overview)
- [2. Key Features](#2-key-features)
- [3. Architecture](#3-architecture)
- [4. AI Pipeline](#4-ai-pipeline)
- [5. Intent Types](#5-intent-types)
- [6. Analytics Engine](#6-analytics-engine)
- [7. Evidence Layer](#7-evidence-layer)
- [8. Strategy Engine](#8-strategy-engine)
- [9. Dynamic Visualization & Charts](#9-dynamic-visualization--charts)
- [10. Technology Stack](#10-technology-stack)
- [11. Project Structure](#11-project-structure)
- [12. Installation & Setup](#12-installation--setup)
- [13. Environment Variables](#13-environment-variables)
- [14. Real-World Example Queries](#14-real-world-example-queries)
- [15. System Screenshots](#15-system-screenshots)
- [16. Architecture & Design Decisions](#16-architecture--design-decisions)
- [17. Future Enhancements](#17-future-enhancements)
- [18. License](#18-license)

---

## 1. Project Overview

### The Business Problem
Executive leadership teams often face a critical dilemma when evaluating enterprise performance:
1. **Siloed Data**: Quantitative sales transactions sit in SQL databases, customer health metrics live in CRM systems, and operational guidelines are locked inside multi-page corporate PDF documents.
2. **LLM Hallucinations & Math Errors**: Standard LLMs frequently hallucinate numbers, fail at basic arithmetic estimations over large datasets, and invent ungrounded advice.
3. **Lack of Evidence Citation**: C-suite leaders require verifiable audit trails showing *why* a strategic recommendation was made and *which* exact database row or document page supports it.

### The Solution: MODUS Enterprise AI
MODUS resolves this by enforcing a strict separation of concerns:
- **100% Deterministic Python Analytics Engine**: Executes Pandas and SQL aggregations for all mathematical calculations, revenue trends, CSAT scores, and churn rates. The LLM is **never** permitted to calculate numbers.
- **Selective Intent Planner & DAG Pipeline**: Evaluates executive questions, classifies intent using Groq LLM, and dispatches *only* the required tool capabilities.
- **Normalized Evidence Package**: Normalizes facts into structured Pydantic containers before sending them to the Strategy Engine.
- **Evidence-Grounded Executive Summarizer**: Uses Groq Llama 3.3 70B to synthesize natural language answers strictly grounded in the ingested evidence.

---

## 2. Key Features

- 💬 **Natural Language Executive Q&A**: Conversational split-screen AI chat supporting natural language queries across commercial data and policy documents.
- 🎯 **LLM Semantic Intent Classification**: Groq-powered semantic classifier (`IntentClassifier`) identifying intent categories with sub-millisecond keyword fallback.
- 🚦 **Selective Intent Planner**: Dynamic capability scheduler (`ExecutionPlanner`) executing *only* necessary tool branches to eliminate data pollution and guarantee fast execution.
- 📈 **Deterministic Sales Analytics**: Python-driven calculations for enterprise revenue, profit margins, deal sizes, product category breakdowns, and regional performance.
- 👥 **Customer Health & Retention Analytics**: Account risk vectors, churn rate percentages, customer satisfaction (CSAT) ratings, and loyalty tier distribution.
- 📄 **Enterprise PDF RAG Inspector**: ChromaDB vector store chunking and embedding PDF manuals (e.g. HR policies, corporate finance handbooks) with interactive page-level quote inspection.
- 🧠 **Divided Response Strategy Engine**: Generates a clean 3-part divided response: **Direct Factual Answer**, **Actionable Recommendation Step** (if relevant), and **Key Strategic Issues** (if risks exist).
- 📊 **Dynamic Recharts Visualizer**: Auto-generates high-contrast Area Line, Category Bar, and Segment Pie charts matching query intent.
- 💵 **Native Currency & Formatting System**: Formats all monetary figures using Indian Rupee (`₹`) and Lakhs/Crores (`₹7.52 Cr`) notation.
- 🛡️ **Zero Hallucination Control**: Guarantees zero fake advice on simple data lookups by returning clean empty arrays (`strategic_issues: []`) for pure metric queries.

---

## 3. Architecture

MODUS is built as a stateful, agentic Directed Acyclic Graph (DAG) orchestrated by the `SupervisorAgent`.

```mermaid
flowchart TD
    User([👤 Executive User]) -->|Natural Language Question| Frontend[💻 Next.js Split-Screen UI]
    Frontend -->|POST /api/chat/ask| API[⚡ FastAPI Service Router]
    API --> Supervisor[👑 SupervisorAgent Orchestrator]
    
    subgraph Stage 1: Intent & Planning
        Supervisor -->|User Question| IntentClass[🧠 IntentClassifier]
        IntentClass -->|IntentType| ExecPlanner[📋 ExecutionPlanner]
        ExecPlanner -->|ExecutionPlan Matrix| CapabilityBranch{Targeted Capability Branch}
    end

    subgraph Stage 2: Selective Tool Dispatch
        CapabilityBranch -->|need_sales=True| SalesTool[📊 SalesAnalyticsTool]
        CapabilityBranch -->|need_customer=True| CustTool[👥 CustomerAnalyticsTool]
        CapabilityBranch -->|need_knowledge=True| KnowledgeTool[📄 KnowledgeTool - ChromaDB RAG]
        CapabilityBranch -->|need_research=True| ResearchTool[🌐 ResearchTool - External Benchmarks]
    end

    subgraph Stage 3: Aggregation & Synthesis
        SalesTool -->|EvidenceItem| Aggregator[📦 EvidenceCollector]
        CustTool -->|EvidenceItem| Aggregator
        KnowledgeTool -->|EvidenceItem| Aggregator
        ResearchTool -->|EvidenceItem| Aggregator
        
        Aggregator -->|Normalized EvidencePackage| StratEngine[🎯 StrategyEngine]
        StratEngine -->|Structured Prompt| GroqLLM[⚡ Groq ChatGroq Llama 3.3 70B]
        GroqLLM -->|StrategicResponse Schema| StratEngine
    end

    StratEngine -->|Unified JSON Payload| API
    Supervisor -->|Chart Data Payload| API
    API -->|Divided Response & Recharts Payload| Frontend
```

### Component Responsibilities

| Component | Class / Module | Purpose |
| :--- | :--- | :--- |
| **Orchestrator** | `SupervisorAgent` | Holds component lifecycle; coordinates intent classification, planner execution, tool dispatch, and payload assembly. |
| **Intent Classifier** | `IntentClassifier` | Evaluates question semantics via Groq LLM structured output to categorize query into discrete intent types. |
| **Execution Planner** | `ExecutionPlanner` | Maps classified intent to boolean capability switches (`need_sales`, `need_customer`, `need_knowledge`, `need_research`). |
| **Sales Analytics Tool** | `SalesAnalyticsTool` | Invokes deterministic Pandas calculations over sales transactions to produce `trend_insights`. |
| **Customer Analytics Tool** | `CustomerAnalyticsTool` | Aggregates account status, CSAT scores, churn risk, and loyalty tiers to produce `customer_insights`. |
| **Knowledge Tool** | `KnowledgeTool` | Vector retrieval engine searching ChromaDB embeddings for PDF document text excerpts. |
| **Evidence Collector** | `EvidenceCollector` | Normalizes, deduplicates, and flattens multi-tool outputs into a validated `EvidencePackage`. |
| **Strategy Engine** | `StrategyEngine` | Invokes Groq LLM with structured output (`StrategicResponse`) to synthesize evidence-grounded answers. |

---

## 4. AI Pipeline

Every user query undergoes an end-to-end execution lifecycle:

```
1. User Question ➔ 2. Intent Classification ➔ 3. Tool Selection ➔ 4. Data Retrieval 
       ➔ 5. Evidence Normalization ➔ 6. Strategic Reasoning ➔ 7. Response Generation ➔ 8. Chart Rendering
```

1. **User Question**: User submits a natural language question via `/chat` or lands on `/`.
2. **Intent Classification**: `IntentClassifier` calls Groq LLM (`Llama 3.3 70B`) with `with_structured_output(IntentClassificationResult)` to identify question intent.
3. **Tool Selection**: `ExecutionPlanner` evaluates capability flags (`need_sales`, `need_customer`, `need_knowledge`, `need_research`).
4. **Data Retrieval**: Selected tools execute Pandas DataFrame operations or ChromaDB vector similarity queries.
5. **Evidence Normalization**: `EvidenceCollector` deduplicates items by composite key `(source, title)` and produces an `EvidencePackage`.
6. **Strategic Reasoning**: `StrategyEngine` reads pre-computed `trend_insights` and `customer_insights` as absolute sources of truth.
7. **Response Generation**: LLM generates a structured `StrategicResponse` divided into `answer`, `recommendation`, and `strategic_issues`.
8. **Chart Rendering**: `_extract_chart_data()` formats Recharts JSON payload for dynamic rendering in Next.js.

---

## 5. Intent Types

| Intent Category | Trigger Scenarios | Tool Capability Matrix Dispatched | Output Type |
| :--- | :--- | :--- | :--- |
| **`INTENT_KNOWLEDGE_DOC`** | Questions about HR policies, leave, travel rules, compliance, PDF documents. | `KnowledgeTool` ONLY | Synthesized Policy Answer + PDF Quote Inspector Card |
| **`INTENT_SALES_ANALYTICS`** | Queries on revenue, sales trends, categories, regional sales, top SKUs, deal sizes. | `SalesAnalyticsTool` ONLY | Direct Sales Fact + Line / Bar / Pie Recharts Chart |
| **`INTENT_CUSTOMER_HEALTH`** | Queries on churn rates, CSAT scores, account risk tiers, loyalty tiers, client spend. | `CustomerAnalyticsTool` (+ `ResearchTool` if benchmarks requested) | Customer Health Fact + Risk Bar / Tier Pie Chart |
| **`INTENT_MASTER_STRATEGY`** | Master prompt, turnaround strategy, full multi-domain executive assessment. | **All Tools Dispatched** (`Sales` + `Customer` + `Knowledge` + `Research`) | Full Strategic Transformation Playbook |

---

## 6. Analytics Engine

All business calculations are performed 100% deterministically in Python using Pandas. The LLM is **never** permitted to calculate numbers or estimate math.

### Primary Service Functions ([services/csv_service.py](file:///Users/shubham/Desktop/moduseti_assessment_backend/services/csv_service.py))

#### 1. `calculate_sales_metrics(df: pd.DataFrame)`
Calculates total revenue, profit margins, average deal sizes, category breakdowns, regional shares, and pre-computes deterministic **`trend_insights`**:
```python
{
  "total_revenue": 75213112.74,
  "total_profit": 15042622.55,
  "profit_margin_pct": 20.0,
  "average_deal_size": 75213.11,
  "trend_insights": {
    "highest_month": "2024-07",
    "highest_revenue": 7637324.95,
    "lowest_month": "2025-02",
    "lowest_revenue": 1506096.20,
    "average_monthly_revenue": 5785624.06,
    "overall_trend": "Fluctuating",
    "largest_increase_month": "2024-07",
    "largest_decrease_month": "2025-02"
  }
}
```

#### 2. `calculate_customer_metrics(df: pd.DataFrame)`
Calculates total accounts, active vs churned numbers, churn rate percentage, CSAT ratings, and pre-computes deterministic **`customer_insights`**:
```python
{
  "total_customers": 300,
  "churn_rate_pct": 26.0,
  "avg_customer_rating": 3.95,
  "customer_insights": {
    "benchmark_status": "Above Target",
    "customer_health": "Poor",
    "highest_risk_tier": "Low",
    "largest_customer_segment": "Online",
    "highest_spending_region": "North"
  }
}
```

#### 3. `query_sales_analytics(df, product, category, region, segment)`
Executes real-time slice-and-dice filter aggregations over sales transactions in memory.

---

## 7. Evidence Layer

The Evidence Layer provides an immutable data contract between tools and reasoning engines.

```
EvidenceItem (Single Fact Unit)
   ├── source: "Sales Analytics Tool" | "MODUS_HR_Policy_Manual_2026.pdf"
   ├── category: "Quantitative Metric" | "Document Excerpt"
   ├── title: "Executive Sales Performance Summary"
   ├── details: { total_revenue: ..., trend_insights: ... }
   └── confidence: "High (100% Deterministic Python Calculation)"

EvidencePackage (Aggregated Container)
   ├── question: "Show monthly revenue trend over time"
   └── items: list[EvidenceItem]
```

### Why Evidence Normalization Exists
- **Data Integrity**: Decouples how tools query data from how the LLM consumes facts.
- **Deduplication**: `EvidenceCollector` deduplicates items by composite key `(source, title)` to prevent context bloat.
- **Transport Safety**: `EvidencePackage` acts strictly as an immutable transport layer containing zero business logic.

---

## 8. Strategy Engine

`StrategyEngine` ([agents/strategy_engine.py](file:///Users/shubham/Desktop/moduseti_assessment_backend/agents/strategy_engine.py)) synthesizes executive responses using Groq LLM with `ChatGroq.with_structured_output(StrategicResponse)`.

### Grounded Source of Truth Rules
- **`trend_insights` Prioritization**: When present, `StrategyEngine` treats `trend_insights` as the absolute source of truth for revenue trends, summarizing highest/lowest months and overall trend without re-inferring raw arrays.
- **`customer_insights` Prioritization**: When present, `customer_insights` provides health status, benchmark compliance, and top spending territories.
- **Divided Output Contract (`StrategicResponse`)**:
  ```python
  class StrategicResponse(BaseModel):
      answer: str           # Direct factual natural language answer (always present)
      recommendation: str   # Actionable advice step (empty string if nothing to recommend)
      strategic_issues: list[str] # Strategic risks (empty list [] if factual query)
      business_impact: str  # Risk or ROI impact description
      priority: str         # Priority level badge (High, Medium, Notice)
      expected_outcome: str # Projected performance gain
  ```

---

## 9. Dynamic Visualization & Charts

MODUS dynamically renders interactive Recharts visualizers in Next.js based on the `chart_data` payload constructed by `SupervisorAgent._extract_chart_data()`.

```json
{
  "chart_type": "line",
  "title": "Monthly Revenue & Growth Trend",
  "data": [
    { "label": "2024-02", "value": 3910477.01 },
    { "label": "2024-03", "value": 6508879.04 },
    { "label": "2024-04", "value": 7334962.92 }
  ]
}
```

### Supported Chart Types
- 📈 **Area Line Chart**: Monthly revenue trends & growth velocity over time.
- 📊 **Bar Chart**: Category revenue breakdowns, loyalty tier account distribution, and CSAT benchmarks.
- 🍩 **Pie / Donut Chart**: Regional sales distribution and customer segment spend share.

---

## 10. Technology Stack

### Frontend
- **Framework**: Next.js 16 (App & Pages Router)
- **UI Library**: React 19, TypeScript
- **Styling**: Vanilla CSS Modules, Tailwind CSS, Sleek Dark Glassmorphism Design System
- **State & Query Management**: `@tanstack/react-query`
- **Visualizations**: Recharts
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI (Python 3.11)
- **ORM / Database**: SQLModel, PostgreSQL (Async / Session execution)
- **Data Processing**: Pandas, NumPy
- **Data Validation**: Pydantic v2

### AI & Vector RAG
- **Orchestration**: LangChain, LangChain Groq
- **LLM Engine**: Groq `llama-3.3-70b-versatile`
- **Vector Database**: ChromaDB
- **Embeddings**: HuggingFace All-MiniLM-L6-v2 / PyTorch
- **PDF Ingestion**: PyMuPDF / ReportLab

---

## 11. Project Structure

```
moduseti_assessment/
├── moduseti_assessment_backend/       # FastAPI Backend Application
│   ├── agents/                         # Agentic Orchestration Layer
│   │   ├── __init__.py
│   │   ├── intent_classifier.py        # Groq LLM Semantic Intent Classifier
│   │   ├── execution_planner.py        # Capability Scheduler & Execution Matrix
│   │   ├── supervisor_agent.py         # Master Supervisor DAG Orchestrator
│   │   └── strategy_engine.py          # Executive Reasoning & LLM Engine
│   ├── api/                            # FastAPI Route Controllers
│   │   ├── chat.py                     # POST /api/chat/ask Endpoint
│   │   ├── dashboard.py                # GET /metrics & POST /generate Endpoints
│   │   └── upload.py                   # POST /api/upload Dropzone Handler
│   ├── database/                       # Database Configurations
│   │   └── postgres.py                 # PostgreSQL Engine Connection
│   ├── models/                         # Pydantic & SQLModel Data Schemas
│   │   ├── db_models.py                # SQLModel DB Tables (SalesTransaction, CustomerRecord)
│   │   ├── evidence.py                 # EvidenceItem & EvidencePackage Contracts
│   │   └── strategy.py                 # StrategicResponse & StrategicIssue Schemas
│   ├── prompts/                        # System Prompt Definitions
│   │   └── system_prompts.py           # Master STRATEGY_ENGINE_SYSTEM_PROMPT
│   ├── services/                       # Core Business & Service Functions
│   │   ├── csv_service.py              # Deterministic Pandas Sales & Customer Analytics
│   │   ├── pdf_service.py              # PyMuPDF Chunking & ChromaDB Vector Store Ingestion
│   │   └── research_service.py         # External Industry Benchmark Retrieval
│   ├── tools/                          # Independent Tool Capabilities
│   │   ├── sales_tool.py               # Sales Analytics Tool
│   │   ├── customer_tool.py            # Customer Analytics Tool
│   │   ├── knowledge_tool.py           # PDF ChromaDB Vector RAG Tool
│   │   ├── research_tool.py            # External Research Benchmark Tool
│   │   └── evidence_collector.py       # Evidence Collector & Deduplicator
│   ├── main.py                         # FastAPI App Lifespan & CORS Configuration
│   ├── requirements.txt                # Python Dependencies Manifest
│   └── sales_transactions.csv          # Default Enterprise Sales Dataset
│
└── moduseti_assessment_frontend/      # Next.js Frontend Application
    ├── charts/                         # Dynamic Recharts Component Visualizers
    │   ├── DynamicChatChart.tsx        # Dynamic Area Line, Bar, Pie Chart Renderer
    │   ├── SalesKPICards.tsx           # Executive Sales Metric Cards
    │   └── CustomerKPICards.tsx        # Customer Health & Churn Risk Cards
    ├── components/                     # Shared UI Components
    │   ├── Navbar.tsx                  # Top Header & Navigation Bar
    │   └── StrategicRecommendationCard.tsx # Landing Strategic Playbook Card
    ├── pages/                          # Next.js Pages & Routes
    │   ├── index.tsx                   # Landing Executive Dashboard (/)
    │   ├── chat.tsx                    # Split-Screen Executive AI Chat (/chat)
    │   └── _app.tsx                    # App Provider Wrapper
    └── styles/                         # Global CSS & Custom Scrollbar Tokens
        └── globals.css
```

---

## 12. Installation & Setup

### Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: v18.0.0 or higher (`npm`)
- **Groq API Key**: Obtain a free API key from [Groq Console](https://console.groq.com/)

---

### Step 1: Clone Repository
```bash
git clone https://github.com/shubhamacharya77/moduseti_assessment_backend.git
cd moduseti_assessment_backend
```

### Step 2: Set Up Backend Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Create a `.env` file inside `moduseti_assessment_backend/`:
```bash
cp .env.example .env
```
Edit `.env` and add your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
POSTGRES_DB_URL=postgresql://postgres:postgres@localhost:5432/modus_db
```

### Step 4: Launch FastAPI Backend Server
```bash
uvicorn main:app --reload --port 8000
```
* backend running at: `http://localhost:8000`
* Swagger API docs at: `http://localhost:8000/docs`

---

### Step 5: Set Up Frontend Application
Open a new terminal window:
```bash
cd moduseti_assessment_frontend

# Install Node dependencies
npm install

# Launch Next.js dev server
npm run dev
```
* Frontend running at: `http://localhost:3000`
* Split-screen AI Chat running at: `http://localhost:3000/chat`

---

## 13. Environment Variables

| Variable Name | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `GROQ_API_KEY` | **Yes** | `""` | API key for Groq Llama 3.3 70B LLM reasoning & intent classification. |
| `POSTGRES_DB_URL` | No | `postgresql://...` | Optional PostgreSQL database URL for SQLModel persistence. |
| `MODEL_NAME` | No | `llama-3.3-70b-versatile` | Groq LLM model name. |

---

## 14. Real-World Example Queries

Try these queries in the **Executive AI Chat** (`/chat`):

### 📈 Sales & Revenue Analytics
- `"Show monthly revenue trend over time"`
- `"What is our product category revenue breakdown?"`
- `"Show regional revenue distribution"`
- `"What is our overall profit margin percentage and average deal size?"`

### 👥 Customer Health & Retention
- `"What is our customer churn risk vector analysis?"`
- `"Show customer spend distribution by segment"`
- `"What is the breakdown of accounts across loyalty tiers?"`
- `"What is our average customer satisfaction rating and feedback score?"`

### 📄 Corporate Document Policy RAG
- `"What is the policy for corporate travel and expense claims?"`
- `"Summarize our HR leave entitlement and vacation rules."`
- `"What are our corporate ethics and compliance guidelines?"`

### 🎯 Strategic Transformation
- `"What high-priority strategic transformation recommendations should we execute?"`
- `"How can we improve our gross profit margin and customer churn rate?"`

---

## 15. System Screenshots

| Interface Component | Placeholder / Description |
| :--- | :--- |
| **Executive Dashboard (`/`)** | ![Dashboard Placeholder](https://via.placeholder.com/800x450?text=Executive+Dashboard+Overview) |
| **Split-Screen AI Chat (`/chat`)** | ![Chat Interface Placeholder](https://via.placeholder.com/800x450?text=Split-Screen+AI+Chat+Interface) |
| **Dynamic Recharts Visualizer** | ![Charts Placeholder](https://via.placeholder.com/800x450?text=Dynamic+Recharts+Visualizer) |
| **PDF RAG Document Inspector** | ![RAG Inspector Placeholder](https://via.placeholder.com/800x450?text=PDF+Document+RAG+Inspector) |

---

## 16. Architecture & Design Decisions

1. **Why Intent Classification?**
   Evaluating user question intent up-front ensures that an HR policy query never triggers unnecessary sales database calculations or external benchmark queries.

2. **Why Selective Tool Execution?**
   Prevents context-window bloat, reduces execution time to milliseconds, and eliminates data pollution across domain boundaries.

3. **Why Deterministic Python Analytics?**
   LLMs are notoriously unreliable at arithmetic over thousands of rows. Performing aggregations in Pandas guarantees 100% accuracy.

4. **Why Evidence Packages?**
   Acts as a strict, verifiable contract between data tools and the LLM, enabling zero-hallucination strategy synthesis.

5. **Why Indian Rupee (`₹`) Formatting?**
   Ensures consistent financial formatting aligned with regional enterprise operations, avoiding currency symbol mismatches.

---

## 17. Future Enhancements

- 🔮 **Predictive Revenue Forecasting**: Integrating ARIMA / Prophet time-series models for predictive quarterly revenue projections.
- ⚡ **Streaming Token Responses**: Implementing Server-Sent Events (SSE) for word-by-word streaming in the chat interface.
- 🔐 **Role-Based Access Control (RBAC)**: Fine-grained authentication for C-suite vs Managerial data access.
- 🌐 **Multi-Tenant Workspace Isolation**: Dedicated ChromaDB collections and DB schemas per enterprise client.

---

## 18. License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

*Crafted with precision by the MODUS AI Engineering Team.*
