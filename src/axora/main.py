from fastapi import FastAPI
from axora.api.routes import router as api_router

app = FastAPI(
    title="Axora API",
    description="From intent to action. Conversational Agent API",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {"status": "ok", "service": "axora"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "name": "Axora",
        "message": "From intent to action.",
        "status": "running",
    }
