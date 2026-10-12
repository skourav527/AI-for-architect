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
from datetime import date, datetime
from enum import Enum
from typing import Protocol


class OutcomeKind(str, Enum):
    """No-results is an expected answer; operational failure is an incident."""

    OK = "ok"
    NO_RESULTS = "no_results"
    OPERATIONAL_FAILURE = "operational_failure"


class Outcome(str, Enum):
    """Typed outcomes. Never raise where one of these would do, and never
    collapse an operational failure into an empty result set."""

    OK = "ok"

    # No-results -- expected, returned as data for the caller to act on.
    NO_MATCHES = "no_matches"
    BELOW_RELEVANCE_THRESHOLD = "below_relevance_threshold"
    FILTERED_OUT_BY_POLICY = "filtered_out_by_policy"

    # Operational failures -- must surface in monitoring.
    CORPUS_UNAVAILABLE = "corpus_unavailable"
    TIMEOUT = "timeout"
    BUDGET_EXCEEDED = "budget_exceeded"
    AUTHORIZATION_UNAVAILABLE = "authorization_unavailable"

    @property
    def kind(self) -> OutcomeKind:
        if self is Outcome.OK:
            return OutcomeKind.OK
        if self in {
            Outcome.NO_MATCHES,
            Outcome.BELOW_RELEVANCE_THRESHOLD,
            Outcome.FILTERED_OUT_BY_POLICY,
        }:
            return OutcomeKind.NO_RESULTS
        return OutcomeKind.OPERATIONAL_FAILURE


class ScoreKind(str, Enum):
    """Scores are not comparable across kinds, stages, or corpora. Any
    threshold must be calibrated per scorer against evaluation data."""

    COSINE_SIMILARITY = "cosine_similarity"
    DOT_PRODUCT = "dot_product"
    BM25 = "bm25"
    RANK_FUSION = "rank_fusion"
    RERANKER = "reranker"


@dataclass(frozen=True)
class CallerIdentity:
    """Trusted, authenticated principal. Resolved by the runtime/host --
    never taken from the query object and never influenced by model output."""

    principal_id: str
    tenant_id: str
    entitlements: tuple[str, ...] = ()


@dataclass(frozen=True)
class SearchFilters:
    """Caller-supplied scoping. Filters NARROW the search; they never GRANT
    access. Effective scope is always `entitlements ∩ filters`.

    Filter placement (pre-, post-, or engine-integrated) is a performance
    decision that depends on the engine and workload -- it is not the
    security control.
    """

    doc_type: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    source_system: str | None = None
    max_age_days: int | None = None


@dataclass(frozen=True)
class SearchQuery:
    """Input contract: typed query + filters. Carries no identity field --
    identity is passed separately so a model-generated query cannot widen
    its own access."""

    text: str
    filters: SearchFilters = field(default_factory=SearchFilters)
    top_k: int = 5


@dataclass(frozen=True)
class SearchResult:
    """One retrieved chunk with the provenance callers need to cite it,
    reproduce it, and judge its freshness."""

    chunk_text: str
    source_id: str
    source_uri: str
    score: float
    score_kind: ScoreKind
    scorer_id: str  # model/algorithm that produced `score`
    document_version: str | None = None  # version or content hash
    last_modified: datetime | None = None
    section: str | None = None  # heading path
    parent_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalAttempt:
    """One attempt inside a bounded loop. Recorded even on success."""

    query_text: str
    top_score: float | None
    score_kind: ScoreKind | None
    decision: str  # e.g. "accepted", "reformulated", "gave_up"
    elapsed_ms: float
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class RetrievalTrace:
    """Observability: enough to reconstruct what the capability did.

    Treat this as data classified like the corpus -- it can contain query
    text and retrieved content.
    """

    corpora_queried: tuple[str, ...]
    attempts: tuple[RetrievalAttempt, ...]
    stage_timings_ms: dict[str, float]
    total_elapsed_ms: float
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class SearchResponse:
    """Output contract: typed results + provenance + a typed outcome.

    `filtered_out_by_policy` must not disclose the existence, count, or
    titles of excluded content.
    """

    results: list[SearchResult]
    query: SearchQuery
    outcome: Outcome = Outcome.OK
    trace: RetrievalTrace | None = None

    @property
    def ok(self) -> bool:
        return self.outcome is Outcome.OK and len(self.results) > 0

    @property
    def is_operational_failure(self) -> bool:
        return self.outcome.kind is OutcomeKind.OPERATIONAL_FAILURE


@dataclass(frozen=True)
class RetrievalPolicy:
    """Enforced inside the capability; decided outside it (Week 21: a
    control-plane concern).

    TODO (Week 8 one-page exercise / Week 9): decide where entitlements are
    resolved -- in-process config, or a separate authorization service the
    capability calls before querying. If they cannot be resolved, the
    capability must fail closed with AUTHORIZATION_UNAVAILABLE.
    """

    allowed_corpora: tuple[str, ...]
    allowed_classifications: tuple[str, ...] = ("public",)


@dataclass(frozen=True)
class CapabilityBudget:
    """Declared, measured budgets and the bounds on any internal loop.

    TODO (Week 9 Saturday): replace the placeholder latency/cost values with
    measured p50/p95 and actual cost per call, and date-stamp the rates used.
    """

    latency_p50_ms: float | None = None
    latency_p95_ms: float | None = None
    cost_per_call_usd: float | None = None
    rates_checked_on: date | None = None

    # Bounds for adaptive/self-corrective retrieval -- all four apply.
    max_attempts: int = 1
    max_latency_ms: float | None = None
    max_tokens: int | None = None
    max_cost_usd: float | None = None


class SearchKnowledgeCapability(Protocol):
    """The `search_knowledge` capability contract.

    Week 9 implements this Protocol with a real retrieval pipeline. The
    runtime (Week 10+) calls only this interface -- it never needs to know
    the chunking strategy, embedding model, or store behind it.
    """

    policy: RetrievalPolicy
    budget: CapabilityBudget

    def search_knowledge(
        self, identity: CallerIdentity, query: SearchQuery
    ) -> SearchResponse:
        """Run the capability.

        Authorization is enforced here, before any result leaves the
        capability. Must never raise for 'no good results' -- return a
        SearchResponse with the appropriate Outcome instead, keeping
        no-results distinct from operational failure.
        """
        ...
