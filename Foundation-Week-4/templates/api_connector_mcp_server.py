"""Day-1 MCP server template for a real REST API (GitHub by default).

Production patterns included:
1) Streamable HTTP transport
2) Error taxonomy mapped to JSON-RPC errors
3) Structured logging with correlation IDs
4) Timeout + retry for external API calls
5) Basic rate-limit awareness from response headers
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, wait_exponential


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s correlation_id=%(correlation_id)s %(message)s",
)
logger = logging.getLogger("github_api_mcp")


class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        return True


for _handler in logging.getLogger().handlers:
    _handler.addFilter(CorrelationIdFilter())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_base_url: str = Field(default="https://api.github.com")
    github_token: str = Field(default="")
    api_timeout_seconds: int = Field(default=20, ge=1, le=120)
    max_retries: int = Field(default=3, ge=1, le=6)
    user_agent: str = Field(default="ai-for-architect-mcp-day1")


settings = Settings()

mcp = FastMCP("GitHubWorkAPI", log_level="INFO")


class ErrorCode:
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    EXTERNAL_API_ERROR = -32001
    AUTHORIZATION_ERROR = -32002
    RESOURCE_NOT_FOUND = -32003
    RATE_LIMITED = -32004


class APIConnectorError(Exception):
    """Base external API error."""


class APITimeoutError(APIConnectorError):
    """Request timed out."""


class APIAuthorizationError(APIConnectorError):
    """401 or 403 response."""


class APINotFoundError(APIConnectorError):
    """404 response."""


class APIRateLimitError(APIConnectorError):
    """Rate limit was reached."""


class APIClientError(APIConnectorError):
    """Other 4xx response errors."""


class APIServerError(APIConnectorError):
    """5xx response errors."""


class ResourcePath(BaseModel):
    resource: str = Field(..., min_length=1, max_length=256)

    @field_validator("resource")
    @classmethod
    def validate_resource(cls, value: str) -> str:
        if value.startswith("/") or ".." in value:
            raise ValueError("Invalid resource path")
        return value


def _log(correlation_id: str) -> logging.LoggerAdapter:
    return logging.LoggerAdapter(logger, extra={"correlation_id": correlation_id})


def _jsonrpc_error(code: int, message: str, correlation_id: str, details: Optional[dict[str, Any]] = None) -> McpError:
    data = {"correlation_id": correlation_id}
    if details:
        data.update(details)
    return McpError(ErrorData(code=code, message=message, data=data))


def _rate_limit_retry_after_seconds(response: httpx.Response) -> Optional[int]:
    reset_at = response.headers.get("x-ratelimit-reset")
    if reset_at and reset_at.isdigit():
        return max(0, int(reset_at) - int(time.time()))
    return None


def _raise_for_status_code(status_code: int) -> None:
    if status_code in (401, 403):
        raise APIAuthorizationError("Authorization failed for external API")
    if status_code == 404:
        raise APINotFoundError("Resource not found")
    if 400 <= status_code < 500:
        raise APIClientError(f"Client error from external API: {status_code}")
    if status_code >= 500:
        raise APIServerError(f"Server error from external API: {status_code}")
    raise APIConnectorError(f"Unexpected status code: {status_code}")


def _map_known_error(exc: Exception, correlation_id: str) -> tuple[int, str, str, str]:
    if isinstance(exc, APITimeoutError):
        return logging.ERROR, "api_timeout", ErrorCode.EXTERNAL_API_ERROR, "External API timeout"
    if isinstance(exc, APIRateLimitError):
        return logging.WARNING, "api_rate_limited", ErrorCode.RATE_LIMITED, str(exc)
    if isinstance(exc, APIAuthorizationError):
        return logging.ERROR, "api_auth_error", ErrorCode.AUTHORIZATION_ERROR, "Authorization failed. Check token and scopes."
    if isinstance(exc, APINotFoundError):
        return logging.INFO, "api_not_found", ErrorCode.RESOURCE_NOT_FOUND, "Requested resource was not found"
    if isinstance(exc, APIClientError):
        return logging.WARNING, "api_client_error", ErrorCode.INVALID_PARAMS, str(exc)
    if isinstance(exc, APIServerError):
        return logging.ERROR, "api_server_error", ErrorCode.EXTERNAL_API_ERROR, str(exc)
    if isinstance(exc, APIConnectorError):
        return logging.ERROR, "api_connector_error", ErrorCode.EXTERNAL_API_ERROR, str(exc)
    raise TypeError("Unsupported exception type for mapping")


def _build_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": settings.user_agent,
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


http_client = httpx.Client(
    base_url=settings.api_base_url,
    timeout=httpx.Timeout(settings.api_timeout_seconds),
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    headers=_build_headers(),
)


@retry(
    retry=retry_if_exception_type((APITimeoutError, APIServerError, APIRateLimitError)),
    wait=wait_exponential(multiplier=1, min=1, max=12),
    stop=stop_after_attempt(settings.max_retries),
    reraise=True,
)
def _request_with_retry(
    method: str,
    path: str,
    correlation_id: str,
    *,
    params: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    log = _log(correlation_id)

    try:
        response = http_client.request(method, path, params=params)
    except httpx.TimeoutException as exc:
        raise APITimeoutError("External API request timed out") from exc
    except httpx.RequestError as exc:
        raise APIConnectorError(f"Network error: {exc}") from exc

    if response.headers.get("x-ratelimit-remaining") == "0":
        retry_after_seconds = _rate_limit_retry_after_seconds(response)
        raise APIRateLimitError(
            f"Rate limit reached. retry_after_seconds={retry_after_seconds if retry_after_seconds is not None else 'unknown'}"
        )

    if 200 <= response.status_code < 300:
        return response.json()

    log.warning("external_api_http_error", extra={"status_code": response.status_code, "path": path})

    _raise_for_status_code(response.status_code)


def _safe_api_call(method: str, path: str, *, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    correlation_id = str(uuid.uuid4())
    log = _log(correlation_id)

    log.info("api_call_start", extra={"method": method, "path": path, "params": params or {}})

    try:
        payload = _request_with_retry(method, path, correlation_id, params=params)
        log.info("api_call_success", extra={"method": method, "path": path})
        return {
            "correlation_id": correlation_id,
            "status": "success",
            "data": payload,
        }
    except RetryError as exc:
        log.error("api_retry_exhausted", extra={"error": str(exc)})
        raise _jsonrpc_error(
            ErrorCode.EXTERNAL_API_ERROR,
            "External API failed after retries",
            correlation_id,
        ) from exc
    except (APITimeoutError, APIRateLimitError, APIAuthorizationError, APINotFoundError, APIClientError, APIServerError, APIConnectorError) as exc:
        level, event, error_code, message = _map_known_error(exc, correlation_id)
        log.log(level, event, extra={"error": str(exc)})
        raise _jsonrpc_error(error_code, message, correlation_id) from exc
    except Exception as exc:  # pragma: no cover
        log.exception("unexpected_server_error")
        raise _jsonrpc_error(
            ErrorCode.INTERNAL_ERROR,
            "Internal server error",
            correlation_id,
        ) from exc


@mcp.tool(name="get_repository", description="Get a GitHub repository by owner and repo name")
def get_repository(owner: str, repo: str) -> dict[str, Any]:
    ResourcePath(resource=f"repos/{owner}/{repo}")
    return _safe_api_call("GET", f"/repos/{owner}/{repo}")


@mcp.tool(name="list_pull_requests", description="List pull requests for a repository")
def list_pull_requests(owner: str, repo: str, state: str = "open", per_page: int = 20) -> dict[str, Any]:
    if state not in {"open", "closed", "all"}:
        raise _jsonrpc_error(ErrorCode.INVALID_PARAMS, "state must be one of: open, closed, all", "validation")
    per_page = max(1, min(per_page, 100))
    return _safe_api_call(
        "GET",
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "per_page": per_page},
    )


@mcp.tool(name="get_pull_request", description="Get pull request details by number")
def get_pull_request(owner: str, repo: str, number: int) -> dict[str, Any]:
    if number <= 0:
        raise _jsonrpc_error(ErrorCode.INVALID_PARAMS, "number must be > 0", "validation")
    return _safe_api_call("GET", f"/repos/{owner}/{repo}/pulls/{number}")


@mcp.tool(name="list_issues", description="List issues for a repository")
def list_issues(owner: str, repo: str, state: str = "open", per_page: int = 20) -> dict[str, Any]:
    if state not in {"open", "closed", "all"}:
        raise _jsonrpc_error(ErrorCode.INVALID_PARAMS, "state must be one of: open, closed, all", "validation")
    per_page = max(1, min(per_page, 100))
    return _safe_api_call(
        "GET",
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": per_page},
    )


@mcp.tool(name="rate_limit_status", description="Check GitHub REST API rate limit status")
def rate_limit_status() -> dict[str, Any]:
    return _safe_api_call("GET", "/rate_limit")


@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "GitHubWorkAPI",
        "transport": "streamable-http",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    # Streamable HTTP transport (MCP over HTTP with SSE support).
    # By default FastMCP serves on localhost:8000.
    mcp.run(transport="streamable-http")
