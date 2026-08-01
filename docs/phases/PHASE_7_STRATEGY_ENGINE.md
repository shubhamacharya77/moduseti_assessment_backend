# Phase 7 Specification: Strategic Intelligence Engine & Supervisor Agent

## 🎯 End Goal
Build the core LLM strategic reasoning engine using the Groq API and a LangGraph Supervisor graph. The Supervisor analyzes user intent, routes execution to required tools, gathers evidence via the Evidence Collector, and feeds the Evidence Package into the Strategy Engine to generate evidence-grounded strategic transformation recommendations.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 7.1: Zero-Hallucination System Prompt Architecture
- File: `backend/prompts/strategy.py`
- System Prompt Constraints:
  - *"You are an Enterprise Strategy Intelligence Engine."*
  - *"You NEVER invent facts, metrics, or policy statements."*
  - *"You reason EXCLUSIVELY over the provided Evidence Package."*
  - *"Every recommendation must cite exact evidence sources."*
  - *"Output must strictly conform to the StrategicResponse JSON schema."*

### Sub-Phase 7.2: Strategy Engine Implementation
- File: `backend/agents/strategy_engine.py`
- Class `StrategicIntelligenceEngine`:
  - Uses `Groq` LLM client (`llama-3.3-70b-versatile` / fast reasoning model).
  - Input: `EvidencePackage` + Executive Question / Intent.
  - Output: Structured `StrategicResponse` Pydantic model:
    ```python
    class StrategicResponse(BaseModel):
        strategic_issues: list[str]
        evidence: list[str]
        business_impact: str
        recommendation: str
        priority: str          # "High (Immediate Quick-Win)", "Medium", "Long-term"
        expected_outcome: str
    ```

### Sub-Phase 7.3: LangGraph Supervisor Graph Orchestration
- File: `backend/agents/supervisor_agent.py`
- Class `SupervisorAgent`:
  - Implements a LangGraph `StateGraph`:
    1. **Intent Node**: Parses executive prompt/request.
    2. **Tool Routing Edge**: Selects required tools (`KnowledgeTool`, `SalesAnalyticsTool`, `CustomerAnalyticsTool`, `ResearchTool`).
    3. **Tool Execution Node**: Runs selected tools in parallel/sequence.
    4. **Collector Node**: Passes tool outputs to `EvidenceCollector`.
    5. **Strategy Node**: Invokes `StrategicIntelligenceEngine` with the assembled `EvidencePackage`.

### Sub-Phase 7.4: Strategy & Dashboard Generation Endpoint
- File: `backend/api/dashboard.py`
- Endpoint: `POST /api/dashboard/generate`
  - Invokes `SupervisorAgent` for complete strategic assessment.
  - Returns `StrategicResponse` + summary evidence package for executive rendering.

---

## 🔍 Verification Criteria
1. Sending a request to `POST /api/dashboard/generate` triggers the Supervisor DAG.
2. Tools execute, Evidence Collector builds package, and Strategy Engine generates a `StrategicResponse`.
3. Every recommendation contains direct source citations from the uploaded files & analytics.
4. Zero hallucinated metrics exist in the response.
