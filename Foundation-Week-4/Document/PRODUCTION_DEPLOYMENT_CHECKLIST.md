# MCP Server Production Deployment Checklist

Use this checklist before deploying any MCP server to production.

---

## ✅ Security Checklist

### Secrets Management
- [ ] All secrets (API keys, passwords, tokens) in environment variables
- [ ] No hardcoded credentials in code
- [ ] `.env` file in `.gitignore`
- [ ] Secrets loaded via `pydantic-settings` or similar
- [ ] Production secrets separate from dev/test

### Input Validation
- [ ] All tool inputs validated with Pydantic schemas
- [ ] String length limits enforced
- [ ] Numeric ranges enforced (min/max)
- [ ] Enum/Literal types for allowlisted values
- [ ] Custom validators for business rules
- [ ] Security validators for dangerous patterns

### SQL Security (if applicable)
- [ ] All SQL queries use parameterization (no string concat)
- [ ] Table/column names from allowlist only
- [ ] SQL keywords blocked in user input
- [ ] Query timeouts configured
- [ ] Read/write permissions separated

### File Access Security (if applicable)
- [ ] All file paths validated against allowed roots
- [ ] Path traversal attacks blocked (`../` rejected)
- [ ] Path resolution with `.resolve()` before access
- [ ] File size limits enforced
- [ ] Binary file handling considered

### API Security
- [ ] Rate limiting implemented or considered
- [ ] API keys/tokens secured
- [ ] Timeout configured on all external calls
- [ ] Retry logic with exponential backoff
- [ ] Circuit breaker for flaky services

---

## ✅ Error Handling Checklist

### Error Taxonomy
- [ ] JSON-RPC error codes defined
- [ ] Invalid params → -32602
- [ ] Internal error → -32603
- [ ] Custom codes for domain errors (-32001+)
- [ ] Error messages actionable for users
- [ ] Stack traces NOT returned to client

### Error Logging
- [ ] All errors logged with context
- [ ] Correlation IDs in error logs
- [ ] Error severity levels correct
- [ ] Sensitive data NOT in logs
- [ ] Log aggregation considered

### Graceful Degradation
- [ ] Partial failures handled
- [ ] Default values for optional features
- [ ] Circuit breaker pattern for dependencies
- [ ] Health check reflects degraded state

---

## ✅ Transport & Scaling Checklist

### Transport Configuration
- [ ] Transport matches deployment (stdio vs HTTP)
- [ ] Stateless flag set correctly for multi-instance
- [ ] Session affinity configured if using streamable HTTP
- [ ] Port configured for production
- [ ] HTTPS/TLS considered for production HTTP

### Horizontal Scaling
- [ ] No session state in server memory (if stateless)
- [ ] External cache if state needed
- [ ] Connection pooling configured
- [ ] Stateless design tested with multiple instances
- [ ] Load balancer configuration documented

---

## ✅ Performance Checklist

### Connection Management
- [ ] Database connection pooling configured
  - [ ] `pool_size` set appropriately
  - [ ] `max_overflow` configured
  - [ ] `pool_timeout` set
  - [ ] `pool_recycle` configured
- [ ] HTTP client reused (not created per request)
- [ ] Connection limits configured
- [ ] Keep-alive configured

### Resource Limits
- [ ] Request timeout configured
- [ ] File size limits enforced
- [ ] Query result limits enforced
- [ ] Memory usage bounded
- [ ] CPU usage considered

---

## ✅ Observability Checklist

### Logging
- [ ] Structured logging configured
- [ ] Log levels appropriate (INFO/WARNING/ERROR)
- [ ] Correlation IDs in all logs
- [ ] Request/response logged (excluding sensitive data)
- [ ] Tool execution duration logged
- [ ] Log rotation configured

### Health Checks
- [ ] `/health` endpoint implemented
- [ ] Health check tests dependencies
- [ ] Returns 200 if healthy, 503 if degraded
- [ ] Includes service name and version
- [ ] Load balancer configured to use it

### Metrics
- [ ] Request count tracked
- [ ] Error rate tracked
- [ ] Response time tracked (p50, p95, p99)
- [ ] Active connections tracked
- [ ] Metrics endpoint exposed (`/metrics`)

---

## ✅ Testing Checklist

### Unit Tests
- [ ] Success path tested
- [ ] Invalid input rejected
- [ ] Edge cases covered (empty, null, huge)
- [ ] Mocked external dependencies

### Security Tests
- [ ] SQL injection attempts blocked
- [ ] Path traversal attempts blocked
- [ ] XSS attempts sanitized
- [ ] Large payloads rejected
- [ ] Malformed input rejected

