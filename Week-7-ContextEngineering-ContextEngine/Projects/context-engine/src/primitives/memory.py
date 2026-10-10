"""Primitive 2 — conversation memory with compaction: keep the last N turns
verbatim, summarize everything older into a running summary."""
from __future__ import annotations

from collections.abc import Callable

from ..state import Message
from .base import PrimitiveReport

Summarize = Callable[[list[Message]], str]


def default_summarize(messages: list[Message]) -> str:
    """Dependency-free fallback summarizer: a deterministic digest.
    Swap for an LLM call in production."""
    lines = [f"turn {m.turn} ({m.role}): {m.content}" for m in messages]
    return "Earlier conversation summary: " + " | ".join(lines)


class ConversationMemory:
    """Compacts anything older than `keep_last` turns into `summary`."""

    name = "conversation_memory"

    def __init__(
        self, keep_last: int = 10, summarize: Summarize = default_summarize
    ) -> None:
        self.keep_last = keep_last
        self.summarize = summarize

    def compact(
        self, messages: list[Message], existing_summary: str
    ) -> tuple[tuple[str, list[Message]], PrimitiveReport]:
        if len(messages) <= self.keep_last:
            report = PrimitiveReport(
                primitive=self.name, action="no_compaction", detail={"turns": len(messages)}
            )
            return (existing_summary, messages), report

        to_summarize = messages[: -self.keep_last]
        kept = messages[-self.keep_last :]
        new_summary_piece = self.summarize(to_summarize)
        merged_summary = f"{existing_summary}\n{new_summary_piece}".strip()

        report = PrimitiveReport(
            primitive=self.name,
            action="compacted",
            detail={"summarized_turns": len(to_summarize), "kept_turns": len(kept)},
        )
        return (merged_summary, kept), report

    def run(
        self, messages: list[Message], existing_summary: str
    ) -> tuple[tuple[str, list[Message]], PrimitiveReport]:
        """Runtime-facing alias for compact() — satisfies ContextPrimitive."""
        return self.compact(messages, existing_summary)
