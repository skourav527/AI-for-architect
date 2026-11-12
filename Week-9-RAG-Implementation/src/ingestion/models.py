from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DocumentMetadata:
    tenant_id: str
    allowed_principals: tuple[str, ...] = ()
    allowed_groups: tuple[str, ...] = ()
    is_public: bool = False
    document_type: str = "text/markdown"

    def __post_init__(self) -> None:
        if not self.tenant_id.strip():
            raise ValueError("tenant_id must not be empty")
        if not self.document_type.strip():
            raise ValueError("document_type must not be empty")
        if not self.is_public and not (
            self.allowed_principals or self.allowed_groups
        ):
            raise ValueError(
                "non-public documents must declare at least one principal or group"
            )


@dataclass(frozen=True)
class Document:
    source_id: str
    source_uri: str
    text: str
    version: str
    last_modified: datetime
    metadata: DocumentMetadata


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    content: str
    source_id: str
    source_uri: str
    parent_id: str
    section: str
    document_version: str
    last_modified: datetime
    tenant_id: str
    allowed_principals: tuple[str, ...]
    allowed_groups: tuple[str, ...]
    is_public: bool
    document_type: str

