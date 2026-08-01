from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from agents import SupervisorAgent

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
