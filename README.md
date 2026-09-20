# AI Platform and Agentic Systems Architect Learning Journey

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A hands-on 24-week journey from LLM foundations and MCP to agent runtimes, governed agent fleets, and enterprise AI platform architecture.

## Current Progress

**Current position: Week 6 - Context Engineering and Prompt Mastery**

- **Weeks 1-5:** Foundation phase complete as of September 10, 2026.
- **Certificates earned:** Anthropic Introduction to MCP and MCP Advanced Topics.
- **Week 6:** Theory and notes in progress, including context lifecycle and context/memory/state separation.
- **Next build:** Week 7 `ContextEngine`, using four reusable runtime primitives.

The repository reflects the learning state, not a claim that every planned topic is already complete. Future weeks are shown below as the intended build sequence.

## Program Coverage

### Phase 1: Foundations (Weeks 1-5)

**Weeks 1-2: Async LLM clients and provider integration**
- Real-time token streaming from OpenAI & Anthropic
- Production-grade error handling & retry logic
- **Topics:** `streaming-api`, `async-python`, `real-time-ai`

**Weeks 3-4: Model Context Protocol and production MCP servers**
- Build custom MCP servers from scratch
- Connect AI to APIs, databases, file systems
- **Topics:** `mcp-protocol`, `anthropic-mcp`, `tool-integration`

**Week 5: Flex review and MCP certifications**
- Review Weeks 1-4 and close any remaining foundation tasks
- Complete the Anthropic MCP certifications
- **Topics:** `mcp-certification`, `review`, `capstone-direction`

### Phase 2: Context Engineering and RAG (Weeks 6-10)

**Week 6: Context engineering and prompt mastery**
- System prompt templates, few-shot patterns, chain-of-thought
- Structured output enforcement with retry
- **Topics:** `prompt-engineering`, `system-prompts`, `structured-outputs`

**Week 7: Context primitives and `ContextEngine`**
- Dynamic token budget management, context lifecycle, compaction
- Context vs memory vs state — the separation reliable agents depend on
- **Topics:** `context-engineering`, `token-optimization`, `agent-state`

**Weeks 8-9: Advanced RAG and retrieval as a capability**
- Self-corrective retrieval, adaptive query refinement
- Hybrid search (BM25 + vector) + reranking
- **Topics:** `agentic-rag`, `self-corrective-ai`, `retrieval-augmented-generation`

**Week 10: Flex review, Phase 2 integration, and ADR-01 draft**
- Integrate `ContextEngine`, the RAG capability, and MCP
- Review Phase 2 and draft ADR-01
- **Topics:** `integration`, `architecture-decisions`, `retrieval-capabilities`

### Phase 3: Agent Runtime Engineering (Weeks 11-15)

**Week 11: Agent Runtime architecture**
- The execution engine that turns a model into a reliable, stateful worker
- Context · state · planning · tool orchestration · subagents · HITL · recovery
- Architecture-first; LangGraph / OpenAI Agents SDK / managed runtimes as reference implementations
- **Topics:** `agent-runtime`, `agent-execution`, `stateful-agents`

**Week 12: Minimal Agent Runtime build**
- Typed durable state, checkpoint-per-step, idempotent resume
- Long-running agent execution, partial failure, graceful degradation
- **Topics:** `durable-execution`, `checkpointing`, `fault-tolerance`

**Weeks 13-14: Reliable, secure, observable runtime hardening**
- Agent identity, capability-based tool permissions, least privilege, sandbox isolation
- Prompt injection containment, tool poisoning, confused deputy, OWASP LLM Top 10
- **Topics:** `llm-security`, `agent-security`, `sandboxing`

**Week 15: Flex review, certifications, and human approval ADR**
- Review the runtime phase and complete planned certifications
- Document human approval architecture and integrate the runtime components
- **Topics:** `runtime-review`, `human-approval`, `certification`

### Phase 4: Agents and Agent Fleet (Weeks 16-20)

