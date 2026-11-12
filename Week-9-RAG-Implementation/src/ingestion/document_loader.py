from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from src.ingestion.models import Document, DocumentMetadata

MetadataProvider = Callable[[str], DocumentMetadata]
SUPPORTED_SUFFIXES = {".md", ".txt"}


def load_documents(root: Path, metadata_provider: MetadataProvider) -> list[Document]:
    """Load Markdown/text files and require trusted ACL metadata for each source."""
    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError(f"document root is not a directory: {root}")

    documents: list[Document] = []
    for path in sorted(resolved_root.rglob("*")):
        if path.suffix.lower() not in SUPPORTED_SUFFIXES or not path.is_file():
            continue

        resolved_path = path.resolve(strict=True)
        if resolved_root not in resolved_path.parents:
            raise ValueError(f"document path escapes the configured root: {path}")

        source_id = path.relative_to(resolved_root).as_posix()
        text = resolved_path.read_text(encoding="utf-8")
        version = hashlib.sha256(text.encode("utf-8")).hexdigest()
        modified = datetime.fromtimestamp(
            resolved_path.stat().st_mtime, tz=UTC
        )
        metadata = metadata_provider(source_id)
        if not isinstance(metadata, DocumentMetadata):
            raise TypeError(f"metadata provider returned invalid ACL for {source_id}")
        documents.append(
            Document(
                source_id=source_id,
                source_uri=source_id,
                text=text,
                version=version,
                last_modified=modified,
                metadata=metadata,
            )
        )
    return documents

