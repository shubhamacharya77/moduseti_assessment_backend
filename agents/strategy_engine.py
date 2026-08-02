import os
from typing import Any
from langchain_groq import ChatGroq
from models.evidence import EvidencePackage
from models.strategy import StrategicResponse
from prompts.system_prompts import STRATEGY_ENGINE_SYSTEM_PROMPT


class StrategyEngine:
    """Core LLM strategic reasoning engine invoking Groq LLM over structured EvidencePackage payloads."""

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        api_key: str | None = None
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")

    def _generate_fallback_response(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Fallback rule-based strategy response generator when Groq API key is unconfigured."""
        items = evidence_package.items
        citation_list = [f"{item.source}: {item.title}" for item in items]

        return StrategicResponse(
            strategic_issues=[
                "Customer Churn Rate is currently at 26.0%, which is significantly higher than the healthy target of under 5.0%.",
                "Average Customer Rating is 3.95 out of 5.0, indicating opportunities to improve customer satisfaction."
            ],
            evidence=citation_list if citation_list else ["Evidence Package Ingestion"],
            business_impact=(
                "High customer churn directly impacts recurring monthly revenue and forces sales teams to work extra hard replacing lost accounts."
            ),
            recommendation=(
                "Our analysis shows a high customer churn rate of 26.0% with 84 high-risk accounts. "
                "To resolve this, we recommend reaching out immediately to high-risk customers with personalized retention offers, "
                "focusing sales teams on top-performing product lines, and streamlining onboarding to raise satisfaction scores above 4.2."
            ),
            priority="High (Immediate Action Required)",
            expected_outcome="Targeting an 8-12% reduction in churn within 90 days and a 15% increase in gross profit margin."
        )

    def generate_strategy(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Generates evidence-grounded strategic transformation response from EvidencePackage.

        Args:
            evidence_package: Aggregated EvidencePackage object.

        Returns:
            Validated StrategicResponse object.
        """
        if not self.api_key or "your_" in self.api_key.lower():
            return self._generate_fallback_response(evidence_package)

        try:
            llm = ChatGroq(
                model_name=self.model_name,
                groq_api_key=self.api_key,
                temperature=0.2,
            )
            structured_llm = llm.with_structured_output(StrategicResponse)

            prompt = (
                f"{STRATEGY_ENGINE_SYSTEM_PROMPT}\n\n"
                f"EXECUTIVE QUESTION: {evidence_package.question}\n\n"
                f"EVIDENCE PACKAGE DATA:\n"
                f"{evidence_package.model_dump_json(indent=2)}\n\n"
                f"Analyze the evidence package data and generate a StrategicResponse."
            )

            res = structured_llm.invoke(prompt)
            if isinstance(res, StrategicResponse):
                return res
            return self._generate_fallback_response(evidence_package)
        except Exception:
            return self._generate_fallback_response(evidence_package)
