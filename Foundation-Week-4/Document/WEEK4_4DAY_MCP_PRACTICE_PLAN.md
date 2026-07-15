# WEEK 4: MCP Production Patterns — 4-Day Practice Sprint

## Sprint Goal
Build production-grade MCP servers with focus on HTTP transport, error handling, validation, security, and real integration patterns.

- Total time: 8-10 hours
- Style: Implementation-first with production mindset
- Standard: Every server must be deployable, not just "working locally"

---

## Why This 4-Day Plan Will Work
Week 3 gave you protocol understanding and basic stdio servers. Week 4 shifts to production patterns you'll actually use when deploying MCP servers at scale.

Core implementation loop for each module:
1. Build server with production transport (streamable HTTP focus)
2. Add validation, error handling, security checks
3. Test with real clients and edge cases
4. Document deployment and ops patterns
5. Extract reusable patterns for your MCP toolkit

---

## Compressed Build Plan (4 Days)

| Day | Focus Blocks | Build Outcome | Production Pattern Learned | Time |
|-----|--------------|---------------|----------------------------|------|
| Day 1 | REST API MCP + streamable HTTP transport | Working API connector with HTTP transport | HTTP deployment, error taxonomy, structured logging | 2.5h |
| Day 2 | Database MCP + security hardening | Secure DB connector with SQL injection prevention | Input validation, secrets management, query parameterization | 2.5h |
| Day 3 | File/RAG MCP + stateless pattern | Scalable file reader with root enforcement | Stateless design, horizontal scaling, path security | 2.5h |
| Day 4 | Testing + observability + production checklist | Complete test suite + deployment guide | Testing patterns, monitoring, production readiness | 2h |

---

## Day 1 Detailed Schedule (REST API MCP + HTTP Transport)

### Block 1 (90 min)
**Build: REST API MCP Server (Your Work API - ADO/SonarQube/GitHub)**

What to build:
- MCP server exposing 3-5 tools for a real REST API you use
- Use streamable HTTP transport (not stdio)
- Structured error handling with proper JSON-RPC error codes

Production patterns to implement:
1. **HTTP transport setup** with SSE for bidirectional communication
2. **Error taxonomy**: client errors (400s) vs server errors (500s) vs external API errors
3. **Structured logging** with correlation IDs for request tracing
4. **Timeout and retry policy** for external API calls
5. **Rate limiting awareness** - respect API rate limits

Definition of done:
- Server runs on HTTP (localhost:8000 or similar)
- Tools call real external API and handle errors gracefully
- Logs show request flow with correlation IDs
- Returns proper JSON-RPC errors for different failure modes

### Block 2 (60 min)
**Add: Progress notifications + error handling patterns**

What to add:
- Progress notifications for long-running API calls
- Logging notifications for debugging
- Circuit breaker pattern for flaky external APIs
- Proper error wrapping and context

Production patterns to implement:
1. **Progress notifications** - emit progress during multi-step API workflows
2. **Circuit breaker** - fail fast when external API is down
3. **Error context** - preserve error chain with actionable messages
4. **Graceful degradation** - partial success when some API calls fail

Testing:
- Test with MCP Inspector or simple client
- Verify progress notifications appear in client
- Test error scenarios: network timeout, API 500, rate limit

### Consolidation (20 min)
**Document patterns learned**

Output:
- HTTP transport template (reusable)
- Error handling checklist
- Logging pattern for correlation IDs

---

## Day 2 Detailed Schedule (Database MCP + Security)

### Block 1 (90 min)
**Build: Database MCP Server (SQL/PostgreSQL/SQLite)**

What to build:
- MCP server with tools for parameterized SQL queries
- SQL injection prevention through proper parameterization
- Connection pooling for production scale

Production patterns to implement:
1. **Parameterized queries** - NEVER string concatenation
2. **Input validation** - strict schema validation before query execution
3. **Connection pooling** - reuse connections, handle pool exhaustion
4. **Secrets management** - never hardcode credentials, use env vars
5. **Query timeouts** - prevent long-running queries from blocking

Definition of done:
- Tools accept parameters and safely construct SQL
- All inputs validated with Pydantic schemas
- Connection pool configured with limits
- Credentials loaded from environment
- Query timeout enforcement

### Block 2 (60 min)
**Add: Query validation + audit logging + access control**

What to add:
- SQL query allowlist or pattern validation
- Audit log for all query executions
- Basic access control (which tools can write vs read)
- Transaction support for multi-step operations

