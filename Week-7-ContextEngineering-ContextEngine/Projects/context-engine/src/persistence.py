"""Durable state persistence — JSON file store so EngineState survives a
process restart. Swap for SQLite if you need concurrent readers/writers or
querying across sessions."""
from __future__ import annotations

from pathlib import Path

from .state import EngineState


def save_state(state: EngineState, path: str) -> None:
    Path(path).write_text(state.model_dump_json(indent=2), encoding="utf-8")


def load_state(path: str) -> EngineState | None:
    file_path = Path(path)
    if not file_path.exists():
        return None
    return EngineState.model_validate_json(file_path.read_text(encoding="utf-8"))
