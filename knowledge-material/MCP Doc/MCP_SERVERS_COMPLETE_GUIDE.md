# MCP Servers in Agentic AI - Complete Learning Path

## Table of Contents
1. [Fundamentals](#fundamentals)
2. [Architecture & How MCP Works](#architecture--how-mcp-works)
3. [MCP in AI Ecosystem](#mcp-in-ai-ecosystem)
4. [Role in Agentic AI](#role-in-agentic-ai)
5. [Building Your Own MCP Server](#building-your-own-mcp-server)
6. [Integrating Pre-built MCP Servers](#integrating-pre-built-mcp-servers)
7. [Practical Examples](#practical-examples)
8. [Using Azure DevOps And SonarQube MCP Servers In VS Code With GitHub Copilot](#using-azure-devops-and-sonarqube-mcp-servers-in-vs-code-with-github-copilot)

---

## Fundamentals

### What is MCP (Model Context Protocol)?

**MCP** is a standardized protocol that enables language models (LLMs) and AI agents to safely and securely connect to external data sources, tools, and services. Think of it as a "plug-and-play" adapter for AI models.

**Key Points:**
- **Open Standard**: Developed by Anthropic, now industry-standard for AI integrations
- **Bidirectional Communication**: Enables two-way conversation between AI models and external services
- **Security First**: Built with security and privacy in mind
- **Language Agnostic**: Works with any programming language
- **Context Efficient**: Allows models to access real-time, relevant context

### Why MCP Matters Now

In the era of **Agentic AI**, models need to:
- Access real-time data (not just training data)
- Execute actions on external systems
- Maintain conversations with multiple tools simultaneously
- Ensure security and auditability
- Scale reliably

**MCP solves these problems** by providing a standardized interface.

### Core Concepts

| Concept | Description |
|---------|-------------|
| **Server** | A service exposing resources, tools, and prompts via MCP |
| **Client** | Application using MCP (e.g., Claude, your AI agent) |
| **Resources** | Data exposed by MCP server (documents, files, databases) |
| **Tools** | Functions that can be called/executed |
| **Prompts** | Pre-defined instruction templates |
| **Context** | Information sent to the model in each interaction |

---

## Architecture & How MCP Works

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Application Layer                     │
│  (Your AI Agent, Claude, LLM, Chat Application)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ MCP Protocol (JSON-RPC over stdio/HTTP)
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    MCP Client                                │
│  (Manages MCP connections, handles requests/responses)      │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
    ┌─────▼──┐ ┌────▼────┐ ┌───▼─────┐
    │ MCP    │ │  MCP    │ │  MCP    │
    │Server 1│ │ Server 2│ │ Server 3│
    └────────┘ └────┬────┘ └────┬────┘
       (Tools)      │           │
                    │      ┌────▼─────┐
                    │      │Database   │
              ┌─────▼──┐   │Documents  │
              │File    │   │APIs       │
              │System  │   └───────────┘
              └────────┘
```

### Communication Flow

```
1. USER INPUT
   ↓
2. MCP CLIENT receives input
   ↓
3. CLIENT queries AVAILABLE RESOURCES/TOOLS from MCP SERVERS
   ↓
4. SERVERS respond with their capabilities
   ↓
5. CLIENT selects relevant tools/resources
   ↓
6. LLM receives context: tools available + data from resources
   ↓
7. LLM decides which tool to call and with what parameters
   ↓
8. CLIENT formats request and sends to appropriate MCP SERVER
   ↓
9. SERVER executes tool/reads resource
   ↓
10. SERVER returns result to CLIENT
    ↓
11. CLIENT provides result to LLM
    ↓
12. LLM generates response based on result
```

### Protocol Details

**MCP uses:**
- **JSON-RPC 2.0** for request/response format
- **stdio** (standard input/output) OR **HTTP** for transport
- **SSE** (Server-Sent Events) for streaming responses
- Async/await patterns for non-blocking calls

**Example MCP Request (JSON-RPC):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_documents",
    "arguments": {
      "query": "deployment strategies"
    }
  }
}
```

**Example MCP Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Found 5 documents about deployment strategies..."
      }
    ]
  }
}
```

---

## MCP in AI Ecosystem

### Where MCP Fits

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI ECOSYSTEM LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  • LLM APIs (OpenAI, Anthropic, Azure OpenAI)                  │
│  • Prompt Engineering & Chain-of-Thought (e.g., LangChain)     │
│  • Memory Management & Context Windows                          │
│  • Retrieval-Augmented Generation (RAG)                         │
│  • Agent Orchestration (e.g., AutoGen, LangGraph)              │
└────────────────────┬────────────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │   MCP LAYER         │
          │ (Integration Hub)   │
          └──────────┬──────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
   │ Data    │ │ Tools   │ │ External│ │ Logging │
   │ Sources │ │ Layer   │ │ APIs    │ │ & Audit │
   ├────────┤ ├────────┤ ├────────┤ ├────────┤
   │Database │ │Slack   │ │Azure   │ │ Traces │
   │Files    │ │GitHub  │ │GitHub  │ │ Events │
   │APIs     │ │Jenkins │ │DevOps  │ │ Logs   │
   │Docs     │ │SonarQube           │         │
   └────────┘ └────────┘ └────────┘ └────────┘
```

### Integration Points

**MCP connects to multiple layers:**

1. **Data Layer**: Databases, files, document stores
2. **Tool Layer**: Slack, GitHub, Jenkins, SonarQube
3. **API Layer**: REST APIs, Cloud services (Azure, AWS, GCP)
4. **Monitoring Layer**: Logging, tracing, auditing

---

## Role in Agentic AI

### What Are AI Agents?

AI Agents are systems that can:
- Perceive environment (receive data)
- Make decisions (reason about data)
- Take actions (execute tools)
- Learn from results
- Iterate autonomously

### MCP's Critical Role in Agents

```
AGENT LOOP:
┌──────────────────────────────────────────────────────┐
│ 1. PERCEPTION: Agent reads from MCP resources        │
│    (current state, recent events, relevant context)  │
├──────────────────────────────────────────────────────┤
│ 2. REASONING: LLM thinks about problem/data          │
│    (chain-of-thought, planning)                      │
├──────────────────────────────────────────────────────┤
│ 3. ACTION: Agent calls MCP tools                     │
│    (create ticket, deploy code, update docs)         │
├──────────────────────────────────────────────────────┤
│ 4. OBSERVATION: Agent receives tool results         │
│    via MCP (feedback from action)                    │
└──────────────────────────────────────────────────────┘
     ↓
    Loop continues until goal achieved
```

### Why MCP is Essential for Agents

| Challenge | How MCP Solves It |
|-----------|-------------------|
| **Context Window Limits** | MCP provides only relevant context on-demand |
| **Real-time Action** | Tools execute immediately, agents respond to live data |
| **Multiple Service Integration** | Single protocol connects all services |
| **Security** | MCP handles authentication, authorization, sandboxing |
| **Auditability** | All agent actions logged through MCP |
| **Scalability** | Multiple MCP servers handle load distribution |

### Agent Architectures Using MCP

**1. Single-Tool Agent**
```
Agent → MCP Client → [MCP Server: GitHub API] → GitHub
```

**2. Multi-Tool Agent (Orchestration)**
```
Agent → MCP Client → ┌→ [MCP Server: GitHub]
                     ├→ [MCP Server: Azure DevOps]
                     └→ [MCP Server: SonarQube]
```

**3. Hierarchical Agent System**
```
Master Agent → MCP Client → ┌→ Sub-Agent (DevOps) → MCP Servers
                            ├→ Sub-Agent (Security) → MCP Servers
                            └→ Sub-Agent (Analytics) → MCP Servers
```

---

## Building Your Own MCP Server

### Prerequisites

- **Understanding of your domain**: What data/tools do you expose?
- **Programming language**: Python, TypeScript, Go, etc.
- **Basic networking knowledge**: HTTP/stdio communication
- **Authentication mechanism**: How to secure access?

### Step 1: Define Your MCP Server Scope

**Ask yourself:**
1. What resources do I want to expose?
   - Database records? Files? Real-time metrics?
2. What tools should users call?
   - Search? Create? Update? Delete? Execute?
3. What's the data format?
   - JSON? Markdown? HTML?
4. Security requirements?
   - Authentication? Rate limiting? Audit logging?

### Step 2: MCP Server Development Frameworks

**Python**
- **mcp-server-python**: Official Python SDK
- Install: `pip install mcp`

**TypeScript/Node.js**
- **@modelcontextprotocol/sdk**: Official TypeScript SDK
- Install: `npm install @modelcontextprotocol/sdk`

**Other Languages**
- Go, Rust, C# implementations available
- Community-maintained in other languages

### Step 3: Basic Structure

**Python Example:**
```python
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent

# Initialize server
server = Server("my-document-server")

# Define resources (what data you expose)
@server.resources()
async def list_resources():
    return [
        Resource(
            uri="document://internal-policies",
            name="Internal Policies",
            mimeType="text/markdown"
        )
    ]

# Define tools (what actions users can perform)
@server.tools()
async def search_documents(query: str):
    # Your implementation
    return {
        "results": [
            # matching documents
        ]
    }

# Start server
server.run()
```

**TypeScript Example:**
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-document-server",
  version: "1.0.0",
});

// Define resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "document://internal-policies",
        name: "Internal Policies",
        mimeType: "text/markdown",
      },
    ],
  };
});

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search_documents",
        description: "Search through all documents",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string" },
          },
        },
      },
    ],
  };
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Step 4: Deployment Options

