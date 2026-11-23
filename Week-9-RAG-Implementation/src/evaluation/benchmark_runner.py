## This component is responsible for running evaluation benchmarks on the retrieval system.
## It reads the evaluation corpus and dataset, constructs the retrieval index,
## and executes search queries.
## It computes various metrics such as NDCG, precision, recall, and reciprocal
## rank for each evaluation case.
## It also checks for proper authorization and records latencies and estimated costs.
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.evaluation.metrics import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from src.ingestion.index_builder import build_chunks
from src.ingestion.models import Document, DocumentMetadata
from src.retrieval.authorization import StaticEntitlementResolver
from src.retrieval.bm25 import BM25Index
from src.retrieval.controller import RetrievalController
from src.retrieval.models import (
    CallerIdentity,
    Entitlements,
    Outcome,
    SearchFilters,
    SearchQuery,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = PROJECT_ROOT / "evaluation"


def _zero_cost(_query: str) -> float:
    return 0.0


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    category: str
    query: str
    expected_source_ids: tuple[str, ...]
    principal_id: str
    tenant_id: str
    expected_behavior: str
    filters: dict[str, str] | None = None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as file:
        rows = [json.loads(line) for line in file if line.strip()]
    if not rows:
        raise ValueError(f"evaluation input is empty: {path.name}")
    return rows


def _load_cases(path: Path) -> list[EvaluationCase]:
    cases = [
        EvaluationCase(
            case_id=row["case_id"],
            category=row["category"],
            query=row["query"],
            expected_source_ids=tuple(row["expected_source_ids"]),
            principal_id=row["principal_id"],
            tenant_id=row["tenant_id"],
            expected_behavior=row["expected_behavior"],
            filters=row.get("filters"),
        )
        for row in _read_jsonl(path)
    ]
    if not 20 <= len(cases) <= 50:
        raise ValueError("the evaluation set must contain 20-50 cases")
    if len({case.case_id for case in cases}) != len(cases):
        raise ValueError("evaluation case IDs must be unique")
    return cases

## It reads the evaluation corpus and dataset, constructs the retrieval index,
## and executes search queries.
## It collects metrics, authorization checks, case results, latencies, and
## estimated costs for each evaluation case.

def run_evaluation() -> dict[str, Any]:
    ##read the evaluation corpus and dataset
    corpus_rows = _read_jsonl(EVALUATION_DIR / "corpus.jsonl")
    cases = _load_cases(EVALUATION_DIR / "dataset.jsonl")
    ## convert corups rows into Document objects
    documents = [
        Document(
            source_id=row["source_id"],
            source_uri=row["source_uri"],
            text=row["text"],
            version=row["version"],
            last_modified=datetime.fromisoformat(row["last_modified"]),
            metadata=DocumentMetadata(
                tenant_id=row["tenant_id"],
                allowed_principals=tuple(row["allowed_principals"]),
                allowed_groups=tuple(row["allowed_groups"]),
                is_public=row["is_public"],
                document_type=row["document_type"],
            ),
        )
        for row in corpus_rows
    ]
    ## build chunks from the documents
    chunks = build_chunks(documents, max_words=180, overlap_words=24)

    ## construct the retrieval index from the chunks
    index = BM25Index(chunks)

    ## define principals and entitlements for authorization checks
    principals = {
        "student": Entitlements(
            subject_id="student",
            tenant_id="sample-tenant",
            groups=("architecture",),
        ),
        "finance-reviewer": Entitlements(
            subject_id="finance-reviewer",
            tenant_id="sample-tenant",
            groups=("finance",),
        ),
    }

    ## initialize the retrieval controller with the index and entitlement resolver
    controller = RetrievalController(
        index,
        StaticEntitlementResolver(principals),
        estimate_cost=_zero_cost,
    )
    metric_rows: list[dict[str, float]] = []
    auth_checks: list[bool] = []
    case_results: list[dict[str, Any]] = []
    latencies_ms: list[float] = []
    estimated_costs_usd: list[float] = []

    ## iterate over each evaluation case and perform search queries
    ## loop through each evaluation case and execute the search query using the retrieval controller
    ## record the response metrics, authorization checks, and case results
    ## Example case (one line of evaluation/dataset.jsonl):
    ##   case_id="q01", category="procedure",
    ##   query="How do operators restore a database from a verified backup?",
    ##   expected_source_ids=["runbooks/recovery.md"],
    ##   principal_id="student", tenant_id="sample-tenant",
    ##   expected_behavior="retrieve"

    for case in cases:
        search_filters = SearchFilters(**(case.filters or {}))
        response = controller.search(
            CallerIdentity(case.principal_id, case.tenant_id),
            SearchQuery(
                case.query,
                top_k=3,
                filters=search_filters,
            )
        )
        latencies_ms.append(response.elapsed_ms)
        estimated_costs_usd.append(response.estimated_cost_usd)
        retrieved = list(dict.fromkeys(item.chunk.source_id for item in response.results))
        if case.expected_behavior == "authorization_unavailable":
            authorization_passed = (
                response.outcome is Outcome.AUTHORIZATION_UNAVAILABLE and not response.results
            )
        elif case.expected_behavior == "tenant_isolation":
            authorization_passed = all (
                item.chunk.tenant_id == case.tenant_id
                and item.chunk.source_id != "tenant-b/internal.md"
                for item in response.results
            )
        elif case.expected_behavior == "no_authorized_results":
            authorization_passed = (
                response.outcome is Outcome.NO_MATCHES and not response.results
            )
        else:
            authorization_passed = all(
                item.chunk.tenant_id == case.tenant_id
                and (
                    item.chunk.is_public
                    or case.principal_id in item.chunk.allowed_principals
                    or bool(
                        set(principals[case.principal_id].groups).intersection(
                            item.chunk.allowed_groups
                        )
                    )
                )
                for item in response.results
            )
            ## record the metrics for the current case
            metric_rows.append(
                {
                    "recall_at_3": recall_at_k(
                        retrieved, set(case.expected_source_ids), 3
                    ),
                    "precision_at_3": precision_at_k(
                        retrieved, set(case.expected_source_ids), 3
                    ),
                    "mrr": reciprocal_rank(
                        retrieved, set(case.expected_source_ids)
                    ),
                    "ndcg_at_3": ndcg_at_k(
                        retrieved,
                        {source_id: 1.0 for source_id in case.expected_source_ids},
                        3,
                    ),
                }
            )
        auth_checks.append(authorization_passed)
        case_results.append(
            {
                "case_id": case.case_id,
                "category": case.category,
                "outcome": response.outcome.value,
                "retrieved_source_ids": retrieved,
                "authorization_passed": authorization_passed,
            }
        )

    metric_names = tuple(metric_rows[0]) if metric_rows else ()
    averages = {
        name: sum(row[name] for row in metric_rows) / len(metric_rows)
        for name in metric_names
    }
    sorted_latencies = sorted(latencies_ms)
    p50_index = max(0, (50 * len(sorted_latencies) + 99) // 100 - 1)
    p95_index = max(0, (95 * len(sorted_latencies) + 99) // 100 - 1)
    dataset_manifest = json.loads(
        (EVALUATION_DIR / "dataset-manifest.json").read_text(encoding="utf-8")
    )
    ## read the dataset manifest to include metadata in the evaluation results
    return {
        "manifest": {
            "dataset_version": dataset_manifest["dataset_version"],
            "corpus_version": dataset_manifest["corpus_version"],
            "embedding_model": None,
            "retrieval_strategy": "bm25",
            "indexing_strategy": "in-memory BM25",
            "chunking_strategy": "heading-aware recursive word-boundary",
            "reranker": None,
            "top_k": 3,
            "timestamp": datetime.now(UTC).isoformat(),
            "configuration_version": "1.0",
        },
        "classification": "synthetic smoke evaluation; not a learner benchmark",
        "case_count": len(cases),
        "retrieval_case_count": len(metric_rows),
        "metrics": averages,
        "latency_ms": {
            "mean": sum(latencies_ms) / len(latencies_ms),
            "p50": sorted_latencies[p50_index],
            "p95": sorted_latencies[p95_index],
            "max": max(latencies_ms),
        },
        "estimated_cost_usd_total": sum(estimated_costs_usd),
        "answer_metrics": {
            "citation_correctness": None,
            "groundedness": None,
            "reason": "retrieval-only smoke; no answer generation is performed",
        },
        "authorization_correctness": {
            "passed": all(auth_checks),
            "cases_passed": sum(auth_checks),
            "cases_total": len(auth_checks),
        },
        "cases": case_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the synthetic retrieval smoke set.")
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_evaluation()
    encoded = json.dumps(result, indent=2, sort_keys=True)
    ## write the evaluation results to the specified output file if provided
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(f"{encoded}\n", encoding="utf-8")
    print(encoded)


if __name__ == "__main__":
    main()

