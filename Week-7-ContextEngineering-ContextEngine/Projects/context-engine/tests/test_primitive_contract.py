"""Tests proving the shared primitive contract exists and is typed
(Task: create a common ContextPrimitive contract)."""
from __future__ import annotations

from pydantic import BaseModel

from src.primitives.base import ContextPrimitive, PrimitiveReport
from src.primitives.budget import TokenBudgetManager
from src.primitives.few_shot import FewShotSelector
from src.primitives.memory import ConversationMemory
from src.primitives.output_validator import OutputValidator
from src.context import ContextSection
from src.state import Message


def test_primitive_report_is_a_typed_pydantic_model() -> None:
    assert issubclass(PrimitiveReport, BaseModel)

    report = PrimitiveReport(primitive="x", action="y", detail={"a": 1})

    assert report.primitive == "x"
    assert report.detail == {"a": 1}


def test_all_four_primitives_conform_to_the_contract() -> None:
    assert isinstance(OutputValidator(model=BaseModel), ContextPrimitive)
    assert isinstance(FewShotSelector(), ContextPrimitive)
    assert isinstance(ConversationMemory(), ContextPrimitive)
    assert isinstance(TokenBudgetManager(total_budget=100), ContextPrimitive)


def test_memory_run_delegates_to_compact() -> None:
    memory = ConversationMemory(keep_last=1)
    messages = [Message(role="user", content="a", turn=1), Message(role="user", content="b", turn=2)]

    via_run, run_report = memory.run(messages, "")
    via_compact, compact_report = memory.compact(messages, "")

    assert via_run == via_compact
    assert run_report == compact_report


def test_budget_run_delegates_to_allocate() -> None:
    manager = TokenBudgetManager(total_budget=1000)
    sections = [ContextSection(name="system", content="hi", priority=0, evictable=False)]

    via_run, run_report = manager.run(sections)
    via_allocate, allocate_report = manager.allocate(sections)

    assert via_run == via_allocate
    assert run_report == allocate_report


def test_contract_declares_name_and_run() -> None:
    assert hasattr(ContextPrimitive, "run")
    assert "name" in ContextPrimitive.__annotations__
