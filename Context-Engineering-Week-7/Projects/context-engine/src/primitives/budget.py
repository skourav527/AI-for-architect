"""Primitive 4 — token budget manager: allocates tokens across context
sections by declared priority. Never silently drops content — every eviction
is named in the report.

Operates directly on the typed ContextSection model (see src/context.py) so
there is one section shape shared by assemble() and the budget manager,
instead of a parallel internal type."""
from __future__ import annotations

from ..context import ContextSection
from .base import PrimitiveReport


def count_tokens(text: str) -> int:
    """Whitespace-token approximation. Swap for tiktoken for real counts."""
    return max(1, len(text.split())) if text else 0


def section_tokens(section: ContextSection) -> int:
    """Use a precomputed token_count when the section supplies one, else estimate."""
    return section.token_count if section.token_count is not None else count_tokens(section.content)


class TokenBudgetManager:
    """Fits sections into `total_budget` tokens, evicting lowest-priority
    evictable sections first when over budget."""

    name = "token_budget_manager"

    def __init__(self, total_budget: int, output_reserve: int = 500) -> None:
        self.total_budget = total_budget
        self.output_reserve = output_reserve

    def allocate(
        self, sections: list[ContextSection]
    ) -> tuple[list[ContextSection], PrimitiveReport]:
        available = self.total_budget - self.output_reserve
        kept = list(sections)
        dropped: list[str] = []

        def used() -> int:
            return sum(section_tokens(s) for s in kept)

        ordered_for_eviction = sorted(
            (s for s in kept if s.evictable), key=lambda s: -s.priority
        )
        idx = 0
        while used() > available and idx < len(ordered_for_eviction):
            victim = ordered_for_eviction[idx]
            if victim in kept:
                kept.remove(victim)
                dropped.append(victim.name)
            idx += 1

        report = PrimitiveReport(
            primitive=self.name,
            action="allocated",
            detail={
                "total_budget": self.total_budget,
                "output_reserve": self.output_reserve,
                "used_tokens": used(),
                "dropped_sections": dropped,
                "over_budget": used() > available,
            },
        )
        return kept, report

    def run(
        self, sections: list[ContextSection]
    ) -> tuple[list[ContextSection], PrimitiveReport]:
        """Runtime-facing alias for allocate() — satisfies ContextPrimitive."""
        return self.allocate(sections)
