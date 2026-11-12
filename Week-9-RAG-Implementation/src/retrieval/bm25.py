from __future__ import annotations

import math
import re
from collections import Counter

from src.ingestion.models import Chunk
from src.retrieval.authorization import is_authorized
from src.retrieval.models import SearchResult, SearchScope

_TOKEN = re.compile(r"\w+", re.UNICODE)
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "with",
    }
)


def tokenize(text: str) -> list[str]:
    return [
        token.casefold()
        for token in _TOKEN.findall(text)
        if token.casefold() not in _STOPWORDS
    ]


class BM25Index:
    """In-memory BM25 baseline; authorization is applied before ranking."""

    def __init__(self, chunks: list[Chunk], *, k1: float = 1.5, b: float = 0.75):
        if k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("BM25 parameters require k1 > 0 and 0 <= b <= 1")
        if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError("chunk IDs must be unique")
        self._chunks = tuple(chunks)
        self._tokens = tuple(tokenize(chunk.content) for chunk in chunks)
        if any(not tokens for tokens in self._tokens):
            raise ValueError("chunks must contain at least one searchable token")
        self._k1 = k1
        self._b = b

    def search(
        self,
        scope: SearchScope,
        top_k: int,
    ) -> tuple[SearchResult, ...]:
        terms = tokenize(scope.query.text)
        if not terms:
            return ()

        allowed = [
            index
            for index, chunk in enumerate(self._chunks)
            if is_authorized(chunk, scope.entitlements)
            and (
                scope.query.filters.source_id is None
                or chunk.source_id == scope.query.filters.source_id
            )
            and (
                scope.query.filters.document_type is None
                or chunk.document_type == scope.query.filters.document_type
            )
        ]
        if not allowed:
            return ()

        frequencies = {
            term: sum(term in set(self._tokens[index]) for index in allowed)
            for term in set(terms)
        }
        average_length = (
            sum(len(self._tokens[index]) for index in allowed) / len(allowed)
        )
        scored: list[SearchResult] = []
        for index in allowed:
            token_counts = Counter(self._tokens[index])
            length = len(self._tokens[index])
            score = 0.0
            for term in terms:
                document_frequency = frequencies[term]
                inverse_frequency = math.log(
                    1 + (len(allowed) - document_frequency + 0.5)
                    / (document_frequency + 0.5)
                )
                term_frequency = token_counts[term]
                denominator = term_frequency + self._k1 * (
                    1 - self._b + self._b * length / average_length
                )
                score += inverse_frequency * (
                    term_frequency * (self._k1 + 1) / denominator
                )
            if score > 0:
                    scored.append(SearchResult(chunk=self._chunks[index], score=score))
        scored.sort(key=lambda result: (-result.score, result.chunk.chunk_id))
        return tuple(scored[:top_k])

