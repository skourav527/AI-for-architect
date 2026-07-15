# Week 4 Production MCP Patterns - Quick Reference

## 🎯 Week 4 Core Focus
Production-grade MCP servers: HTTP transport, security, validation, scaling, observability.

---

## 1) Transport Decision (Stateless vs Streamable HTTP)

| Feature | Stateless HTTP | Streamable HTTP |
|---------|----------------|-----------------|
| Horizontal scaling | ✅ Easy | ⚠️ Needs sticky sessions |
| Sampling | ❌ Not supported | ✅ Supported |
| Progress notifications | ❌ Not supported | ✅ Supported |
| Load balancer | ✅ Simple | ⚠️ Session affinity required |
| Session state | ❌ None | ✅ Server tracks sessions |
| Use when | Multi-instance, high scale | Rich features, single/sticky instances |

**Quick rule**: Start stateless for production scaling, use streamable only if you need sampling/progress.

---

## 2) Error Taxonomy (Production Standard)

| Error | JSON-RPC Code | Use Case |
|-------|---------------|----------|
| Invalid params | -32602 | Bad input from client |
| Internal error | -32603 | Server bug/crash |
| External API error | -32001 (custom) | Dependency failure |
| Auth error | -32002 (custom) | Permission denied |
| Not found | -32003 (custom) | Resource missing |

**Implementation**:
```python
def handle_error(e: Exception) -> dict:
    if isinstance(e, ValidationError):
        return {"code": -32602, "message": str(e)}
    elif isinstance(e, PermissionError):
        return {"code": -32002, "message": "Access denied"}
    # ... map all error types
```

---

## 3) Input Validation (3-Layer Pattern)

**Layer 1: Schema validation (Pydantic)**
```python
class ToolInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(default=10, ge=1, le=100)
```

**Layer 2: Business validation**
```python
@validator('query')
def validate_query(cls, v):
    if 'forbidden_word' in v.lower():
        raise ValueError("Query contains forbidden content")
    return v
```

**Layer 3: Security validation**
```python
def validate_safe_path(path: str, allowed_roots: list[str]) -> bool:
    resolved = Path(path).resolve()
    return any(resolved.is_relative_to(root) for root in allowed_roots)
```

---

## 4) Secrets Management (Production Pattern)

❌ **Never**:
```python
API_KEY = "hardcoded"
```

✅ **Always**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    db_password: str
    
    class Config:
        env_file = ".env"

settings = Settings()  # Auto-loads from environment
```

---

## 5) SQL Injection Prevention

❌ **Vulnerable**:
```python
query = f"SELECT * FROM users WHERE name = '{user_input}'"
```

✅ **Safe**:
```python
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
```

✅ **With validation**:
```python
class QueryInput(BaseModel):
    table: Literal["users", "orders"]  # Allowlist only
    name: str = Field(..., max_length=100)
    
    @validator('name')
    def no_sql_keywords(cls, v):
        forbidden = ['--', ';', 'DROP', 'DELETE']
        if any(kw in v.upper() for kw in forbidden):
            raise ValueError("Invalid characters")
        return v
```

---

## 6) Path Traversal Prevention

❌ **Vulnerable**:
```python
def read_file(filename: str):
    return open(filename).read()  # ../../../etc/passwd
```

✅ **Safe**:
```python
def read_file(filename: str, allowed_roots: list[Path]):
    path = Path(filename).resolve()
    if not any(path.is_relative_to(root) for root in allowed_roots):
        raise ValueError(f"Path outside allowed roots")
    return path.read_text()
```

---

## 7) Connection Pooling (Database)

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,           # Normal connections
    max_overflow=10,       # Burst capacity
    pool_timeout=30,       # Wait for connection
    pool_recycle=3600,     # Recycle after 1hr
)
```

---

## 8) HTTP Client Reuse

❌ **Don't create new client per request**:
```python
def call_api():
    client = httpx.Client()  # New connection each time
    return client.get(url)
```

✅ **Reuse client**:
```python
# Module level
http_client = httpx.Client(
    timeout=10.0,
    limits=httpx.Limits(max_connections=100)
)

def call_api():
    return http_client.get(url)
```

---

## 9) Structured Logging Pattern

```python
import logging
import uuid

logger = logging.getLogger(__name__)

@mcp.tool()
def my_tool(input: str, context):
    request_id = str(uuid.uuid4())
    logger.info(
        "Tool started",
        extra={
            "request_id": request_id,
            "tool_name": "my_tool",
            "input_length": len(input)
        }
    )
    try:
        result = do_work(input)
        logger.info("Tool succeeded", extra={"request_id": request_id})
        return result
    except Exception as e:
        logger.error("Tool failed", extra={"request_id": request_id, "error": str(e)})
        raise
```

