"""MCP Server Template: MongoDB Connector (Production Pattern)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional, Union

from bson import ObjectId
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient
from pymongo.errors import PyMongoError, WaitQueueTimeoutError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("mongodb_mcp")

Scalar = Union[str, int, float, bool, None]
CollectionName = Literal["users", "orders", "products", "Test"]
MAX_DOCUMENT_NESTING = 10
MAX_ARRAY_ITEMS = 1_000

# The client can only query or write these fields using simple equality values.
ALLOWED_FIELDS: dict[str, set[str]] = {
    "users": {"email", "name", "status"},
    "orders": {"order_id", "user_id", "status", "total"},
    "products": {"sku", "name", "category", "price", "stock"},
    "Test": {
        "BasinCode", "BusinessFunctions", "BusinessLines", "Capabilities", "City",
        "ClientFacility", "Country", "Distance", "EntityType", "FacilityCommonId",
        "FacilityStatus", "FacilityType", "FmdCommonId", "GeoUnitCode", "GeositeId",
        "GeositeName", "Id", "Location", "MailingAddress", "Name", "State", "Timezone",
        "WorkCenterId",
    },
}


class Settings(BaseSettings):
    """Settings for one low-concurrency learning server; tune after measuring production traffic."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = Field(default="mongodb://localhost:27017")
    mongodb_database: str = Field(default="mcp_learning")
    mongo_max_pool_size: int = Field(default=10, ge=1, le=100)
    mongo_min_pool_size: int = Field(default=0, ge=0, le=100)
    mongo_wait_queue_timeout_ms: int = Field(default=5_000, ge=100)
    mongo_server_selection_timeout_ms: int = Field(default=5_000, ge=100)
    mongo_connect_timeout_ms: int = Field(default=5_000, ge=100)
    mongo_socket_timeout_ms: int = Field(default=30_000, ge=100)
    mongo_max_idle_time_ms: int = Field(default=300_000, ge=1_000)
    mongo_query_timeout_ms: int = Field(default=5_000, ge=100)
    writes_enabled: bool = Field(default=False)


settings = Settings()

mongo_client: Optional[MongoClient] = None
OPERATION_COUNTS = {"total": 0, "failed": 0}


def get_database() -> Any:
    """Create one pooled client on first database use, not while the module imports."""
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(
            settings.mongodb_uri,
            maxPoolSize=settings.mongo_max_pool_size,
            minPoolSize=settings.mongo_min_pool_size,
            waitQueueTimeoutMS=settings.mongo_wait_queue_timeout_ms,
            serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
            connectTimeoutMS=settings.mongo_connect_timeout_ms,
            socketTimeoutMS=settings.mongo_socket_timeout_ms,
            maxIdleTimeMS=settings.mongo_max_idle_time_ms,
        )
    return mongo_client[settings.mongodb_database]

mcp = FastMCP(
    "MongoDBConnector",
    log_level="INFO",
    host="127.0.0.1",
    port=8000,
)


class ErrorCode:
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    DATABASE_ERROR = -32004
    AUTHORIZATION_ERROR = -32002


class QueryInput(BaseModel):
    collection: CollectionName
    filters: Optional[dict[str, Scalar]] = Field(default=None, description="Allowed equality filters")
    limit: int = Field(default=100, ge=1, le=1_000)

    @field_validator("filters")
    @classmethod
    def reject_mongo_operators(cls, filters: Optional[dict[str, Scalar]]) -> Optional[dict[str, Scalar]]:
        if filters is None:
            return filters
        if any(field.startswith("$") or "." in field for field in filters):
            raise ValueError("MongoDB operators and dotted field paths are not allowed")
        return filters

    @model_validator(mode="after")
    def validate_filter_fields(self) -> "QueryInput":
        invalid_fields = set(self.filters or {}) - ALLOWED_FIELDS[self.collection]
        if invalid_fields:
            raise ValueError(f"Fields not allowed for {self.collection}: {sorted(invalid_fields)}")
        return self


class InsertInput(BaseModel):
    collection: CollectionName
    data: dict[str, Any] = Field(..., min_length=1, description="Allowed JSON document fields")

    @field_validator("data")
    @classmethod
    def validate_document_values(cls, data: dict[str, Any]) -> dict[str, Any]:
        _validate_json_document(data)
        return data

    @model_validator(mode="after")
    def validate_document_fields(self) -> "InsertInput":
        invalid_fields = set(self.data) - ALLOWED_FIELDS[self.collection]
        if invalid_fields:
            raise ValueError(f"Fields not allowed for {self.collection}: {sorted(invalid_fields)}")
        return self


