from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Transformation Strategy Intelligence Platform API",
    description="Enterprise backend providing evidence-backed AI transformation strategy for C-suite leaders.",
    version="1.0.0",
)

# Enable CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": "MODUS Enterprise AI Platform",
        "version": "1.0.0",
    }
