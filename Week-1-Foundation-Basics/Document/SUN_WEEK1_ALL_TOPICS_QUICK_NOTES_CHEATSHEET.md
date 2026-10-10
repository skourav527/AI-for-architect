# Sunday Quick Notes + Cheat Sheet (1-2h)

Purpose: Review all Week 1 topics in one place and prepare for Week 2 implementation.

Week status snapshot:
- Mon: async/await fundamentals + asyncio patterns - Done
- Tue: decorators, context managers, generators - Done
- Wed: OpenAI SDK (chat, streaming, function calling) - Done
- Thu: Anthropic SDK (messages, streaming, tool use) - In progress / review
- Sat: Pydantic v2 + httpx + tenacity retry patterns - Planned

---

## 1) Sunday 1-2 Hour Review Plan

### 0-15 min: Recall without notes

Write from memory:
1. `async` + `await` + `asyncio.gather` usage
2. one decorator use case
3. one context manager use case
4. OpenAI function-calling loop
5. Anthropic tool-use loop
6. Pydantic + httpx + tenacity integration idea

### 15-45 min: Topic-by-topic quick refresh

Use sections 2-7 in this file. Focus only on gaps, not full reread.

### 45-75 min: Mini whiteboard drill

On paper/text note, sketch:
1. provider-agnostic request flow
2. error and retry handling path
3. where model validation happens
4. where token usage is logged

### 75-120 min (optional): Light coding recap

1. Run one OpenAI streaming example.
2. Run one Anthropic tool-use example.
3. Implement one retry wrapper with `tenacity`.

---

## 2) Mon Notes: async/await + asyncio patterns

Core idea:
- Async helps when waiting on I/O (API calls, network, file, DB), not CPU-heavy loops.

Must-know patterns:

```python
import asyncio


async def task(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"


async def main() -> None:
    results = await asyncio.gather(
        task("a", 0.5),
        task("b", 0.2),
    )
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
```

Rules:
1. Use `async def` when function contains `await`.
2. Use `await` for coroutines.
3. Use `asyncio.gather` for parallel I/O calls.
4. Avoid blocking calls inside async functions.

---

## 3) Tue Notes: decorators + context managers + generators

### Decorators

Purpose:
- Add behavior (retry/log/timing/auth) without changing core business logic.

```python
from functools import wraps
import time


def timing(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper
```

### Context Managers

Purpose:
- Guarantee setup/cleanup (files, clients, connections) even on errors.

Use:
- `with open(...) as f:`
- `with httpx.Client(...) as client:`

### Generators

Purpose:
- Yield items lazily to save memory.

```python
def even_numbers(limit: int):
    for n in range(limit):
        if n % 2 == 0:
            yield n
```

---

## 4) Wed Notes: OpenAI SDK quick sheet

Main building blocks:
1. Normal call: `client.responses.create(...)`
2. Streaming: iterate events, collect `response.output_text.delta`
3. Function calling: loop until model returns final natural language answer

OpenAI function-calling loop:
1. Send input + tool schema
2. Receive `function_call`
3. Execute local function
4. Send `function_call_output`
5. Request final response

Safety:
1. Validate tool args before function execution.
2. Keep schema minimal and strict.
3. Log model, latency, tokens.

---

## 5) Thu Notes: Anthropic SDK quick sheet

Main building blocks:
1. Messages API: `client.messages.create(...)`
2. Streaming: `client.messages.stream(...)` and iterate `text_stream`
3. Tool use: watch `stop_reason == "tool_use"`

Anthropic tool-use loop:
1. Send messages + tools
2. Receive tool request block(s)
3. Execute local tool
4. Send tool result block(s)
5. Request final response

Safety:
1. Validate tool input before execution.
2. Return explicit tool errors when needed.
3. Track stop reason, usage, latency.

---

## 6) Sat Notes: Pydantic v2 + httpx + tenacity

### Pydantic v2

Use for:
- request/response validation
- guarding against malformed provider payloads

Key APIs:
- `model_validate(...)`
- `model_dump()`
- `Field(...)` constraints

### httpx

Use for:
- sync + async HTTP calls
- timeout + status handling

Key exceptions:
- `httpx.TimeoutException`
- `httpx.HTTPStatusError`
- `httpx.ConnectError`

### tenacity

Use for:
- controlled retries on transient failures only

Common config:
- `stop_after_attempt(3)`
- `wait_exponential(multiplier=1, min=1, max=8)`
- retry only network/transient exceptions

Do not retry:
- validation errors
- auth errors
- bad request/schema errors

---

## 7) One Unified Implementation Pattern (Week 2 Ready)

1. Build provider request payload.
2. Call provider API with timeout.
3. If transient error, retry with backoff.
4. Parse/validate response via Pydantic.
5. Handle streaming/tool events.
6. Log model, latency, token usage.
7. Return normalized response to CLI/user.

---

## 8) Final Sunday Checklist

- [ ] I can explain async concurrency with one working example.
- [ ] I can write one decorator and one context manager from memory.
- [ ] I can explain OpenAI function-calling loop clearly.
- [ ] I can explain Anthropic tool-use loop clearly.
- [ ] I can implement retry logic with safe exception filters.
- [ ] I can validate provider response with Pydantic before use.
- [ ] I can describe one provider-agnostic architecture for Week 2.

If all checked, Week 1 revision is complete.