Production patterns to implement:
1. **Query allowlist** - only allow known safe query patterns
2. **Audit logging** - log who ran what query when
3. **Read/write separation** - different tools for reads vs writes
4. **Transaction boundaries** - commit/rollback support

Testing:
- Test SQL injection attempts (should fail)
- Test connection pool exhaustion (should handle gracefully)
- Test invalid input (should reject with clear errors)

### Consolidation (20 min)
**Document security patterns**

Output:
- SQL security checklist
- Input validation template
- Secrets management guide

---

## Day 3 Detailed Schedule (File/RAG MCP + Stateless Pattern)

### Block 1 (90 min)
**Build: File System MCP with Root Enforcement**

What to build:
- MCP server with file reading tools + simple search
- Root-based path allowlisting (Week 3 concept, production implementation)
- Stateless HTTP design for horizontal scaling

Production patterns to implement:
1. **Stateless design** - no session state in server memory
2. **Root enforcement** - strict path validation, reject path traversal
3. **File size limits** - prevent memory exhaustion from large files
4. **Streaming reads** - chunk large files instead of loading fully
5. **Search indexing** - simple in-memory index (or external search service)

Definition of done:
- Tools accept root-scoped file paths only
- Path traversal attempts (../) are rejected
- Large files are chunked or size-limited
- Server can run multiple instances (stateless)
- Simple keyword search works across allowed files

### Block 2 (60 min)
**Add: Stateless HTTP deployment + load balancer ready**

What to add:
- Stateless HTTP flag configuration
- Health check endpoint for load balancers
- Metrics endpoint (request count, error rate, latency)
- Graceful shutdown handling

Production patterns to implement:
1. **Stateless HTTP flag** - disable session-dependent features
2. **Health checks** - /health endpoint for k8s/LB probes
3. **Metrics** - /metrics endpoint with Prometheus format
4. **Graceful shutdown** - finish in-flight requests before exit

Testing:
- Run 2+ server instances behind a simple load balancer (or test manually)
- Verify requests work regardless of which instance handles them
- Test health check endpoint
- Test path traversal attacks (should all fail)

### Consolidation (20 min)
**Document scaling patterns**

Output:
- Stateless design checklist
- Load balancer configuration example
- Path security enforcement template

---

## Day 4 Detailed Schedule (Testing + Observability + Production Readiness)

### Block 1 (75 min)
**Build: Test suite for all 3 MCP servers**

What to build:
- Pytest test suite covering success + failure paths
- Integration tests with real external dependencies (or mocks)
- Error injection tests (network failures, timeouts, bad inputs)

Test coverage priorities:
1. **Tool success path** - normal operation with valid inputs
2. **Input validation** - reject invalid/malicious inputs
3. **Error handling** - network errors, API errors, timeouts
4. **Edge cases** - empty results, large payloads, concurrent requests
5. **Security tests** - SQL injection, path traversal, XSS in outputs

Definition of done:
- Each server has 10+ tests covering main scenarios
- Tests run in CI/CD pipeline (or can run locally)
- Coverage report shows critical paths tested

### Block 2 (45 min)
**Add: Observability + production deployment guide**

What to add:
- Structured logging with log levels and correlation IDs
- OpenTelemetry tracing (or simple request duration logging)
- Production deployment checklist
- Runbook for common failure scenarios

Production patterns to document:
1. **Logging strategy** - what to log, log levels, correlation IDs
2. **Metrics to track** - request rate, error rate, latency p50/p95/p99
3. **Deployment checklist** - env vars, secrets, health checks, scaling config
4. **Runbook** - how to debug common failures (API timeout, DB connection pool exhausted, etc.)

Output artifacts:
- Logging configuration template
- Metrics dashboard config (Grafana/Prometheus or simple)
- Production deployment checklist (reusable for any MCP server)
- Runbook template

---

## Production Patterns Deep Dive (Reference Section)

### Pattern 1: Stateless HTTP Design
**When to use**: Multi-instance deployment behind load balancer

**Implementation checklist**:
- [ ] No in-memory session state (use external cache if needed)
- [ ] Set `stateless=true` in HTTP transport config
- [ ] Disable sampling and progress notifications (not supported in stateless)
- [ ] Add health check endpoint
- [ ] Add metrics endpoint
- [ ] Test with multiple instances

