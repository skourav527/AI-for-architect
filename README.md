# 🚀 AI & LLM Engineering Learning Journey

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **A comprehensive, hands-on learning repository for mastering AI Engineering, LLM integration, and Model Context Protocol (MCP) development.**

## � Top 20 AI Topics Covered

### **Foundation & Core Skills** (Weeks 1-5)

**1. ⚡ Async Streaming LLM Clients**
- Real-time token streaming from OpenAI & Anthropic
- Production-grade error handling & retry logic
- **Topics:** `streaming-api`, `async-python`, `real-time-ai`

**2. 🔌 Model Context Protocol (MCP) Servers**
- Build custom MCP servers from scratch
- Connect AI to APIs, databases, file systems
- **Topics:** `mcp-protocol`, `anthropic-mcp`, `tool-integration`

**3. 🎯 Multi-Provider LLM Gateway**
- Abstract OpenAI, Anthropic, Cohere behind unified interface
- Auto-failover & cost optimization
- **Topics:** `llm-gateway`, `multi-provider`, `ai-abstraction`

### **Context & Prompt Engineering** (Weeks 6-10)

**4. 📝 Production Prompt Engineering Patterns**
- System prompt templates, few-shot patterns, chain-of-thought
- Structured output enforcement with retry
- **Topics:** `prompt-engineering`, `system-prompts`, `structured-outputs`

**5. 🧠 Intelligent Context Assembly**
- Dynamic token budget management
- Context window optimization strategies
- **Topics:** `context-management`, `token-optimization`, `memory-management`

**6. 🔍 Agentic RAG Systems**
- Self-corrective retrieval, adaptive query refinement
- Hybrid search (BM25 + vector) + reranking
- **Topics:** `agentic-rag`, `self-corrective-ai`, `retrieval-augmented-generation`

**7. 📊 Vector Search & Embeddings Pipeline**
- Semantic chunking, embedding strategies, hybrid search
- ChromaDB, FAISS, Pinecone integration examples
- **Topics:** `vector-search`, `embeddings`, `semantic-search`

### **Orchestration & Reliability** (Weeks 11-15)

**8. 🔀 LangGraph Workflow Orchestration**
- State machines for AI workflows
- Human-in-the-loop, persistence, conditional routing
- **Topics:** `langgraph`, `workflow-orchestration`, `ai-pipelines`

**9. 🛡️ LLM Guardrails & Safety**
- Input validation, prompt injection detection
- Output filtering (PII, toxicity), OWASP LLM Top 10
- **Topics:** `llm-security`, `guardrails`, `prompt-injection-prevention`

**10. 🔄 Self-Healing AI Systems**
- Self-critique loops, output validation & refinement
- Fallback models & graceful degradation
- **Topics:** `self-healing`, `ai-reliability`, `fault-tolerance`

**11. 💰 AI Cost Optimization Framework**
- Model routing (cheap → expensive), token budgets
- Request caching, response streaming optimization
- **Topics:** `cost-optimization`, `token-budgeting`, `ai-economics`

### **Agentic AI** (Weeks 16-20)

**12. 🤖 ReAct & Tool-Using Agents**
- Reasoning + Acting loop, tool selection & execution
- Memory persistence across sessions
- **Topics:** `react-pattern`, `ai-agents`, `tool-use`

**13. 🎭 Multi-Agent Orchestration**
- Coordinator-worker patterns, agent handoffs
- Shared memory & governance (audit trails)
- **Topics:** `multi-agent-systems`, `agent-coordination`, `distributed-ai`

**14. 🧪 Plan-and-Execute AI Agents**
- Task decomposition, step-by-step execution
- Dynamic replanning based on outcomes
- **Topics:** `plan-execute`, `task-decomposition`, `autonomous-agents`

**15. 🔗 MCP-Powered Agent Toolchain**
- Agents using MCP servers as tools
- Enterprise integrations (Azure DevOps, Jira, GitHub)
- **Topics:** `mcp-agents`, `enterprise-ai`, `tool-agents`

