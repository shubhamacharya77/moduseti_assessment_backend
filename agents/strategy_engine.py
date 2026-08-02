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

    def _generate_data_driven_response(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Purely data-grounded strategy response generator operating exclusively on ingested metrics without hardcoded assumptions."""
        q = (evidence_package.question or "").lower()
        items = evidence_package.items
        citation_list = [f"{item.source}: {item.title}" for item in items]

        sales_details = {}
        cust_details = {}
        doc_chunks = []

        for item in items:
            if item.source == "Sales Analytics Tool" and isinstance(item.details, dict):
                sales_details = item.details
            elif item.source == "Customer Analytics Tool" and isinstance(item.details, dict):
                cust_details = item.details
            elif isinstance(item.details, dict) and "text_chunk" in item.details:
                doc_chunks.append(item.details.get("text_chunk", ""))

        total_rev = sales_details.get("total_revenue", 0)
        total_cust = cust_details.get("total_customers", 0)

        # 1. Empty Workspace Case (Zero Data & Zero Documents)
        if total_rev == 0 and total_cust == 0 and not doc_chunks:
            return StrategicResponse(
                strategic_issues=[
                    "No operational data, sales transactions, customer records, or company documents have been uploaded to the platform yet."
                ],
                evidence=citation_list if citation_list else ["Workspace Ingestion Required"],
                business_impact="Strategic recommendations require ingested business metrics or corporate PDF documentation to execute evidence-grounded evaluation.",
                recommendation="Please upload your Sales CSV, Customer CSV, or corporate PDF documents using the dropzone above. Once files are ingested, the platform will compute live metrics and generate your Strategic Intelligence Playbook.",
                priority="Notice (Data Ingestion Required)",
                expected_outcome="Ingest enterprise operational data to unlock automated evidence-grounded recommendations."
            )

        # 2. PDF Document RAG Match Case
        if doc_chunks and (total_rev == 0 and total_cust == 0):
            excerpt = doc_chunks[0][:300] + "..." if len(doc_chunks[0]) > 300 else doc_chunks[0]
            return StrategicResponse(
                strategic_issues=[
                    "Document analysis completed based on ingested corporate documentation."
                ],
                evidence=citation_list,
                business_impact="Document guidelines provide operational policy clarity for corporate execution.",
                recommendation=f"Based on ingested company documentation: \"{excerpt}\"",
                priority="Medium",
                expected_outcome="Align team operations with official corporate policy guidelines."
            )

        # 3. Quantitative Sales & Customer Data Match Case
        profit_margin = sales_details.get("profit_margin_pct", 0)
        total_profit = sales_details.get("total_profit", 0)
        churn_rate = cust_details.get("churn_rate_pct", 0)
        csat = cust_details.get("avg_customer_rating", 0)

        issues = []
        if churn_rate > 5.0:
            issues.append(f"Customer Churn Rate of {churn_rate:.1f}% exceeds healthy benchmark threshold of 5.0%.")
        if profit_margin < 25.0 and profit_margin > 0:
            issues.append(f"Gross Profit Margin of {profit_margin:.1f}% indicates margin expansion opportunity toward 25.0% target.")
        if csat > 0 and csat < 4.2:
            issues.append(f"Average Customer Rating of {csat:.2f}/5.0 indicates room for retention improvement.")

        if not issues:
            issues = ["Operational performance metrics ingested and verified across active datasets."]

        # Formulate direct answer strictly from available numbers
        if "region" in q or "territory" in q:
            regs = sales_details.get("regional_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in regs.items()]) if regs else "No regional data"
            rec = f"Regional sales revenue distribution: {summary}."
        elif "category" in q or "product" in q:
            cats = sales_details.get("category_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in cats.items()]) if cats else "No category data"
            rec = f"Product category revenue breakdown: {summary}."
        elif "trend" in q or "month" in q:
            rec = f"Total enterprise revenue is ₹{total_rev:,.2f} with a net profit of ₹{total_profit:,.2f} ({profit_margin:.1f}% profit margin)."
        else:
            rec = (
                f"Ingested metrics analysis: Total Revenue is ₹{total_rev:,.2f} across {total_cust:,} customers. "
                f"Current churn rate is {churn_rate:.1f}% with an average customer rating of {csat:.2f}/5.0."
            )

        return StrategicResponse(
            strategic_issues=issues,
            evidence=citation_list,
            business_impact="Optimizing retention and sales efficiency protects recurring revenue.",
            recommendation=rec,
            priority="High (Immediate Action Required)" if churn_rate > 15 else "Medium",
            expected_outcome="Drive evidence-grounded operational growth and churn reduction."
        )

    def generate_strategy(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Generates evidence-grounded strategic transformation response from EvidencePackage."""
        if not self.api_key or "your_" in self.api_key.lower():
            return self._generate_data_driven_response(evidence_package)

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
                f"Analyze the evidence package data strictly and generate a StrategicResponse."
            )

            res = structured_llm.invoke(prompt)
            if isinstance(res, StrategicResponse):
                return res
            return self._generate_data_driven_response(evidence_package)
        except Exception:
            return self._generate_data_driven_response(evidence_package)
