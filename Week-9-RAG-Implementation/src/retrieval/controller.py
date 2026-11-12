from __future__ import annotations

import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Protocol

from src.retrieval.authorization import AuthorizationUnavailable, EntitlementResolver
from src.retrieval.models import (
    CallerIdentity,
    Outcome,
    RetrievalAttempt,
    SearchQuery,
    SearchResponse,
    SearchResult,
    SearchScope,
)


class SearchBackend(Protocol):
    def search(
        self, scope: SearchScope, top_k: int
    ) -> tuple[SearchResult, ...]: ...


class QueryRewriter(Protocol):
    def rewrite(
        self, query: str, *, max_output_tokens: int, timeout_ms: float
    ) -> str | None: ...


@dataclass(frozen=True)
class RetrievalBudget:
    max_attempts: int = 1
    max_tool_calls: int = 3
    max_latency_ms: float = 1_000
    max_total_tokens: int = 4_000
    max_cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.max_tool_calls < 1:
            raise ValueError("max_tool_calls must be at least 1")
        if self.max_latency_ms <= 0 or self.max_total_tokens < 1:
            raise ValueError("latency and token budgets must be positive")
        if self.max_cost_usd < 0:
            raise ValueError("max_cost_usd must not be negative")


def _token_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


class RetrievalController:
    def __init__(
        self,
        backend: SearchBackend,
        entitlement_resolver: EntitlementResolver,
        *,
        budget: RetrievalBudget | None = None,
        rewriter: QueryRewriter | None = None,
        estimate_cost: Callable[[str], float],
        estimate_rewrite_cost: Callable[[str], float] | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if rewriter is not None and estimate_rewrite_cost is None:
            raise ValueError("a query rewriter requires an explicit cost estimator")
        self._backend = backend
        self._entitlement_resolver = entitlement_resolver
        self._budget = budget if budget is not None else RetrievalBudget()
        self._rewriter = rewriter
        self._estimate_cost = estimate_cost
        self._estimate_rewrite_cost = estimate_rewrite_cost
        self._clock = clock

    def search(
        self, identity: CallerIdentity, query: SearchQuery
    ) -> SearchResponse:
        started = self._clock()
        if (
            not identity.subject_id.strip()
            or not identity.tenant_id.strip()
            or not query.text.strip()
            or not 1 <= query.top_k <= 100
        ):
            return self._response(
                Outcome.INVALID_INPUT, (), (), "invalid_input", started, 0, 0.0
            )

        try:
            entitlements = self._entitlement_resolver.resolve(identity)
        except AuthorizationUnavailable:
            return self._response(
                Outcome.AUTHORIZATION_UNAVAILABLE,
                (),
                (),
                "authorization_unavailable",
                started,
                0,
                0.0,
            )

        current_query = query.text.strip()
        attempts: list[RetrievalAttempt] = []
        used_tokens = 0
        used_cost = 0.0
        used_tool_calls = 0

        for attempt_number in range(self._budget.max_attempts):
            elapsed_ms = (self._clock() - started) * 1_000
            query_tokens = _token_count(current_query)
            cost = self._estimate_cost(current_query)
            if not isfinite(cost) or cost < 0:
                raise ValueError("cost estimator must return a finite non-negative value")
            if elapsed_ms >= self._budget.max_latency_ms:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "latency_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if used_tool_calls >= self._budget.max_tool_calls:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "tool_call_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if used_tokens + query_tokens > self._budget.max_total_tokens:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "token_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if used_cost + cost > self._budget.max_cost_usd:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "cost_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )

            used_tokens += query_tokens
            used_cost += cost
            scope = SearchScope(
                identity=identity,
                entitlements=entitlements,
                query=SearchQuery(
                    text=current_query, top_k=query.top_k, filters=query.filters
                ),
            )
            results = self._backend.search(scope, query.top_k)
            used_tool_calls += 1
            result_tokens = sum(_token_count(item.chunk.content) for item in results)
            if used_tokens + result_tokens > self._budget.max_total_tokens:
                attempts.append(
                    RetrievalAttempt(
                        current_query,
                        "token_budget",
                        (self._clock() - started) * 1_000,
                        cost,
                        query_tokens,
                        0,
                    )
                )
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "token_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )

            used_tokens += result_tokens
            attempts.append(
                RetrievalAttempt(
                    current_query,
                    "accepted" if results else "no_matches",
                    (self._clock() - started) * 1_000,
                    cost,
                    query_tokens,
                    result_tokens,
                )
            )
            if (self._clock() - started) * 1_000 >= self._budget.max_latency_ms:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "latency_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if results:
                return self._response(
                    Outcome.OK,
                    results,
                    attempts,
                    "results_found",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )

            if self._rewriter is None:
                break
            if attempt_number + 1 == self._budget.max_attempts:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "attempt_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if used_tool_calls >= self._budget.max_tool_calls:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "tool_call_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if self._estimate_rewrite_cost is None:
                raise RuntimeError("rewrite cost estimator is not configured")
            rewrite_cost = self._estimate_rewrite_cost(current_query)
            if not isfinite(rewrite_cost) or rewrite_cost < 0:
                raise ValueError(
                    "rewrite cost estimator must return a finite non-negative value"
                )
            if used_cost + rewrite_cost > self._budget.max_cost_usd:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "cost_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            remaining_latency = self._budget.max_latency_ms - (
                self._clock() - started
            ) * 1_000
            if remaining_latency <= 0:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "latency_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            remaining_tokens = self._budget.max_total_tokens - used_tokens
            if remaining_tokens < 1:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "token_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            rewritten = self._rewriter.rewrite(
                current_query,
                max_output_tokens=remaining_tokens,
                timeout_ms=remaining_latency,
            )
            used_cost += rewrite_cost
            used_tool_calls += 1
            if (
                self._clock() - started
            ) * 1_000 >= self._budget.max_latency_ms:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "latency_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            rewrite_tokens = _token_count(rewritten or "")
            used_tokens += rewrite_tokens
            if used_tokens > self._budget.max_total_tokens:
                return self._response(
                    Outcome.BUDGET_EXCEEDED,
                    (),
                    attempts,
                    "token_budget",
                    started,
                    used_tokens,
                    used_cost,
                    tool_calls=used_tool_calls,
                )
            if not rewritten or rewritten.strip() == current_query:
                break
            current_query = rewritten.strip()

        return self._response(
            Outcome.NO_MATCHES,
            (),
            attempts,
            "no_matches",
            started,
            used_tokens,
            used_cost,
            tool_calls=used_tool_calls,
        )

    def _response(
        self,
        outcome: Outcome,
        results: tuple[SearchResult, ...],
        attempts: tuple[RetrievalAttempt, ...] | list[RetrievalAttempt],
        stop_reason: str,
        started: float,
        total_tokens: int,
        estimated_cost_usd: float,
        *,
        tool_calls: int = 0,
    ) -> SearchResponse:
        return SearchResponse(
            outcome=outcome,
            results=tuple(results),
            attempts=tuple(attempts),
            stop_reason=stop_reason,
            elapsed_ms=max(0.0, (self._clock() - started) * 1_000),
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost_usd,
            tool_calls=tool_calls,
        )