---

## 10) Health Check Endpoint

```python
@mcp.resource("health://status")
def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "MyMCPServer",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## 11) Progress Notifications (Streamable HTTP Only)

```python
@mcp.tool()
def long_task(items: list[str], context):
    total = len(items)
    for i, item in enumerate(items):
        context.report_progress(i, total)
        context.info(f"Processing {item}")
        process(item)
    return {"processed": total}
```

**Note**: Only works with streamable HTTP (not stateless).

---

## 12) Testing Checklist

**Must test**:
- [ ] Success path with valid input
- [ ] Invalid input (schema validation)
- [ ] Security attacks (SQL injection, path traversal)
- [ ] Network errors (timeout, connection refused)
- [ ] External API errors (500, rate limit)
- [ ] Edge cases (empty input, huge input, special characters)
- [ ] Concurrent requests (race conditions)

**Test template**:
```python
def test_tool_success():
    result = mcp_client.call_tool("my_tool", {"input": "valid"})
    assert result["status"] == "success"

def test_tool_invalid_input():
    with pytest.raises(ValidationError):
        mcp_client.call_tool("my_tool", {"input": ""})

def test_tool_sql_injection_blocked():
    result = mcp_client.call_tool("query", {"input": "'; DROP TABLE users--"})
    assert "error" in result
```

---

## 13) Production Deployment Checklist

**Before deploying**:
- [ ] All secrets in environment variables (not code)
- [ ] Input validation on all tools
- [ ] Error handling with proper JSON-RPC codes
- [ ] Structured logging with correlation IDs
- [ ] Health check endpoint implemented
- [ ] Connection pooling configured
- [ ] Timeout and retry policies set
- [ ] Rate limiting considered
- [ ] Tests passing (>70% coverage on critical paths)
- [ ] Security tests passing (SQL injection, path traversal)
- [ ] Transport matches deployment (stateless for multi-instance)
- [ ] Documentation: README, runbook, deployment guide

---

## 14) Common Production Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Hardcoded secrets | Use environment variables |
| String concatenation for SQL | Use parameterized queries |
| No input validation | Add Pydantic schemas |
| Creating new DB connection per request | Use connection pool |
| No error logging | Add structured logging |
| Returning stack traces to client | Return generic error, log details |
| No timeouts on external calls | Set timeout on all HTTP/DB calls |
| Stdio in production | Use HTTP transport |
| No health checks | Add /health endpoint |
| Stateful design with load balancer | Use stateless pattern |

---

## 15) Quick Debugging Guide

**Problem**: "Tool call times out"
- Check external API timeout settings
- Check database query performance
- Add progress notifications to see where it hangs

**Problem**: "Connection pool exhausted"
- Increase pool_size and max_overflow
- Check for connection leaks (not closing connections)
- Add connection pool metrics

**Problem**: "SQL injection vulnerability"
- Never use f-strings or string concat for SQL
- Always use parameterized queries
- Add validator to block SQL keywords in user input

**Problem**: "Path traversal attack"
- Always resolve paths with Path.resolve()
- Check if resolved path is within allowed roots
- Reject ../ in user input

**Problem**: "Load balancer routing breaks session"
- Use stateless=true in HTTP config
- OR configure sticky sessions on load balancer
- Remove session-dependent features

---

## 16) Week 4 Mental Model

```
Production MCP Server = 
    HTTP Transport 
    + Input Validation (3 layers)
    + Error Taxonomy (5 types)
    + Secrets Management (env vars)
    + Connection Pooling (DB/HTTP)
    + Structured Logging (correlation IDs)
    + Security (SQL/path/XSS prevention)
    + Testing (success + failure + security)
    + Observability (health + metrics)
```

If you forget everything, remember:
1. Validate all inputs (schema + business + security)
2. Never trust user data (SQL, paths, commands)
3. Handle all errors gracefully (no crashes, no stack traces to client)
4. Log everything with context (correlation IDs)
5. Use stateless pattern for scaling

---

## 17) One-Minute Review

**Transport**: Stateless for scale, streamable for features  
**Errors**: Map to JSON-RPC codes, log details, return generic  
**Validation**: Pydantic + business rules + security checks  
**Secrets**: Environment variables only  
**SQL**: Parameterized queries only  
**Paths**: Root enforcement + traversal prevention  
**Logging**: Structured with correlation IDs  
**Testing**: Success + failure + security attacks  
**Deploy**: Checklist before production  

That's the Week 4 production MCP mindset.
