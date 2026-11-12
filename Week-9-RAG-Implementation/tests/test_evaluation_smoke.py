from src.evaluation.benchmark_runner import run_evaluation


def test_synthetic_smoke_evaluation_has_manifest_and_authorization_results():
    result = run_evaluation()

    assert result["case_count"] == 20
    assert result["classification"] == (
        "synthetic smoke evaluation; not a learner benchmark"
    )
    assert result["authorization_correctness"] == {
        "passed": True,
        "cases_passed": 20,
        "cases_total": 20,
    }
    finance_case = next(case for case in result["cases"] if case["case_id"] == "q08")
    assert finance_case["retrieved_source_ids"] == ["finance/payroll.md"]
    assert result["manifest"]["embedding_model"] is None
    assert result["manifest"]["retrieval_strategy"] == "bm25"
    assert result["manifest"]["indexing_strategy"] == "in-memory BM25"
    assert result["manifest"]["dataset_version"] == "1.0"
    assert result["manifest"]["corpus_version"] == "1.0"
    assert result["manifest"]["timestamp"]
    assert result["latency_ms"]["p95"] >= 0
    assert result["answer_metrics"]["groundedness"] is None
    assert result["metrics"]["recall_at_3"] >= 0
