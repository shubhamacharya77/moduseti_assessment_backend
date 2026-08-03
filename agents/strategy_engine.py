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

    def _generate_empty_data_response(self) -> StrategicResponse:
        """Returns clean empty workspace response when no user data or documents exist."""
        return StrategicResponse(
            strategic_issues=[
                "No company sales, customer, or document data found in the workspace."
            ],
            evidence=["No Data Uploaded"],
            business_impact="No data available to calculate churn rate, revenue metrics, or business performance.",
            recommendation="Please upload your Sales CSV, Customer CSV, or corporate PDF documents using the dropzone above to generate strategic recommendations.",
            priority="Notice",
            expected_outcome="Upload operational data to generate automated AI strategy insights."
        )

    def _generate_data_driven_response(self, evidence_package: EvidencePackage) -> StrategicResponse:
        """Purely data-grounded strategy response generator operating exclusively on ingested metrics."""
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
            return self._generate_empty_data_response()

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

        trend_insights = sales_details.get("trend_insights", {})
        customer_insights = cust_details.get("customer_insights", {})

        issues = []
        if customer_insights:
            health = customer_insights.get("customer_health", "Good")
            status = customer_insights.get("benchmark_status", "Within Target")
            risk_tier = customer_insights.get("highest_risk_tier", "Low")
            if status == "Above Target" or health in ["Fair", "Poor"]:
                issues.append(f"Customer Health evaluated as {health} ({status}) with highest risk observed in {risk_tier} risk tier.")
        elif churn_rate > 5.0:
            issues.append(f"Customer Churn Rate of {churn_rate:.1f}% exceeds healthy benchmark threshold of 5.0%.")

        if profit_margin < 25.0 and profit_margin > 0:
            issues.append(f"Gross Profit Margin of {profit_margin:.1f}% indicates margin expansion opportunity toward 25.0% target.")
        if csat > 0 and csat < 4.2:
            issues.append(f"Average Customer Rating of {csat:.2f}/5.0 indicates room for retention improvement.")

        if not issues:
            issues = ["Operational performance metrics ingested and verified across active datasets."]

        # Formulate direct answer prioritizing trend_insights & customer_insights
        if trend_insights and any(k in q for k in ["trend", "month", "time", "history", "growth"]):
            high_m = trend_insights.get("highest_month", "N/A")
            high_r = trend_insights.get("highest_revenue", 0.0)
            low_m = trend_insights.get("lowest_month", "N/A")
            low_r = trend_insights.get("lowest_revenue", 0.0)
            avg_m = trend_insights.get("average_monthly_revenue", 0.0)
            overall = trend_insights.get("overall_trend", "Stable")
            inc_m = trend_insights.get("largest_increase_month", "N/A")
            dec_m = trend_insights.get("largest_decrease_month", "N/A")

            rec = (
                f"Sales Trend Analysis (Source of Truth): Overall trend is {overall}. "
                f"Peak revenue occurred in {high_m} (₹{high_r:,.2f}), lowest in {low_m} (₹{low_r:,.2f}). "
                f"Average monthly revenue is ₹{avg_m:,.2f}. "
                f"Largest single-month revenue increase was in {inc_m}, largest decrease in {dec_m}."
            )
        elif "region" in q or "territory" in q:
            regs = sales_details.get("regional_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in regs.items()]) if regs else "No regional data"
            top_reg = customer_insights.get("highest_spending_region", "N/A") if customer_insights else "N/A"
            rec = f"Regional sales revenue distribution: {summary}. Top spending region: {top_reg}."
        elif "category" in q or "product" in q:
            cats = sales_details.get("category_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in cats.items()]) if cats else "No category data"
            rec = f"Product category revenue breakdown: {summary}."
        else:
            c_health = customer_insights.get("customer_health", "Good") if customer_insights else "N/A"
            b_status = customer_insights.get("benchmark_status", "Within Target") if customer_insights else "N/A"
            rec = (
                f"Ingested metrics analysis: Total Revenue is ₹{total_rev:,.2f} across {total_cust:,} customers. "
                f"Customer health status is {c_health} ({b_status}) with a churn rate of {churn_rate:.1f}%."
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
        items = evidence_package.items
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

        # CRITICAL MANDATORY CHECK: If user has 0 sales, 0 customers, and 0 uploaded documents,
        # DO NOT call LLM or research benchmarks. Return clean empty workspace response!
        if total_rev == 0 and total_cust == 0 and not doc_chunks:
            return self._generate_empty_data_response()

        if not self.api_key or "your_" in self.api_key.lower():
            return self._generate_data_driven_response(evidence_package)

        try:
            llm = ChatGroq(
                model_name=self.model_name,
                groq_api_key=self.api_key,
                temperature=0.2,
            )
            structured_llm = llm.with_structured_output(StrategicResponse)

            prompt = f"""
{STRATEGY_ENGINE_SYSTEM_PROMPT}

## Executive Question
{evidence_package.question}

## Grounded Evidence Payload
{evidence_package.model_dump_json(indent=2)}

## CRITICAL INSTRUCTION: SOURCE OF TRUTH PRIORITIZATION
1. If `trend_insights` exists in `sales_details`:
   - Treat `trend_insights` as the ABSOLUTE SOURCE OF TRUTH for all revenue trend analysis.
   - Summarize its exact fields (`highest_month`, `highest_revenue`, `lowest_month`, `lowest_revenue`, `average_monthly_revenue`, `overall_trend`, `largest_increase_month`, `largest_decrease_month`).
   - Do NOT re-infer or recalculate trends from raw `monthly_revenue_trends`.
   - Do NOT ask the user to analyze the data.
   - Do NOT speculate or invent ungrounded trend explanations.

2. If `customer_insights` exists in `customer_details`:
   - Treat `customer_insights` as the ABSOLUTE SOURCE OF TRUTH for customer health.
   - Directly incorporate `benchmark_status`, `customer_health`, `highest_risk_tier`, `largest_customer_segment`, and `highest_spending_region` into the response.

## General Response Guidelines:
- If user requests analytics, trends, or metrics:
  * Summarize findings using `trend_insights` / `customer_insights`.
  * Do NOT provide recommendations unless explicitly requested.

- If user requests strategy or improvements:
  * Explain current situation using `trend_insights` / `customer_insights`.
  * Identify business issues supported by the evidence.
  * Recommend practical actions.

- If user requests company document info:
  * Answer strictly from retrieved document excerpts.
  * Quote policies where appropriate.

Never invent facts.
Never reference internal tool names.
Never mention missing data unless required.
Generate the StrategicResponse strictly grounded in evidence.
"""

            res = structured_llm.invoke(prompt)
            if isinstance(res, StrategicResponse):
                return res
            return self._generate_data_driven_response(evidence_package)
        except Exception:
            return self._generate_data_driven_response(evidence_package)
