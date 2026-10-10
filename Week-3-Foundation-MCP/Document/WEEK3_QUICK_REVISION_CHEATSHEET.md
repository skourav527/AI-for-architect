# Week 3 Quick Revision Cheat Sheet

Scope: MCP architecture + JSON-RPC flow + Tools/Resources/Prompts + advanced features + transports + production thinking
Use this as a fast 5-10 minute review before implementation.

---

## 1) What Week 3 Was About

Week 3 was about understanding MCP as a protocol and server design model, not just using ready-made examples:
- architecture and roles
- JSON-RPC message flow
- Tools vs Resources vs Prompts
- advanced features (sampling, notifications, roots)
- transport choices (stdio vs HTTP)
- production-readiness and security basics

Main learning goal:
- choose the right MCP primitive for the right job, and explain why

---

## 2) Core MCP Mental Model

Think in three layers:
1. Protocol layer: JSON-RPC request/response/error
2. Capability layer: Tools, Resources, Prompts
3. Transport layer: stdio or HTTP

Memory hook:
- Protocol = message grammar
- Capability = what server can do
- Transport = how messages travel

---

## 3) JSON-RPC Essentials (MCP Backbone)

### Request shape
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_docs",
    "arguments": {"query": "retry strategy"}
  }
}
```

### Success response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{"type": "text", "text": "Found 3 matches"}]
  }
}
```

### Error response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params"
  }
}
```

What to remember:
- `id` links request to response
- success has `result`, failures have `error`
- method names define operation type

---

## 4) Tools vs Resources vs Prompts

### Tool
Use when the client asks server to perform an action/operation.
Examples:
- run query
- trigger analysis
- call external API

### Resource
Use when exposing retrievable data/context.
Examples:
- config file contents
- documentation snippets
- status/state data

### Prompt
Use when providing reusable prompt templates/instructions.
Examples:
- standardized analysis prompt
- guided troubleshooting prompt

### Decision shortcut
- Need execution side effects? -> Tool
- Need fetch/read context? -> Resource
- Need reusable instruction scaffold? -> Prompt

---

## 5) Tool Design Rules (High Value)

- keep input schema explicit and strict
- validate arguments before work starts
- return structured, predictable output
- separate user errors from server/internal errors
- keep error messages actionable

Common mistakes:
- weak validation
- ambiguous output format
- mixing logs with returned content
- retrying non-retryable failures blindly

---

## 6) Resources and Prompts Practical Notes

Resources:
- should be discoverable and stable
- content should be deterministic when possible
- avoid huge payloads without paging/chunking strategy

Prompts:
- keep templates versioned and named clearly
- include placeholders with clear meaning
- avoid hidden assumptions in prompt text

---

## 7) Advanced MCP Features

### Sampling
- **What is it?** Server asks Client to run an LLM call mid-tool execution (`Server -> Client -> LLM -> Server`).
- **Why it matters:**
  - **No API Keys in Server:** Server reuses Client's LLM connection/credentials safely.
  - **User & Client Control:** Client can inspect, audit, or request user consent before LLM runs.
  - **Model Flexible:** Server doesn't hardcode models; Client selects model and settings.
  - **Smart Tools:** Server tools can use LLM reasoning internally without embedding heavy AI libraries.

### Notifications
- server/client one-way event updates (no direct response expected)
- useful for progress, status changes, or state events

### Roots
- define trusted workspace/file boundaries
- reduce accidental overreach and improve safety/control

Memory hook:
- sampling = generate
- notifications = inform
- roots = constrain scope

---

## 8) Transport Choice: stdio vs HTTP

### stdio (usually local)
- simple local integration
- low setup overhead
- good for editor-integrated tooling

### HTTP (often distributed/remote)
- easier networked deployment
- better for service-style scaling and infra controls
- requires stronger auth, observability, and ops discipline

Decision pattern:
- local/dev/editor use -> start with stdio
- shared/team/remote service -> prefer HTTP

---

## 9) Production Readiness Checklist (MCP Servers)

- input validation on every tool/resource entry point
- authentication/authorization model defined
- secrets are not hardcoded
- structured logging with correlation IDs
- clear error taxonomy (client vs server errors)
- timeout + retry policy for outbound dependencies
- request size and rate controls
- transport security assumptions documented

---

## 10) Quick Gap Review for Your Existing MCP Servers

When reviewing ADO/SonarQube servers, check:
- are tool schemas strict enough?
- are errors mapped to consistent JSON-RPC responses?
- is logging useful for debugging failures?
- are permissions and secrets handling explicit?
- are transport and deployment assumptions documented?

---

## 11) What You Should Be Able To Explain

- MCP architecture and role boundaries
- full JSON-RPC success and failure flow
- when to choose Tool vs Resource vs Prompt
- what sampling/notifications/roots add in practice
- why stdio and HTTP choices change production design

---

## 12) Two-Minute Memory Check

If you forget everything, remember this:
- MCP = Protocol + Capabilities + Transport
- JSON-RPC = `id`-linked request/response/error
- Tool = do, Resource = read, Prompt = guide
- Advanced set = sampling, notifications, roots
- Transport = stdio for local simplicity, HTTP for remote scale

That is the Week 3 core model.
