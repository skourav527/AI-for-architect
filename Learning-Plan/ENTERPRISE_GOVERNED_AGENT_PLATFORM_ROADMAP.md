# Enterprise Governed Agent Platform Roadmap

The 24-week curriculum builds one cumulative architecture. Week-level projects
are evidence and integration points for that platform, not independent
capstones.

| Phase | Weeks | Platform capability added | Cumulative evidence |
|---|---:|---|---|
| Foundations | 1-5 | LLM client and MCP integration foundations | Reusable provider, async, and MCP patterns |
| Context Engineering and RAG | 6-10 | Context lifecycle, governed retrieval, evaluation, typed capabilities | `ContextEngine` plus retrieval capability with trusted identity and provenance |
| Agent Runtime Engineering | 11-15 | Framework-neutral runtime, harness isolation, delegated identity, evaluation, recovery, and operations | One secure, observable, recoverable runtime |
| Agentic AI, Interoperability and Orchestration | 16-20 | Patterns, MCP/A2A, multi-agent coordination, durable workflows, and fleet operations | Agents and workflows operating under shared runtime, identity, policy, and isolation |
| Enterprise Architecture and Production | 21-24 | Control plane, governance/provenance, LLMOps, reliability, FinOps, and architecture review | Integrated **Enterprise Governed Agent Platform** capstone |

## Architecture boundaries

- **Runtime / data plane:** executes agent work and enforces per-run budgets,
  permissions, recovery, and capability boundaries.
- **Control plane:** owns shared identity, policy, registry, governance,
  evaluation, and cost controls; it configures and observes runtimes rather than
  replacing them.
- **Retrieval:** returns only content authorized for trusted caller identity.
  Retrieval policy and entitlements are not caller-controlled search filters.
- **Evidence:** each design choice is justified by a versioned evaluation or a
  documented constraint. Synthetic smoke data is not production evidence.

## Integration gates

1. **Week 10:** combine Week 7 context primitives and Week 9 retrieval while
   preserving identity and typed failure outcomes.
2. **Weeks 11-15:** define framework-neutral runtime roles and interfaces;
   build one harness/runtime with filesystem, process, network, tools/effects,
   memory/context, and identity/credential isolation; add delegated identity,
   evaluation, telemetry, recovery, and operational readiness.
3. **Weeks 16-20:** compare architecture patterns; implement/test MCP and A2A
   boundaries; add coordination and durable workflows; operate a fleet on the
   same runtime with bounded delegation and auditable handoffs.
4. **Weeks 21-22:** centralize registry, lifecycle, identity, policy,
   governance, provenance, and oversight in the control plane. Keep it
   separate from runtime execution.
5. **Week 23:** produce measured evaluation, SLO, reliability, capacity,
   performance, and cost evidence with environment and limitations.
6. **Week 24:** integrate and review the **Enterprise Governed Agent Platform**
   with implementation, automated/security/isolation tests, datasets/results,
   observability, deployment/recovery instructions, threat model, and
   production-readiness assessment.

The Agent Isolation Boundary is a cumulative invariant, not a Week 12-only
topic. A design, synthetic smoke run, or unverified prototype is not described
as production-ready.

The final architecture review and capstone remain Week 24 work. No future-phase
deliverable is marked complete by this roadmap.

