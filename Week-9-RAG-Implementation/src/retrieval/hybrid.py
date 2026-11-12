from __future__ import annotations

from typing import Protocol

from src.retrieval.models import SearchResult, SearchScope


class RankedSearch(Protocol):
    def search(
        self, scope: SearchScope, top_k: int
    ) -> tuple[SearchResult, ...]: ...


class HybridIndex:
    """Reciprocal-rank fusion over compatible, authorization-aware indexes."""

    def __init__(
        self,
        keyword_index: RankedSearch,
        dense_index: RankedSearch,
        *,
        rank_constant: int = 60,
    ) -> None:
        if rank_constant < 1:
            raise ValueError("rank_constant must be at least 1")
        self._keyword_index = keyword_index
        self._dense_index = dense_index
        self._rank_constant = rank_constant

    def search(self, scope: SearchScope, top_k: int) -> tuple[SearchResult, ...]:
        keyword_results = self._keyword_index.search(scope, top_k)
        dense_results = self._dense_index.search(scope, top_k)
        by_id: dict[str, SearchResult] = {}
        fused_scores: dict[str, float] = {}

        for results in (keyword_results, dense_results):
            for rank, result in enumerate(results, start=1):
                chunk_id = result.chunk.chunk_id
                by_id[chunk_id] = result
                fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + (
                    1 / (self._rank_constant + rank)
                )

        ranked = [
            SearchResult(
                chunk=by_id[chunk_id].chunk,
                score=score,
                score_kind="reciprocal_rank_fusion",
            )
            for chunk_id, score in fused_scores.items()
        ]
        ranked.sort(key=lambda result: (-result.score, result.chunk.chunk_id))
        return tuple(ranked[:top_k])

