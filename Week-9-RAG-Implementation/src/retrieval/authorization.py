from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from src.ingestion.models import Chunk
from src.retrieval.models import CallerIdentity, Entitlements


class AuthorizationUnavailable(Exception):
    """Raised when trusted entitlements cannot be established."""


class EntitlementResolver(Protocol):
    def resolve(self, identity: CallerIdentity) -> Entitlements: ...


class StaticEntitlementResolver:
    """Small local adapter for tests; production must use authenticated identity."""

    def __init__(self, principals: Mapping[str, Entitlements]) -> None:
        self._principals = dict(principals)

    def resolve(self, identity: CallerIdentity) -> Entitlements:
        entitlements = self._principals.get(identity.subject_id)
        if (
            entitlements is None
            or entitlements.subject_id != identity.subject_id
            or entitlements.tenant_id != identity.tenant_id
        ):
            raise AuthorizationUnavailable("trusted entitlements are unavailable")
        return entitlements


def is_authorized(chunk: Chunk, entitlements: Entitlements) -> bool:
    if chunk.tenant_id != entitlements.tenant_id:
        return False
    if chunk.is_public:
        return True
    return (
        entitlements.subject_id in chunk.allowed_principals
        or bool(set(entitlements.groups).intersection(chunk.allowed_groups))
    )

