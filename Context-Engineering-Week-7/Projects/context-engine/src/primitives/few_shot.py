"""Primitive 3 — dynamic few-shot selection by embedding similarity: rank an
example bank against the query and return the top-K.

The example bank is FewShotSelector's own configuration/dependency, not part
of EngineState — it is injected into ContextEngine, not stored in State.

The embedding function is swappable: a dependency-free bag-of-words vector by
default, a real embedding model (OpenAI/sentence-transformers) in production.
The `run` contract does not change either way."""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from .base import PrimitiveReport

EmbedFn = Callable[[str], dict[str, float]]


class FewShotExample(BaseModel):
    """One example in a FewShotSelector's example bank — selector config,
    not session state."""

    model_config = ConfigDict(extra="forbid")

    query: str
    answer: str


def bag_of_words_embed(text: str) -> dict[str, float]:
    """Dependency-free stand-in embedding: term-frequency vector."""
    return dict(Counter(text.lower().split()))


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    shared = set(a) & set(b)
    dot = sum(a[k] * b[k] for k in shared)
    norm_a = math.sqrt(sum(v * v for v in a.values())) or 1.0
    norm_b = math.sqrt(sum(v * v for v in b.values())) or 1.0
    return dot / (norm_a * norm_b)


class FewShotSelector:
    """Ranks an example bank against the query and returns the top-K."""

    name = "few_shot_selector"

    def __init__(self, embed: EmbedFn = bag_of_words_embed, top_k: int = 3) -> None:
        self.embed = embed
        self.top_k = top_k

    def run(
        self, query: str, bank: list[FewShotExample]
    ) -> tuple[list[FewShotExample], PrimitiveReport]:
        if not bank:
            return [], PrimitiveReport(primitive=self.name, action="empty_bank", detail={})

        query_vec = self.embed(query)
        scored = sorted(
            bank,
            key=lambda ex: cosine_similarity(query_vec, self.embed(ex.query)),
            reverse=True,
        )
        selected = scored[: self.top_k]

        report = PrimitiveReport(
            primitive=self.name,
            action="selected",
            detail={
                "query": query,
                "selected_count": len(selected),
                "bank_size": len(bank),
            },
        )
        return selected, report
