# Day 4: Runbook (Common Failure Scenarios)

One-page reference for the 3 MCP servers: `api_connector`, `mongodb_connector`, `file_connector`.

| Symptom | Likely cause | Where to look | Fix |
|---|---|---|---|
| Tool call fails with `-32602` | Invalid input (bad enum, missing field, disallowed operator/path) | Server logs: `validation_failed` / `api_call_start` line before the error | Correct the tool arguments; this is a client bug, not a server bug |
| `-32001` from `api_connector` | GitHub API timeout, 5xx, or network error, retries exhausted | Logs: `api_retry_exhausted`, `api_server_error` | Check GitHub status; confirm `API_TIMEOUT_SECONDS` / `MAX_RETRIES` are reasonable |
| `-32004` (rate limited) from `api_connector` | `x-ratelimit-remaining: 0` header seen | Response `retry_after_seconds` in the error message | Wait until reset, or use `rate_limit_status` tool to check before bursts |
| `-32002` (auth) from `api_connector` | Missing/expired `GITHUB_TOKEN`, wrong scopes | `.env` `GITHUB_TOKEN` | Rotate token, verify scopes cover the repo |
| `-32004` (database error) from `mongodb_connector` | Mongo unreachable, pool exhausted, query timeout | Logs: `database_error`; `health://status` reports `disconnected` | Check `MONGODB_URI`, network/firewall, `MONGO_MAX_POOL_SIZE` under load |
| Write denied (`-32002`) from `mongodb_connector` | `WRITES_ENABLED=false` (default) | `.env` | Set `WRITES_ENABLED=true` only when writes are intended |
| `-32003` from `file_connector` | File does not exist under `ALLOWED_ROOTS` | `read_file` request path in logs | Confirm the relative path and that the root actually contains it |
| `-32002` from `file_connector` | Path traversal (`../`) or absolute path | Logs: `path_traversal_blocked` | Expected behavior — reject the request, do not relax `resolve_safe_path` |
| `-32005` from `file_connector` | File larger than `MAX_FILE_SIZE_MB` | File size in the error message | Raise the limit deliberately in `.env`, or read a smaller file |
| `health://status` reports `degraded` | External dependency down (Mongo ping fails / no accessible file roots) | Same resource per server | Restore the dependency; do not restart the process for stateless servers unless health stays degraded |
| Server exits immediately on startup | Missing `.env` / bad env var type (e.g. non-integer port) | Startup traceback | Copy the matching `*.env.example`, fix the failing field |

## Escalation order
1. Check the relevant `health://status` resource.
2. Check `metrics://stats` for failure counts / recent activity.
3. Grep server logs for the `request_id` / `correlation_id` in the error.
4. Only then treat as a server bug and open an issue with the request/correlation ID.
