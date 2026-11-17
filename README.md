# AI Platform and Agentic Systems Architect Learning Journey

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A hands-on 24-week journey from LLM foundations and MCP to agent runtimes, governed agent fleets, and enterprise AI platform architecture.

## Current Progress

**Current position: Week 9 — planned start November 18, 2026.**

- **Weeks 1-5:** Foundation phase complete as of September 10, 2026.
- **Certificates earned:** Anthropic Introduction to MCP and MCP Advanced Topics.
- **Week 6:** Theory and notes complete, including context lifecycle and context/memory/state separation.
- **Week 7:** Practice complete. `ContextEngine` and four reusable runtime primitives are implemented and verified.
- **Week 8:** Complete based on the learner's report on November 17, 2026. The exact completion date, hours, score, and assessment artifacts were not supplied. See the [Week 8 acceptance checklist](Week-8-ContextEngineering-RAG/Document/WEEK8_ACCEPTANCE_CHECKLIST.md).
- **Week 9:** A practical baseline exists in [Week-9-RAG-Implementation](Week-9-RAG-Implementation/); learner acceptance is not verified. Its tests and synthetic smoke set are implementation evidence only, not learner completion or a representative benchmark.
- **Weeks 10-24:** Planned; not started.

The repository reflects the learning state, not a claim that every planned topic is already complete. Prepared material is not the same as completed learning. Future weeks are shown below as the intended build sequence.

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

**Week 5: Flex review and optional MCP certification readiness**
- Review Weeks 1-4 and close any remaining foundation tasks
- Validate MCP architecture, security, and operational readiness
- Use the Anthropic MCP certifications as optional validation
- **Topics:** `mcp-certification`, `review`, `capstone-direction`

### Phase 2: Context Engineering and RAG (Weeks 6-10)

**Week 6: Context engineering and prompt mastery**
- System prompt templates, few-shot patterns, chain-of-thought
- Structured output enforcement with retry
- **Topics:** `prompt-engineering`, `system-prompts`, `structured-outputs`

**Week 7: Context primitives and `ContextEngine` (complete)**
- Dynamic token budget management, context lifecycle, compaction
- Context vs memory vs state — the separation reliable agents depend on
- **Topics:** `context-engineering`, `token-optimization`, `agent-state`

**Weeks 8-9: Advanced retrieval and retrieval as a capability**
- Retrieval evaluation first: Recall@K, Precision@K, MRR, nDCG, citation correctness, groundedness, latency, cost, authorization correctness
- Keyword, dense-vector, and hybrid retrieval chosen by measurement; reranking as an optional measured trade-off
- Bounded self-corrective retrieval, adaptive query refinement, and routing
- Retrieval exposed as a typed capability with enforced authorization and typed failure outcomes
- **Topics:** `agentic-rag`, `retrieval-evaluation`, `retrieval-augmented-generation`

**Week 10: Flex review, Phase 2 integration, and ADR-01 draft**
- Integrate `ContextEngine`, the RAG capability, and MCP, with caller identity preserved end to end
- Review Phase 2 and draft ADR-01
- **Topics:** `integration`, `architecture-decisions`, `retrieval-capabilities`

### Phase 3: Agent Runtime Engineering (Weeks 11-15)

**Week 11: Agent Runtime architecture**
- The execution engine that turns a model into a reliable, stateful worker
- Context · state · planning · tool orchestration · subagents · HITL · recovery
- Agent isolation boundary: protected assets, allowed capabilities, and sandbox choices
- Architecture-first; LangGraph / OpenAI Agents SDK / managed runtimes as reference implementations
- **Topics:** `agent-runtime`, `agent-execution`, `stateful-agents`

**Week 12: Agent harness and isolation**
- Build the trusted execution harness around the runtime and define testable isolation invariants
- Enforce filesystem, process, network, tool/side-effect, memory/context, and identity/credential boundaries
- **Topics:** `agent-harness`, `isolation-boundary`, `sandboxing`

**Week 13: Identity and delegated authorization**
- Separate user and agent identity; prototype scoped delegation, credential brokerage, expiry, revocation and audit
- **Topics:** `delegated-authorization`, `least-privilege`, `identity-propagation`

