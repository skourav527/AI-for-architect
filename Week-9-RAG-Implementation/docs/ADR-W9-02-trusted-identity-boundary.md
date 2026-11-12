# ADR-W9-02: Trusted Identity at the Retrieval Boundary

- **Status:** Proposed for learner review
- **Scope:** Week 9 learning implementation only

## Context

Retrieval filters are model-controlled input and cannot safely establish
entitlement. A caller-supplied tenant or principal field would create a
confused-deputy path if accepted as authorization evidence.

## Decision

Resolve caller identity from an injected authenticated host-context adapter.
Resolve entitlements server-side and enforce tenant, principal, and group access
before ranking. User-supplied metadata filters may narrow the authorized set
only. If identity or entitlement resolution is unavailable, return a typed
fail-closed outcome.

## Alternatives considered

- Accept `tenant_id`, groups, or principal IDs as tool arguments: rejected
  because the model can influence those fields.
- Apply authorization after retrieval: rejected because unauthorized content
  may already have crossed the capability boundary.
- Infer identity from a query or document: rejected because neither is trusted
  authentication evidence.

## Consequences

- Tests can verify that the MCP schema omits identity fields and that missing
  identity fails closed.
- A production deployment still needs an authenticated host adapter and,
  for HTTP transport, a conforming authorization integration; this repository
  does not provide either.
- This is a proposed Week 9 implementation decision, not a claim that the
  learner completed the Week 8 security acceptance.