**Tradeoffs**:
- ✅ Horizontal scaling works
- ✅ Simple load balancer setup
- ❌ No sampling support
- ❌ No progress notifications
- ❌ No long-lived SSE connections

### Pattern 2: Streamable HTTP (Session-Aware)
**When to use**: Single instance or sticky sessions, need full MCP features

**Implementation checklist**:
- [ ] Session ID tracking in HTTP headers
- [ ] Long-lived SSE connection for progress/sampling
- [ ] Short-lived SSE for tool results
- [ ] Session cleanup on timeout/disconnect
- [ ] Use same transport in dev and prod

**Tradeoffs**:
- ✅ Full MCP feature support (sampling, notifications)
- ✅ Rich user experience
- ❌ More complex deployment (sticky sessions required)
- ❌ Harder to scale horizontally

### Pattern 3: Error Taxonomy for Production
**Error classification**:

| Error Type | JSON-RPC Code | When to Use | Example |
|------------|---------------|-------------|---------|
| Invalid params | -32602 | Client sent bad input | Missing required field, wrong type |
| Internal error | -32603 | Server bug or panic | Unexpected exception, null pointer |
| External API error | Custom (e.g. -32001) | External dependency failed | API timeout, rate limit, 500 |
| Authorization error | Custom (e.g. -32002) | Permission denied | User lacks access, invalid token |
| Resource not found | Custom (e.g. -32003) | Requested item doesn't exist | Doc not found, invalid ID |

**Implementation**:
```python
class MCPErrorCode(Enum):
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    EXTERNAL_API_ERROR = -32001
    AUTHORIZATION_ERROR = -32002
    RESOURCE_NOT_FOUND = -32003

def handle_error(e: Exception) -> dict:
    if isinstance(e, ValidationError):
        return {"code": MCPErrorCode.INVALID_PARAMS.value, "message": str(e)}
    elif isinstance(e, PermissionError):
        return {"code": MCPErrorCode.AUTHORIZATION_ERROR.value, "message": "Access denied"}
    elif isinstance(e, requests.Timeout):
        return {"code": MCPErrorCode.EXTERNAL_API_ERROR.value, "message": "API timeout"}
    else:
        return {"code": MCPErrorCode.INTERNAL_ERROR.value, "message": "Internal server error"}
```

### Pattern 4: Input Validation Template
**Validation layers**:
1. **Schema validation** (Pydantic) - type, required fields, format
2. **Business validation** - value ranges, allowlists, relationships
3. **Security validation** - path traversal, SQL injection, XSS
4. **Rate limiting** - per-user, per-tool request limits

**Example**:
```python
from pydantic import BaseModel, Field, validator
import re

class QueryToolInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=100)
    
    @validator('query')
    def validate_query_safe(cls, v):
        # Block SQL keywords in user input if used in LIKE clauses
        dangerous_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE']
        for pattern in dangerous_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f"Query contains forbidden pattern: {pattern}")
        return v
```

### Pattern 5: Secrets Management
**Never do this**:
```python
DB_PASSWORD = "hardcoded_secret_123"  # ❌ NEVER
API_KEY = "your_api_key_here"          # ❌ NEVER
```

**Always do this**:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_password: str
    api_key: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
# Usage: settings.db_password, settings.api_key
```

### Pattern 6: Connection Pooling
**For database connections**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # Max connections in pool
    max_overflow=10,      # Additional connections if pool exhausted
    pool_timeout=30,      # Wait time for connection
    pool_recycle=3600,    # Recycle connections after 1 hour
)
```

