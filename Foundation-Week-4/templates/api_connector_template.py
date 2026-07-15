"""
MCP Server Template: REST API Connector (Production Pattern)
Day 1 starter template with HTTP transport and production patterns.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, validator
import httpx
import logging
import uuid
from datetime import datetime
from typing import Optional
import os

# Structured logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Settings from environment
class Settings(BaseModel):
    api_base_url: str = Field(default="https://api.example.com")
    api_key: str = Field(default="")  # Load from env
    api_timeout: int = Field(default=30)
    
    class Config:
        env_file = ".env"

settings = Settings()

# Initialize MCP server
mcp = FastMCP("APIConnector", log_level="INFO")

# Reusable HTTP client with connection pooling
http_client = httpx.Client(
    base_url=settings.api_base_url,
    timeout=settings.api_timeout,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    headers={"Authorization": f"Bearer {settings.api_key}"} if settings.api_key else {}
)

# Error codes
class ErrorCode:
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    EXTERNAL_API_ERROR = -32001
    AUTHORIZATION_ERROR = -32002
    RESOURCE_NOT_FOUND = -32003

# Input validation schema
class APIQueryInput(BaseModel):
    resource: str = Field(..., min_length=1, max_length=200, description="API resource path")
    params: Optional[dict] = Field(default=None, description="Query parameters")
    
    @validator('resource')
    def validate_resource_path(cls, v):
        # Add security checks here
        if '..' in v or v.startswith('/'):
            raise ValueError("Invalid resource path")
        return v

# Tool: Query API endpoint
@mcp.tool(
    name="query_api",
    description="Query a REST API endpoint with optional parameters"
)
def query_api(resource: str, params: Optional[dict] = None, context=None) -> dict:
    """
    Query external API with proper error handling and logging.
    """
    request_id = str(uuid.uuid4())
    
    # Validate input
    try:
        validated = APIQueryInput(resource=resource, params=params)
    except Exception as e:
        logger.error("Validation failed", extra={"request_id": request_id, "error": str(e)})
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(e)}}
    
    logger.info(
        "API request started",
        extra={
            "request_id": request_id,
            "resource": resource,
            "params": params
        }
    )
    
    # Optional: Report progress for long operations
    if context:
        context.info(f"Calling API: {resource}")
    
    try:
        # Make API call
        response = http_client.get(
            f"/{resource}",
            params=params or {}
        )
        response.raise_for_status()
        
        result = response.json()
        
        logger.info(
            "API request succeeded",
            extra={"request_id": request_id, "status_code": response.status_code}
        )
        
        return {"data": result, "status": "success"}
        
    except httpx.TimeoutException as e:
        logger.error(
            "API timeout",
            extra={"request_id": request_id, "error": str(e)}
        )
        return {
            "error": {
                "code": ErrorCode.EXTERNAL_API_ERROR,
                "message": "API request timed out"
            }
        }
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {
                "error": {
                    "code": ErrorCode.RESOURCE_NOT_FOUND,
                    "message": f"Resource not found: {resource}"
                }
            }
        elif e.response.status_code in [401, 403]:
            return {
                "error": {
                    "code": ErrorCode.AUTHORIZATION_ERROR,
                    "message": "Authorization failed"
                }
            }
        else:
            logger.error(
                "API error",
                extra={
                    "request_id": request_id,
                    "status_code": e.response.status_code
                }
            )
            return {
                "error": {
                    "code": ErrorCode.EXTERNAL_API_ERROR,
                    "message": f"API error: {e.response.status_code}"
                }
            }
    
    except Exception as e:
        logger.exception(
            "Unexpected error",
            extra={"request_id": request_id}
        )
        return {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Internal server error"
            }
        }

# Health check resource
@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict:
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "APIConnector",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# TODO: Add more tools for your specific API
# Example patterns:
# - List items
# - Create item
# - Update item
# - Delete item
# - Search

if __name__ == "__main__":
    # For production: use HTTP transport
    # transport can be "stdio" for local dev or "streamable-http" for deployment
    
    # Stateless HTTP (for horizontal scaling):
    # mcp.run(transport="streamable-http", port=8000, stateless=True)
    
    # Streamable HTTP (for full features with sticky sessions):
    # mcp.run(transport="streamable-http", port=8000)
    
    # Stdio (for local development):
    mcp.run(transport="stdio")
