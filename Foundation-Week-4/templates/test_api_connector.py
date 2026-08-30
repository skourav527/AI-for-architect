"""Day 4 tests: api_connector_mcp_server (unit tests, no real network calls)."""

import httpx
import pytest
from mcp.shared.exceptions import McpError

import api_connector_mcp_server as server


def _fake_response(status_code: int, json_body: dict, headers: dict | None = None) -> httpx.Response:
    return httpx.Response(status_code, json=json_body, headers=headers or {}, request=httpx.Request("GET", "http://test"))


def test_get_repository_success(monkeypatch):
    monkeypatch.setattr(server.http_client, "request", lambda *a, **k: _fake_response(200, {"full_name": "octo/repo"}))
    result = server.get_repository("octo", "repo")
    assert result["status"] == "success"
    assert result["data"]["full_name"] == "octo/repo"


def test_get_pull_request_not_found(monkeypatch):
    monkeypatch.setattr(server.http_client, "request", lambda *a, **k: _fake_response(404, {}))
    with pytest.raises(McpError) as excinfo:
        server.get_pull_request("octo", "repo", 1)
    assert excinfo.value.error.code == server.ErrorCode.RESOURCE_NOT_FOUND


def test_get_repository_auth_error(monkeypatch):
    monkeypatch.setattr(server.http_client, "request", lambda *a, **k: _fake_response(401, {}))
    with pytest.raises(McpError) as excinfo:
        server.get_repository("octo", "repo")
    assert excinfo.value.error.code == server.ErrorCode.AUTHORIZATION_ERROR


def test_list_pull_requests_invalid_state_rejected():
    with pytest.raises(McpError) as excinfo:
        server.list_pull_requests("octo", "repo", state="bogus")
    assert excinfo.value.error.code == server.ErrorCode.INVALID_PARAMS


def test_get_pull_request_invalid_number_rejected():
    with pytest.raises(McpError) as excinfo:
        server.get_pull_request("octo", "repo", 0)
    assert excinfo.value.error.code == server.ErrorCode.INVALID_PARAMS


def test_health_check_reports_healthy():
    result = server.health_check()
    assert result["status"] == "healthy"
    assert "timestamp_utc" in result


def test_metrics_counts_requests(monkeypatch):
    monkeypatch.setattr(server, "REQUEST_COUNTS", {"total": 0, "failed": 0})
    monkeypatch.setattr(server.http_client, "request", lambda *a, **k: _fake_response(200, {"full_name": "octo/repo"}))
    server.get_repository("octo", "repo")
    result = server.metrics()
    assert result["requests_total"] == 1
    assert result["requests_failed"] == 0