def _validate_json_document(value: Any, depth: int = 0) -> None:
    """Allow JSON-like write values while blocking unsafe MongoDB field names."""
    if depth > MAX_DOCUMENT_NESTING:
        raise ValueError(f"Document nesting cannot exceed {MAX_DOCUMENT_NESTING} levels")
    if isinstance(value, dict):
        for field, nested_value in value.items():
            if not isinstance(field, str) or field.startswith("$") or "." in field:
                raise ValueError("MongoDB operators and dotted field paths are not allowed")
            _validate_json_document(nested_value, depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_ARRAY_ITEMS:
            raise ValueError(f"Arrays cannot contain more than {MAX_ARRAY_ITEMS} items")
        for item in value:
            _validate_json_document(item, depth + 1)
    elif not isinstance(value, (str, int, float, bool, type(None))):
        raise ValueError("Document values must be JSON-compatible scalars, arrays, or objects")


def _serialize_document(value: Any) -> Any:
    """Convert MongoDB-specific values into JSON-compatible MCP response values."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize_document(nested_value) for key, nested_value in value.items()}
    if isinstance(value, list):
        return [_serialize_document(item) for item in value]
    return value


def audit_log(request_id: str, operation: str, collection: str, actor: str = "system", **details: Any) -> None:
    """Log metadata only. Never write secret or document values to logs."""
    OPERATION_COUNTS["total"] += 1
    logger.info(
        "database_operation request_id=%s actor=%s operation=%s collection=%s details=%s",
        request_id,
        actor,
        operation,
        collection,
        details,
    )


def _validation_error(request_id: str, error: Exception) -> dict[str, Any]:
    logger.warning("validation_failed request_id=%s error=%s", request_id, error)
    return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(error)}}


def _database_error(request_id: str, error: Exception) -> dict[str, Any]:
    OPERATION_COUNTS["failed"] += 1
    logger.exception("database_error request_id=%s", request_id)
    message = "Database connection pool is busy" if isinstance(error, WaitQueueTimeoutError) else "Database operation failed"
    return {"error": {"code": ErrorCode.DATABASE_ERROR, "message": message}}


@mcp.tool(name="find_documents", description="Read documents using approved equality filters")
def find_documents(
    collection: str,
    filters: Optional[dict[str, Scalar]] = None,
    limit: int = 100,
    actor: str = "system",
) -> dict[str, Any]:
    """Arbitrary MongoDB queries are intentionally unsupported."""
    request_id = str(uuid.uuid4())
    try:
        validated = QueryInput(collection=collection, filters=filters, limit=limit)
    except Exception as error:
        return _validation_error(request_id, error)

    audit_log(request_id, "FIND", validated.collection, actor, limit=validated.limit)
    try:
        cursor = get_database()[validated.collection].find(
            validated.filters or {},
            max_time_ms=settings.mongo_query_timeout_ms,
        ).limit(validated.limit)
        documents = [_serialize_document(document) for document in cursor]
        logger.info("query_succeeded request_id=%s documents_returned=%s", request_id, len(documents))
        return {"data": documents, "count": len(documents), "status": "success", "request_id": request_id}
    except PyMongoError as error:
        return _database_error(request_id, error)


@mcp.tool(name="insert_document", description="Insert one approved document when writes are enabled")
def insert_document(collection: str, data: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    """Keep writes separate from reads; authenticate actor upstream in real deployments."""
    request_id = str(uuid.uuid4())
    try:
        validated = InsertInput(collection=collection, data=data)
    except Exception as error:
        return _validation_error(request_id, error)

    if not settings.writes_enabled:
        audit_log(request_id, "INSERT_DENIED", validated.collection, actor)
        return {"error": {"code": ErrorCode.AUTHORIZATION_ERROR, "message": "Writes are disabled for this server"}}

    audit_log(request_id, "INSERT", validated.collection, actor)
    try:
        result = get_database()[validated.collection].insert_one(validated.data)
        logger.info("insert_succeeded request_id=%s collection=%s", request_id, validated.collection)
        return {"status": "success", "inserted_id": str(result.inserted_id), "request_id": request_id}
    except PyMongoError as error:
        return _database_error(request_id, error)


@mcp.tool(name="insert_documents_transaction", description="Insert approved documents atomically when transactions are available")
def insert_documents_transaction(collection: str, documents: list[dict[str, Any]], actor: str = "system") -> dict[str, Any]:
    """Transactions require a replica set or sharded cluster, not standalone MongoDB."""
    request_id = str(uuid.uuid4())
    if not settings.writes_enabled:
        return {"error": {"code": ErrorCode.AUTHORIZATION_ERROR, "message": "Writes are disabled for this server"}}
    if not 1 <= len(documents) <= 100:
        return _validation_error(request_id, ValueError("documents must contain between 1 and 100 items"))

    try:
        validated_documents = [InsertInput(collection=collection, data=document).data for document in documents]
        validated_collection = QueryInput(collection=collection, limit=1).collection
    except Exception as error:
        return _validation_error(request_id, error)

    audit_log(request_id, "TRANSACTIONAL_INSERT", validated_collection, actor, document_count=len(validated_documents))
    try:
        get_database()
        with mongo_client.start_session() as session:
            with session.start_transaction():
                result = get_database()[validated_collection].insert_many(validated_documents, session=session)
        return {"status": "success", "inserted_count": len(result.inserted_ids), "request_id": request_id}
    except PyMongoError as error:
        return _database_error(request_id, error)


@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict[str, Any]:
    """Check MongoDB connectivity with a small ping command."""
    try:
        get_database().client.admin.command("ping", maxTimeMS=settings.mongo_query_timeout_ms)
        database_status = "connected"
    except PyMongoError:
        database_status = "disconnected"
    return {
        "status": "healthy" if database_status == "connected" else "degraded",
        "service": "MongoDBConnector",
        "database": database_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.resource("metrics://stats", mime_type="application/json")
def metrics() -> dict[str, Any]:
    """Basic in-process counters; wire into Prometheus for real deployments."""
    return {"operations_total": OPERATION_COUNTS["total"], "operations_failed": OPERATION_COUNTS["failed"]}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")