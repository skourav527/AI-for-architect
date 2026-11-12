from src.retrieval.bm25 import BM25Index
from src.retrieval.dense import DenseIndex
from src.retrieval.hybrid import HybridIndex
from src.retrieval.models import SearchFilters, SearchQuery, SearchScope


def test_bm25_retrieves_relevant_public_chunk(index, entitlements, identity):
    results = index.search(
        SearchScope(
            identity=identity,
            entitlements=entitlements,
            query=SearchQuery("database backup recovery"),
        ),
        top_k=3,
    )

    assert results
    assert results[0].chunk.source_id == "public.md"
    assert results[0].score_kind == "bm25"


def test_metadata_filter_only_narrows_authorized_scope(
    chunks, entitlements, identity
):
    index = BM25Index(
        chunks(
            "runbook.md", "Database recovery", is_public=True, document_type="runbook"
        )
        + chunks(
            "secret.md",
            "Database recovery",
            allowed_groups=("finance",),
            document_type="runbook",
        )
    )
    results = index.search(
        SearchScope(
            identity=identity,
            entitlements=entitlements,
            query=SearchQuery(
                "database recovery",
                filters=SearchFilters(document_type="runbook"),
            ),
        ),
        top_k=5,
    )

    assert {item.chunk.source_id for item in results} == {"runbook.md"}


class FixedEmbedder:
    model_id = "test-fixture-v1"

    def embed(self, text):
        if "database" in text.casefold():
            return (1.0, 0.0)
        return (0.0, 1.0)


def test_dense_retrieval_uses_provider_vectors_and_enforces_acl(
    chunks, entitlements, identity
):
    documents = chunks("database.md", "database recovery", is_public=True)
    documents += chunks(
        "payroll.md",
        "database finance",
        allowed_groups=("finance",),
    )
    index = DenseIndex(documents, FixedEmbedder())

    results = index.search(
        SearchScope(
            identity=identity,
            entitlements=entitlements,
            query=SearchQuery("database"),
        ),
        top_k=5,
    )

    assert [item.chunk.source_id for item in results] == ["database.md"]
    assert results[0].score_kind == "cosine:test-fixture-v1"


def test_hybrid_fuses_keyword_and_dense_ranks(
    chunks, entitlements, identity
):
    documents = chunks("database.md", "database recovery", is_public=True)
    keyword = BM25Index(documents)
    dense = DenseIndex(documents, FixedEmbedder())
    hybrid = HybridIndex(keyword, dense)
    scope = SearchScope(
        identity=identity,
        entitlements=entitlements,
        query=SearchQuery("database recovery"),
    )

    results = hybrid.search(scope, top_k=1)

    assert len(results) == 1
    assert results[0].score_kind == "reciprocal_rank_fusion"

