"""Tests for priority-driven token budget allocation (Primitive 4)."""
from __future__ import annotations

from src.context import ContextSection
from src.primitives.budget import TokenBudgetManager


def test_keeps_everything_when_under_budget() -> None:
    manager = TokenBudgetManager(total_budget=1000, output_reserve=100)
    sections = [
        ContextSection(name="system", content="you are helpful", priority=0, evictable=False),
        ContextSection(name="memory", content="hi there", priority=3),
    ]

    kept, report = manager.allocate(sections)

    assert len(kept) == 2
    assert report.detail["dropped_sections"] == []
    assert report.detail["over_budget"] is False
    print(kept)
    print(report)
    print(report.detail["dropped_sections"])
    print(report.detail["over_budget"])


def test_evicts_lowest_priority_evictable_section_first() -> None:
    manager = TokenBudgetManager(total_budget=10, output_reserve=0)
    sections = [
        ContextSection(name="system", content="core instructions here", priority=0, evictable=False),
        ContextSection(name="few_shot", content="example one example two example three", priority=2),
        ContextSection(
            name="memory",
            content="old turn one old turn two old turn three old turn four",
            priority=3,
        ),
    ]

    kept, report = manager.allocate(sections)

    assert "memory" in report.detail["dropped_sections"]  # lowest priority dropped first
    assert all(s.name != "memory" for s in kept)
    assert any(s.name == "system" for s in kept)  # non-evictable always survives
    print(kept)
    print(report)
    print(report.detail["dropped_sections"])
    print(report.detail["over_budget"]) 


def test_reports_over_budget_when_core_alone_exceeds() -> None:
    manager = TokenBudgetManager(total_budget=3, output_reserve=0)
    sections = [
        ContextSection(
            name="system",
            content="way more tokens than the budget allows here",
            priority=0,
            evictable=False,
        ),
    ]

    kept, report = manager.allocate(sections)

    assert kept == sections  # non-evictable, cannot be dropped
    assert report.detail["over_budget"] is True
    assert report.detail["dropped_sections"] == []
    print(kept)
    print(report)
    print(report.detail["dropped_sections"])
    print(report.detail["over_budget"])


def test_uses_precomputed_token_count_when_provided() -> None:
    manager = TokenBudgetManager(total_budget=5, output_reserve=0)
    # Content looks short (1 word) but declares a large precomputed count.
    sections = [ContextSection(name="memory", content="hi", priority=1, token_count=100)]

    kept, report = manager.allocate(sections)

    assert kept == []
    assert report.detail["dropped_sections"] == ["memory"]
    print(kept)
    print(report)
    print(report.detail["dropped_sections"])
    print(report.detail["over_budget"])
