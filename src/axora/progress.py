from datetime import datetime, timezone
from typing import Callable, Literal

from pydantic import BaseModel, Field


class ProgressEvent(BaseModel):
    type: Literal["progress", "completed", "error"] = "progress"
    phase: str
    status: Literal["started", "completed", "failed"] | None = None
    message: str
    tool: str | None = None
    iteration: int | None = None
    max_iterations: int | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


ProgressCallback = Callable[[ProgressEvent], None]


def publish_progress(
    callback: ProgressCallback | None,
    *,
    phase: str,
    message: str,
    event_type: Literal["progress", "completed", "error"] = "progress",
    status: Literal["started", "completed", "failed"] | None = None,
    tool: str | None = None,
    iteration: int | None = None,
    max_iterations: int | None = None,
) -> None:
    if callback is None:
        return
    callback(
        ProgressEvent(
            type=event_type,
            phase=phase,
            status=status,
            message=message,
            tool=tool,
            iteration=iteration,
            max_iterations=max_iterations,
        )
    )
