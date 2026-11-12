# Enterprise Governed Agent Platform Roadmap

The 24-week curriculum builds one cumulative architecture. Week-level projects
are evidence and integration points for that platform, not independent
capstones.

| Phase | Weeks | Platform capability added | Cumulative evidence |
|---|---:|---|---|
| Foundations | 1-5 | LLM client and MCP integration foundations | Reusable provider, async, and MCP patterns |
| Context Engineering and RAG | 6-10 | Context lifecycle, governed retrieval, evaluation, typed capabilities | `ContextEngine` plus retrieval capability with trusted identity and provenance |
| Agent Runtime Engineering | 11-15 | Durable execution, state, recovery, approvals, isolation, and observability | One runtime that invokes capabilities under explicit limits and policy |
| Agents and Agent Fleet | 16-20 | Agent configurations, delegated authority, coordination, and registry | Multiple agents using the same governed runtime and bounded handoffs |
| Control Plane and Platform Architecture | 21-24 | Identity, policy, registry, cost, evaluation, audit, governance | Integrated **Enterprise Governed Agent Platform** capstone |

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
2. **Weeks 11-15:** make the runtime the enforcement and recovery boundary for
   tool/capability calls.
3. **Weeks 16-20:** configure agents on the same runtime; limit delegated
   authority and make handoffs auditable.
4. **Weeks 21-24:** centralize shared policy and governance in the control
   plane, then document the end-to-end governed platform and its threat,
   evaluation, and operating model.

The final architecture review and capstone remain Week 24 work. No future-phase
deliverable is marked complete by this roadmap.

