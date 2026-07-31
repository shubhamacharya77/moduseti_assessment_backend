# Phase 9 Specification: Grounded AI Executive Chat & End-to-End Verification

## 🎯 End Goal
Build an interactive Grounded Executive Chat component enabling CEOs to ask follow-up questions about their organization, receiving sub-second Groq-powered answers with interactive evidence citation pills. Conduct complete end-to-end system testing and verification.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 9.1: Executive Chat Backend Endpoint
- File: `backend/api/chat.py`
- Endpoint: `POST /api/chat`
  - Accepts user question string + session ID.
  - Invokes `SupervisorAgent`:
    - Determines intent & selects required tools.
    - Assembles targeted `EvidencePackage`.
    - Invokes `StrategicIntelligenceEngine` on Groq.
  - Returns answer string + list of cited `EvidenceItem` objects.

### Sub-Phase 9.2: Grounded Chat Frontend Interface
- Path: `moduseti assissment_frontend/chat/`
- Components:
  - `ExecutiveChatDrawer.tsx` / `ChatPanel.tsx`: Collapsible or dedicated chat view.
  - `ChatMessage.tsx`: Displays executive question and grounded AI response with markdown formatting.
  - `CitationBadge.tsx`: Interactive pill rendered for every cited source (e.g. `[Source: Sales Analytics Tool]`, `[Source: HR_Policy_2025.pdf (Sec 4.2)]`). Clicking opens evidence popup modal.

### Sub-Phase 9.3: System End-to-End Testing & Verification
- Full End-to-End Operational Checklist:
  1. **Upload Flow**: Upload Company Profile PDF, HR Policy PDF, Sales CSV, Customer CSV.
  2. **Analytics Ingestion**: Verify Pandas parses CSVs and Chroma embeds PDFs.
  3. **Dashboard Synthesis**: Verify Supervisor routes tools, Evidence Collector builds package, Strategy Engine outputs evidence-grounded recommendations.
  4. **Executive Visuals**: Verify Recharts display exact revenue and churn numbers.
  5. **Grounded Q&A**: Ask follow-up executive questions in chat; verify answers cite underlying evidence with zero hallucination.

---

## 🔍 Verification Criteria
1. Chat endpoint responds within 1-2 seconds (powered by Groq).
2. Every answer includes interactive source citation pills.
3. Full system fulfills the core success criteria:
   > *"What should this organization transform, why, what evidence supports it, and what should be done first?"*
