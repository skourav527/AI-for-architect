import asyncio

from src.mcp.rag_server import create_server
from src.retrieval.authorization import AuthorizationUnavailable
from src.retrieval.controller import RetrievalController
from src.retrieval.models import CallerIdentity, Outcome


def zero_cost(_query):
    return 0.0


class FixtureIdentityProvider:
    def from_context(self, _context):
        return CallerIdentity(subject_id="alice", tenant_id="tenant-a")


class MissingIdentityProvider:
    def from_context(self, _context):
        raise AuthorizationUnavailable("no authenticated principal")


def test_mcp_tool_schema_does_not_accept_identity(index, resolver):
    server = create_server(
        RetrievalController(index, resolver, estimate_cost=zero_cost),
        FixtureIdentityProvider(),
    )
    tool = asyncio.run(server.list_tools())[0]

    assert tool.name == "search_knowledge"
    assert "query_text" in tool.input_schema["properties"]
    assert "identity" not in tool.input_schema["properties"]
    assert "tenant_id" not in tool.input_schema["properties"]


def test_mcp_tool_returns_typed_authorization_failure(index, resolver):
    server = create_server(
        RetrievalController(index, resolver, estimate_cost=zero_cost),
        MissingIdentityProvider(),
    )
    response = asyncio.run(
        server.call_tool("search_knowledge", {"query_text": "payroll"})
    )

    assert response.structured_content["outcome"] == Outcome.AUTHORIZATION_UNAVAILABLE
    assert response.structured_content["results"] == []


def test_mcp_tool_uses_host_identity_for_authorized_search(index, resolver):
    server = create_server(
        RetrievalController(index, resolver, estimate_cost=zero_cost),
        FixtureIdentityProvider(),
    )
    response = asyncio.run(
        server.call_tool("search_knowledge", {"query_text": "database recovery"})
    )

    assert response.structured_content["outcome"] == Outcome.OK
    assert response.structured_content["results"][0]["source_id"] == "public.md"
    assert response.structured_content["tool_calls"] == 1
