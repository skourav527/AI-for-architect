"""Typed models for a single turn's Context — ephemeral, assembled from
State, never persisted — plus the small result models ContextEngine's
public methods return so every operation communicates what it did.

`retrieved` exists only as an extensibility point for Week 8's RAG work;
nothing here implements retrieval yet."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SectionName = Literal["system", "query", "memory", "few_shot", "retrieved", "metadata"]


class ContextSection(BaseModel):
    """One named block of a Context, and everything the budget manager needs
    to decide whether to keep or evict it."""

    model_config = ConfigDict(extra="forbid")

    name: SectionName
    content: str
    priority: int  # lower number = higher priority, evicted last
    evictable: bool = True
    token_count: int | None = None  # precomputed count; falls back to an estimate if unset


class EvictionReport(BaseModel):
    """What TokenBudgetManager.allocate() did: what fit, what was dropped, and why."""

    model_config = ConfigDict(extra="forbid")

    total_budget: int
    output_reserve: int
    used_tokens: int
    dropped_sections: list[str] = Field(default_factory=list)
    over_budget: bool = False


class Context(BaseModel):
    """What the model sees this turn — ephemeral, assembled from State.
    Never persisted; rebuilt by assemble() on every turn."""

    model_config = ConfigDict(extra="forbid")

    sections: list[ContextSection] = Field(default_factory=list)
    prompt: str
    eviction: EvictionReport | None = None
    few_shot_examples: list[str] = Field(default_factory=list)  # selected example queries

    @property
    def dropped_sections(self) -> list[str]:
        return self.eviction.dropped_sections if self.eviction else []


class Observation(BaseModel):
    """What observe() recorded about a turn — telemetry only. observe() must
    never mutate Context or State; this model only reads from them."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens_approx: int
    sections_included: list[str] = Field(default_factory=list)
    sections_dropped: list[str] = Field(default_factory=list)
    selected_few_shot: list[str] = Field(default_factory=list)
    result_preview: str = ""
    detail: dict[str, Any] = Field(default_factory=dict)


class CompactionResult(BaseModel):
    """What compact() did to State: how many turns were folded into the
    running summary vs kept verbatim."""

    model_config = ConfigDict(extra="forbid")

    summarized_turns: int = 0
    kept_turns: int = 0
    compacted: bool = False


class PersistenceResult(BaseModel):
    """What persist() did: where State was written, and for which session."""

    model_config = ConfigDict(extra="forbid")

    path: str
    session_id: str
    persisted: bool = True
