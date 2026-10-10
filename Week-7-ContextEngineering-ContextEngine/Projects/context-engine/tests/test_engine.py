"""Tests for the ContextEngine: assemble/observe/compact/persist end to end,
including the two non-negotiable proofs — budget eviction is reported, and
state survives a simulated restart."""
from __future__ import annotations

from pathlib import Path

from src.engine import ContextEngine
from src.primitives.budget import TokenBudgetManager
from src.primitives.few_shot import FewShotExample
from src.state import EngineState, Message

EXAMPLE_BANK = [FewShotExample(query="reverse a list", answer="lst[::-1]")]


def make_state(session_id: str = "test-session") -> EngineState:
    return EngineState(session_id=session_id)


def test_context_engine_exposes_public_api() -> None:
    engine = ContextEngine(system_prompt="sys")

    for method in ("assemble", "observe", "compact", "persist"):
        assert callable(getattr(engine, method))


def test_assemble_reports_dropped_sections_when_over_budget(tmp_path: Path) -> None:
    store_path = str(tmp_path / "state.json")
    engine = ContextEngine(
        system_prompt="You are a helpful assistant.",
        example_bank=EXAMPLE_BANK,
        budget=TokenBudgetManager(total_budget=8, output_reserve=1),
        store_path=store_path,
    )
    state = make_state()
    state.messages = [
        Message(role="user", content=f"a rather long message about topic {i}", turn=i)
        for i in range(1, 6)
    ]

    context, report = engine.assemble(state, query="reverse a list please")

    assert context.dropped_sections, "expected budget to evict at least one section"
    assert "system" not in context.dropped_sections  # non-evictable core survives
    assert report.action == "assembled"


def test_compact_returns_new_state_and_report() -> None:
    engine = ContextEngine(system_prompt="sys")
    state = make_state()
    state.messages = [Message(role="user", content=f"turn {i}", turn=i) for i in range(1, 13)]

    new_state, report = engine.compact(state)

    assert new_state is not state  # state is immutable per turn
    assert len(new_state.messages) == 10
    assert report.action == "compacted"


def test_persist_and_reload_survives_restart(tmp_path: Path) -> None:
    store_path = str(tmp_path / "state.json")
    engine = ContextEngine(system_prompt="sys", store_path=store_path)
    state = make_state()
    state.messages = [Message(role="user", content="hello", turn=1)]

    assert engine.load() is None  # nothing persisted yet

    result = engine.persist(state)
    assert result.path == store_path
    assert result.session_id == state.session_id

    reloaded_engine = ContextEngine(system_prompt="sys", store_path=store_path)
    reloaded_state = reloaded_engine.load()

    assert reloaded_state is not None
    assert reloaded_state.session_id == state.session_id
    assert reloaded_state.messages[0].content == "hello"


def test_observe_returns_observation_and_does_not_mutate_context() -> None:
    engine = ContextEngine(system_prompt="sys", example_bank=EXAMPLE_BANK)
    state = make_state()
    context, _ = engine.assemble(state, query="reverse a list")
    prompt_before = context.prompt

    observation = engine.observe(context, result="the model's answer")

    assert context.prompt == prompt_before  # observe() never mutates Context
    assert observation.result_preview == "the model's answer"
    assert "few_shot" in observation.sections_included
    assert observation.selected_few_shot == ["reverse a list"]