**Local/Development**
```bash
# Run directly
python my_mcp_server.py

# Or with stdio
node my_mcp_server.js
```

**Docker Container**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "my_mcp_server.py"]
```

**Cloud Platforms**
- **AWS Lambda** (serverless, event-driven)
- **Azure Functions** (serverless, HTTP triggers)
- **Google Cloud Functions** (serverless)
- **Kubernetes** (container orchestration)
- **Your own server** (traditional VM/bare metal)

### Step 5: Common MCP Server Types

**Database Server**
- Exposes database records as resources
- Tools: search, create, update, delete
- Example: Connect to MongoDB, PostgreSQL

**File System Server**
- Exposes files/documents
- Tools: read, write, search, organize

**API Proxy Server**
- Wraps external APIs (GitHub, Slack, Jira)
- Adds authentication, rate limiting, caching

**Real-time Data Server**
- Streams metrics, logs, events
- Uses WebSockets or SSE

---

## Integrating Pre-built MCP Servers

### Available MCP Servers (Ecosystem)

#### 1. **Azure DevOps (ADO) MCP Server**

**What it exposes:**
- Work items (user stories, bugs, tasks)
- Git repositories and pull requests
- Build and release pipelines
- Test results and coverage

**Setup:**
```bash
# Install
pip install mcp-azure-devops

