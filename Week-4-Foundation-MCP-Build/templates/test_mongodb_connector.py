"""Day 4 tests: mongodb_connector_mcp_server (unit tests, no real MongoDB needed)."""

from unittest.mock import MagicMock

import mongodb_connector_mcp_server as server


class FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    def limit(self, _n):
        return self

    def __iter__(self):
        return iter(self._docs)


def _fake_db(docs=None, inserted_id="507f1f77bcf86cd799439011"):
    collection = MagicMock()
    collection.find.return_value = FakeCursor(docs or [])
    collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)
    db = MagicMock()
    db.__getitem__.return_value = collection
    return db


def test_find_documents_success(monkeypatch):
    monkeypatch.setattr(server, "get_database", lambda: _fake_db(docs=[{"City": "Addison"}]))
    result = server.find_documents(collection="Test", filters={"City": "Addison"}, limit=10)
    assert result["status"] == "success"
    assert result["count"] == 1


def test_find_documents_rejects_mongo_operator():
    result = server.find_documents(collection="Test", filters={"$where": "1==1"})
    assert result["error"]["code"] == server.ErrorCode.INVALID_PARAMS


def test_find_documents_rejects_unknown_field():
    result = server.find_documents(collection="Test", filters={"not_allowed": "x"})
    assert result["error"]["code"] == server.ErrorCode.INVALID_PARAMS


def test_insert_document_denied_by_default(monkeypatch):
    monkeypatch.setattr(server.settings, "writes_enabled", False)
    result = server.insert_document(collection="Test", data={"City": "Addison"})
    assert result["error"]["code"] == server.ErrorCode.AUTHORIZATION_ERROR


def test_insert_document_succeeds_when_enabled(monkeypatch):
    monkeypatch.setattr(server.settings, "writes_enabled", True)
    monkeypatch.setattr(server, "get_database", lambda: _fake_db())
    result = server.insert_document(collection="Test", data={"City": "Addison"})
    assert result["status"] == "success"
    assert "inserted_id" in result


def test_insert_document_rejects_nested_operator(monkeypatch):
    monkeypatch.setattr(server.settings, "writes_enabled", True)
    result = server.insert_document(collection="Test", data={"Location": {"$where": "x"}})
    assert result["error"]["code"] == server.ErrorCode.INVALID_PARAMS


def test_metrics_counts_operations(monkeypatch):
    monkeypatch.setattr(server, "OPERATION_COUNTS", {"total": 0, "failed": 0})
    monkeypatch.setattr(server, "get_database", lambda: _fake_db())
    server.find_documents(collection="Test", filters={"City": "Addison"})
    result = server.metrics()
    assert result["operations_total"] == 1
