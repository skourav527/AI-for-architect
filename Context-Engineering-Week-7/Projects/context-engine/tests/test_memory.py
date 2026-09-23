"""Tests for conversation memory compaction (Primitive 2)."""
from __future__ import annotations

from src.primitives.memory import ConversationMemory
from src.state import Message


def make_messages(count: int) -> list[Message]:
    return [Message(role="user", content=f"turn {i}", turn=i) for i in range(1, count + 1)]


def test_no_compaction_under_threshold() -> None:
    memory = ConversationMemory(keep_last=10)
    messages = make_messages(5)

    (summary, kept), report = memory.compact(messages, existing_summary="")

    assert kept == messages
    assert summary == ""
    assert report.action == "no_compaction"
    print(summary, kept, report)


def test_compacts_messages_older_than_keep_last() -> None:
    memory = ConversationMemory(keep_last=10)
    messages = make_messages(12)

    (summary, kept), report = memory.compact(messages, existing_summary="")

    assert len(kept) == 10
    assert kept[0].turn == 3  # oldest 2 turns summarized away
    assert "turn 1" in summary and "turn 2" in summary
    assert report.action == "compacted"
    assert report.detail == {"summarized_turns": 2, "kept_turns": 10}


def test_compaction_merges_with_existing_summary() -> None:
    memory = ConversationMemory(keep_last=2)
    messages = make_messages(4)

    (summary, _), _ = memory.compact(messages, existing_summary="Prior summary.")

    assert summary.startswith("Prior summary.")

def test_compaction_is_noop_when_already_within_threshold() -> None:
    memory = ConversationMemory(keep_last=10)
    messages = make_messages(10)

    (summary, kept), report = memory.compact(
        messages,
        existing_summary="Existing summary.",
    )

    assert kept == messages
    assert summary == "Existing summary."
    assert report.action == "no_compaction"
    assert report.detail == {"turns": 10}