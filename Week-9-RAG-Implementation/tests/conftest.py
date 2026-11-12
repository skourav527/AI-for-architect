from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.ingestion.chunker import chunk_document
from src.ingestion.models import Document, DocumentMetadata
from src.retrieval.authorization import StaticEntitlementResolver
from src.retrieval.bm25 import BM25Index
from src.retrieval.models import CallerIdentity, Entitlements


@pytest.fixture
def identity() -> CallerIdentity:
    return CallerIdentity(subject_id="alice", tenant_id="tenant-a")


@pytest.fixture
def entitlements() -> Entitlements:
    return Entitlements(
        subject_id="alice", tenant_id="tenant-a", groups=("engineering",)
    )


@pytest.fixture
def resolver(entitlements: Entitlements) -> StaticEntitlementResolver:
    return StaticEntitlementResolver({"alice": entitlements})


@pytest.fixture
def zero_cost():
    def estimate(_query: str) -> float:
        return 0.0

    return estimate


@pytest.fixture
def chunks():
    timestamp = datetime(2026, 11, 12, tzinfo=UTC)

    def create(
        source_id: str,
        text: str,
        *,
        tenant_id: str = "tenant-a",
        allowed_principals: tuple[str, ...] = (),
        allowed_groups: tuple[str, ...] = (),
        is_public: bool = False,
        document_type: str = "text/markdown",
    ):
        document = Document(
            source_id=source_id,
            source_uri=source_id,
            text=text,
            version=f"version-{source_id}",
            last_modified=timestamp,
            metadata=DocumentMetadata(
                tenant_id=tenant_id,
                allowed_principals=allowed_principals,
                allowed_groups=allowed_groups,
                is_public=is_public,
                document_type=document_type,
            ),
        )
        return chunk_document(document, max_words=200, overlap_words=0)

    return create


@pytest.fixture
def index(chunks):
    return BM25Index(
        chunks("public.md", "Runbook describes database backup recovery.", is_public=True)
        + chunks(
            "secret.md",
            "Payroll details for executives.",
            allowed_groups=("finance",),
        )
        + chunks(
            "other-tenant.md",
            "Database recovery procedures.",
            tenant_id="tenant-b",
            is_public=True,
        )
    )

