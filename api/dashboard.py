from typing import Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from agents import SupervisorAgent
from database.chroma import get_collection_stats
from tools import CustomerAnalyticsTool, SalesAnalyticsTool

router = APIRouter()


class DashboardRequest(BaseModel):
    """Executive strategy generation request payload."""

    question: Optional[str] = Field(
        default="What high-priority strategic transformation recommendations should we execute?",
        description="Executive prompt or strategy inquiry."
    )


@router.post("/generate", status_code=status.HTTP_200_OK)
async def generate_dashboard_strategy(
    payload: DashboardRequest
) -> dict[str, Any]:
    """Triggers the Supervisor agent DAG, collects evidence across all domain tools, and generates strategic recommendations."""
    query_text = payload.question.strip() if payload.question else "What high-priority strategic transformation recommendations should we execute?"

    try:
        agent = SupervisorAgent()
        result = agent.route_and_execute(user_question=query_text)

        return {
            "status": "success",
            "message": "Strategic intelligence payload generated successfully.",
            "question": result.get("question", query_text),
            "evidence_package": result.get("evidence_package", {}),
            "strategic_response": result.get("strategic_response", {}),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate strategic dashboard response: {str(e)}"
        )


@router.get("/metrics", status_code=status.HTTP_200_OK)
async def get_dashboard_metrics() -> dict[str, Any]:
    """Retrieves aggregated executive KPIs, sales performance summary, customer churn health, and document RAG collection stats."""
    try:
        sales_tool = SalesAnalyticsTool()
        customer_tool = CustomerAnalyticsTool()

        sales_items = sales_tool.get_summary_metrics()
        customer_items = customer_tool.get_summary_metrics()

        sales_details = sales_items[0].details if sales_items else {}
        customer_details = customer_items[0].details if customer_items else {}

        chroma_stats = get_collection_stats()

        return {
            "status": "success",
            "message": "Executive dashboard metrics retrieved successfully.",
            "metrics": {
                "sales_summary": sales_details,
                "customer_summary": customer_details,
                "document_vector_store": chroma_stats,
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard metrics: {str(e)}"
        )


@router.get("/sales-slice", status_code=status.HTTP_200_OK)
async def get_sales_slice(
    category: Optional[str] = Query(default=None, description="Filter by product category"),
    region: Optional[str] = Query(default=None, description="Filter by geographic region"),
    product: Optional[str] = Query(default=None, description="Filter by specific product name"),
    segment: Optional[str] = Query(default=None, description="Filter by customer segment")
) -> dict[str, Any]:
    """Runs on-the-fly dynamic slice aggregation over sales records based on filter criteria."""
    try:
        sales_tool = SalesAnalyticsTool()
        slice_items = sales_tool.query_slice(
            category=category,
            region=region,
            product=product,
            segment=segment
        )

        slice_details = slice_items[0].details if slice_items else {}

        return {
            "status": "success",
            "message": "Sales analytics slice computed successfully.",
            "filters_applied": {
                "category": category,
                "region": region,
                "product": product,
                "segment": segment,
            },
            "slice_data": slice_details
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query sales slice: {str(e)}"
        )