### **Production & Architecture** (Weeks 21-24)

**16. 🏗️ AI System Architecture Patterns**
- Reference architectures for RAG, agentic, batch AI
- Multi-tenant AI design, scalability patterns
- **Topics:** `ai-architecture`, `system-design`, `enterprise-ai`

**17. 📈 LLMOps & AI Observability**
- Logging, tracing, evaluation pipelines
- Cost tracking, quality metrics, A/B testing
- **Topics:** `llmops`, `ai-observability`, `mlops`

**18. 🔐 Enterprise AI Security & Governance**
- Data isolation, access control, compliance
- Audit logging, model governance, responsible AI
- **Topics:** `ai-security`, `ai-governance`, `responsible-ai`

**19. ⚙️ AI Platform Engineering**
- Model gateways (LiteLLM), inference routing
- Kubernetes for AI workloads, vector DB scaling
- **Topics:** `ai-platform`, `platform-engineering`, `ai-infrastructure`

**20. 🎯 Production AI Application (Capstone)**
- End-to-end system: MCP + RAG + Agents + Guardrails
- Your work automation tool (ADO assistant, code reviewer, etc.)
- **Topics:** `production-ai`, `enterprise-application`, `ai-automation`

---

## �📖 About This Repository

This repository documents my **24-week intensive journey** into AI Engineering, covering everything from Python fundamentals to production-ready LLM applications and MCP server development. Perfect for developers looking to transition into AI/ML roles or enhance their LLM integration skills.

### 🎯 What You'll Learn

- **Foundation** (Weeks 1-4): Python async patterns, LLM client implementations (OpenAI, Anthropic), streaming responses, error handling
- **MCP Development** (Weeks 3-4): Building production-grade Model Context Protocol servers and clients
- **Production Patterns**: Token tracking, rate limiting, retry logic, monitoring, and deployment strategies
- **Real-World Projects**: Multi-provider CLI tools, streaming clients, MCP integrations

## 🗂️ Repository Structure

```
📁 Foundation-Week-1/          # Python fundamentals & LLM basics
  ├── project1-llm-client/     # OpenAI & Anthropic streaming clients
  ├── project2-multi-provider-cli/  # Cross-provider CLI tool
  ├── project3-token-tracker/  # Usage monitoring & budgeting
  └── quick-references/        # Cheat sheets & patterns

📁 Foundation-Week-2/          # Advanced async patterns
  └── Project-1/               # Enhanced multi-provider implementation

📁 Foundation-Week-3/          # MCP Protocol deep-dive
  └── Mcp-Project-1/          # MCP server/client implementations
    ├── core/                  # Core MCP abstractions
    ├── sampling/              # Prompt sampling patterns
    └── stdio-vs-statelesshttptransport/  # Transport comparisons

📁 Foundation-Week-4/          # Production deployment
  ├── templates/               # Production-ready templates
  └── Document/                # Deployment guides & checklists

📁 mcp-servers/                # Real-world MCP integrations
  ├── ado_server.py           # Azure DevOps MCP server
  └── sonarqube_server.py     # SonarQube MCP server

📁 knowledge-material/         # Learning resources & documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- OpenAI and/or Anthropic API keys

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-llm-learning-journey.git
   cd ai-llm-learning-journey
   ```

2. **Set up environment**
   ```bash
   # Install uv if not already installed
   pip install uv

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Configure API keys**
   ```bash
   # Copy the template
   cp .env.template .env
   
   # Edit .env and add your API keys
   # OPENAI_API_KEY=sk-your-key-here
   # ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

### Example Usage

#### 1. Basic Streaming Chat

```bash
cd Foundation-Week-1/project1-llm-client
uv run openAPI_streaming_client.py
```

#### 2. Multi-Provider CLI

