from typing import Any
from models.evidence import EvidenceItem
from services.research_service import fetch_industry_benchmarks


class ResearchTool:
    """Independent fact-retrieval tool querying curated external industry research benchmarks."""

    def __init__(self, default_sector: str = "Technology & SaaS"):
        self.default_sector = default_sector

    def query(
        self,
        query_text: str = "",
        industry_sector: str | None = None
    ) -> list[EvidenceItem]:
        """Queries research benchmark engine for matching market data and strategic best practices.

        Args:
            query_text: Target topic or natural language query (e.g. 'churn', 'sales margin').
            industry_sector: Optional industry sector filter.

        Returns:
            List of normalized EvidenceItem objects ONLY.
        """
        target_sector = industry_sector if industry_sector else self.default_sector
        raw_benchmarks = fetch_industry_benchmarks(
            query_text=query_text,
            industry_sector=target_sector
        )

        evidence_items: list[EvidenceItem] = []

        for bm in raw_benchmarks:
            item = EvidenceItem(
                source=bm.get("source", "External Industry Research"),
                category=bm.get("category", "Industry Benchmark"),
                title=bm.get("title", "Industry Strategic Benchmark"),
                details=bm.get("details", {}),
                confidence=bm.get("confidence", "High (Industry Benchmark)"),
            )
            evidence_items.append(item)

        return evidence_items
