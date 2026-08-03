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
            combined_docs = "\n\n".join(doc_chunks)
            return StrategicResponse(
                answer=f"Based on ingested company documentation:\n{combined_docs}",
                strategic_issues=[],
                evidence=citation_list,
                business_impact="Document guidelines provide operational policy clarity for corporate execution.",
                recommendation="",
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
        # Include issues ONLY if asking for strategy/improvements or if severe risk exists
        if any(k in q for k in ["strategy", "improve", "action", "recommend", "risk", "issue"]):
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

        # Formulate direct answer prioritizing trend_insights & customer_insights
        recommendation_step = ""
        if any(k in q for k in ["strategy", "improve", "action", "recommend", "how can we"]):
            if profit_margin < 25.0 and profit_margin > 0:
                recommendation_step = "Focus sales rep incentives on high-margin product categories to expand gross margin toward 25.0% target."
            elif churn_rate > 5.0:
                recommendation_step = "Deploy proactive customer success interventions for High risk tier accounts to lower annual churn rate."
            else:
                recommendation_step = "Optimize regional distribution channels to accelerate market penetration in top-performing regions."

        if trend_insights and any(k in q for k in ["trend", "month", "time", "history", "growth"]):
            high_m = trend_insights.get("highest_month", "N/A")
            high_r = trend_insights.get("highest_revenue", 0.0)
            low_m = trend_insights.get("lowest_month", "N/A")
            low_r = trend_insights.get("lowest_revenue", 0.0)
            avg_m = trend_insights.get("average_monthly_revenue", 0.0)
            overall = trend_insights.get("overall_trend", "Stable")
            inc_m = trend_insights.get("largest_increase_month", "N/A")
            dec_m = trend_insights.get("largest_decrease_month", "N/A")

            ans = (
                f"Sales Trend Analysis: Overall trend is {overall}. "
                f"Peak revenue occurred in {high_m} (₹{high_r:,.2f}), lowest in {low_m} (₹{low_r:,.2f}). "
                f"Average monthly revenue is ₹{avg_m:,.2f}. "
                f"Largest single-month revenue increase was in {inc_m}, largest decrease in {dec_m}."
            )
        elif "region" in q or "territory" in q:
            regs = sales_details.get("regional_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in regs.items()]) if regs else "No regional data"
            top_reg = customer_insights.get("highest_spending_region", "N/A") if customer_insights else "N/A"
            ans = f"Regional sales revenue breakdown: {summary}. Top spending region is {top_reg}."
        elif "segment" in q:
            segs = sales_details.get("segment_breakdown", {}) or cust_details.get("segment_breakdown", {})
            if isinstance(segs, dict):
                summary_items = []
                for k, v in segs.items():
                    val = v.get("total_spend", v) if isinstance(v, dict) else v
                    summary_items.append(f"{k}: ₹{val:,.2f}" if isinstance(val, (int, float)) else f"{k}: {val}")
                summary = ", ".join(summary_items)
            else:
                summary = "No segment data"
            top_seg = customer_insights.get("largest_customer_segment", "N/A") if customer_insights else "N/A"
            ans = f"Customer segment spend breakdown: {summary}. Largest customer segment is {top_seg}."
        elif "loyalty" in q or "tier" in q or "platinum" in q or "gold" in q or "silver" in q:
            tiers = cust_details.get("loyalty_tier_breakdown", {})
            summary = ", ".join([f"{k}: {v:,} accounts" for k, v in tiers.items()]) if tiers else "No loyalty tier data"
            ans = f"Loyalty tier account distribution: {summary}."
        elif "csat" in q or "rating" in q or "satisfaction" in q or "feedback" in q:
            ans = f"Our average customer satisfaction rating is {csat:.2f} out of 5.0 across {total_cust:,} total customer accounts."
        elif "deal" in q or "margin" in q:
            deal_size = sales_details.get("average_deal_size", 0.0)
            ans = f"Our overall profit margin percentage is {profit_margin:.1f}% and the average deal size is ₹{deal_size:,.2f}."
        elif "category" in q or "product" in q:
            cats = sales_details.get("category_breakdown", {})
            summary = ", ".join([f"{k}: ₹{v:,.2f}" for k, v in cats.items()]) if cats else "No category data"
            ans = f"Product category revenue breakdown: {summary}."
        else:
            c_health = customer_insights.get("customer_health", "Good") if customer_insights else "N/A"
            b_status = customer_insights.get("benchmark_status", "Within Target") if customer_insights else "N/A"
            ans = (
                f"Ingested metrics summary: Total Revenue is ₹{total_rev:,.2f} across {total_cust:,} customers. "
                f"Customer health status is {c_health} ({b_status}) with a churn rate of {churn_rate:.1f}%."
            )

        return StrategicResponse(
            answer=ans,
            strategic_issues=issues,
            evidence=citation_list,
            business_impact="Optimizing retention and sales efficiency protects recurring revenue.",
            recommendation=recommendation_step,
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
                temperature=0.1,
            )
            structured_llm = llm.with_structured_output(StrategicResponse)

            prompt = f"""
{STRATEGY_ENGINE_SYSTEM_PROMPT}

## Executive Question
{evidence_package.question}

## Grounded Evidence Payload
{evidence_package.model_dump_json(indent=2)}

## DIVIDED RESPONSE INSTRUCTIONS:
1. `answer`: Direct factual natural language summary answering the question directly with exact figures (e.g. "Our overall profit margin percentage is 20.0% and average deal size is ₹75,213.11."). Format ALL currency using Indian Rupee `₹`.
   - For PDF document / company policy queries: Synthesize a complete, professional natural language answer from the retrieved excerpts. NEVER truncate text mid-sentence or mid-word.
2. `recommendation`: Actionable advice. If there is a genuine, valuable recommendation step, provide it here. IF THERE IS NOTHING MEANINGFUL TO RECOMMEND FOR THIS QUERY, RETURN AN EMPTY STRING `""`. DO NOT FORCE FAKE OR PREACHY ADVICE.
3. `strategic_issues`: List of core operational risks or bottlenecks. FOR PDF DOCUMENT POLICY QUERIES OR FACTUAL METRIC QUERIES, RETURN AN EMPTY ARRAY `[]`.

Generate the StrategicResponse strictly grounded in evidence.
"""

            res = structured_llm.invoke(prompt)
            if isinstance(res, StrategicResponse):
                # Ensure answer fallback if LLM populated recommendation into answer
                if not res.answer and res.recommendation:
                    res.answer = res.recommendation
                    res.recommendation = ""
                return res
            return self._generate_data_driven_response(evidence_package)
        except Exception:
            return self._generate_data_driven_response(evidence_package)
