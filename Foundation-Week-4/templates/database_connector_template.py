"""
MCP Server Template: Database Connector (Production Pattern)
Day 2 starter template with SQL injection prevention and security patterns.
"""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
import logging
import uuid
from typing import Optional, Literal
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
import re

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Settings with secrets management
class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./test.db")
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_pool_timeout: int = Field(default=30)
    
    class Config:
        env_file = ".env"

settings = Settings()

# Database engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False
)

SessionLocal = sessionmaker(bind=engine)

# Initialize MCP server
mcp = FastMCP("DatabaseConnector", log_level="INFO")

# Error codes
class ErrorCode:
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    DATABASE_ERROR = -32004
    AUTHORIZATION_ERROR = -32002

# Input validation for queries
class QueryInput(BaseModel):
    table: Literal["users", "orders", "products"]  # Allowlist tables only
    filters: Optional[dict] = Field(default=None, description="WHERE clause filters")
    limit: int = Field(default=100, ge=1, le=1000)
    
    @validator('table')
    def validate_table_name(cls, v):
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', v):
            raise ValueError("Invalid table name")
        return v

class InsertInput(BaseModel):
    table: Literal["users", "orders", "products"]
    data: dict = Field(..., description="Column-value pairs to insert")
    
    @validator('data')
    def validate_data(cls, v):
        # Validate that keys are safe column names
        for key in v.keys():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                raise ValueError(f"Invalid column name: {key}")
        return v

# Audit logging
def audit_log(request_id: str, operation: str, table: str, user: str = "system"):
    """Log all database operations for security audit."""
    logger.info(
        "Database operation",
        extra={
            "request_id": request_id,
            "operation": operation,
            "table": table,
            "user": user,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Tool: Query database (READ only)
@mcp.tool(
    name="query_database",
    description="Query database table with filters (parameterized for safety)"
)
def query_database(
    table: str,
    filters: Optional[dict] = None,
    limit: int = 100,
    context=None
) -> dict:
    """
    Safe database query with parameterized SQL to prevent injection.
    """
    request_id = str(uuid.uuid4())
    
    # Validate input
    try:
        validated = QueryInput(table=table, filters=filters, limit=limit)
    except Exception as e:
        logger.error("Validation failed", extra={"request_id": request_id, "error": str(e)})
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(e)}}
    
    audit_log(request_id, "SELECT", table)
    
    if context:
        context.info(f"Querying table: {table}")
    
    try:
        with SessionLocal() as session:
            # Build safe parameterized query
            query = f"SELECT * FROM {validated.table}"
            params = {}
            
            if validated.filters:
                # Build WHERE clause with parameterized values
                where_clauses = []
                for i, (column, value) in enumerate(validated.filters.items()):
                    param_name = f"param_{i}"
                    where_clauses.append(f"{column} = :{param_name}")
                    params[param_name] = value
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            query += f" LIMIT :limit"
            params['limit'] = validated.limit
            
            # Execute with parameterized query
            result = session.execute(text(query), params)
            rows = [dict(row._mapping) for row in result]
            
            logger.info(
                "Query succeeded",
                extra={"request_id": request_id, "rows_returned": len(rows)}
            )
            
            return {
                "data": rows,
                "count": len(rows),
                "status": "success"
            }
    
    except Exception as e:
        logger.exception(
            "Database error",
            extra={"request_id": request_id}
        )
        return {
            "error": {
                "code": ErrorCode.DATABASE_ERROR,
                "message": "Database query failed"
            }
        }

# Tool: Insert into database (WRITE operation)
@mcp.tool(
    name="insert_record",
    description="Insert a record into database table (with validation)"
)
def insert_record(table: str, data: dict, context=None) -> dict:
    """
    Safe database insert with parameterized SQL.
    """
    request_id = str(uuid.uuid4())
    
    # Validate input
    try:
        validated = InsertInput(table=table, data=data)
    except Exception as e:
        logger.error("Validation failed", extra={"request_id": request_id, "error": str(e)})
        return {"error": {"code": ErrorCode.INVALID_PARAMS, "message": str(e)}}
    
    audit_log(request_id, "INSERT", table)
    
    if context:
        context.info(f"Inserting into table: {table}")
    
    try:
        with SessionLocal() as session:
            # Build parameterized INSERT
            columns = list(validated.data.keys())
            values = list(validated.data.values())
            
            placeholders = [f":{col}" for col in columns]
            query = f"INSERT INTO {validated.table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            params = {col: val for col, val in zip(columns, values)}
            
            session.execute(text(query), params)
            session.commit()
            
            logger.info(
                "Insert succeeded",
                extra={"request_id": request_id, "table": table}
            )
            
            return {"status": "success", "message": f"Record inserted into {table}"}
    
    except Exception as e:
        logger.exception(
            "Database error",
            extra={"request_id": request_id}
        )
        return {
            "error": {
                "code": ErrorCode.DATABASE_ERROR,
                "message": "Database insert failed"
            }
        }

# Health check with DB connection test
@mcp.resource("health://status", mime_type="application/json")
def health_check() -> dict:
    """Health check that tests database connectivity."""
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "DatabaseConnector",
        "database": db_status,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# TODO: Add more database tools
# - Update record (with WHERE parameterization)
# - Delete record (with confirmation)
# - Execute stored procedure
# - Bulk operations with transaction support

if __name__ == "__main__":
    # For production deployment
    # mcp.run(transport="streamable-http", port=8000, stateless=True)
    
    # For local development
    mcp.run(transport="stdio")
