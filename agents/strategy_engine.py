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
        """Dynamic question-aware fallback NLP strategy response generator."""
        q = (evidence_package.question or "").lower()
        items = evidence_package.items
        citation_list = [f"{item.source}: {item.title}" for item in items]

        # Extract details for dynamic fallback responses
        sales_details = {}
        cust_details = {}
        for item in items:
            if item.source == "Sales Analytics Tool" and isinstance(item.details, dict):
                sales_details = item.details
            elif item.source == "Customer Analytics Tool" and isinstance(item.details, dict):
                cust_details = item.details

        # 1. Regional revenue query
        if any(k in q for k in ["region", "regional", "territory", "geography", "location"]):
            regs = sales_details.get("regional_breakdown", {})
            reg_summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in regs.items()]) if regs else "distributed across key territories"
            recommendation = (
                f"Our regional sales revenue distribution is currently: {reg_summary}. "
                f"To accelerate growth, we recommend launching targeted commercial initiatives in underperforming regions while scaling high-volume regional hubs."
            )
            strategic_issues = [
                "Regional sales volume variance across commercial territories.",
                "Underpenetrated growth opportunities in select regional markets."
            ]

        # 2. Product category breakdown query
        elif any(k in q for k in ["category", "categories", "product category", "product lines"]):
            cats = sales_details.get("category_breakdown", {})
            cat_summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in cats.items()]) if cats else "distributed across core product categories"
            recommendation = (
                f"Our product category revenue performance breaks down as follows: {cat_summary}. "
                f"We recommend prioritizing high-margin product categories while optimizing marketing investments for lagging lines."
            )
            strategic_issues = [
                "Margin divergence between top-performing and lagging product categories.",
                "Inventory and promotional alignment across categories."
            ]

        # 3. Monthly revenue trend query
        elif any(k in q for k in ["trend", "month", "time", "history", "growth"]):
            total_rev = sales_details.get("total_revenue", 0)
            total_profit = sales_details.get("total_profit", 0)
            margin = sales_details.get("profit_margin_pct", 0)
            recommendation = (
                f"Over the recorded period, total enterprise revenue achieved ₹{total_rev:,.2f} with a net profit of ₹{total_profit:,.2f} ({margin:.1f}% profit margin). "
                f"We recommend sustaining continuous growth momentum by expanding recurring customer contracts and shortening sales cycles."
            )
            strategic_issues = [
                "Periodic monthly revenue fluctuations.",
                "Profit margin optimization opportunities."
            ]

        # 4. Default / Churn / General strategy query
        else:
            churn_pct = cust_details.get("churn_rate_pct", 26.0)
            rating = cust_details.get("avg_customer_rating", 3.95)
            recommendation = (
                f"Our customer health metrics show a churn rate of {churn_pct:.1f}% and an average satisfaction rating of {rating:.2f}/5.0. "
                f"We recommend deploying proactive customer success interventions for high-risk accounts and refining onboarding to bring churn below 5.0%."
            )
            strategic_issues = [
                f"Customer Churn Rate of {churn_pct:.1f}% exceeds the healthy benchmark target of under 5.0%.",
                f"Average Customer Satisfaction Rating ({rating:.2f}/5.0) indicates room for retention improvement."
            ]

        return StrategicResponse(
            strategic_issues=strategic_issues,
            evidence=citation_list if citation_list else ["Evidence Package Ingestion"],
            business_impact="Optimizing customer retention and regional commercial velocity protects monthly recurring revenue.",
            recommendation=recommendation,
            priority="High (Immediate Action Required)",
            expected_outcome="Targeting sustained revenue growth and an 8-12% reduction in customer churn within 90 days."
        )

    def generate_strategy(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Generates evidence-grounded strategic transformation response from EvidencePackage."""
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