# Configure
export ADO_ORG_URL="https://dev.azure.com/yourorg"
export ADO_PROJECT="YourProject"
export ADO_PAT="your-personal-access-token"

# Use in your agent
from mcp_servers import AzureDevOpsMCPServer
server = AzureDevOpsMCPServer()
```

**Example Agent Usage:**
```python
# Agent can now:
# 1. List all open bugs
# 2. Get PR status
# 3. Query build history
# 4. Create work items
# 5. Update pipeline triggers
```

#### 2. **GitHub MCP Server**

**What it exposes:**
- Repositories and branches
- Issues and pull requests
- Workflows and actions
- Repository settings

**Setup:**
```bash
# Install
pip install mcp-github

# Configure
export GITHUB_TOKEN="your-github-token"

# Use in your agent
from mcp_servers import GitHubMCPServer
server = GitHubMCPServer()
```

**Example Tools:**
```
- list_repositories()
- get_pull_requests(repo, state="open")
- create_issue(repo, title, body)
- merge_pull_request(repo, pr_number)
- trigger_workflow(repo, workflow_name)
```

#### 3. **Microsoft Azure MCP Server**

**What it exposes:**
- Azure resources (VMs, databases, storage)
- Azure Key Vault secrets
- Application Insights logs
- Azure Functions and Logic Apps

**Setup:**
```bash
# Install
pip install mcp-azure

# Configure with Azure CLI
az login
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Use in your agent
from mcp_servers import AzureMCPServer
server = AzureMCPServer()
```

**Example Tools:**
```
- list_resources()
- get_resource_metrics(resource_id)
- execute_query(query_language, query)
- get_secret(vault_name, secret_name)
- deploy_function_app()
```

#### 4. **SonarQube MCP Server**

**What it exposes:**
- Project quality metrics
- Code smells and vulnerabilities
- Test coverage data
- Analysis history

**Setup:**
```bash
# Install
pip install mcp-sonarqube

