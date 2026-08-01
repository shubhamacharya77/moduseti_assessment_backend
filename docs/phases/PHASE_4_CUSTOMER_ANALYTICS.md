# Phase 4 Specification: Customer Analytics Engine & Customer Tool

## 🎯 End Goal
Build a quantitative Pandas analytics pipeline for Customer CSV datasets. The pipeline validates CSV schemas, computes customer metrics (churn rate, CAC, LTV, CSAT, support ticket volume, customer segment health), persists metrics to PostgreSQL, and exposes an independent `CustomerAnalyticsTool`.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 4.1: Customer CSV Schema Validation & Processing Service
- File: `backend/services/csv_service.py`
- Functions:
  - `validate_customer_csv(df: pd.DataFrame) -> bool`: Validates required columns (`CustomerID`, `SignupDate`, `ChurnStatus`, `MonthlySpend`, `CAC`, `SupportTickets`, `CSAT`).
  - `clean_customer_data(df: pd.DataFrame) -> pd.DataFrame`: Cleans nulls, standardizes boolean churn indicators, formats numeric spend.

### Sub-Phase 4.2: Pandas Quantitative Customer Analytics Engine
- File: `backend/services/csv_service.py`
- Calculations performed purely in Python (Zero LLM involvement):
  - Overall Churn Rate & Customer Attrition trends.
  - Average Customer Acquisition Cost (CAC) vs. Customer Lifetime Value (LTV).
  - LTV:CAC Ratio calculation.
  - Average Customer Satisfaction Score (CSAT) & Support Ticket Volume.
  - Identification of High-Risk Customer Segments (e.g. churn rate by tenure/spend tier).

### Sub-Phase 4.3: PostgreSQL Database Persistence
- File: `backend/models/db_models.py`
  - SQLAlchemy model `CustomerRecord`: Stores raw customer data.
  - SQLAlchemy model `CustomerAnalyticsSummary`: Stores computed customer metrics (churn rate, CAC, LTV, CSAT breakdown).
- File: `backend/services/csv_service.py`
  - Persists processed customer data and summary metrics into PostgreSQL.

### Sub-Phase 4.4: Customer Analytics Tool Implementation
- File: `backend/tools/customer_tool.py`
- Class `CustomerAnalyticsTool(BaseTool)`:
  - Input: Analytical query or metric request (e.g. `"churn_analysis"`, `"customer_health"`).
  - Action: Queries PostgreSQL customer summary tables / executes Pandas aggregations.
  - Output: Returns list of normalized `EvidenceItem` objects ONLY.
  - `EvidenceItem` format:
    - `source`: `"Customer Analytics Tool"`
    - `category`: `"Quantitative Metric"`
    - `title`: Metric title (e.g., `"Customer Retention & Churn Health"`)
    - `details`: `{"churn_rate_pct": float, "avg_cac": float, "avg_ltv": float, "ltv_cac_ratio": float, "avg_csat": float}`
    - `confidence`: `"High (100% Deterministic Python Calculation)"`

### Sub-Phase 4.5: Customer CSV Upload API Endpoint
- File: `backend/api/upload.py`
- Endpoint: `POST /api/upload/customer`
  - Accepts Customer CSV file.
  - Triggers validation, Pandas customer metrics calculation, and PostgreSQL storage.
  - Returns `{"status": "success", "total_customers": int, "churn_rate_pct": float}`.

---

## 🔍 Verification Criteria
1. Uploading Customer CSV via `POST /api/upload/customer` stores data cleanly in PostgreSQL.
2. Executing `CustomerAnalyticsTool.execute()` returns exact churn, CAC, LTV, and CSAT metrics.
3. Outputs are 100% deterministic numeric metrics wrapped in standard `EvidenceItem` objects.
