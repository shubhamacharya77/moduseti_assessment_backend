# Phase 6 Specification: Evidence Collector

## 🎯 End Goal
Build a centralized `EvidenceCollector` tool that aggregates raw evidence items produced by the Knowledge, Sales Analytics, Customer Analytics, and Research tools, normalizes and deduplicates them, validates compliance with strict Pydantic models, and builds a single unified `EvidencePackage`.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 6.1: Evidence Collector Engine Implementation
- File: `backend/tools/evidence/evidence_collector.py`
- Class `EvidenceCollector`:
  - Responsibility: Gather multi-source evidence outputs and assemble the final payload for LLM strategy reasoning.
  - Core Method: `collect_and_package(tool_outputs: list[list[EvidenceItem]], user_question: str) -> EvidencePackage`

### Sub-Phase 6.2: Normalization, Deduplication & Validation Pipeline
- Actions:
  1. Flatten multi-tool output arrays.
  2. Validate each item against `EvidenceItem` Pydantic schema:
     ```python
     class EvidenceItem(BaseModel):
         source: str
         category: str
         title: str
         details: dict | str
         confidence: str
     ```
  3. Remove exact duplicate evidence entries based on content hashing/title match.
  4. Construct immutable `EvidencePackage`:
     ```python
     class EvidencePackage(BaseModel):
         question: str
         items: list[EvidenceItem]
     ```

### Sub-Phase 6.3: Unit Testing & Package Verification
- File: `backend/tests/test_evidence_collector.py`
- Tests:
  - Validates schema rejection on corrupted tool inputs.
  - Verifies multi-tool aggregation preserves source tags.
  - Ensures clean JSON serialization ready for Groq LLM prompt ingestion.

---

## 🔍 Verification Criteria
1. Passing mock outputs from Knowledge, Sales, Customer, and Research tools into `EvidenceCollector` returns a valid `EvidencePackage`.
2. 100% of items in `EvidencePackage.items` conform to the Pydantic model.
3. The package contains complete traceability (`source`, `category`, `confidence`).
