# Week 5 — Consolidated Week 1-4 Quick Revision Cheatsheet

One page to re-read. If you can explain every line here without notes, Phase 1 is done.

---

## 1. Python / HTTP Foundations (Week 1)

| Concept | The point |
|---------|-----------|
| `httpx.Client` vs `AsyncClient` | Reuse one client per process — connection pooling. Never create per request. |
| `async with` | Guarantees the transport pool is closed; skipping it leaks sockets. |
| `asyncio.gather` | Fan-out concurrent calls; `return_exceptions=True` so one failure doesn't kill the batch. |
| `asyncio.Semaphore` | Your rate-limit throttle. Concurrency control belongs to the caller, not the client. |
| Blocking call in async fn | Poisons the event loop. Push to `asyncio.to_thread`. |
| Context managers | `__enter__`/`__exit__` — deterministic cleanup, no reliance on GC. |
| Decorators | Wrap behaviour (retry, timing, auth) without touching the function body. |

### Tenacity retry policy
- **Retry:** 429, 5xx, timeouts, connection errors.
- **Never retry:** 400, 401, 403, 404 — the request is wrong, repeating won't fix it.
- Always `wait_exponential` + `jitter` + a hard `stop_after_attempt`.
- Honour `Retry-After` when the server sends it.

### Pydantic at the boundary
- Parse untrusted JSON into models the moment it enters your process.
- `Field(...)` for required + description; descriptions become MCP tool schema docs for free.
- Validation errors are a *contract* failure — surface them, don't swallow them.

---

## 2. Provider Abstraction (Week 2)

- One internal `ChatRequest` / `ChatResponse` shape; adapters translate per provider.
- Differences that bite:
  - **OpenAI:** `messages[]` includes system role; usage in `response.usage`.
  - **Anthropic:** `system` is a *top-level* parameter, not a message; `max_tokens` is required.
- Streaming deltas differ: OpenAI `choices[].delta.content`, Anthropic `content_block_delta.delta.text`.
- Normalise `finish_reason` / `stop_reason` into your own enum.
- Token accounting belongs in the adapter, not the caller.

---

## 3. MCP Fundamentals (Week 3)

| Primitive | Controlled by | Use for |
|-----------|---------------|---------|
| **Tool** | The model (it decides to call) | Actions with side effects, computation |
| **Resource** | The application/user | Read-only context the client attaches |
| **Prompt** | The user (explicit invocation) | Reusable, parameterised workflows |

### Transports
| Transport | When |
|-----------|------|
| **stdio** | Local, single-client, subprocess-owned. Simplest. Never log to stdout. |
| **Streamable HTTP (stateful)** | Remote, sessions, server→client notifications, sampling |
| **Stateless HTTP** | Serverless / horizontally scaled; no session affinity, no server-initiated messages |

### Advanced primitives
- **Sampling** — server asks the *client* to run an LLM completion. Server stays model-agnostic and pays no API cost; client keeps control and consent.
- **Roots** — client tells the server which filesystem/URI boundaries it may operate in. A capability negotiation, not a security boundary on its own.
- **Log notifications / progress** — server→client async messages; require a stateful transport.
- **Lifespan** — set up pools/connections once at server start, tear down cleanly.

---

## 4. Production MCP Patterns (Week 4)

### API connector
- Inject auth via headers from env/secret store — never a literal in code.
- Timeouts on every call. Retries with backoff. Circuit-break on repeated failure.
- Paginate and cap result size — a tool returning 50k tokens destroys the context window.
- Return structured errors the model can reason about, not raw stack traces.

### Database connector
- **Parameterised queries only.** String-interpolated SQL is the #1 finding.
- Read-only credentials by default; separate, explicitly-named tools for writes.
- Enforce `LIMIT`; never `SELECT *` into a model context.
- Expose schema as a *resource* so the model can plan queries.

### File / RAG connector
- Resolve and validate paths against the allowed root — block `..` traversal and symlinks.
- Allow-list extensions; cap file size before reading.
- Chunk with overlap; return citations (path + offset) with every chunk.

### Cross-cutting
- Secrets from env/vault; never logged.
- Structured logging to **stderr** on stdio transport.
- Tests: mock the upstream, assert error paths, assert output truncation.

---

## 5. Weak Spots (fill this in yourself during Day 2)

> After each recall block, list what you got wrong here. This becomes your Week 6 warm-up.

- [ ] …
- [ ] …
- [ ] …
