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
- Dynamic token budget management, context lifecycle, compaction
- Context vs memory vs state — the separation reliable agents depend on
- **Topics:** `context-engineering`, `token-optimization`, `agent-state`

**6. 🔍 Agentic RAG Systems**
- Self-corrective retrieval, adaptive query refinement
- Hybrid search (BM25 + vector) + reranking
- **Topics:** `agentic-rag`, `self-corrective-ai`, `retrieval-augmented-generation`

**7. 📊 Vector Search & Embeddings Pipeline**
- Semantic chunking, embedding strategies, hybrid search
- ChromaDB, FAISS, Pinecone integration examples
- **Topics:** `vector-search`, `embeddings`, `semantic-search`

### **Agent Runtime Engineering** (Weeks 11-15)

**8. 🔁 Agent Runtime Architecture**
- The execution engine that turns a model into a reliable, stateful worker
- Context · state · planning · tool orchestration · subagents · HITL · recovery
- Architecture-first; LangGraph / OpenAI Agents SDK / managed runtimes as reference implementations
- **Topics:** `agent-runtime`, `agent-execution`, `stateful-agents`

**9. 💾 Checkpointing, Resume & Failure Recovery**
- Typed durable state, checkpoint-per-step, idempotent resume
- Long-running agent execution, partial failure, graceful degradation
- **Topics:** `durable-execution`, `checkpointing`, `fault-tolerance`

**10. 🛡️ Runtime Security & Guardrails**
- Agent identity, capability-based tool permissions, least privilege, sandbox isolation
- Prompt injection containment, tool poisoning, confused deputy, OWASP LLM Top 10
- **Topics:** `llm-security`, `agent-security`, `sandboxing`

**11. 🔎 Agent Observability (OpenTelemetry-first)**
- OTel GenAI semantic conventions → agent, tool and model spans
- Vendor-neutral tracing; backends (LangSmith/Phoenix) as interchangeable implementations
- **Topics:** `opentelemetry`, `ai-observability`, `agent-tracing`

### **Agents & Agent Fleet** (Weeks 16-20)

**12. 🤖 Agents as Runtime Configurations**
- ReAct and Plan-Execute running on ONE runtime — identity, capabilities, budgets
- Scoped tool permissions enforced by the runtime, not the prompt
- **Topics:** `react-pattern`, `ai-agents`, `tool-use`

**13. 🎭 Multi-Agent Orchestration & Agent Fleet**
- Coordinator-worker patterns, delegation, handoff contracts
- Shared vs isolated state, agent registry, discovery, versioning
- **Topics:** `multi-agent-systems`, `agent-fleet`, `agent-coordination`

**14. 🧪 Plan-and-Execute AI Agents**
- Task decomposition, step-by-step execution
- Dynamic replanning based on outcomes
- **Topics:** `plan-execute`, `task-decomposition`, `autonomous-agents`

**15. 🔗 MCP & A2A — Tools vs Agents**
- Agents using MCP servers as tools; A2A for agent-to-agent interop
- Enterprise integrations (Azure DevOps, Jira, GitHub) + cross-agent trust
- **Topics:** `mcp-agents`, `a2a`, `enterprise-ai`

### **Control Plane & Platform Architecture** (Weeks 21-24)

**16. 🏛️ Enterprise AI Control Plane**
- Identity · policy-as-code · agent registry · governance · evaluation · observability · cost
- Control plane vs runtime; data plane separation; policy enforcement points
- **Topics:** `ai-control-plane`, `ai-governance`, `platform-architecture`

**17. 📈 Evaluation, Quality Gates & LLMOps**
- Golden sets, LLM-as-judge, **agent trajectory evaluation**
- Quality gates that block promotion; CI/CD for agents
- **Topics:** `llmops`, `ai-evaluation`, `quality-gates`

**18. 💰 AI Cost Management & FinOps**
- Token + tool cost attribution to agent → tenant → business owner
- Budgets, quotas, rate limits, model routing
- **Topics:** `ai-finops`, `cost-attribution`, `token-budgeting`

**19. 🔐 Governance, Risk, Audit & Multi-Tenancy**
- Risk classification → required controls, audit trails, provenance, compliance
- Tenant isolation across data, state, budget, policy and traces
- **Topics:** `ai-governance`, `responsible-ai`, `multi-tenancy`

**20. 🎯 Enterprise Governed Agent Platform (Capstone)**
- End-to-end: Control Plane → Agent Runtime → Models / Tools / Agents via MCP
- 20-section architecture document + 12 ADRs
- **Topics:** `governed-agent-fleet`, `enterprise-ai-platform`, `production-ai`

---

## 🧭 Architecture Progression

```
LLM → Context → RAG → Tools/MCP → Agent → Agent Runtime
    → Multi-Agent System → Enterprise AI Control Plane
    → Governed Agent Fleet → Enterprise AI Platform
```

| Phase | Weeks | Capability |
|-------|-------|-----------|
| Foundations | 1-5 | Models · Tools · MCP |
| Context + RAG | 6-10 | Context lifecycle · retrieval as a capability |
| **Agent Runtime** | 11-15 | Execution · recovery · security · observability |
| Agents & Fleet | 16-20 | Identity · delegation · registry |
| **Control Plane** | 21-22 | Policy · governance · evaluation · cost |
| Governed Platform | 23-24 | The capstone |

Full roadmap: [Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md](Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md)
Progress tracker: [Learning-Plan/AI_24W_MASTER_TRACKER.md](Learning-Plan/AI_24W_MASTER_TRACKER.md)

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
