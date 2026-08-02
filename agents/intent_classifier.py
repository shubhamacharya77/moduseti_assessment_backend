import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq

IntentType = Literal[
    "INTENT_KNOWLEDGE_DOC",
    "INTENT_SALES_ANALYTICS",
    "INTENT_CUSTOMER_HEALTH",
    "INTENT_MASTER_STRATEGY",
]


class IntentClassificationResult(BaseModel):
    """Structured LLM intent classification output schema."""

    intent: IntentType = Field(
        ...,
        description=(
            "Classified intent: INTENT_KNOWLEDGE_DOC (HR/PDF policy/documents), "
            "INTENT_SALES_ANALYTICS (revenue/sales/products/margin), "
            "INTENT_CUSTOMER_HEALTH (churn/CSAT/loyalty/accounts), or "
            "INTENT_MASTER_STRATEGY (master prompt/turnaround play)."
        ),
    )
    confidence: float = Field(
        default=0.95, description="Classification confidence score between 0.0 and 1.0"
    )
    reasoning: str = Field(
        ..., description="Brief 1-sentence reasoning for the classified intent"
    )


class IntentClassifier:
    """LLM-powered semantic intent classifier with fallback keyword heuristic."""

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")

    def _classify_keyword_fallback(self, question: str) -> IntentType:
        """Fast keyword heuristic fallback when LLM API is unconfigured or offline."""
        q = (question or "").lower().strip()

        # 1. Knowledge / PDF Document RAG queries
        doc_keywords = [
            "policy",
            "hr",
            "leave",
            "vacation",
            "travel",
            "reimbursement",
            "guideline",
            "conduct",
            "ethics",
            "compliance",
            "document",
            "pdf",
            "manual",
            "rule",
            "allowance",
            "handbook",
        ]
        if any(k in q for k in doc_keywords):
            return "INTENT_KNOWLEDGE_DOC"

        # 2. Sales Analytics queries
        sales_keywords = [
            "sales",
            "revenue",
            "product",
            "category",
            "sku",
            "margin",
            "profit",
            "transaction",
            "deal size",
            "units",
            "quarterly",
        ]
        if any(k in q for k in sales_keywords) and not any(
            k in q for k in ["churn", "customer", "csat", "retention"]
        ):
            return "INTENT_SALES_ANALYTICS"

        # 3. Customer Health & Retention queries
        customer_keywords = [
            "churn",
            "customer",
            "csat",
            "rating",
            "retention",
            "loyalty",
            "segment",
            "account",
            "attrition",
        ]
        if any(k in q for k in customer_keywords):
            return "INTENT_CUSTOMER_HEALTH"

        # 4. Fallback / Master Strategy queries
        return "INTENT_MASTER_STRATEGY"

    def classify(self, question: str) -> IntentType:
        """Classifies executive query into discrete intent category using Groq LLM with fallback heuristic."""
        if self.api_key and "your_" not in self.api_key.lower():
            try:
                llm = ChatGroq(
                    model_name=self.model_name,
                    groq_api_key=self.api_key,
                    temperature=0.0,
                )
                structured_llm = llm.with_structured_output(
                    IntentClassificationResult
                )

                prompt = (
                    f"Classify the following executive question into exactly one intent category:\n"
                    f"1. INTENT_KNOWLEDGE_DOC: Questions about HR policies, leave allowance, travel reimbursement, code of conduct, or company PDF documentation.\n"
                    f"2. INTENT_SALES_ANALYTICS: Questions about sales revenue, product category breakdown, regional sales, top SKUs, or profit margins.\n"
                    f"3. INTENT_CUSTOMER_HEALTH: Questions about customer churn rate, CSAT ratings, account risk levels, customer segments, or loyalty tiers.\n"
                    f"4. INTENT_MASTER_STRATEGY: High-level strategic transformation recommendations, Master Assessment Prompt, or multi-domain turnaround playbooks.\n\n"
                    f"EXECUTIVE QUESTION: \"{question}\""
                )

                res = structured_llm.invoke(prompt)
                if isinstance(res, IntentClassificationResult):
                    return res.intent
            except Exception:
                pass

        return self._classify_keyword_fallback(question)
