"""Tests proving State and Context are typed models, and that the few-shot
example bank is not part of EngineState (Tasks: separate state from
configuration, make Context a first-class typed model)."""
from __future__ import annotations

from pydantic import BaseModel

from src.context import Context, ContextSection, EvictionReport
from src.state import EngineState


def test_engine_state_is_a_typed_pydantic_model() -> None:
    assert issubclass(EngineState, BaseModel)


def test_engine_state_does_not_carry_the_example_bank() -> None:
    assert "example_bank" not in EngineState.model_fields
    assert set(EngineState.model_fields) == {
        "session_id",
        "messages",
        "summary",
        "turn_count",
        "metadata",
        "updated_at",
    }


def test_context_and_context_section_are_typed_pydantic_models() -> None:
    assert issubclass(Context, BaseModel)
    assert issubclass(ContextSection, BaseModel)
    assert issubclass(EvictionReport, BaseModel)


def test_context_section_supports_budget_relevant_fields() -> None:
    section = ContextSection(name="memory", content="hi", priority=1, evictable=True, token_count=5)

    assert section.name == "memory"
    assert section.priority == 1
    assert section.evictable is True
    assert section.token_count == 5