**Weeks 16-17: Agents as runtime configurations**
- ReAct and Plan-Execute running on ONE runtime — identity, capabilities, budgets
- Scoped tool permissions enforced by the runtime, not the prompt
- **Topics:** `react-pattern`, `ai-agents`, `tool-use`

**Weeks 18-19: Multi-agent coordination, A2A concepts, and agent registry**
- Coordinator-worker patterns, delegation, handoff contracts
- Shared vs isolated state, agent registry, discovery, versioning
- **Topics:** `multi-agent-systems`, `agent-fleet`, `agent-coordination`

**Week 20: Flex review, portfolio, and Claude Code certification**
- Complete the Claude Code certification and review the fleet phase
- Prepare the runtime, agent, and registry work for the portfolio
- **Topics:** `portfolio`, `certification`, `architecture-review`

### Phase 5: Control Plane and Platform Architecture (Weeks 21-24)

**Week 21: Enterprise AI Control Plane theory**
- Identity · policy-as-code · agent registry · governance · evaluation · observability · cost
- Control plane vs runtime; data plane separation; policy enforcement points
- **Topics:** `ai-control-plane`, `ai-governance`, `platform-architecture`

**Week 22: Simplified Control Plane build**
- Build identity, registry, policy, cost, audit, observability, and evaluation capabilities
- Integrate the control plane with the Agent Runtime
- **Topics:** `control-plane`, `policy-enforcement`, `multi-tenancy`

**Week 23: Evaluation, observability, cost, and governance**
- Golden sets, trajectory evaluation, quality gates, OpenTelemetry, and provenance
- Cost attribution, budgets, quotas, risk classification, and governance
- **Topics:** `llmops`, `agent-evaluation`, `ai-governance`

**Week 24: Governed Agent Platform capstone and certification exam**
- Complete the Claude Certified Architect exam and final architecture document
- Assemble the governed platform from the control plane, runtime, agents, and MCP layer
- **Topics:** `capstone`, `enterprise-ai-platform`, `governed-agent-fleet`

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
| **Control Plane** | 21-22 | Identity · policy · registry · audit |
| **Operability and Capstone** | 23-24 | Evaluation · cost · governance · final platform |

Full roadmap: [Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md](Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md)
Progress tracker: [Learning-Plan/AI_24W_MASTER_TRACKER.md](Learning-Plan/AI_24W_MASTER_TRACKER.md)

---

## About This Repository

This repository documents a **24-week architecture-first learning journey**. It starts with Python and LLM integration, then builds context-aware systems, a reliable agent runtime, an agent fleet, and an enterprise control plane. The code and notes are added incrementally as each phase is completed.

### What You Will Learn

- **Foundations** (Weeks 1-5): Python async patterns, multi-provider LLM clients, streaming, MCP, production integrations, and certifications
- **Context and RAG** (Weeks 6-10): Prompt architecture, structured outputs, memory, context budgets, compaction, hybrid retrieval, reranking, and retrieval capabilities
- **Agent Runtime** (Weeks 11-15): Execution loops, typed state, tools, checkpointing, resume, approvals, security, sandboxing, reliability, and OpenTelemetry
- **Agents and Fleet** (Weeks 16-20): Agent configurations, budgets, permissions, delegation, MCP versus A2A, multi-agent coordination, and registry design
- **Control Plane** (Weeks 21-24): Identity, policy, governance, evaluation gates, observability, cost attribution, audit, multi-tenancy, and the governed platform capstone

## 24-Week Coverage at a Glance

