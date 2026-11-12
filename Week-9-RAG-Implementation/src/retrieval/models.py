from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.ingestion.models import Chunk


class Outcome(StrEnum):
    OK = "ok"
    NO_MATCHES = "no_matches"
    AUTHORIZATION_UNAVAILABLE = "authorization_unavailable"
    INVALID_INPUT = "invalid_input"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass(frozen=True)
class CallerIdentity:
    """Identity asserted by the authenticated host, never by query/tool arguments."""

    subject_id: str
    tenant_id: str


@dataclass(frozen=True)
class Entitlements:
    subject_id: str
    tenant_id: str
    groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchFilters:
    source_id: str | None = None
    document_type: str | None = None


@dataclass(frozen=True)
class SearchQuery:
    text: str
    top_k: int = 5
    filters: SearchFilters = SearchFilters()


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float
    score_kind: str = "bm25"


@dataclass(frozen=True)
class RetrievalAttempt:
    query_text: str
    decision: str
    elapsed_ms: float
    estimated_cost_usd: float
    query_tokens: int
    result_tokens: int


@dataclass(frozen=True)
class SearchResponse:
    outcome: Outcome
    results: tuple[SearchResult, ...]
    attempts: tuple[RetrievalAttempt, ...]
    stop_reason: str
    elapsed_ms: float
    total_tokens: int
    estimated_cost_usd: float
    tool_calls: int = 0


@dataclass(frozen=True)
class SearchScope:
    identity: CallerIdentity
    entitlements: Entitlements
    query: SearchQuery

