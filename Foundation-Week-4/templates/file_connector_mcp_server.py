"""MCP Server Template: File/RAG Connector (Stateless Production Pattern)."""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("file_mcp")

TEXT_SUFFIXES = {".txt", ".md", ".py", ".json"}
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    """Root paths and limits are configuration, never hardcoded."""

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    allowed_roots: str = Field(default="./data")
    max_file_size_mb: int = Field(default=10, ge=1, le=500)
    chunk_size_bytes: int = Field(default=1_048_576, ge=1_024)


settings = Settings()
ALLOWED_ROOTS = [Path(root.strip()).resolve() for root in settings.allowed_roots.split(",")]


def resolve_safe_path(file_path: str) -> Optional[Path]:
    """Reject traversal and return the resolved path only if inside an allowed root."""
    if ".." in file_path or Path(file_path).is_absolute():
        return None
    for root in ALLOWED_ROOTS:
        candidate = (root / file_path).resolve()
        if candidate.is_relative_to(root):
            return candidate
    return None


# Stateless HTTP: no session state kept in server memory, so any instance can serve any request.
mcp = FastMCP(
    "FileSystemConnector",
    log_level="INFO",
    host="127.0.0.1",
    port=8000,
    stateless_http=True,
)


class ErrorCode:
    INVALID_PARAMS = -32602
    FILE_NOT_FOUND = -32003
    AUTHORIZATION_ERROR = -32002
    FILE_TOO_LARGE = -32005
    INTERNAL_ERROR = -32603


class ReadFileInput(BaseModel):
    file_path: str = Field(..., min_length=1, max_length=500)


class SearchFilesInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    max_results: int = Field(default=10, ge=1, le=100)

    @field_validator("query")
    @classmethod
    def reject_control_chars(cls, value: str) -> str:
        if any(ord(char) < 32 for char in value):
            raise ValueError("Query contains invalid control characters")
        return value


def _validation_error(request_id: str, error: Exception) -> dict[str, Any]:
    logger.warning("validation_failed request_id=%s error=%s", request_id, error)
    return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(error)}}


@mcp.tool(name="read_file", description="Read a text file's contents from an allowed root only")
def read_file(file_path: str) -> dict[str, Any]:
    """Root enforcement plus a size limit keeps this tool safe and memory-bounded."""
    request_id = str(uuid.uuid4())
    try:
        validated = ReadFileInput(file_path=file_path)
    except Exception as error:
        return _validation_error(request_id, error)

    resolved = resolve_safe_path(validated.file_path)
    if resolved is None:
        logger.warning("path_traversal_blocked request_id=%s path=%s", request_id, file_path)
        return {"error": {"code": ErrorCode.AUTHORIZATION_ERROR, "message": "Path outside allowed roots"}}

    if not resolved.exists():
        return {"error": {"code": ErrorCode.FILE_NOT_FOUND, "message": f"File not found: {file_path}"}}

    size_mb = resolved.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        return {"error": {"code": ErrorCode.FILE_TOO_LARGE, "message": f"File too large: {size_mb:.2f}MB (max {settings.max_file_size_mb}MB)"}}

    try:
        # Chunked read bounds memory use even under the size limit.
        chunks = []
        with resolved.open("r", encoding="utf-8") as handle:
            while chunk := handle.read(settings.chunk_size_bytes):
                chunks.append(chunk)
        content = "".join(chunks)
    except UnicodeDecodeError:
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": "File is not text (binary file not supported)"}}
    except OSError as error:
        logger.exception("file_read_error request_id=%s", request_id)
        return {"error": {"code": ErrorCode.INTERNAL_ERROR, "message": "Failed to read file"}}

    logger.info("file_read_succeeded request_id=%s path=%s size_bytes=%s", request_id, file_path, len(content))
    return {"content": content, "file_path": file_path, "size_bytes": len(content), "status": "success", "request_id": request_id}


@mcp.tool(name="search_files", description="Search filenames and text content across allowed roots")
def search_files(query: str, max_results: int = 10) -> dict[str, Any]:
    """Simple in-memory scan; swap for an external search index at larger scale."""
    request_id = str(uuid.uuid4())
    try:
        validated = SearchFilesInput(query=query, max_results=max_results)
    except Exception as error:
        return _validation_error(request_id, error)

    results = []
    for root in ALLOWED_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if len(results) >= validated.max_results:
                break
            if not path.is_file():
                continue
            if validated.query.lower() in path.name.lower():
                results.append({"path": str(path.relative_to(root)), "match_type": "filename"})
                continue
            if path.suffix in TEXT_SUFFIXES:
                try:
                    if validated.query.lower() in path.read_text(encoding="utf-8").lower():
                        results.append({"path": str(path.relative_to(root)), "match_type": "content"})
                except (OSError, UnicodeDecodeError):
                    continue

    logger.info("search_succeeded request_id=%s query=%s count=%s", request_id, query, len(results))
    return {"results": results, "count": len(results), "status": "success", "request_id": request_id}


@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict[str, Any]:
    """Stateless check: no server memory to inspect, only root accessibility."""
    accessible = sum(1 for root in ALLOWED_ROOTS if root.exists())
    return {
        "status": "healthy" if accessible > 0 else "degraded",
        "service": "FileSystemConnector",
        "roots_accessible": accessible,
        "roots_total": len(ALLOWED_ROOTS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.resource("metrics://stats", mime_type="application/json")
def metrics() -> dict[str, Any]:
    """Basic counters; wire into Prometheus for real deployments."""
    total_files = 0
    total_size = 0
    for root in ALLOWED_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                total_files += 1
                total_size += path.stat().st_size
    return {"files_total": total_files, "storage_bytes_total": total_size, "roots_count": len(ALLOWED_ROOTS)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
