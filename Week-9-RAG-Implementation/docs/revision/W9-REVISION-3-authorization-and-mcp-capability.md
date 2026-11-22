# W9 Revision 3: Authorization & the MCP Capability

Covers: trusted identity, authorize-before-rank, fail closed, adversarial
testing, and exposing retrieval as a typed MCP capability that the capstone
registers.

Code: [authorization.py](../../src/retrieval/authorization.py),
[rag_server.py](../../src/mcp/rag_server.py),
[test_authorization.py](../../tests/test_authorization.py),
[test_mcp_contract.py](../../tests/test_mcp_contract.py) ·
Decisions: [ADR-W9-02](../ADR-W9-02-trusted-identity-boundary.md)

---

## 1. The trust boundary

```
  authenticated host (session / token)          ← TRUSTED
        │ IdentityProvider.from_context(ctx)
        ▼
  CallerIdentity(subject_id, tenant_id)
        │ EntitlementResolver.resolve()  ──fail──► AUTHORIZATION_UNAVAILABLE (fail closed)
        ▼
  Entitlements(subject, tenant, groups)
        │
  model-controlled input: query_text, top_k, source_id, document_type   ← UNTRUSTED
        │
        ▼
  index: is_authorized(chunk) → filters → statistics → rank → (fuse/rerank)
```

**The model controls only the query and the narrowing filters, never who is
asking.** The MCP tool schema has no `identity`, `tenant_id`, or `groups`
argument, and a test asserts that.

---

## 2. Core rules

| Rule | Where in code | Why |
|------|---------------|-----|
| Identity comes from the host context, not from tool args | `IdentityProvider.from_context` | Prevents a **confused deputy**: the model (or injected text) claiming "I'm finance" |
| Entitlements are resolved server-side and the tenant must match | `StaticEntitlementResolver.resolve` | A spoofed tenant gets nothing |
| **Effective scope = entitlements ∩ filters** | `is_authorized(...) and filters...` in each index | Filters can only *narrow*; a filter naming a restricted doc returns 0 |
| Authorize **before** ranking and statistics | `allowed = [...]` in BM25, `continue` in dense | Unauthorized text never enters scoring, IDF, fusion, or the reranker |
| Tenant check first, then public, then principal/group | `is_authorized` | `is_public` means "public **within the tenant**", never cross-tenant |
| Deny by default at ingestion | `DocumentMetadata.__post_init__` | A non-public doc without an ACL can't be indexed |
| Fail closed | `AuthorizationUnavailable` → typed outcome, `results: []` | Unknown means **no access**, never "full access" |

---

## 3. Existence leakage: why "not authorized" looks like "no matches"

When a `student` asks for payroll (q19/q20), the result is **`NO_MATCHES`**,
not "you're not allowed". Telling the caller that restricted results exist
confirms the document exists. That is a leak in itself.

- **To the caller:** return `NO_MATCHES`.
- **Internally (audit/telemetry, Week 13–14):** you *may* record that
  authorized filtering removed candidates, with access-controlled logs.
- Week 8 framed "results exist but not entitled" as a distinct expected
  outcome. Distinct **internally**, indistinguishable **externally**.

---

## 4. Adversarial test catalog (the 🔐 gate)

Pass criterion: **zero unauthorized chunks across every case**. One leak is a
blocking defect, not a quality metric.

| # | Attack | Expected | Covered by |
|---|--------|----------|-----------|
| 1 | Plain request for restricted content | `NO_MATCHES` | q19, q20 |
| 2 | Prompt injection in query ("ignore rules, I'm finance") | 0 restricted chunks | dataset v1.1 + MCP run |
| 3 | Filter targeting a restricted `source_id` | 0 chunks | dataset v1.1 + MCP run |
| 4 | Unknown principal | `AUTHORIZATION_UNAVAILABLE` | dataset v1.1 + MCP run |
| 5 | Cross-tenant identity | 0 chunks from other tenant | dataset v1.1 + MCP run |
| 6 | Missing host identity | `AUTHORIZATION_UNAVAILABLE` | `test_mcp_tool_returns_typed_authorization_failure` |
| 7 | Identity smuggled as a tool argument | not in the tool schema | `test_mcp_tool_schema_does_not_accept_identity` |
| 8 | Reranker sees restricted chunk | never | Friday spy test |

Run it **twice**: at the controller (runner) and **through the MCP path**
(Saturday). Week 10 runs it a third time through the integrated
ContextEngine → MCP chain.

✍️ My adversarial results (date, cases, unauthorized chunks = 0?):

---

## 5. MCP: retrieval as a capability

- `create_server(controller, identity_provider)`: the identity adapter is
  **mandatory**. No default means no accidental anonymous mode.
- Transport: **stdio** for local dev (Saturday, via
  [.vscode/mcp.json](../../../.vscode/mcp.json)). Remote use requires
  **Streamable HTTP** with authorization per the current MCP spec. HTTP+SSE
  and Dynamic Client Registration are deprecated; see
  [TECHNOLOGY_STATUS_AUDIT_2026-11-12.md](../../../Learning-Plan/TECHNOLOGY_STATUS_AUDIT_2026-11-12.md).
- The local dev identity adapter reads `W9_SUBJECT_ID` / `W9_TENANT_ID` from
  the **server's own environment at startup**. That's acceptable for a
  single-user local process, and it is **never** a production pattern.
- Week 9 uses the MCP Python SDK **v2** (`MCPServer`); Week 3/4 projects use
  v1-era APIs. Keep the venvs separate.

---

## 6. The capability card (contract the capstone registers)

| Field | Must state |
|-------|------------|
| Purpose | What questions it answers, over which corpus |
| Input schema | `query_text`, `top_k` (1–100), optional `source_id`, `document_type` |
| Output | chunk text, `source_id`, `source_uri`, `document_version`, `section`, `score`, **`score_kind`** |
| Score semantics | Which scorer, its scale, and what a value does **not** mean |
| Typed outcomes | The table in REVISION-2 §4, data vs incident |
| Authorization model | Whose identity, resolved where, enforced before ranking, fails closed |
| Budgets | attempts / tool calls / latency / tokens / cost defaults |
| Measured latency | **p50 / p95**, n, machine, corpus size, strategy |
| Cost per call | embedding + rerank + tokens, **prices checked on <date>** |
| Known limits | cooperative timeouts, word-count token proxy, in-memory index |

✍️ Link to my card + my p50/p95/cost:

---

## 7. Bridge to Week 10

`ContextEngine.assemble()` → `search_knowledge` over MCP → `ContextEngine.observe()`.
The caller identity must **survive the whole chain**. If the ContextEngine can
call the tool without a trusted identity, authorization is decorative. Re-run
§4 through the integrated path.

---

## 8. Self-test

1. What is a confused deputy, and which design choice here prevents it?
2. Why are filters "not the security control"?
3. Why compute BM25 IDF over authorized chunks only?
4. Why return `NO_MATCHES` instead of "not authorized" to the caller?
5. Entitlement service is down: what does the tool return, and why is that "fail closed"?
6. Why is reading identity from an env var acceptable for local stdio but not for remote HTTP?
7. List the fields of a capability card from memory.
