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

    def route_and_execute(self, user_question: str) -> dict[str, Any]:
        """Routes execution across tools, packages evidence, and generates strategic recommendations.

        Args:
            user_question: Executive strategy prompt or inquiry.

        Returns:
            Dictionary payload containing question, evidence_package, and strategic_response.
        """
        question_lower = user_question.lower()
        tool_outputs: list[list[EvidenceItem]] = []

        # 1. Intent routing & tool dispatch
        # Always run Sales & Customer Analytics summaries for strategic context
        sales_items = self.sales_tool.get_summary_metrics()
        tool_outputs.append(sales_items)

        cust_items = self.customer_tool.get_summary_metrics()
        tool_outputs.append(cust_items)

        # Retrieve matching external research benchmarks
        benchmarks = self.research_tool.query(query_text=user_question)
        tool_outputs.append(benchmarks)

        # Retrieve relevant vector document chunks if RAG search is relevant
        rag_items = self.knowledge_tool.query(query_text=user_question, n_results=3)
        if rag_items:
            tool_outputs.append(rag_items)

        # 2. Package evidence via EvidenceCollector
        evidence_package: EvidencePackage = self.evidence_collector.collect_and_package(
            tool_outputs=tool_outputs,
            user_question=user_question
        )

        # 3. Generate strategic response via StrategyEngine
        strategic_response: StrategicResponse = self.strategy_engine.generate_strategy(evidence_package)

        return {
            "question": user_question,
            "evidence_package": evidence_package.model_dump(),
            "strategic_response": strategic_response.model_dump()
        }
