from __future__ import annotations

import math
from collections.abc import Mapping, Sequence


def _validate_k(k: int) -> None:
    if k < 1:
        raise ValueError("k must be at least 1")


def recall_at_k(
    retrieved: Sequence[str], relevant: set[str], k: int
) -> float:
    _validate_k(k)
    if not relevant:
        raise ValueError("relevant set must not be empty")
    return len(set(retrieved[:k]).intersection(relevant)) / len(relevant)


def precision_at_k(
    retrieved: Sequence[str], relevant: set[str], k: int
) -> float:
    _validate_k(k)
    return len(set(retrieved[:k]).intersection(relevant)) / k


def reciprocal_rank(retrieved: Sequence[str], relevant: set[str]) -> float:
    if not relevant:
        raise ValueError("relevant set must not be empty")
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1 / rank
    return 0.0


def ndcg_at_k(
    retrieved: Sequence[str], relevance: Mapping[str, float], k: int
) -> float:
    _validate_k(k)
    if any(not math.isfinite(gain) or gain < 0 for gain in relevance.values()):
        raise ValueError("relevance gains must be finite and non-negative")

    def dcg(items: Sequence[str]) -> float:
        return sum(
            (2 ** relevance.get(item, 0) - 1) / math.log2(rank + 1)
            for rank, item in enumerate(items[:k], start=1)
        )

    ideal = sorted(relevance.values(), reverse=True)[:k]
    ideal_dcg = sum(
        (2**gain - 1) / math.log2(rank + 1)
        for rank, gain in enumerate(ideal, start=1)
    )
    return dcg(retrieved) / ideal_dcg if ideal_dcg else 0.0