**For HTTP sessions**:
```python
import httpx

# Reuse client across requests
http_client = httpx.Client(
    timeout=10.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

---

## Copilot Prompts for Week 4 (Production Focus)

Use these prompts in sequence as you build:

### Day 1 (REST API + HTTP)
```
1. "Create MCP server in Python with streamable HTTP transport exposing tools for [API name]"
2. "Add structured logging with correlation IDs to this MCP server"
3. "Implement circuit breaker pattern for external API calls in this tool"
4. "Add progress notifications to this long-running API tool with proper SSE handling"
5. "Create error taxonomy with proper JSON-RPC error codes for this server"
```

### Day 2 (Database + Security)
```
1. "Create MCP server with parameterized SQL query tools preventing SQL injection"
2. "Add Pydantic validation schema for SQL query inputs with security checks"
3. "Implement connection pooling for PostgreSQL in this MCP server"
4. "Add secrets management using environment variables and pydantic-settings"
5. "Create audit logging for all database query executions with user tracking"
```

### Day 3 (File/RAG + Stateless)
```
1. "Create stateless MCP server with file reading tools and root path enforcement"
2. "Add path traversal attack prevention to these file access tools"
3. "Implement file chunking for large file reads to prevent memory issues"
4. "Add health check and metrics endpoints for load balancer integration"
5. "Configure this MCP server for stateless HTTP with horizontal scaling"
```

### Day 4 (Testing + Observability)
```
1. "Write pytest tests for this MCP server covering success and failure paths"
2. "Add security tests for SQL injection and path traversal attacks"
3. "Create integration tests with mocked external API dependencies"
4. "Add OpenTelemetry tracing to this MCP server for observability"
5. "Generate production deployment checklist for this MCP server"
```

---

## Week 4 Artifacts to Create

- [ ] **Server 1**: REST API MCP with HTTP transport (ADO/SonarQube/GitHub)
- [ ] **Server 2**: Database MCP with security hardening
- [ ] **Server 3**: File/RAG MCP with stateless pattern
- [ ] **Test Suite**: Pytest tests for all 3 servers
- [ ] **Production Checklist**: Reusable deployment checklist
- [ ] **Error Handling Template**: Error taxonomy + handling patterns
- [ ] **Secrets Management Guide**: Environment-based config template
- [ ] **Scaling Playbook**: Stateless vs stateful design decision guide
- [ ] **Observability Dashboard**: Logging + metrics configuration

---

## Week 4 Done When (4-Day Version)

### Knowledge Validation
- [ ] Can explain stateless HTTP vs streamable HTTP tradeoffs
- [ ] Can implement proper input validation with Pydantic
- [ ] Can prevent SQL injection and path traversal attacks
- [ ] Can configure connection pooling for production scale
- [ ] Can add structured logging with correlation IDs
- [ ] Can deploy MCP server with proper secrets management

### Implementation Validation
- [ ] MCP Server #1 (API): Working with HTTP transport + error handling
- [ ] MCP Server #2 (Database): Secure with parameterized queries + validation
- [ ] MCP Server #3 (File): Stateless design with root enforcement
- [ ] All 3 servers have test coverage >70% on critical paths
- [ ] All 3 servers have production deployment documentation
- [ ] Can build production-ready MCP server from scratch in <2 hours

### Production Readiness
- [ ] All servers use environment variables for secrets
- [ ] All servers have health check endpoints
- [ ] All servers have proper error taxonomy and logging
- [ ] All servers handle edge cases (timeouts, rate limits, bad inputs)
- [ ] All servers have deployment and runbook documentation

---

## 4-Day Risk Controls

If stuck for more than 30 minutes:
1. Reduce scope to 1-2 tools per server instead of 3-5
2. Use sqlite instead of PostgreSQL for Day 2
3. Skip advanced patterns (circuit breaker, tracing) and focus on basics
4. Ask Copilot for working example, then refactor with production patterns

If Day 1 slips:
- Keep HTTP transport and error handling
- Skip progress notifications if needed
- Move logging patterns to Day 4

If Day 2 slips:
- Keep parameterized queries and input validation
- Use environment variables for secrets
- Skip connection pooling if needed

If Day 3 slips:
- Keep root enforcement and path security
- Skip stateless pattern and use regular HTTP
- Skip health/metrics endpoints

If Day 4 slips:
- Keep security tests (SQL injection, path traversal)
- Keep basic success path tests
- Create minimal deployment checklist only

---

## Final Output Expectation By End Of Week 4

You should have:
- 3 production-grade MCP servers with real integrations
- Deep understanding of stateless vs stateful HTTP transport
- Reusable security and validation patterns
- Test suite covering critical security scenarios
- Production deployment knowledge (secrets, scaling, monitoring)
- Confidence to build MCP servers for real work projects

This is the bridge from "learning MCP" to "using MCP in production" - the patterns you build this week will be templates for all future MCP work.

---

## Post-Week 4: What's Next

After completing Week 4, you'll be ready to:
1. **Upgrade your existing ADO/SonarQube MCP servers** with production patterns
2. **Build new MCP servers** for work use cases in <2 hours
3. **Move to Week 5** with confidence in both theory and practice
4. **Start contributing** to open-source MCP projects or building your own

Week 4 is your MCP confidence multiplier - invest the time here and everything else becomes easier.