### Integration Tests
- [ ] Real database tested (or staging)
- [ ] Real API tested (or staging)
- [ ] End-to-end workflows tested
- [ ] Concurrent requests tested

### Test Coverage
- [ ] >70% coverage on critical paths
- [ ] All security validators tested
- [ ] All error paths tested
- [ ] Performance tests run

---

## ✅ Documentation Checklist

### README
- [ ] Setup instructions
- [ ] Environment variable documentation
- [ ] Dependency installation steps
- [ ] How to run locally
- [ ] How to run tests

### Deployment Guide
- [ ] Production deployment steps
- [ ] Environment setup
- [ ] Secrets configuration
- [ ] Health check verification
- [ ] Rollback procedure

### Runbook
- [ ] Common failure scenarios documented
- [ ] Debugging steps for each failure
- [ ] Log locations documented
- [ ] Metrics dashboard links
- [ ] On-call escalation path

### API Documentation
- [ ] All tools documented
- [ ] Input schemas documented
- [ ] Output formats documented
- [ ] Error codes documented
- [ ] Example requests/responses

---

## ✅ Infrastructure Checklist

### Environment Setup
- [ ] Production environment configured
- [ ] Staging environment configured
- [ ] Development environment documented
- [ ] Environment parity considered

### Deployment
- [ ] Container image built (if using Docker)
- [ ] CI/CD pipeline configured
- [ ] Automated tests in pipeline
- [ ] Deployment automation
- [ ] Blue-green or canary deployment

### Monitoring
- [ ] Application logs centralized
- [ ] Metrics dashboard created
- [ ] Alerts configured for errors
- [ ] Alerts configured for latency
- [ ] On-call rotation configured

---

## ✅ Pre-Deploy Verification

### Smoke Tests
- [ ] Health check returns 200
- [ ] One tool call succeeds
- [ ] Error case returns proper error
- [ ] Logs appear in log aggregation
- [ ] Metrics appear in dashboard

### Security Scan
- [ ] No secrets in code (scan with git-secrets)
- [ ] Dependencies scanned for vulnerabilities
- [ ] Security tests passing
- [ ] Manual penetration test considered

### Load Test
- [ ] Server handles expected load
- [ ] Connection pool doesn't exhaust
- [ ] Response time acceptable under load
- [ ] Graceful degradation works

---

## ✅ Post-Deploy Verification

### Deployment Success
- [ ] Health check green
- [ ] No error spikes in logs
- [ ] Response time within SLA
- [ ] All instances healthy

### Monitoring
- [ ] Dashboard shows traffic
- [ ] Alerts configured and tested
- [ ] Logs flowing correctly
- [ ] Metrics baseline established

### Documentation Updated
- [ ] Deployment date recorded
- [ ] Version documented
- [ ] Known issues documented
- [ ] Rollback tested

---

## 🚨 Red Flags (Do NOT Deploy If)

- ❌ Secrets hardcoded in code
- ❌ No input validation
- ❌ SQL queries use string concatenation
- ❌ No error handling
- ❌ No health check endpoint
- ❌ No logging
- ❌ No tests
- ❌ Stack traces returned to client
- ❌ No timeout on external calls
- ❌ Stdio transport for multi-instance deployment

---

## 📊 Deployment Readiness Score

Count your checkmarks in each section:

- **Security**: ___/25 (minimum 20 required)
- **Error Handling**: ___/12 (minimum 10 required)
- **Transport & Scaling**: ___/10 (minimum 8 required)
- **Performance**: ___/10 (minimum 8 required)
- **Observability**: ___/13 (minimum 10 required)
- **Testing**: ___/14 (minimum 10 required)
- **Documentation**: ___/14 (minimum 10 required)
- **Infrastructure**: ___/12 (minimum 8 required)

**Total**: ___/110

### Scoring Guide
- **90-110**: Production ready ✅
- **70-89**: Ready with minor improvements ⚠️
- **50-69**: Not ready - significant work needed 🔴
- **<50**: Do not deploy - critical gaps ⛔

---

## 🔄 Continuous Improvement

After deployment:
- [ ] Monitor error rates weekly
- [ ] Review slow queries monthly
- [ ] Update dependencies monthly
- [ ] Security scan quarterly
- [ ] Load test before scaling
- [ ] Runbook updated with new issues

---

**Remember**: Production deployment is not a one-time event. It's an ongoing responsibility of monitoring, maintenance, and improvement.
