"""Retrieval capability contract — the typed shape Week 9 implements.

This mirrors Week 7's `ContextPrimitive` discipline: define the interface
before writing any retrieval code. Nothing here is executable logic yet —
it is the contract from Document/retrieval-capability-contract.md expressed
as types, so Week 9's build fills in `search_knowledge()` against a shape
that already exists instead of inventing one mid-build.

Fill in the TODOs during Week 9. Do not add retrieval logic to this file —
it stays a contract; implementations live in Week 9's `Projects/` build.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Protocol


class FailureReason(str, Enum):
    """Why a search returned no usable results -- never raise for these."""

    NO_MATCHES = "no_matches"
    BELOW_RELEVANCE_THRESHOLD = "below_relevance_threshold"
    FILTERED_OUT_BY_POLICY = "filtered_out_by_policy"
    CORPUS_UNAVAILABLE = "corpus_unavailable"


@dataclass(frozen=True)
class SearchFilters:
    """Query-time metadata filters -- applied alongside similarity search,
    never as a post-filter on an already-truncated top-K."""

    doc_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    tenant_id: str | None = None
    classification: str | None = None


@dataclass(frozen=True)
class SearchQuery:
    """Input contract: typed query + filters."""

    text: str
    filters: SearchFilters = field(default_factory=SearchFilters)
    top_k: int = 5


@dataclass(frozen=True)
class SearchResult:
    """One retrieved chunk with the citation/scoring info callers need."""

    chunk_text: str
    source_id: str
    score: float
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResponse:
    """Output contract: typed results + scores + citations, or a typed
    failure reason -- never an unhandled exception for 'no good results'."""

    results: list[SearchResult]
    query: SearchQuery
    failure_reason: FailureReason | None = None

    @property
    def ok(self) -> bool:
        return self.failure_reason is None and len(self.results) > 0


@dataclass(frozen=True)
class RetrievalPolicy:
    """Who decides what this capability is allowed to retrieve.

    TODO (Week 8 one-page exercise / Week 9): decide where this is enforced
    -- inside the capability, or by a separate policy check the capability
    calls before querying the vector DB.
    """

    allowed_corpora: tuple[str, ...]
    allowed_classifications: tuple[str, ...] = ("public",)


@dataclass(frozen=True)
class CapabilityBudget:
    """Declared, measured budgets -- not guesses.

    TODO (Week 9 Saturday): replace placeholder values with measured p95
    latency and actual cost-per-call once the pipeline is built.
    """

    latency_p95_ms: float | None = None
    cost_per_call_usd: float | None = None


class SearchKnowledgeCapability(Protocol):
    """The `search_knowledge` capability contract.

    Week 9 implements this Protocol with a real hybrid-search + rerank +
    self-corrective pipeline. The runtime (Week 10+) calls only this
    interface -- it never needs to know chunking strategy, embedding model,
    or vector DB choice.
    """

    policy: RetrievalPolicy
    budget: CapabilityBudget

    def search_knowledge(self, query: SearchQuery) -> SearchResponse:
        """Run the capability. Must never raise for 'no good results' --
        return a SearchResponse with a FailureReason instead."""
        ...
