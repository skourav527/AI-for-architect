from datetime import UTC, datetime

import pytest

from src.ingestion.chunker import chunk_document
from src.ingestion.models import Document, DocumentMetadata


def make_document(text: str) -> Document:
    return Document(
        source_id="guide.md",
        source_uri="guide.md",
        text=text,
        version="content-hash",
        last_modified=datetime(2026, 11, 12, tzinfo=UTC),
        metadata=DocumentMetadata(tenant_id="tenant-a", is_public=True),
    )


def test_chunks_are_bounded_provenance_bearing_and_deterministic():
    document = make_document("# Recovery\n\n" + "step " * 12)

    first = chunk_document(document, max_words=5, overlap_words=1)
    second = chunk_document(document, max_words=5, overlap_words=1)

    assert len(first) > 1
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert all(len(chunk.content.split()) <= 7 for chunk in first)
    assert all(chunk.section == "Recovery" for chunk in first)
    assert all(chunk.document_version == "content-hash" for chunk in first)
    assert all(chunk.parent_id == "guide.md:0" for chunk in first)


@pytest.mark.parametrize(
    ("max_words", "overlap_words"),
    [(0, 0), (5, -1), (5, 5)],
)
def test_rejects_invalid_chunk_limits(max_words, overlap_words):
    with pytest.raises(ValueError):
        chunk_document(
            make_document("Some text."),
            max_words=max_words,
            overlap_words=overlap_words,
        )

