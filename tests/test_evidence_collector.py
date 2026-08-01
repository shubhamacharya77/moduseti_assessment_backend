from models.evidence import EvidenceItem, EvidencePackage
from tools.customer_tool import CustomerAnalyticsTool
from tools.evidence_collector import EvidenceCollector
from tools.research_tool import ResearchTool
from tools.sales_tool import SalesAnalyticsTool


def test_evidence_collector_aggregation():
    """Verifies that EvidenceCollector aggregates items from multiple domain tools correctly."""
    collector = EvidenceCollector()
    sales_tool = SalesAnalyticsTool()
    cust_tool = CustomerAnalyticsTool()
    research_tool = ResearchTool()

    sales_items = sales_tool.get_summary_metrics()
    cust_items = cust_tool.get_summary_metrics()
    research_items = research_tool.query(query_text="churn")

    pkg = collector.collect_and_package(
        tool_outputs=[sales_items, cust_items, research_items],
        user_question="How can we optimize revenue and customer retention?"
    )

    assert isinstance(pkg, EvidencePackage)
    assert pkg.question == "How can we optimize revenue and customer retention?"
    assert len(pkg.items) > 0
    assert any("Sales" in item.source for item in pkg.items)
    assert any("Customer" in item.source for item in pkg.items)


def test_evidence_collector_deduplication():
    """Verifies that EvidenceCollector deduplicates identical items based on source & title."""
    collector = EvidenceCollector()
    dummy_item = EvidenceItem(
        source="Test Source",
        category="Test Category",
        title="Test Metric Title",
        details={"val": 100},
        confidence="High"
    )

    pkg = collector.collect_and_package(
        tool_outputs=[[dummy_item], [dummy_item], [dummy_item]],
        user_question="Test Question"
    )

    assert len(pkg.items) == 1
    assert pkg.items[0].title == "Test Metric Title"


def test_evidence_package_json_serialization():
    """Verifies that EvidencePackage serializes cleanly to JSON for Groq LLM prompt consumption."""
    collector = EvidenceCollector()
    dummy_item = EvidenceItem(
        source="Test Source",
        category="Test Category",
        title="Test Metric Title",
        details={"metric": 42.0},
        confidence="High"
    )

    pkg = collector.collect_and_package(
        tool_outputs=[[dummy_item]],
        user_question="JSON Serialization Test"
    )

    json_str = pkg.model_dump_json()
    assert "JSON Serialization Test" in json_str
    assert "Test Metric Title" in json_str
