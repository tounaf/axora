from fastapi import FastAPI

app = FastAPI(
    title="Axora API",
    description="From intent to action.",
    version="0.1.0",
)


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