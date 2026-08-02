from typing import Any
from agents.strategy_engine import StrategyEngine
from models.evidence import EvidenceItem, EvidencePackage
from models.strategy import StrategicResponse
from tools import (
    CustomerAnalyticsTool,
    EvidenceCollector,
    KnowledgeTool,
    ResearchTool,
    SalesAnalyticsTool,
)


class SupervisorAgent:
    """Stateful Supervisor agent coordinating intent routing, tool execution, evidence collection, and strategic reasoning."""

    def __init__(self):
        self.knowledge_tool = KnowledgeTool()
        self.sales_tool = SalesAnalyticsTool()
        self.customer_tool = CustomerAnalyticsTool()
        self.research_tool = ResearchTool()
        self.evidence_collector = EvidenceCollector()
        self.strategy_engine = StrategyEngine()

    def _extract_chart_data(
        self, user_question: str, sales_details: dict[str, Any], customer_details: dict[str, Any]
    ) -> dict[str, Any] | None:
        q = user_question.lower()

        # 1. Monthly revenue trend (Line/Area)
        if any(k in q for k in ["trend", "month", "time", "over time", "history", "growth"]):
            trends = sales_details.get("monthly_revenue_trends", {})
            if trends:
                return {
                    "chart_type": "line",
                    "title": "Monthly Revenue & Growth Trend",
                    "data": [{"label": k, "value": v} for k, v in trends.items()],
                }

        # 2. Product Category breakdown (Bar)
        if any(k in q for k in ["category", "categories", "product category", "product lines"]):
            cats = sales_details.get("category_breakdown", {})
            if cats:
                return {
                    "chart_type": "bar",
                    "title": "Product Category Revenue Breakdown",
                    "data": [{"label": k, "value": v} for k, v in cats.items()],
                }

        # 3. Regional breakdown (Pie/Donut)
        if any(k in q for k in ["region", "regional", "territory", "geography", "location"]):
            regs = sales_details.get("regional_breakdown", {})
            if regs:
                return {
                    "chart_type": "pie",
                    "title": "Regional Revenue Distribution",
                    "data": [{"label": k, "value": v} for k, v in regs.items()],
                }

        # 4. Churn Risk breakdown (Bar)
        if any(k in q for k in ["churn", "risk", "retention", "attrition", "customer loss"]):
            churns = customer_details.get("churn_risk_breakdown", {})
            if churns:
                return {
                    "chart_type": "bar",
                    "title": "Customer Churn Risk Vector Analysis",
                    "data": [{"label": k, "value": v} for k, v in churns.items()],
                }

        # 5. Customer Segment breakdown (Pie)
        if any(k in q for k in ["segment", "customer segment", "enterprise", "smb"]):
            segs = customer_details.get("segment_breakdown", {})
            if segs:
                formatted = []
                for k, v in segs.items():
                    val = v.get("total_spend", 0) if isinstance(v, dict) else v
                    formatted.append({"label": k, "value": val})
                return {
                    "chart_type": "pie",
                    "title": "Customer Segment Spend Share",
                    "data": formatted,
                }

        # 6. Product breakdown (Bar)
        if any(k in q for k in ["product", "sku", "item", "top selling"]):
            prods = sales_details.get("product_breakdown", {})
            if prods:
                return {
                    "chart_type": "bar",
                    "title": "Top Product Revenue Ranking",
                    "data": [{"label": k, "value": v} for k, v in list(prods.items())[:6]],
                }

        # Default fallback for general sales/revenue/profit queries
        if any(k in q for k in ["sales", "revenue", "profit"]):
            cats = sales_details.get("category_breakdown", {})
            if cats:
                return {
                    "chart_type": "bar",
                    "title": "Product Category Revenue Breakdown",
                    "data": [{"label": k, "value": v} for k, v in cats.items()],
                }

        return None

    def route_and_execute(self, user_question: str) -> dict[str, Any]:
        """Routes execution across tools, packages evidence, and generates strategic recommendations."""
        tool_outputs: list[list[EvidenceItem]] = []

        # 1. Intent routing & tool dispatch
        sales_items = self.sales_tool.get_summary_metrics()
        tool_outputs.append(sales_items)

        cust_items = self.customer_tool.get_summary_metrics()
        tool_outputs.append(cust_items)

        benchmarks = self.research_tool.query(query_text=user_question)
        tool_outputs.append(benchmarks)

        rag_items = self.knowledge_tool.query(query_text=user_question, n_results=3)
        if rag_items:
            tool_outputs.append(rag_items)

        # Extract details for chart data generation
        sales_details = sales_items[0].details if sales_items else {}
        customer_details = cust_items[0].details if cust_items else {}

        chart_data = self._extract_chart_data(
            user_question=user_question,
            sales_details=sales_details,
            customer_details=customer_details,
        )

        # 2. Package evidence via EvidenceCollector
        evidence_package: EvidencePackage = self.evidence_collector.collect_and_package(
            tool_outputs=tool_outputs, user_question=user_question
        )

        # 3. Generate strategic response via StrategyEngine
        strategic_response: StrategicResponse = self.strategy_engine.generate_strategy(
            evidence_package
        )

        return {
            "question": user_question,
            "evidence_package": evidence_package.model_dump(),
            "strategic_response": strategic_response.model_dump(),
            "chart_data": chart_data,
        }
