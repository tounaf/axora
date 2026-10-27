import datetime
import uuid
from typing import Any
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class ConversationSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[ConversationMessage] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class ConversationRepository:
    """In-memory and persistent conversation session repository."""

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create_session(self, session_id: str | None = None) -> ConversationSession:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        new_session = ConversationSession(id=session_id or str(uuid.uuid4()))
        self._sessions[new_session.id] = new_session
        return new_session

    def add_message(self, session_id: str, role: str, content: str) -> ConversationMessage:
        session = self.get_or_create_session(session_id)
        msg = ConversationMessage(role=role, content=content)
        session.messages.append(msg)
        session.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return msg

    def get_history_for_agent(self, session_id: str) -> list[dict[str, str]]:
        session = self.get_or_create_session(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in session.messages]


# Global conversation repository singleton
conversation_repo = ConversationRepository()
