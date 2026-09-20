"""Tests for dynamic few-shot selection by embedding similarity (Primitive 3)."""
from __future__ import annotations

from src.primitives.few_shot import FewShotExample, FewShotSelector

BANK = [
    FewShotExample(query="reverse a list", answer="lst[::-1]"),
    FewShotExample(query="reverse a string", answer="s[::-1]"),
    FewShotExample(query="connect to a postgres database", answer="psycopg2.connect(...)"),
    FewShotExample(query="run a sql query against postgres", answer="cursor.execute(...)"),
]


def test_returns_top_k_most_similar() -> None:
    selector = FewShotSelector(top_k=2)

    selected, report = selector.run("how do I reverse a list in python?", BANK)

    assert len(selected) == 2
    assert all("reverse" in ex.query for ex in selected)
    assert report.detail["selected_count"] == 2
    assert report.detail["bank_size"] == len(BANK)
    print(selected)
    print(report)
    print(report.detail["selected_count"])
    print(report.detail["bank_size"])

def test_ranking_changes_with_query_topic() -> None:
    selector = FewShotSelector(top_k=2)

    # No trailing punctuation: the bag-of-words embed is punctuation-sensitive,
    # so "postgres?" would not match the bank's "postgres" token.
    selected, _ = selector.run("how do I query database", BANK)

    assert all("postgres" in ex.query for ex in selected)
    print(selected)


def test_empty_bank_reports_and_returns_nothing() -> None:
    selector = FewShotSelector()

    selected, report = selector.run("anything", [])

    assert selected == []
    assert report.action == "empty_bank"
