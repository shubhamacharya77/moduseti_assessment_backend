from typing import Any
from pydantic import BaseModel, Field
from agents.intent_classifier import IntentType


class ExecutionPlan(BaseModel):
    """Structured plan specifying which capabilities and tools to dispatch."""

    intent: IntentType
    need_sales: bool = False
    need_customer: bool = False
    need_knowledge: bool = False
    need_research: bool = False
    generate_chart: bool = False
    description: str = Field(..., description="Human-readable summary of planned tool execution branch")


class ExecutionPlanner:
    """Decides capability requirement matrix and plans tool dispatch branch based on classified intent."""

    def plan(self, intent: IntentType, question: str) -> ExecutionPlan:
        q = (question or "").lower()

        if intent == "INTENT_KNOWLEDGE_DOC":
            return ExecutionPlan(
                intent=intent,
                need_sales=False,
                need_customer=False,
                need_knowledge=True,
                need_research=False,
                generate_chart=False,
                description="Targeted RAG execution: Dispatching KnowledgeTool (ChromaDB PDF Vector Store) only.",
            )

        if intent == "INTENT_SALES_ANALYTICS":
            return ExecutionPlan(
                intent=intent,
                need_sales=True,
                need_customer=False,
                need_knowledge=False,
                need_research=False,
                generate_chart=True,
                description="Targeted Sales execution: Dispatching SalesAnalyticsTool and generating dynamic Recharts payload.",
            )

        if intent == "INTENT_CUSTOMER_HEALTH":
            # Include research benchmarks if asking about benchmarks or strategy
            need_res = any(k in q for k in ["benchmark", "target", "industry", "gartner"])
            return ExecutionPlan(
                intent=intent,
                need_sales=False,
                need_customer=True,
                need_knowledge=False,
                need_research=need_res,
                generate_chart=True,
                description="Targeted Customer execution: Dispatching CustomerAnalyticsTool and generating churn risk visualization.",
            )

        # INTENT_MASTER_STRATEGY: Multi-Modal DAG Dispatch
        return ExecutionPlan(
            intent=intent,
            need_sales=True,
            need_customer=True,
            need_knowledge=True,
            need_research=True,
            generate_chart=True,
            description="Multi-Modal Strategy execution: Dispatching Sales, Customer, Knowledge RAG, and Industry Research tools.",
        )
