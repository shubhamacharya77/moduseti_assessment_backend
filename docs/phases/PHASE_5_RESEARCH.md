# Phase 5 Specification: External Industry Research Tool

## 🎯 End Goal
Build an independent `ResearchTool` that retrieves industry benchmarks, market trends, competitive metrics, and AI transformation best practices for the enterprise's industry sector, returning normalized `EvidenceItem` objects.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 5.1: Research Service & Benchmark Data Engine
- File: `backend/services/research_service.py`
- Functions:
  - `fetch_industry_benchmarks(industry_sector: str) -> list[dict]`: Retrieves curated industry standards (e.g. SaaS churn benchmarks, sales commission standards, HR retention benchmarks from Gartner/McKinsey models).
  - Integrates external web search/API wrapper if live search credentials are provided, or curated domain-specific benchmark dataset.

### Sub-Phase 5.2: Research Tool Implementation
- File: `backend/tools/research/research_tool.py`
- Class `ResearchTool(BaseTool)`:
  - Input: Query string or industry category (e.g., `"SaaS sales compensation benchmarks"`).
  - Action: Queries research benchmark engine for matching market data and strategic best practices.
  - Output: Returns list of normalized `EvidenceItem` objects ONLY.
  - `EvidenceItem` format:
    - `source`: `"Research Tool (" + benchmark_source + ")"`
    - `category`: `"Industry Benchmark"`
    - `title`: Benchmark title (e.g., `"Enterprise Sales Compensation Standard 2025"`)
    - `details`: `{"benchmark_metric": str, "industry_standard_value": str, "market_insight": str}`
    - `confidence`: `"Medium-High (External Research Benchmark)"`

---

## 🔍 Verification Criteria
1. Calling `ResearchTool.execute(query="sales incentive benchmarks")` returns structured benchmark evidence objects.
2. Returned evidence adheres to the exact `{source, category, title, details, confidence}` schema.
3. Tool provides clean market context to evaluate internal company performance against industry standards.
