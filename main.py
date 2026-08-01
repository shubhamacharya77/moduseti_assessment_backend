from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api.dashboard import router as dashboard_router
from api.upload import router as upload_router

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


@app.get("/", include_in_schema=False)
async def root_to_docs() -> RedirectResponse:
    """Redirect root endpoint to Swagger UI documentation."""
    return RedirectResponse(url="/docs")


app.include_router(upload_router, prefix="/api/upload", tags=["Document Upload"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Strategic Dashboard"])


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": "MODUS Enterprise AI Platform",
        "version": "1.0.0",
    }