**Week 14: Agent evaluation, observability and runtime hardening**
- Trajectory/tool/side-effect evaluation, versioned test data, runtime traces and isolation tests
- Provider-neutral telemetry with an explicit OpenTelemetry GenAI convention maturity/version decision
- **Topics:** `agent-evaluation`, `observability`, `runtime-hardening`

**Week 15: Flex review and runtime reliability/operations**
- Integrate Weeks 11-14 as one secure, observable, recoverable runtime; exercise cancellation and recovery
- Review versioning, migration, release readiness, runbooks and human approval architecture
- **Topics:** `runtime-reliability`, `recovery`, `operational-readiness`

### Phase 4: Agentic AI, Interoperability and Orchestration (Weeks 16-20)

**Week 16: Agentic architecture patterns**
- ReAct, planner-executor, router, supervisor, workflow-based, human-in-the-loop, tool-centric, and deterministic versus autonomous choices
- Compare use/non-use, failure modes, complexity, cost, and security; choose the simplest suitable pattern
- **Topics:** `agent-patterns`, `orchestration`, `human-oversight`

**Week 17: MCP and A2A interoperability**
- Current MCP capability discovery, tools/resources/prompts, transport, authorization, identity, errors, versions, and trust
- A2A discovery/cards, delegation, task lifecycle, communication, identity, and peer trust
- **Topics:** `mcp-interoperability`, `a2a`, `protocol-security`

**Week 18: Multi-agent coordination**
- Delegation, shared/isolated state, ownership, concurrency/conflicts, trust, and failure boundaries
- Justify multi-agent systems only where simpler workflows or one agent are insufficient
- **Topics:** `multi-agent-systems`, `delegation`, `coordination`

**Week 19: Durable agent workflows**
- Resumable enterprise workflows, approval, retries, compensation, idempotency, versioning, and side-effect safety
- **Topics:** `durable-workflows`, `checkpointing`, `recovery`

**Week 20: Flex review and agent fleet engineering**
- Lifecycle/scheduling, concurrency/quotas/routing, placement/capacity, cost/governance, versioning, and monitoring
- **Topics:** `agent-fleet`, `capacity-planning`, `operations-review`

### Phase 5: Enterprise Architecture and Production (Weeks 21-24)

**Week 21: Enterprise AI Control Plane theory**
- Identity · policy-as-code · agent registry · governance · evaluation · observability · cost
- Control plane vs runtime; data plane separation; policy enforcement points
- Production isolation: hardened boundaries, ephemeral credentials, kill/revoke, independent evidence, provenance
- **Topics:** `ai-control-plane`, `ai-governance`, `platform-architecture`

**Week 22: Governance, Security and Provenance (control-plane practice)**
- Implement enforceable risk-tiered policy, access control, audit/provenance, revocation, and human oversight in the control plane
- **Topics:** `ai-governance`, `provenance`, `policy-enforcement`

**Week 23: LLMOps, Reliability and FinOps**
- Evaluation, observability, SLOs, incident response, model lifecycle, deployment/rollback, capacity and cost evidence
- **Topics:** `llmops`, `reliability`, `finops`

**Week 24: Enterprise Governed Agent Platform capstone and architecture review**
- Integrate context/RAG/MCP, secure runtime/isolation, delegated identity, coordination/workflows, control plane, governance, and production operations
- Verify implementation, automated/security tests, evaluation evidence, observability, recovery, threat model and readiness limits
- **Topics:** `capstone`, `enterprise-ai-platform`, `production-readiness`

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
| Agentic AI, Interoperability & Orchestration | 16-20 | Patterns · MCP/A2A · durable workflows · fleet |
| **Enterprise Control Plane** | 21-22 | Identity · policy · registry · governance · provenance |
| **Production and Capstone** | 23-24 | SLOs · evaluation · FinOps · final platform |

Full roadmap: [Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md](Learning-Plan/AI_LEARNING_PATHWAY_2026_FINAL.md)
Progress tracker: [Learning-Plan/AI_24W_MASTER_TRACKER.md](Learning-Plan/AI_24W_MASTER_TRACKER.md)
Platform roadmap: [Learning-Plan/ENTERPRISE_GOVERNED_AGENT_PLATFORM_ROADMAP.md](Learning-Plan/ENTERPRISE_GOVERNED_AGENT_PLATFORM_ROADMAP.md)
Progress changes: [Learning-Plan/CURRICULUM_CHANGELOG.md](Learning-Plan/CURRICULUM_CHANGELOG.md)
Technology audit: [Learning-Plan/TECHNOLOGY_STATUS_AUDIT_2026-11-12.md](Learning-Plan/TECHNOLOGY_STATUS_AUDIT_2026-11-12.md)

