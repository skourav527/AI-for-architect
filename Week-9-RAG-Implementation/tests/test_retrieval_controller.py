import pytest

from src.retrieval.controller import RetrievalBudget, RetrievalController
from src.retrieval.models import Outcome, SearchQuery


class RewriteOnce:
    def __init__(self):
        self.calls = 0
        self.max_output_tokens = 0
        self.timeout_ms = 0

    def rewrite(self, query, *, max_output_tokens, timeout_ms):
        self.calls += 1
        self.max_output_tokens = max_output_tokens
        self.timeout_ms = timeout_ms
        return "database backup recovery"


def test_controller_returns_auditable_success_and_typed_no_results(
    index, resolver, identity, zero_cost
):
    controller = RetrievalController(index, resolver, estimate_cost=zero_cost)

    success = controller.search(identity, SearchQuery("database backup"))
    no_results = controller.search(identity, SearchQuery("unmatched phrase"))

    assert success.outcome is Outcome.OK
    assert success.stop_reason == "results_found"
    assert len(success.attempts) == 1
    assert no_results.outcome is Outcome.NO_MATCHES
    assert no_results.stop_reason == "no_matches"


def test_retries_stop_at_max_attempts(index, resolver, identity, zero_cost):
    rewriter = RewriteOnce()
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_attempts=2),
        rewriter=rewriter,
        estimate_cost=zero_cost,
        estimate_rewrite_cost=zero_cost,
    )

    response = controller.search(identity, SearchQuery("unmatched phrase"))

    assert response.outcome is Outcome.OK
    assert len(response.attempts) == 2
    assert rewriter.calls == 1
    assert response.tool_calls == 3
    assert rewriter.max_output_tokens > 0
    assert rewriter.timeout_ms > 0


def test_token_budget_stops_before_querying(index, resolver, identity, zero_cost):
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_total_tokens=1),
        estimate_cost=zero_cost,
    )

    response = controller.search(identity, SearchQuery("two token query"))

    assert response.outcome is Outcome.BUDGET_EXCEEDED
    assert response.stop_reason == "token_budget"
    assert response.attempts == ()


def test_cost_budget_fails_before_backend_call(index, resolver, identity):
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_cost_usd=0.01),
        estimate_cost=lambda _query: 0.02,
    )

    response = controller.search(identity, SearchQuery("database"))

    assert response.outcome is Outcome.BUDGET_EXCEEDED
    assert response.stop_reason == "cost_budget"
    assert response.attempts == ()


def test_attempt_limit_is_explicit(index, resolver, identity, zero_cost):
    rewriter = RewriteOnce()
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_attempts=1),
        rewriter=rewriter,
        estimate_cost=zero_cost,
        estimate_rewrite_cost=zero_cost,
    )

    response = controller.search(identity, SearchQuery("unmatched phrase"))

    assert response.outcome is Outcome.BUDGET_EXCEEDED
    assert response.stop_reason == "attempt_budget"
    assert len(response.attempts) == 1
    assert rewriter.calls == 0


def test_tool_call_budget_stops_before_rewrite(index, resolver, identity, zero_cost):
    rewriter = RewriteOnce()
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_attempts=2, max_tool_calls=1),
        rewriter=rewriter,
        estimate_cost=zero_cost,
        estimate_rewrite_cost=zero_cost,
    )

    response = controller.search(identity, SearchQuery("unmatched phrase"))

    assert response.outcome is Outcome.BUDGET_EXCEEDED
    assert response.stop_reason == "tool_call_budget"
    assert response.tool_calls == 1
    assert rewriter.calls == 0


def test_rewrite_cost_is_reserved_before_rewrite(
    index, resolver, identity, zero_cost
):
    rewriter = RewriteOnce()
    controller = RetrievalController(
        index,
        resolver,
        budget=RetrievalBudget(max_attempts=2, max_cost_usd=0.01),
        rewriter=rewriter,
        estimate_cost=zero_cost,
        estimate_rewrite_cost=lambda _query: 0.02,
    )

    response = controller.search(identity, SearchQuery("unmatched phrase"))

    assert response.outcome is Outcome.BUDGET_EXCEEDED
    assert response.stop_reason == "cost_budget"
    assert response.estimated_cost_usd == 0
    assert response.tool_calls == 1
    assert rewriter.calls == 0


def test_query_rewriter_requires_a_cost_estimator(index, resolver, zero_cost):
    with pytest.raises(ValueError, match="requires an explicit cost estimator"):
        RetrievalController(
            index,
            resolver,
            rewriter=RewriteOnce(),
            estimate_cost=zero_cost,
        )