```bash
cd Foundation-Week-1/project2-multi-provider-cli
uv run chat_cli.py --provider openai --prompt "Explain async Python"
```

#### 3. MCP Server

```bash
cd Foundation-Week-3/Mcp-Project-1
uv run mcp_server.py
```

## 🎓 Learning Path

### Week 1: Foundations
- ✅ Python async/await patterns
- ✅ HTTP clients with `httpx`
- ✅ Retry logic with `tenacity`
- ✅ Data validation with `pydantic`
- ✅ OpenAI & Anthropic SDK integration

### Week 2: Advanced Integration
- ✅ Streaming responses
- ✅ Error handling strategies
- ✅ Provider abstraction patterns
- ✅ CLI tool development

### Week 3: MCP Protocol
- ✅ MCP architecture & concepts
- ✅ Server/client implementation
- ✅ Tool registration & invocation
- ✅ Prompt sampling
- ✅ Transport mechanisms (stdio, HTTP)

### Week 4: Production Readiness
- ✅ Deployment patterns
- ✅ Monitoring & logging
- ✅ Security best practices
- ✅ Performance optimization

## 📚 Key Projects

### 🤖 Multi-Provider LLM CLI
A unified CLI interface for multiple LLM providers with streaming support, error handling, and token tracking.

**Features:**
- Provider abstraction (OpenAI, Anthropic, extensible)
- Real-time streaming responses
- Comprehensive error handling
- Token usage monitoring
- Async/await patterns

[View Project →](Foundation-Week-1/project2-multi-provider-cli/)

### 🔌 MCP Server Framework
Production-ready Model Context Protocol server implementations with real-world integrations.

**Features:**
- Standard MCP protocol compliance
- Tool registration & execution
- Prompt sampling
- Multiple transport options
- Azure DevOps & SonarQube integrations

[View Project →](Foundation-Week-3/Mcp-Project-1/)

## 🛠️ Tech Stack

**Core Technologies:**
- Python 3.10+
- `asyncio` for concurrency
- `httpx` for HTTP clients
- `pydantic` for data validation
- `tenacity` for retry logic

**LLM Integration:**
- OpenAI SDK
- Anthropic SDK
- Model Context Protocol (MCP)

**Development Tools:**
- `uv` for package management
- `pytest` for testing
- `black` for code formatting
- VS Code with Python extensions

## 📈 Progress Tracking

Track my learning journey through the [AI_24W_MASTER_TRACKER](Learning-Plan/AI_24W_MASTER_TRACKER.md) which includes:
- Daily study logs
- Project milestones
- Knowledge checkpoints
- Resource compilations

## 🤝 Contributing

Contributions, suggestions, and feedback are welcome! Whether you're:
- Fixing bugs or improving code
- Adding new examples or projects
- Enhancing documentation
- Sharing learning resources

Please check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 Learning Resources

Each week includes comprehensive documentation:
- 📖 Study sheets with key concepts
- 🎯 Quick reference cheatsheets
- 📋 Practice plans with exercises
- 💡 Production best practices

## 🔒 Security

- **Never commit API keys** - Use `.env` files (already in .gitignore)
- **Review code before pushing** - Check for sensitive data
- API keys in examples are placeholders only
- See [SECURITY.md](SECURITY.md) for full security guidelines

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If you find this repository helpful:
- ⭐ Star this repository
- 🔀 Fork it for your own learning
- 📣 Share it with others
- 💬 Open issues for questions/discussions

## 📬 Connect

Have questions or want to collaborate? Feel free to:
- Open an issue for technical questions
- Start a discussion for general topics
- Share your own learning journey

---

**📌 Note:** This is a learning repository. Code examples prioritize educational clarity over production optimization. For production use, additional error handling, testing, and security measures should be implemented.

**🚧 Status:** Actively maintained and updated weekly as I progress through the learning curriculum.

---

*Happy Learning! 🎉*