---

## About This Repository

This repository documents a **24-week architecture-first learning journey**. It starts with Python and LLM integration, then builds context-aware systems, a reliable agent runtime, an agent fleet, and an enterprise control plane. The code and notes are added incrementally as each phase is completed.

### What You Will Learn

- **Foundations** (Weeks 1-5): Python async patterns, multi-provider LLM clients, streaming, MCP, production integrations, and optional certification readiness
- **Context and RAG** (Weeks 6-10): Prompt architecture, structured outputs, memory, context budgets, compaction, retrieval evaluation, method selection, reranking trade-offs, and retrieval capabilities with enforced authorization
- **Agent Runtime** (Weeks 11-15): Execution loops, typed state, tools, checkpointing, resume, approvals, isolation boundaries, security, sandboxing, reliability, and OpenTelemetry
- **Agentic AI, Interoperability and Orchestration** (Weeks 16-20): Pattern selection, MCP/A2A boundaries, multi-agent coordination, durable workflows, and shared-runtime fleet operations
- **Enterprise Architecture and Production** (Weeks 21-24): Control plane, governance/provenance, SLOs, evaluation, incident response, FinOps, and the governed platform capstone

## 24-Week Coverage at a Glance

| Week | Type | What the week covers | Main outcome |
|------|------|----------------------|--------------|
| 1 | Theory | Python async patterns, LLM APIs, streaming, Pydantic, retries | Foundation notes and comparisons |
| 2 | Practice | OpenAI and Anthropic clients, streaming, retry, rate limiting, CLI | Multi-provider CLI |
| 3 | Theory | MCP architecture, JSON-RPC, tools, resources, prompts, transports | MCP architecture and security notes |
| 4 | Practice | API, database, and file/RAG MCP servers; validation, security, testing | Three production-pattern MCP builds |
| 5 | Flex | Review, catch-up, optional MCP readiness checkpoint, capstone direction | MCP foundation review and readiness evidence |
| 6 | Theory | Prompt patterns, structured outputs, memory, token economics, grounding, context lifecycle | Context engineering playbook |
| 7 | Practice | Output validation, memory compaction, few-shot selection, budget enforcement | Typed `ContextEngine` |
| 8 | Theory | Retrieval evaluation, chunking, embeddings, method selection, reranking trade-offs, bounded adaptive retrieval | RAG decision tree and capability contract |
| 9 | Practice | Measured retrieval, bounded self-correction, reranking decision, authorization correctness, work-document evaluation | RAG exposed as a typed MCP capability |
| 10 | Flex | Review, ContextEngine + RAG + MCP integration with identity propagation, ADR-01 draft | Phase 2 integration checkpoint |
| 11 | Theory | Framework-neutral runtime, state/control flow, interfaces, failure/cancellation/timeout, six runtime roles | Architecture, lifecycle, interfaces and failure catalog |
| 12 | Practice | Harness engineering; filesystem, process, network, tools/effects, memory/context, identity/credentials isolation | Runtime harness with invariants and denial tests |
| 13 | Theory + prototype | Delegated authorization, distinct user/agent identity, scope, token exchange, brokerage, expiry/revocation/audit | Scoped identity propagation prototype and tests |
| 14 | Practice | Trajectory/tool/side-effect evaluation, dataset, trace correlation, provider-neutral OTel, runtime hardening | Evaluation cases/results and observability evidence |
| 15 | Flex | Checkpoint/recovery, cancellation/retry, idempotency, upgrades/versioning, release and operations | Integrated Weeks 11-14 runtime with recovery drill and runbook |
| 16 | Theory | ReAct, planner-executor, router, supervisor, workflow, HITL, tool-centric, deterministic/autonomous trade-offs | Pattern comparison and scenario-based architecture choice |
| 17 | Practice | Current MCP and A2A protocols, discovery, identity, transport, errors/versioning/security | Testable interoperability boundary; optional certification is not a substitute |
| 18 | Theory | Multi-agent delegation, ownership, state, concurrency/conflicts, trust/failure; when not to use multi-agent | Coordination design, failure boundaries and justification |
| 19 | Practice | Durable state, checkpoint/approval, compensation, idempotency, resumption, versioning and side effects | Resumable workflow with recovery/side-effect evidence |
| 20 | Flex | Fleet lifecycle/scheduling, concurrency/quotas/routing, placement/capacity, cost/governance/versioning/monitoring | Fleet operations exercise and Phase 4 review |
| 21 | Theory | Control-plane registry/lifecycle/API/configuration, identity/routing/policy and data-plane separation | Capability/interface map and ADR-07 |
| 22 | Practice | Enforceable governance/security/provenance controls integrated with the simplified control plane | Policy, approval, revocation and provenance tests |
| 23 | Theory + operations | Evaluation, observability/SLOs, incident response, model lifecycle/deploy/rollback, capacity/performance/FinOps | Measured operational evidence with method and limitations |
| 24 | Capstone | Cumulative platform integration and final architecture review | Enterprise Governed Agent Platform evidence manifest |

