# MCP Servers - Quick Reference Cheat Sheet

## Installation & Setup
```bash
# Install MCP SDK (Python)
pip install mcp pydantic httpx

# Install MCP SDK (TypeScript)
npm install @modelcontextprotocol/sdk
```

## Minimal MCP Server Structure (Python)
```python
from mcp.server import Server

server = Server("my-server")

@server.tools()
async def my_tool(param: str):
    """Tool description"""
    return {"result": "value"}

@server.resources()
async def list_resources():
    return [{"uri": "resource://1", "name": "Resource 1"}]

server.run()
```

## MCP Request/Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "tool_name",
    "arguments": {"key": "value"}
  }
}
```

## Pre-built MCP Servers
| Server | Purpose | Key Tools |
|--------|---------|-----------|
| **Azure DevOps** | Work items, pipelines | list_work_items, create_work_item |
| **GitHub** | Repos, PRs, Issues | list_repos, get_pr, create_issue |
| **Microsoft Azure** | Resources, metrics | list_resource_groups, scale_app |
| **SonarQube** | Code quality | get_metrics, list_issues |
| **Slack** | Team comms | send_message, list_channels |
| **Jira** | Issue tracking | create_issue, update_status |

## MCP Server Security Checklist
- [ ] Implement token-based authentication
- [ ] Add role-based access control (RBAC)
- [ ] Enforce read-only constraints where needed
- [ ] Use parameterized queries (prevent injection)
- [ ] Add audit logging
- [ ] Rate limit requests
- [ ] Validate input schemas
- [ ] Use HTTPS in production

## Agent Loop Pattern
```python
while not goal_achieved:
    1. Perceive()      # Read from MCP resources
    2. Reason()        # LLM decides next action
    3. Act()           # Call MCP tool
    4. Observe()       # Receive feedback, update memory
```

## Docker Deployment
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "mcp_server.py"]
```

## Common Error Codes
| Error | Meaning | Fix |
|-------|---------|-----|
| 400 | Bad Request | Check JSON-RPC format |
| 401 | Unauthorized | Verify authentication token |
| 403 | Forbidden | Check RBAC scopes |
| 404 | Not Found | Tool/resource doesn't exist |
| 500 | Internal Error | Check server logs |

## Testing MCP Servers
```python
# List available tools
response = server.handle_request({
    "jsonrpc": "2.0", "id": 1, "method": "tools/list"
})

# Call a tool
response = server.handle_request({
    "jsonrpc": "2.0", "id": 2,
    "method": "tools/call",
    "params": {"name": "tool_name", "arguments": {}}
})

# List resources
response = server.handle_request({
    "jsonrpc": "2.0", "id": 3, "method": "resources/list"
})
```

## Performance Tips
- Use async/await for I/O operations
- Implement caching for frequently accessed data
- Add result pagination/limits
- Monitor tool execution time
- Use connection pooling for databases
- Implement graceful degradation/fallbacks

## Deployment Platforms
- **Azure Container Instances**: Serverless, event-driven
- **Azure App Service**: Managed web apps with auto-scale
- **Azure Functions**: Serverless functions
- **Kubernetes**: Container orchestration
- **Lambda/Cloud Functions**: Serverless compute

## Learning Resources
- MCP Official Docs: https://modelcontextprotocol.io/
- GitHub MCP Repos: Search "mcp-server-"
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

## Quick Debugging Commands
```bash
# Check if server is running
curl http://localhost:8000/health

# View server logs
docker logs <container_id>

# Test MCP request
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Docker interactive shell
docker exec -it <container_id> /bin/bash
```

---

**Remember**: MCP is the bridge between AI agents and the real world! 🚀