# Configure
export SONARQUBE_URL="https://sonarqube.yourcompany.com"
export SONARQUBE_TOKEN="your-sonarqube-token"

# Use in your agent
from mcp_servers import SonarQubeMCPServer
server = SonarQubeMCPServer()
```

**Example Tools:**
```
- get_project_metrics(project_key)
- list_issues(project_key, severity="HIGH")
- get_coverage_history(project_key)
- get_duplications(project_key)
```

#### 5. **Other Popular Pre-built Servers**

| Server | Purpose | Tools Provided |
|--------|---------|-----------------|
| **Slack MCP** | Team communication | Send messages, list channels, get history |
| **Jira MCP** | Issue tracking | Create issues, update status, add comments |
| **Jenkins MCP** | CI/CD pipelines | Trigger builds, get results, view logs |
| **Datadog MCP** | Monitoring | Query metrics, get alerts, list dashboards |
| **Notion MCP** | Knowledge base | Read pages, create pages, search database |
| **Confluence MCP** | Wiki/docs | Read pages, create pages, search content |
| **Linear MCP** | Product management | List issues, create, update, comment |
| **Stripe MCP** | Payments | Get transactions, create charges, check customers |

### Step 6: Integrating Multiple MCP Servers

**Configuration File (mcp_config.json):**
```json
{
  "servers": [
    {
      "name": "azure-devops",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_azure_devops_server.py"],
      "env": {
        "ADO_ORG_URL": "https://dev.azure.com/myorg",
        "ADO_PAT": "${ADO_PAT}"
      }
    },
    {
      "name": "github",
      "type": "stdio",
      "command": "python",
      "args": ["mcp_github_server.py"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    {
      "name": "sonarqube",
      "type": "http",
      "url": "http://localhost:8000",
      "auth": {
        "type": "bearer",
        "token": "${SONARQUBE_TOKEN}"
      }
    }
  ]
}
```

**Python Agent with Multiple Servers:**
```python
from mcp.client import MCPClient
import json

# Load configuration
with open('mcp_config.json') as f:
    config = json.load(f)

# Initialize client
client = MCPClient()

# Connect to all servers
for server_config in config['servers']:
    if server_config['type'] == 'stdio':
        client.connect_stdio(
            name=server_config['name'],
            command=server_config['command'],
            args=server_config['args'],
            env=server_config['env']
        )
    elif server_config['type'] == 'http':
        client.connect_http(
            name=server_config['name'],
            url=server_config['url'],
            auth=server_config['auth']
        )

# Now your agent has access to all tools from all servers
```

---

## Practical Examples

### Example 1: DevOps Agent Using ADO + GitHub + SonarQube

**Scenario:** Automatically improve code quality

**Agent Workflow:**
```
1. Poll SonarQube for high-severity issues in project
2. For each issue, create GitHub issue in repository
3. Create ADO work item for engineering team
4. Trigger GitHub Actions to run security scan
5. Update ADO dashboard with metrics
6. Send notification to team
```

**Implementation:**
```python
from mcp.client import MCPClient
from anthropic import Anthropic

class DevOpsAgent:
    def __init__(self):
        self.client = MCPClient()
        self.llm = Anthropic()
        
        # Connect to MCP servers
        self.client.connect_stdio("sonarqube", ["python", "mcp_sonarqube.py"])
        self.client.connect_stdio("github", ["python", "mcp_github.py"])
        self.client.connect_stdio("ado", ["python", "mcp_ado.py"])
    
    async def improve_code_quality(self):
        # Get available tools from all servers
        tools = await self.client.list_available_tools()
        
        # Create system prompt
        system = f"""You are a DevOps agent. You have access to these tools:
        {json.dumps(tools)}
        
        Your goal is to improve code quality:
        1. Check SonarQube for high-severity issues
        2. Create GitHub issues for each problem
        3. Create ADO work items
        4. Trigger quality scans
        5. Report results
        """
        
        # Run agent loop
        response = await self.llm.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system,
            messages=[
                {"role": "user", "content": "Improve code quality for all projects"}
            ],
            tools=tools  # Claude sees all available tools
        )
        
        # Execute tool calls
        while response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    tool_result = await self.client.call_tool(
                        block.name,
                        block.input
                    )
                    response = await self.llm.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4096,
                        system=system,
                        messages=[
                            {"role": "user", "content": "Improve code quality"},
                            {"role": "assistant", "content": response.content},
                            {"role": "user", "content": [
                                {"type": "tool_result", "tool_use_id": block.id, "content": str(tool_result)}
                            ]}
                        ],
                        tools=tools
                    )

