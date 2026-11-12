import pytest

from src.evaluation.metrics import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_retrieval_metrics_match_expected_rankings():
    retrieved = ["doc-b", "doc-a", "doc-c"]
    relevant = {"doc-a", "doc-c"}

    assert recall_at_k(retrieved, relevant, 2) == 0.5
    assert precision_at_k(retrieved, relevant, 2) == 0.5
    assert reciprocal_rank(retrieved, relevant) == 0.5
    assert ndcg_at_k(retrieved, {"doc-a": 2, "doc-c": 1}, 3) == pytest.approx(
        0.6590, abs=1e-4
    )


def test_metrics_reject_undefined_or_invalid_inputs():
    with pytest.raises(ValueError):
        recall_at_k(["a"], set(), 1)
    with pytest.raises(ValueError):
        precision_at_k(["a"], {"a"}, 0)
    with pytest.raises(ValueError):
        ndcg_at_k(["a"], {"a": -1}, 1)

