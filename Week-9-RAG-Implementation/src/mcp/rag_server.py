from __future__ import annotations

from typing import Protocol

from mcp.server.mcpserver import Context, MCPServer

from src.retrieval.authorization import AuthorizationUnavailable
from src.retrieval.controller import RetrievalController
from src.retrieval.models import CallerIdentity, Outcome, SearchFilters, SearchQuery


class IdentityProvider(Protocol):
    """Resolve identity only from the authenticated host request context."""

    def from_context(self, context: Context) -> CallerIdentity: ...


def create_server(
    controller: RetrievalController, identity_provider: IdentityProvider
) -> MCPServer:
    """Create an MCP server; callers must supply their trusted identity adapter."""
    server = MCPServer("week-9-rag")

    @server.tool()
    async def search_knowledge(
        query_text: str,
        ctx: Context,
        top_k: int = 5,
        source_id: str | None = None,
        document_type: str | None = None,
    ) -> dict[str, object]:
        """Search authorized documents; caller identity is not a tool argument."""
        try:
            identity = identity_provider.from_context(ctx)
        except AuthorizationUnavailable:
            return {
                "outcome": Outcome.AUTHORIZATION_UNAVAILABLE.value,
                "results": [],
                "stop_reason": "authorization_unavailable",
            }

        response = controller.search(
            identity,
            SearchQuery(
                text=query_text,
                top_k=top_k,
                filters=SearchFilters(
                    source_id=source_id, document_type=document_type
                ),
            ),
        )
        return {
            "outcome": response.outcome.value,
            "stop_reason": response.stop_reason,
            "results": [
                {
                    "chunk_text": result.chunk.content,
                    "source_id": result.chunk.source_id,
                    "source_uri": result.chunk.source_uri,
                    "document_version": result.chunk.document_version,
                    "section": result.chunk.section,
                    "score": result.score,
                    "score_kind": result.score_kind,
                }
                for result in response.results
            ],
            "attempts": [
                {
                    "decision": attempt.decision,
                    "elapsed_ms": attempt.elapsed_ms,
                    "query_tokens": attempt.query_tokens,
                    "result_tokens": attempt.result_tokens,
                }
                for attempt in response.attempts
            ],
            "total_tokens": response.total_tokens,
            "estimated_cost_usd": response.estimated_cost_usd,
            "elapsed_ms": response.elapsed_ms,
            "tool_calls": response.tool_calls,
        }

    return server

