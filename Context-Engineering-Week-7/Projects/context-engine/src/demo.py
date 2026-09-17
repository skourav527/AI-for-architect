"""Runnable demo proving the Week 7 Done-When bar:
1) state survives a process restart, 2) budget eviction is reported,
3) assemble/observe/compact/persist all work end to end.

Run this twice in a row: `python -m src.demo`
"""
from __future__ import annotations

from .engine import ContextEngine
from .primitives.budget import TokenBudgetManager
from .primitives.few_shot import FewShotExample
from .state import EngineState, Message

STORE_PATH = "week7_demo_state.json"


def fresh_state() -> EngineState:
    return EngineState(session_id="demo-session")


EXAMPLE_BANK = [
    FewShotExample(query="reverse a list", answer="lst[::-1]"),
    FewShotExample(
        query="sort a dict by value",
        answer="sorted(d.items(), key=lambda kv: kv[1])",
    ),
    FewShotExample(
        query="read a json file",
        answer="json.loads(Path(p).read_text())",
    ),
]


def run_demo() -> None:
    engine = ContextEngine(
        system_prompt="You are a Python assistant.",
        example_bank=EXAMPLE_BANK,
        budget=TokenBudgetManager(total_budget=40, output_reserve=5),
        store_path=STORE_PATH,
    )

    loaded = engine.load()
    print(f"Loaded prior state from disk: {loaded is not None}")
    state = loaded or fresh_state()

    for turn in range(1, 13):
        state.messages.append(
            Message(role="user", content=f"question {turn} about python lists", turn=turn)
        )
    state.turn_count += 12

    context, assemble_report = engine.assemble(state, query="how do I reverse a list?")
    print("Dropped sections due to budget:", context.dropped_sections)

    observation = engine.observe(context, result="lst[::-1]")
    print("Observation:", observation)

    state, compact_report = engine.compact(state)
    print("Compaction report:", compact_report)

    result = engine.persist(state)
    print(f"Persisted to {result.path}. Rerun this script to prove restart-safety.")


if __name__ == "__main__":
    run_demo()