# Usage
agent = DevOpsAgent()
await agent.improve_code_quality()
```

### Example 2: Custom Database MCP Server

**Scenario:** Expose employee database to AI agents

**Implementation:**
```python
from mcp.server import Server
from pymongo import MongoClient
import json

server = Server("employee-database-server")

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["company"]
employees_collection = db["employees"]

@server.resources()
async def list_resources():
    return [
        {
            "uri": "database://employees",
            "name": "Employee Database",
            "mimeType": "application/json"
        }
    ]

@server.tools()
async def find_employees(department=None, role=None, years_employed=None):
    """Search employees by criteria"""
    query = {}
    if department:
        query["department"] = department
    if role:
        query["role"] = role
    if years_employed:
        query["years_employed"] = {"$gte": years_employed}
    
    results = list(employees_collection.find(query, {"_id": 0}))
    return {
        "total": len(results),
        "employees": results
    }

@server.tools()
async def get_employee_by_id(employee_id: str):
    """Get specific employee details"""
    employee = employees_collection.find_one(
        {"id": employee_id},
        {"_id": 0}
    )
    return employee or {"error": "Not found"}

@server.tools()
async def get_department_stats(department: str):
    """Get department statistics"""
    stats = employees_collection.aggregate([
        {"$match": {"department": department}},
        {"$group": {
            "_id": "$department",
            "total_employees": {"$sum": 1},
            "avg_salary": {"$avg": "$salary"},
            "roles": {"$push": "$role"}
        }}
    ])
    return list(stats)[0] if stats else {}

if __name__ == "__main__":
    server.run()
