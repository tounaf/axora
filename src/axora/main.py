from pathlib import Path
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from axora.api.routes import router as api_router

logger = logging.getLogger("axora.health")

app = FastAPI(
    title="Axora API & Dashboard",
    description="From intent to action. Conversational Agent API & Web UI Dashboard",
    version="0.5.0",
)

# Enable CORS for Next.js web application and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_router)

HTML_PATH = Path("src/axora/web/index.html")


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {"status": "ok", "service": "axora"}


async def _database_is_ready() -> bool:
    from axora.data.database import engine

    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        logger.exception("Database readiness check failed.")
        return False


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> dict[str, str]:
    """Report readiness only when the API can reach its configured database."""
    if not await _database_is_ready():
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "database": "unavailable"},
        )
    return {"status": "ready", "service": "axora", "database": "ready"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    return {
        "name": "Axora",
        "message": "From intent to action.",
        "status": "running",
    }


@app.get("/ui", tags=["UI Dashboard"])
@app.get("/dashboard", tags=["UI Dashboard"])
async def serve_ui():
    """Serves the Axora Web UI Dashboard."""
    if HTML_PATH.is_file():
        return FileResponse(HTML_PATH)
    return {"status": "running", "name": "Axora", "message": "From intent to action."}
