## This component is responsible for building chunks from documents.
## It ensures that each document has a unique source_id and splits the document
## into chunks based on the specified max_words and overlap_words.
## It returns a list of Chunk objects, ready for indexing or further processing.
## It is used internally by the document ingestion pipeline to prepare documents for indexing.

from __future__ import annotations

from collections.abc import Iterable

from src.ingestion.chunker import chunk_document
from src.ingestion.models import Chunk, Document


def build_chunks(
    documents: Iterable[Document], *, max_words: int = 180, overlap_words: int = 24
) -> list[Chunk]:
    chunks: list[Chunk] = []
    seen_sources: set[str] = set()
    for document in documents:
        if document.source_id in seen_sources:
            raise ValueError(f"duplicate source_id: {document.source_id}")
        seen_sources.add(document.source_id)
        chunks.extend(
            chunk_document(
                document, max_words=max_words, overlap_words=overlap_words
            )
        )
    return chunks

