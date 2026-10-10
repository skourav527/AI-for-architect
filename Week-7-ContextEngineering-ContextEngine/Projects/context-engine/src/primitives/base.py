"""Common, framework-agnostic contract every context primitive conforms to,
so the ContextEngine (and later the Week 12 Agent Runtime) can call any of
them the same way: a name, a `run(...)` operation, and a
(result, PrimitiveReport) return pattern.

All four primitives literally expose `run()`. OutputValidator and
FewShotSelector implement it directly; ConversationMemory and
TokenBudgetManager keep their readable domain-specific methods
(`compact()`/`allocate()`) and expose `run()` as a thin delegate to the same
method, so callers that only know the runtime-uniform shape can use any of
the four interchangeably. This is intentionally a thin Protocol, not a base
class hierarchy: no external framework, no forced inheritance."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class PrimitiveReport(BaseModel):
    """What a primitive did on this call — the trace record (Week 14 hook)."""

    model_config = ConfigDict(extra="forbid")

    primitive: str
    action: str
    detail: dict[str, Any] = Field(default_factory=dict)


@runtime_checkable
class ContextPrimitive(Protocol):
    """Every context primitive exposes a name and a `run` entry point that
    returns its result plus a report describing what happened."""

    name: str

    def run(self, *args: Any, **kwargs: Any) -> tuple[Any, PrimitiveReport]:
        ...
