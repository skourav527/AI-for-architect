"""
MCP Server Template: File System / RAG Connector (Production Pattern)
Day 3 starter template with stateless design and path security.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import logging
import uuid
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import mimetypes

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Settings
class Settings(BaseSettings):
    allowed_roots: str = Field(default="./data,./documents")  # Comma-separated paths
    max_file_size_mb: int = Field(default=10)
    chunk_size_bytes: int = Field(default=1024 * 1024)  # 1MB chunks
    
    class Config:
        env_file = ".env"

settings = Settings()

# Parse allowed roots
ALLOWED_ROOTS = [
    Path(root.strip()).resolve()
    for root in settings.allowed_roots.split(',')
]

# Initialize MCP server
mcp = FastMCP("FileSystemConnector", log_level="INFO")

# Error codes
class ErrorCode:
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    FILE_NOT_FOUND = -32003
    AUTHORIZATION_ERROR = -32002
    FILE_TOO_LARGE = -32005

# Path validation
def is_path_safe(file_path: str, allowed_roots: List[Path]) -> tuple[bool, Optional[Path]]:
    """
    Check if path is within allowed roots and doesn't contain traversal attacks.
    Returns (is_safe, resolved_path)
    """
    try:
        # Resolve to absolute path
        resolved = Path(file_path).resolve()
        
        # Check if within any allowed root
        for root in allowed_roots:
            if resolved.is_relative_to(root):
                return True, resolved
        
        return False, None
    except Exception:
        return False, None

# Input validation
class FileReadInput(BaseModel):
    file_path: str = Field(..., description="Path to file relative to allowed roots")
    
    @validator('file_path')
    def validate_path(cls, v):
        # Block obvious traversal attempts
        if '..' in v or v.startswith('/'):
            raise ValueError("Invalid file path")
        return v

class FileSearchInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    root_path: Optional[str] = Field(default=None, description="Search within specific root")
    max_results: int = Field(default=10, ge=1, le=100)

# Tool: Read file contents
@mcp.tool(
    name="read_file",
    description="Read file contents from allowed directories only"
)
def read_file(file_path: str, context=None) -> dict:
    """
    Safely read file with path validation and size limits.
    """
    request_id = str(uuid.uuid4())
    
    # Validate input
    try:
        validated = FileReadInput(file_path=file_path)
    except Exception as e:
        logger.error("Validation failed", extra={"request_id": request_id, "error": str(e)})
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(e)}}
    
    # Security check: validate path is within allowed roots
    is_safe, resolved_path = is_path_safe(file_path, ALLOWED_ROOTS)
    
    if not is_safe:
        logger.warning(
            "Path traversal attempt blocked",
            extra={"request_id": request_id, "path": file_path}
        )
        return {
            "error": {
                "code": ErrorCode.AUTHORIZATION_ERROR,
                "message": "Path outside allowed roots"
            }
        }
    
    if context:
        context.info(f"Reading file: {file_path}")
    
    try:
        # Check file exists
        if not resolved_path.exists():
            return {
                "error": {
                    "code": ErrorCode.FILE_NOT_FOUND,
                    "message": f"File not found: {file_path}"
                }
            }
        
        # Check file size
        file_size_mb = resolved_path.stat().st_size / (1024 * 1024)
        if file_size_mb > settings.max_file_size_mb:
            return {
                "error": {
                    "code": ErrorCode.FILE_TOO_LARGE,
                    "message": f"File too large: {file_size_mb:.2f}MB (max: {settings.max_file_size_mb}MB)"
                }
            }
        
        # Read file
        content = resolved_path.read_text(encoding='utf-8')
        mime_type = mimetypes.guess_type(str(resolved_path))[0] or "text/plain"
        
        logger.info(
            "File read succeeded",
            extra={
                "request_id": request_id,
                "file_path": file_path,
                "size_bytes": len(content)
            }
        )
        
        return {
            "content": content,
            "file_path": file_path,
            "mime_type": mime_type,
            "size_bytes": len(content),
            "status": "success"
        }
    
    except UnicodeDecodeError:
        return {
            "error": {
                "code": ErrorCode.INVALID_PARAMS,
                "message": "File is not text (binary file not supported)"
            }
        }
    
    except Exception as e:
        logger.exception(
            "File read error",
            extra={"request_id": request_id}
        )
        return {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Failed to read file"
            }
        }

# Tool: Search files
@mcp.tool(
    name="search_files",
    description="Search for files by keyword in allowed directories"
)
def search_files(
    query: str,
    root_path: Optional[str] = None,
    max_results: int = 10,
    context=None
) -> dict:
    """
    Search files by content or name within allowed roots.
    """
    request_id = str(uuid.uuid4())
    
    # Validate input
    try:
        validated = FileSearchInput(query=query, root_path=root_path, max_results=max_results)
    except Exception as e:
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(e)}}
    
    # Determine search roots
    search_roots = ALLOWED_ROOTS
    if root_path:
        is_safe, resolved = is_path_safe(root_path, ALLOWED_ROOTS)
        if not is_safe:
            return {
                "error": {
                    "code": ErrorCode.AUTHORIZATION_ERROR,
                    "message": "Search path outside allowed roots"
                }
            }
        search_roots = [resolved]
    
    if context:
        context.info(f"Searching for: {query}")
    
    try:
        results = []
        
        for root in search_roots:
            if not root.exists():
                continue
            
            # Search files (simple implementation - can be enhanced with indexing)
            for file_path in root.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Search by filename
                if query.lower() in file_path.name.lower():
                    results.append({
                        "path": str(file_path.relative_to(root)),
                        "name": file_path.name,
                        "size_bytes": file_path.stat().st_size,
                        "match_type": "filename"
                    })
                    
                    if len(results) >= validated.max_results:
                        break
                
                # Search by content (for text files only)
                if len(results) < validated.max_results:
                    try:
                        if file_path.suffix in ['.txt', '.md', '.py', '.json']:
                            content = file_path.read_text(encoding='utf-8')
                            if query.lower() in content.lower():
                                results.append({
                                    "path": str(file_path.relative_to(root)),
                                    "name": file_path.name,
                                    "size_bytes": file_path.stat().st_size,
                                    "match_type": "content"
                                })
                    except Exception:
                        pass  # Skip files that can't be read
            
            if len(results) >= validated.max_results:
                break
        
        logger.info(
            "Search completed",
            extra={
                "request_id": request_id,
                "query": query,
                "results_count": len(results)
            }
        )
        
        return {
            "results": results[:validated.max_results],
            "query": query,
            "count": len(results),
            "status": "success"
        }
    
    except Exception as e:
        logger.exception(
            "Search error",
            extra={"request_id": request_id}
        )
        return {
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Search failed"
            }
        }

# Resource: List allowed roots
@mcp.resource("roots://list", mime_type="application/json")
def list_roots() -> dict:
    """List all allowed root directories."""
    return {
        "roots": [str(root) for root in ALLOWED_ROOTS],
        "count": len(ALLOWED_ROOTS)
    }

# Health check (stateless-friendly)
@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict:
    """Stateless health check."""
    roots_accessible = sum(1 for root in ALLOWED_ROOTS if root.exists())
    
    return {
        "status": "healthy" if roots_accessible > 0 else "degraded",
        "service": "FileSystemConnector",
        "roots_accessible": roots_accessible,
        "roots_total": len(ALLOWED_ROOTS),
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Metrics endpoint (for monitoring)
@mcp.resource("metrics://stats", mime_type="application/json")
def metrics() -> dict:
    """Prometheus-style metrics endpoint."""
    total_files = 0
    total_size = 0
    
    for root in ALLOWED_ROOTS:
        if root.exists():
            for file_path in root.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
    
    return {
        "files_total": total_files,
        "storage_bytes_total": total_size,
        "roots_count": len(ALLOWED_ROOTS)
    }

# TODO: Add more file operations
# - List directory contents
# - Write file (with safety checks)
# - Delete file (with confirmation)
# - Advanced search with indexing (vector search for RAG)

if __name__ == "__main__":
    # For production: use stateless HTTP for horizontal scaling
    # mcp.run(transport="streamable-http", port=8000, stateless=True)
    
    # For local development
    mcp.run(transport="stdio")
