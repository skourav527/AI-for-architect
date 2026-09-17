"""Typed, durable state for the ContextEngine — a Pydantic model, not a dict
and not a bare list of messages. This is what `persist()`/`load()` round-trip
through JSON to survive a process restart.

EngineState holds only durable session/runtime state. Configuration for a
primitive (e.g. the FewShotSelector's example bank) is injected into
ContextEngine instead — see src/primitives/few_shot.py."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant"]
    content: str
    turn: int


class EngineState(BaseModel):
    """The durable, typed state a ContextEngine persists and reloads."""

    model_config = ConfigDict(extra="forbid")

    session_id: str
    messages: list[Message] = Field(default_factory=list)
    summary: str = ""
    turn_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