## Repository Structure

```
📁 Week-1-Foundation-Basics/        # Python fundamentals & LLM basics
  ├── project1-llm-client/          # OpenAI & Anthropic streaming clients
  ├── project2-multi-provider-cli/  # Cross-provider CLI tool
  ├── project3-token-tracker/       # Usage monitoring & budgeting
  └── quick-references/             # Cheat sheets & patterns

📁 Week-2-Foundation-Basic-Build/   # Advanced async patterns
  └── Project-1/                    # Enhanced multi-provider implementation

📁 Week-3-Foundation-MCP/           # MCP Protocol deep-dive
  └── Mcp-Project-1/                # MCP server/client implementations

📁 Week-4-Foundation-MCP-Build/     # Production deployment
  ├── templates/                    # Production-ready templates
  └── Document/                     # Deployment guides & checklists

📁 Week-6-ContextEngineering-Basic/ # Context engineering theory + templates
📁 Week-7-ContextEngineering-ContextEngine/  # ContextEngine build
📁 Week-8-ContextEngineering-RAG/   # Retrieval theory, notes, capability contract
📁 Week-9-RAG-Implementation/       # Provider-neutral retrieval baseline

📁 mcp-servers/                     # Real-world MCP integrations
  ├── ado_server.py                 # Azure DevOps MCP server
  └── sonarqube_server.py           # SonarQube MCP server

📁 knowledge-material/              # Learning resources & documentation
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
cd Week-1-Foundation-Basics/project1-llm-client
uv run openAPI_streaming_client.py
```

#### 2. Multi-Provider CLI

```bash
cd Week-1-Foundation-Basics/project2-multi-provider-cli
uv run chat_cli.py --provider openai --prompt "Explain async Python"
```

#### 3. MCP Server

```bash
cd Week-3-Foundation-MCP/Mcp-Project-1
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

### Week 5: Optional MCP Certification Validation
- ✅ Anthropic Introduction to MCP (certificate earned)
- ✅ Anthropic MCP Advanced Topics (certificate earned)

## 📚 Key Projects

### Multi-Provider LLM CLI
A unified CLI interface for multiple LLM providers with streaming support, error handling, and token tracking.

**Features:**
- Provider abstraction (OpenAI, Anthropic, extensible)
- Real-time streaming responses
- Comprehensive error handling
- Token usage monitoring
- Async/await patterns

[View Project →](Week-1-Foundation-Basics/project2-multi-provider-cli/)

### MCP Server Framework
Production-ready Model Context Protocol server implementations with real-world integrations.

**Features:**
- Standard MCP protocol compliance
- Tool registration & execution
- Prompt sampling
- Multiple transport options
- Azure DevOps & SonarQube integrations

[View Project →](Week-3-Foundation-MCP/Mcp-Project-1/)

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

**🚧 Status:** Weeks 1-8 are complete. Week 9 is planned to start November 18, 2026; its implementation baseline is not learner-acceptance evidence. Future phases remain planned.

---

*Happy Learning! 🎉*
