# AI Transformation Strategy Intelligence Platform — Agent Rules

## 🎯 Rules the Coding Agent Must Follow

Every AI Agent working on this codebase MUST adhere strictly to the following rules:

---

## 1. Business Logic Ownership 🔒

1. **Deterministic Logic Belongs in Python**:
   - The LLM MUST NOT implement business rules, calculations, filtering, ranking, or data transformations.
   - All quantitative metrics (revenue growth, churn rates, CAC, LTV, CSAT) MUST be calculated deterministically in Python using `pandas`. Zero mathematical calculations by the LLM.
   - All document facts MUST be retrieved via semantic vector search in Chroma DB using the `KnowledgeTool`.

2. **LLM Cognitive Responsibility**:
   - The LLM is responsible ONLY for reasoning over collected evidence, summarization, and natural-language generation.
   - Prompts MUST NEVER contain business logic. Prompts should ONLY describe: task, context, available evidence, and required output schema.

3. **No Direct DB / File Access by LLM**:
   - The LLM is NEVER allowed to execute SQL queries directly against PostgreSQL.
   - The LLM is NEVER allowed to read or parse raw CSV files directly.
   - The LLM is NEVER allowed to read or search un-chunked raw PDFs directly.

4. **Evidence Triangulation & Grounding**:
   - The LLM acts EXCLUSIVELY as a reasoning engine over an `EvidencePackage` assembled by the `EvidenceCollector`.
   - Every claim, strategic recommendation, or chat response MUST cite specific items from the evidence package (`{source, category, title, details, confidence}`).

---

## 2. Tool Architecture & Single Responsibility 🛠️

1. **Single Responsibility & Independence**:
   - Every tool implements the `BaseTool` abstract interface.
   - Every tool MUST perform exactly one domain task and return structured output.
   - Tools MUST NEVER call other tools internally. Tool orchestration belongs ONLY to the Supervisor.

2. **Structured Error Handling**:
   - All tools MUST return structured errors.
   - NEVER raise raw exceptions to the API layer.
   - Failures MUST include: `error_type`, `user_friendly_message`, `debug_information`.

3. **Comprehensive Tool Execution Logging**:
   - Every tool execution MUST be logged.
   - Logs MUST include: `tool_name`, `execution_time` (ms), `success_or_failure` status, `input_summary`, `output_summary`.

4. **Strict Pydantic Schemas & Type Hints**:
   - All inputs, outputs, tool payloads, and API requests/responses MUST be validated using Pydantic `BaseModel` schemas.
   - 100% strict Python type hints on every function, method, and variable.

---

## 3. Codebase & Directory Discipline 📁

1. **No Unneeded Files/Folders**:
   - Do NOT create new files or folders unless explicitly required.
   - Reuse existing modules whenever appropriate.
   - Follow the established project structure strictly (`backend/api`, `backend/agents`, `backend/tools`, `backend/services`, `backend/database`, `backend/models`, `backend/prompts`).

---

## 4. Phase-Gated Workflow Protocol 📋

1. **Phase-by-Phase Execution**:
   - Development follows the Master Execution Roadmap (`docs/phases/`).
   - NEVER skip ahead to subsequent phases without completing the current phase.

2. **Step-by-Step Communication**:
   - **Before Phase Start**: Summarize explicitly **what we are going to do** in the phase.
   - **During Execution**: Write clean, modular, production-ready code.
   - **After Phase End**: Summarize explicitly **what we have done**, run tests/verification, and present debug status.

3. **Explicit Pause**:
   - After completing a phase, STOP and wait for the user's explicit signal (e.g. *"move to next phase"*) before proceeding.
