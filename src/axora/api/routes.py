from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from axora.agent.runtime import AgentRuntime
from axora.conversations.repository import conversation_repo
from axora.data.database import AsyncSessionLocal
from axora.data.dynamic_models import build_dynamic_tables
from axora.llm.provider import get_llm_adapter
from axora.semantic.service import SemanticModelService
from axora.tools.create_record import CreateRecordTool
from axora.tools.discover_model import DiscoverModelTool
from axora.tools.query_data import QueryDataTool
from axora.tools.registry import ToolRegistry
from axora.tools.update_record import UpdateRecordTool

router = APIRouter(prefix="/api/v1", tags=["Conversational Agent API"])

# Initialize Agent Runtime Dependency
YAML_PATH = Path("src/axora/semantic/definitions/gestion_paroissiale.yaml")
semantic_service = SemanticModelService.from_yaml(YAML_PATH)
build_dynamic_tables(semantic_service)

tool_registry = ToolRegistry()
tool_registry.register(DiscoverModelTool(semantic_service))
tool_registry.register(QueryDataTool(semantic_service, AsyncSessionLocal))
tool_registry.register(CreateRecordTool(semantic_service, AsyncSessionLocal))
tool_registry.register(UpdateRecordTool(semantic_service, AsyncSessionLocal))

agent_runtime = AgentRuntime(tool_registry=tool_registry, llm_adapter=get_llm_adapter())


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Intent message from user")
    conversation_id: str | None = Field(default=None, description="Optional persistent conversation session UUID")


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    status: str = "completed"


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
    session = conversation_repo.get_or_create_session(request.conversation_id)

    # 1. Retrieve history before appending current message
    history = conversation_repo.get_history_for_agent(session.id)

    # 2. Record user message
    conversation_repo.add_message(session.id, role="user", content=request.message)

    # 3. Process intent via Agent Runtime
    try:
        agent_response = await agent_runtime.process_intent(
            user_message=request.message,
            history=history,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process intent: {exc}",
        ) from exc

    # 4. Record agent response
    conversation_repo.add_message(session.id, role="assistant", content=agent_response)

    return ChatResponse(
        conversation_id=session.id,
        response=agent_response,
        status="completed",
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
