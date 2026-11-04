from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from axora.api.routes import router as api_router

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
