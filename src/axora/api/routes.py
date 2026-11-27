import asyncio
import json
import logging
from pathlib import Path
from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse
from axora.agent.context import AgentContext
from axora.agent.runtime import AgentRuntime
from axora.config import settings
from axora.conversations.repository import conversation_repo
from axora.data.database import AsyncSessionLocal
from axora.data.dynamic_models import build_dynamic_tables
from axora.llm.provider import get_llm_adapter
from axora.progress import ProgressCallback, ProgressEvent
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.query_data import QueryDataTool
from axora.tools.render_view import RenderViewTool
from axora.tools.registry import ToolRegistry
from axora.tools.update_record import UpdateRecordTool
from axora.views.registry import ViewRegistry
from axora.views.builders import (
    DynamicTableViewBuilder,
    DynamicChartViewBuilder,
    DynamicMetricCardsBuilder,
)

router = APIRouter(prefix="/api/v1", tags=["Conversational Agent API"])
logger = logging.getLogger("axora.api")

# Initialize Semantic Model & Tables
logger.info("Axora bootstrap: loading semantic model.")
YAML_PATH = Path(settings.SEMANTIC_MODEL_PATH)
semantic_service = SemanticModelService.from_yaml(YAML_PATH)
build_dynamic_tables(semantic_service)
logger.info("Axora bootstrap: semantic model and dynamic tables ready.")

# Initialize Extensible View Registry
view_registry = ViewRegistry()
view_registry.register(DynamicTableViewBuilder(semantic_service))
view_registry.register(DynamicChartViewBuilder())
view_registry.register(DynamicMetricCardsBuilder())
logger.info("Axora bootstrap: view registry ready.")

# Initialize Tool Registry
tool_registry = ToolRegistry()
tool_registry.register(DiscoverModelTool(semantic_service))
tool_registry.register(QueryDataTool(semantic_service, AsyncSessionLocal))
tool_registry.register(CreateRecordTool(semantic_service, AsyncSessionLocal))
tool_registry.register(UpdateRecordTool(semantic_service, AsyncSessionLocal))
tool_registry.register(RenderViewTool(view_registry))
logger.info("Axora bootstrap: tool registry ready.")

# Initialize Agent Runtime
agent_runtime = AgentRuntime(tool_registry=tool_registry, llm_adapter=get_llm_adapter())
logger.info("Axora bootstrap: agent runtime ready.")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Intent message from user")
    conversation_id: str | None = Field(default=None, description="Optional persistent conversation session UUID")


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    view: dict[str, Any] | None = None
    status: str = "completed"


def _extract_view(context: Any) -> dict[str, Any] | None:
    if not context.observations:
        return None
    for obs in reversed(context.observations):
        if (
            obs.tool_call.name == "render_view"
            and obs.result.status == "success"
            and isinstance(obs.result.data, dict)
        ):
            return obs.result.data
        if (
            obs.tool_call.name == "query_data"
            and obs.result.status == "success"
            and isinstance(obs.result.data, dict)
        ):
            records = obs.result.data.get("records", [])
            if records and view_registry.has("table"):
                return view_registry.build_view("table", obs.result.data).model_dump()
            return None
    return None


async def _process_chat_message(
    request: ChatRequest,
    progress_callback: ProgressCallback | None = None,
) -> ChatResponse:
    session = conversation_repo.get_or_create_session(request.conversation_id)
    history = conversation_repo.get_history_for_agent(session.id)
    conversation_repo.add_message(session.id, role="user", content=request.message)

    run_result = await agent_runtime.process_intent_with_context(
        user_message=request.message,
        history=history,
        progress_callback=progress_callback,
    )
    conversation_repo.add_message(session.id, role="assistant", content=run_result.response)
    return ChatResponse(
        conversation_id=session.id,
        response=run_result.response,
        view=_extract_view(run_result.context),
        status="completed",
    )


class MessageSchema(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class SessionSchema(BaseModel):
    id: str
    messages: list[MessageSchema]
    created_at: str
    updated_at: str


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def process_chat_message(request: ChatRequest) -> ChatResponse:
    """Processes a natural language intent message through Axora Agent Runtime."""
    try:
        return await _process_chat_message(request)
    except Exception as exc:
        logger.exception("Failed to process chat request.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process intent: {exc}",
        ) from exc


@router.post("/chat/stream", response_class=StreamingResponse)
async def stream_chat_message(request: ChatRequest) -> StreamingResponse:
    """Streams safe progress events and the final chat result as server-sent events."""
    async def event_stream():
        event_queue: asyncio.Queue[tuple[str | None, dict[str, Any] | None]] = asyncio.Queue()

        def enqueue_progress(event: ProgressEvent) -> None:
            event_queue.put_nowait((event.type, event.model_dump(mode="json")))

        async def process_request() -> None:
            try:
                result = await _process_chat_message(request, progress_callback=enqueue_progress)
                await event_queue.put(("completed", result.model_dump(mode="json")))
            except Exception:
                logger.exception("Failed to process streamed chat request.")
                await event_queue.put((
                    "error",
                    {"message": "Une erreur est survenue pendant le traitement de la demande."},
                ))
            finally:
                await event_queue.put((None, None))

        processing_task = asyncio.create_task(process_request())
        try:
            while True:
                event_type, payload = await event_queue.get()
                if event_type is None:
                    break
                data = json.dumps(payload, ensure_ascii=False)
                yield f"event: {event_type}\ndata: {data}\n\n"
            await processing_task
        except asyncio.CancelledError:
            processing_task.cancel()
            raise

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/conversations/{conversation_id}", response_model=SessionSchema)
async def get_conversation_session(conversation_id: str) -> SessionSchema:
    """Retrieves full conversation message history for a session."""
    session = conversation_repo.get_or_create_session(conversation_id)
    return SessionSchema(
        id=session.id,
        messages=[MessageSchema(**m.model_dump()) for m in session.messages],
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/model/overview")
async def get_model_overview():
    """Retrieves overview of entities and synonyms defined in the semantic model."""
    overview = semantic_service.get_entities_overview()
    return {
        "model_name": semantic_service.model_name,
        "version": semantic_service.version,
        "entities": [e.model_dump() for e in overview],
    }


@router.get("/tools")
async def list_registered_tools():
    """Lists registered tools and their parameters schemas."""
    return {
        "tools": tool_registry.list_schemas()
    }


@router.get("/views/types")
async def list_view_types():
    """Lists registered extensible view types."""
    return {
        "view_types": view_registry.list_types()
    }
