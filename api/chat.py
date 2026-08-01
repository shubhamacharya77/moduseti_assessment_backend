from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from agents import SupervisorAgent

router = APIRouter()


class ChatQueryRequest(BaseModel):
    """Executive chat Q&A query request payload."""

    message: str = Field(
        ...,
        description="Executive strategy question or prompt (e.g. 'What is our churn risk and how do we fix it?')"
    )


@router.post("/ask", status_code=status.HTTP_200_OK)
async def ask_executive_chat(
    payload: ChatQueryRequest
) -> dict[str, Any]:
    """Processes executive chat queries through the Supervisor agent, returning evidence-grounded responses with citations."""
    query_text = payload.message.strip()
    if not query_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat message query cannot be empty."
        )

    try:
        agent = SupervisorAgent()
        result = agent.route_and_execute(user_question=query_text)

        evidence_pkg = result.get("evidence_package", {})
        strat_resp = result.get("strategic_response", {})

        return {
            "status": "success",
            "message": "Grounded executive chat answer generated successfully.",
            "user_query": query_text,
            "answer": strat_resp.get("recommendation", "No specific recommendation generated."),
            "strategic_issues": strat_resp.get("strategic_issues", []),
            "business_impact": strat_resp.get("business_impact", ""),
            "priority": strat_resp.get("priority", "Medium"),
            "expected_outcome": strat_resp.get("expected_outcome", ""),
            "evidence_citations": evidence_pkg.get("items", []),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate grounded chat response: {str(e)}"
        )
