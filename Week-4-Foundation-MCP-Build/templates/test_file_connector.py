"""Day 4 tests: file_connector_mcp_server (real filesystem, isolated tmp_path)."""

import pytest

import file_connector_mcp_server as server


@pytest.fixture(autouse=True)
def isolated_root(tmp_path, monkeypatch):
    (tmp_path / "sample.txt").write_text("hello plan content", encoding="utf-8")
    monkeypatch.setattr(server, "ALLOWED_ROOTS", [tmp_path.resolve()])
    return tmp_path


def test_read_file_success():
    result = server.read_file("sample.txt")
    assert result["status"] == "success"
    assert "hello" in result["content"]


def test_read_file_not_found():
    result = server.read_file("missing.txt")
    assert result["error"]["code"] == server.ErrorCode.FILE_NOT_FOUND


def test_read_file_blocks_path_traversal():
    result = server.read_file("../secret.txt")
    assert result["error"]["code"] == server.ErrorCode.AUTHORIZATION_ERROR


def test_read_file_rejects_oversized(monkeypatch):
    monkeypatch.setattr(server.settings, "max_file_size_mb", 0)
    result = server.read_file("sample.txt")
    assert result["error"]["code"] == server.ErrorCode.FILE_TOO_LARGE


def test_search_files_finds_content_match():
    result = server.search_files("plan")
    assert result["count"] == 1
    assert result["results"][0]["path"] == "sample.txt"


def test_health_check_reports_healthy():
    result = server.health_check()
    assert result["status"] == "healthy"
    assert result["roots_accessible"] == 1


def test_metrics_counts_files():
    result = server.metrics()
    assert result["files_total"] == 1
