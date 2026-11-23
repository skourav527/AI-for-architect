## This component is responsible for splitting documents into chunks based on word count.
## It ensures that each chunk has a deterministic ID and maintains provenance information.
## It returns a list of Chunk objects, each representing a portion of the document.
## It is used internally by the document ingestion pipeline to prepare documents for indexing.

from __future__ import annotations

import hashlib
import re

from src.ingestion.models import Chunk, Document
from src.ingestion.parser import ParsedSection, parse_document


def _paragraphs(section: ParsedSection, max_words: int) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    for paragraph in re.split(r"\n\s*\n", section.text):
        words = paragraph.split()
        while len(words) > max_words:
            if current:
                result.append(current)
                current = []
            result.append(words[:max_words])
            words = words[max_words:]
        if words and current and len(current) + len(words) > max_words:
            result.append(current)
            current = []
        current.extend(words)
    if current:
        result.append(current)
    return result


def chunk_document(
    document: Document, *, max_words: int = 180, overlap_words: int = 24
) -> list[Chunk]:
    """Create deterministic, provenance-bearing recursive word-boundary chunks."""
    if max_words < 1:
        raise ValueError("max_words must be at least 1")
    if overlap_words < 0 or overlap_words >= max_words:
        raise ValueError("overlap_words must be between 0 and max_words - 1")

    chunks: list[Chunk] = []
    for section_index, section in enumerate(parse_document(document.text)):
        pieces = _paragraphs(section, max_words)
        prior_words: list[str] = []
        for chunk_index, piece in enumerate(pieces):
            words = prior_words + piece if chunk_index else piece
            body = " ".join(words)
            content = f"{section.heading}\n\n{body}" if section.heading else body
            digest = hashlib.sha256(
                f"{document.source_id}\0{document.version}\0{section_index}\0"
                f"{chunk_index}\0{content}".encode()
            ).hexdigest()[:24]
            chunks.append(
                Chunk(
                    chunk_id=digest,
                    content=content,
                    source_id=document.source_id,
                    source_uri=document.source_uri,
                    parent_id=f"{document.source_id}:{section_index}",
                    section=section.heading,
                    document_version=document.version,
                    last_modified=document.last_modified,
                    tenant_id=document.metadata.tenant_id,
                    allowed_principals=document.metadata.allowed_principals,
                    allowed_groups=document.metadata.allowed_groups,
                    is_public=document.metadata.is_public,
                    document_type=document.metadata.document_type,
                )
            )
            prior_words = piece[-overlap_words:] if overlap_words else []
    return chunks

