from src.retrieval.authorization import StaticEntitlementResolver
from src.retrieval.controller import RetrievalController
from src.retrieval.models import (
    CallerIdentity,
    Entitlements,
    Outcome,
    SearchQuery,
)


def test_retrieval_never_returns_other_group_or_tenant_documents(
    index, resolver, identity, zero_cost
):
    response = RetrievalController(
        index, resolver, estimate_cost=zero_cost
    ).search(
        identity, SearchQuery("database recovery payroll")
    )

    assert response.outcome is Outcome.OK
    assert {item.chunk.source_id for item in response.results} == {"public.md"}


def test_unresolvable_identity_fails_closed(index, identity, zero_cost):
    response = RetrievalController(
        index, StaticEntitlementResolver({}), estimate_cost=zero_cost
    ).search(identity, SearchQuery("payroll"))

    assert response.outcome is Outcome.AUTHORIZATION_UNAVAILABLE
    assert response.results == ()
    assert response.stop_reason == "authorization_unavailable"


def test_mismatched_tenant_identity_is_not_resolved(index, zero_cost):
    resolver = StaticEntitlementResolver(
        {"alice": Entitlements(subject_id="alice", tenant_id="tenant-a")}
    )
    response = RetrievalController(
        index, resolver, estimate_cost=zero_cost
    ).search(
        CallerIdentity(subject_id="alice", tenant_id="tenant-b"),
        SearchQuery("database"),
    )

    assert response.outcome is Outcome.AUTHORIZATION_UNAVAILABLE
    assert response.results == ()