```

### Example 3: Connecting Pre-built Servers in Claude Web Interface

**If using Claude Desktop with MCP support:**

**config.json (typically ~/.claude_config/config.json):**
```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "python",
      "args": ["-m", "mcp_servers.azure_devops"],
      "env": {
        "ADO_ORG_URL": "https://dev.azure.com/myorg",
        "ADO_PAT": "your-pat-here"
      }
    },
    "github": {
      "command": "python",
      "args": ["-m", "mcp_servers.github"],
      "env": {
        "GITHUB_TOKEN": "your-token-here"
      }
    },
    "sonarqube": {
      "command": "python",
      "args": ["-m", "mcp_servers.sonarqube"],
      "env": {
        "SONARQUBE_URL": "https://sonarqube.company.com",
        "SONARQUBE_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Then in Claude, you can ask:**
- "What's the status of PR #42 in my GitHub repo?"
- "Show me all high-priority bugs in Azure DevOps"
- "List code smells in my SonarQube project"
- "Create an issue in GitHub and link it to ADO work item"

---

## Using Azure DevOps And SonarQube MCP Servers In VS Code With GitHub Copilot

This is the workflow you asked about directly: using **GitHub Copilot inside VS Code** as the MCP client, so Copilot can call Azure DevOps and SonarQube tools during chat or agent-driven work.

### What VS Code Supports

VS Code can load MCP servers from either:

- `.vscode/mcp.json` in your workspace
- your user-level `mcp.json` profile configuration

Once a server is started and trusted, its **tools**, **resources**, and **prompts** become available to GitHub Copilot Chat and agent mode in VS Code.

That means you can ask Copilot things like:

- "Use Azure DevOps to get PR 123, summarize the review comments, and tell me what code changes I should make in this repo."
- "Use SonarQube to list the open critical issues for this project and then fix the matching files in my workspace."
- "Compare the active Azure DevOps PR feedback with the current local branch and propose a patch."

### Practical Architecture In VS Code

```text
VS Code + GitHub Copilot Chat/Agent
            |
            v
       .vscode/mcp.json
            |
   -------------------------
   |                       |
   v                       v
ADO MCP Server       SonarQube MCP Server
   |                       |
   v                       v
Azure DevOps REST API   SonarQube REST API
```

### What You Need

1. VS Code with GitHub Copilot Chat enabled.
2. A workspace-level or user-level `mcp.json`.
3. One MCP server for Azure DevOps.
4. One MCP server for SonarQube.
5. Credentials:
   - Azure DevOps PAT
   - SonarQube token

### Recommended Setup In Your Workspace

In this workspace, use:

- `.vscode/mcp.json` for Copilot MCP configuration
- `mcp-servers/ado_server.py` for Azure DevOps tools
- `mcp-servers/sonarqube_server.py` for SonarQube tools

This keeps the setup local to the project and lets Copilot use those tools only when you are in this workspace.

### Step-By-Step Setup In VS Code

#### 1. Install Python dependencies

Use your workspace interpreter and install the MCP runtime dependencies:

```bash
python -m pip install mcp requests
```

#### 2. Configure `.vscode/mcp.json`

Define both servers in `.vscode/mcp.json`. VS Code will detect them and prompt you to trust them before first start.

Example:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "ado-org-url",
      "description": "Azure DevOps organization URL, for example https://dev.azure.com/yourorg"
    },
    {
      "type": "promptString",
      "id": "ado-project",
      "description": "Azure DevOps project name"
    },
    {
      "type": "promptString",
      "id": "ado-pat",
      "description": "Azure DevOps personal access token"
    },
    {
      "type": "promptString",
      "id": "sonarqube-url",
      "description": "SonarQube base URL, for example https://sonarqube.company.com"
    },
    {
      "type": "promptString",
      "id": "sonarqube-token",
      "description": "SonarQube token",
      "password": true
    }
  ],
  "servers": {
    "azureDevOps": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/mcp-servers/ado_server.py"],
      "env": {
        "ADO_ORG_URL": "${input:ado-org-url}",
        "ADO_PROJECT": "${input:ado-project}",
        "ADO_PAT": "${input:ado-pat}"
      }
    },
    "sonarQube": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/mcp-servers/sonarqube_server.py"],
      "env": {
        "SONARQUBE_URL": "${input:sonarqube-url}",
        "SONARQUBE_TOKEN": "${input:sonarqube-token}"
      }
    }
  }
}
```

#### 3. Start and trust the servers

From VS Code:

1. Run `MCP: List Servers`
2. Start `azureDevOps` and `sonarQube`
3. Confirm the trust prompt
4. If tools do not appear, run `MCP: Reset Cached Tools`

#### 4. Use them from GitHub Copilot Chat

Open Chat in **Agent** mode when you want Copilot to actively call tools.

Good prompts:

- "Use Azure DevOps to list active pull requests for repository `my-service` and summarize the highest-risk PR."
- "Use Azure DevOps to fetch PR 456 in repository `my-service`, get the discussion threads, and tell me what changes are needed locally."
- "Use SonarQube to list open blocker and critical issues for project `my-service`, then fix the matching code in this workspace."
- "Use SonarQube quality metrics for project `my-service`, explain the biggest quality risks, and patch the easiest wins first."

### Best Workflow For PR Review In Azure DevOps

For Azure DevOps PR review, the strongest workflow is:

1. Open the repository locally in VS Code.
2. Check out the PR branch or the source branch.
3. Let Copilot use the Azure DevOps MCP server to pull PR metadata and review threads.
4. Let Copilot use local workspace context to inspect the actual changed files.
5. Ask Copilot to produce or apply code fixes locally.

This is better than using ADO alone because ADO gives Copilot the review metadata, while the local workspace gives Copilot the actual codebase context.

### Best Workflow For SonarQube Fixes

For SonarQube, the best loop is:

1. Ask Copilot to fetch open issues for a project using the SonarQube MCP server.
2. Filter to `BLOCKER`, `CRITICAL`, or a specific rule.
3. Ask Copilot to map those issues to files currently open in the workspace.
4. Ask Copilot to patch the code locally.
5. Re-run your local tests and Sonar scan.

Example prompt:

"Use SonarQube to list open critical issues for project `my-service`. For each issue that maps to a file in this repo, fix it locally and explain the change."

### Limitations You Should Expect

- Copilot can only use the tools your MCP server exposes.
- If your Azure DevOps server only exposes read APIs, Copilot can review PRs but not approve or update them.
- If your SonarQube server only exposes issue-read APIs, Copilot can fix code locally but cannot mark issues resolved in SonarQube directly.
- Tool calls may require your confirmation depending on your VS Code trust and tool approval settings.
- Sandboxing for local stdio MCP servers is not available on Windows today.

### Minimal Tool Set You Actually Need

For Azure DevOps:

- `list_pull_requests`
- `get_pull_request`
- `list_pull_request_threads`
- `list_pull_request_work_items`

For SonarQube:

- `project_quality_gate`
- `list_project_issues`
- `get_issue`
- `get_project_measures`

If you expose only those tools, Copilot already becomes useful for PR review and issue fixing.

### What I Added In This Workspace

I added starter files for exactly this setup:

- `.vscode/mcp.json`
- `mcp-servers/ado_server.py`
- `mcp-servers/sonarqube_server.py`
- `mcp-servers/requirements.txt`

You can use those as the starting point for your own Copilot + Azure DevOps + SonarQube MCP workflow in VS Code.

---

## Learning Path Summary

### Phase 1: Understanding (Week 1-2)
- [ ] Understand MCP protocol and concepts
- [ ] Learn architecture and communication flow
- [ ] Explore existing MCP server ecosystem
- [ ] Read official documentation

### Phase 2: Hands-On Integration (Week 2-3)
- [ ] Install and configure pre-built MCP servers
- [ ] Connect Azure DevOps MCP server
- [ ] Connect GitHub MCP server
- [ ] Test tools manually

### Phase 3: Building Custom Servers (Week 3-4)
- [ ] Design your custom MCP server
- [ ] Choose technology stack
- [ ] Implement resources and tools
- [ ] Test and deploy

### Phase 4: Agent Development (Week 4-5)
- [ ] Build agent logic
- [ ] Integrate multiple MCP servers
- [ ] Implement decision-making
- [ ] Add monitoring and logging

### Phase 5: Production (Week 5+)
- [ ] Security hardening
- [ ] Performance optimization
- [ ] Scaling and reliability
- [ ] Monitoring and observability

---

## Resources & Documentation

### Official Documentation
- **MCP Specification**: https://modelcontextprotocol.io/
- **Anthropic MCP**: https://github.com/modelcontextprotocol
- **Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk

### Community & Examples
- **MCP Hub**: Registry of community MCP servers
- **GitHub MCP Repos**: Search "mcp-" for implementations
- **Discord Communities**: MCP discussions and support

### Key Topics to Explore Next
- Protocol buffers for serialization (advanced)
- OAuth2 and authentication patterns
- Rate limiting and caching strategies
- Monitoring and observability
- Semantic versioning for APIs
- Performance optimization

---

## Quick Decision Trees

### Should I Use Pre-built or Build Custom?

```
START
  ├─ "Need to connect to popular service (GitHub, Jira, etc)?"
  │  ├─ YES → Use pre-built server
  │  └─ NO → Continue
  └─ "Need specialized internal data/tools?"
     ├─ YES → Build custom server
     └─ NO → Use pre-built or compose existing
```

### Which Transport Should I Use?

```
START
  ├─ "Local development/testing?"
  │  ├─ YES → Use stdio (simpler)
  │  └─ NO → Continue
  └─ "Need HTTP access from multiple clients?"
     ├─ YES → Use HTTP/WebSocket
     └─ NO → Use stdio
```

### Where Should I Deploy?

```
START
  ├─ "Always on, high-traffic service?"
  │  ├─ YES → Kubernetes or VMs
  │  └─ NO → Continue
  └─ "Low-traffic, event-driven?"
     ├─ YES → Serverless (AWS Lambda, Azure Functions)
     └─ NO → Traditional server or containers
```

---

## Next Steps

1. **Read official MCP documentation** to solidify concepts
2. **Set up a pre-built server** (GitHub or Azure DevOps)
3. **Create your first custom MCP server** with a database
4. **Build a simple agent** that uses multiple servers
5. **Deploy to production** with monitoring

Good luck on your MCP journey!
