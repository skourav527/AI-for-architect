from __future__ import annotations

import math
from typing import Protocol

from src.ingestion.models import Chunk
from src.retrieval.authorization import is_authorized
from src.retrieval.models import SearchResult, SearchScope


class EmbeddingProvider(Protocol):
    """Inject a provider adapter; model/version and residency stay explicit."""

    model_id: str

    def embed(self, text: str) -> tuple[float, ...]: ...


def _validate_vector(vector: tuple[float, ...]) -> None:
    if not vector or any(not math.isfinite(value) for value in vector):
        raise ValueError("embedding must be a non-empty finite vector")


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError("query and document embedding dimensions do not match")
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


class DenseIndex:
    """In-memory cosine retrieval using an injected embedding implementation."""

    def __init__(self, chunks: list[Chunk], embedder: EmbeddingProvider):
        if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError("chunk IDs must be unique")
        self._chunks = tuple(chunks)
        self._embedder = embedder
        self._vectors = tuple(embedder.embed(chunk.content) for chunk in chunks)
        for vector in self._vectors:
            _validate_vector(vector)
        if self._vectors and len({len(vector) for vector in self._vectors}) != 1:
            raise ValueError("document embeddings must have a consistent dimension")

    def search(self, scope: SearchScope, top_k: int) -> tuple[SearchResult, ...]:
        query_vector = self._embedder.embed(scope.query.text)
        _validate_vector(query_vector)
        ranked: list[SearchResult] = []
        for chunk, vector in zip(self._chunks, self._vectors, strict=True):
            if not is_authorized(chunk, scope.entitlements):
                continue
            if (
                scope.query.filters.source_id is not None
                and chunk.source_id != scope.query.filters.source_id
            ):
                continue
            if (
                scope.query.filters.document_type is not None
                and chunk.document_type != scope.query.filters.document_type
            ):
                continue
            ranked.append(
                SearchResult(
                    chunk=chunk,
                    score=_cosine(query_vector, vector),
                    score_kind=f"cosine:{self._embedder.model_id}",
                )
            )
        ranked.sort(key=lambda result: (-result.score, result.chunk.chunk_id))
        return tuple(ranked[:top_k])