| Week | Type | What the week covers | Main outcome |
|------|------|----------------------|--------------|
| 1 | Theory | Python async patterns, LLM APIs, streaming, Pydantic, retries | Foundation notes and comparisons |
| 2 | Practice | OpenAI and Anthropic clients, streaming, retry, rate limiting, CLI | Multi-provider CLI |
| 3 | Theory | MCP architecture, JSON-RPC, tools, resources, prompts, transports | MCP architecture and security notes |
| 4 | Practice | API, database, and file/RAG MCP servers; validation, security, testing | Three production-pattern MCP builds |
| 5 | Flex | Review, catch-up, MCP certifications, capstone direction | Two Anthropic MCP certificates |
| 6 | Theory | Prompt patterns, structured outputs, memory, token economics, grounding, context lifecycle | Context engineering playbook |
| 7 | Practice | Output validation, memory compaction, few-shot selection, budget enforcement | Typed `ContextEngine` |
| 8 | Theory | Chunking, embeddings, hybrid search, reranking, agentic RAG | RAG decision tree and capability contract |
| 9 | Practice | Hybrid RAG, bounded self-correction, reranking, work-document evaluation | RAG exposed as a typed MCP capability |
| 10 | Flex | Review, ContextEngine + RAG + MCP integration, ADR-01 draft | Phase 2 integration checkpoint |
| 11 | Theory | Runtime anatomy, state, planning, tools, durability, approvals, sandboxing | Agent Runtime reference architecture |
| 12 | Practice | Minimal runtime loop, SQLite state, checkpointing, resume, approvals, tracing | Recoverable Agent Runtime |
| 13 | Theory | Reliability, prompt injection containment, identity, authorization, guardrails, OTel | Runtime threat and reliability model |
| 14 | Practice | Runtime hardening, fallbacks, idempotency, permissions, sandbox, stress tests | Secure and observable runtime |
| 15 | Flex | Review, certifications, runtime integration, human approval architecture | ADR-04 and phase consolidation |
| 16 | Theory | ReAct, Plan-Execute, Reflexion, agent identity, capabilities, memory boundaries | Agent pattern and configuration catalog |
| 17 | Practice | Agents on one runtime, budgets, permissions, retrievable memory, sandboxing | ReAct and Plan-Execute agents |
| 18 | Theory | Multi-agent coordination, delegation, MCP versus A2A, fleet concepts | Fleet and handoff design |
| 19 | Practice | Coordinator and specialists, handoffs, isolated state, registry, policy enforcement | Multi-agent system with registry seed |
| 20 | Flex | Review, Claude Code certification, portfolio preparation | Portfolio repos and ADR consolidation |
| 21 | Theory | Control-plane capabilities, four identities, policy enforcement points, governance | Control Plane capability map and ADR-07 |
| 22 | Practice | Identity, registry, policy, cost, audit, traces, evaluation gate, integration | Simplified Control Plane and design document |
| 23 | Theory | Output/tool/trajectory evaluation, quality gates, OTel, FinOps, risk, provenance | Evaluation and governance model |
| 24 | Capstone | Certification exam and final governed-agent architecture | Enterprise Governed Agent Platform |

## Repository Structure

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

## Quick Start

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

## Completed Foundation Work

### Weeks 1-2: LLM Client Foundations
- ✅ Python async/await patterns
- ✅ HTTP clients with `httpx`
- ✅ Retry logic with `tenacity`
- ✅ Data validation with `pydantic`
- ✅ OpenAI & Anthropic SDK integration

### Weeks 3-4: MCP Development
- ✅ MCP architecture & concepts
- ✅ Server/client implementation
- ✅ Tool registration & invocation
- ✅ Prompt sampling
- ✅ Transport mechanisms (stdio, HTTP)
- ✅ Deployment patterns
- ✅ Monitoring & logging
- ✅ Security best practices
- ✅ Performance optimization

### Week 5: Certifications
- ✅ Anthropic Introduction to MCP
- ✅ Anthropic MCP Advanced Topics

## 📚 Key Projects

### Multi-Provider LLM CLI
A unified CLI interface for multiple LLM providers with streaming support, error handling, and token tracking.

**Features:**
- Provider abstraction (OpenAI, Anthropic, extensible)
- Real-time streaming responses
- Comprehensive error handling
- Token usage monitoring
- Async/await patterns

[View Project →](Foundation-Week-1/project2-multi-provider-cli/)

### MCP Server Framework
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

**🚧 Status:** Phase 1 complete. Currently progressing through Week 6 of Phase 2; future phases are planned and will be implemented incrementally.

---

*Happy Learning! 🎉*
