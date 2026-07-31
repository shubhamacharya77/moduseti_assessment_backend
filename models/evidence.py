from typing import Any, Union
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Normalized evidence unit returned by independent tools."""

    source: str = Field(..., description="Origin tool or document name (e.g. Sales Analytics Tool, HR_Policy_2025.pdf)")
    category: str = Field(..., description="Type of evidence (e.g. Quantitative Metric, Document Excerpt, Industry Benchmark)")
    title: str = Field(..., description="Short summary title of the evidence finding")
    details: Union[dict[str, Any], str] = Field(..., description="Structured metrics dictionary or extracted text chunk")
    confidence: str = Field(..., description="Confidence score or calculation type (e.g. High (100% Deterministic Python Calculation))")


class EvidencePackage(BaseModel):
    """Unified container of normalized evidence items passed to the Strategic Intelligence Engine."""

    question: str = Field(..., description="Executive question or synthesis target")
    items: list[EvidenceItem] = Field(default_factory=list, description="Array of normalized evidence objects")
