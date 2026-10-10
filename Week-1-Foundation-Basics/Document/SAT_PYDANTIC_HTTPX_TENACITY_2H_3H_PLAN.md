# Saturday Learning Plan (2-3h)

Topic: Pydantic v2 models + httpx + tenacity retry patterns  
Goal: Build confidence to use typed request/response models, robust HTTP calls, and safe retry logic in your Week 2 implementation.

---

## 0) Outcome First

By the end of this session, you should be able to:

1. Create and validate nested Pydantic v2 models using `BaseModel`, `Field`, and `model_validate`.
2. Make sync and async API calls using `httpx.Client` and `httpx.AsyncClient` with timeout handling.
3. Add retries with `tenacity` using exponential backoff and retry filters.
4. Combine all three in one mini workflow: fetch -> validate -> retry on transient failures.

---

## 1) Timeboxed Plan

### Block A (35 min): Pydantic v2 essentials

Focus:
- `BaseModel`, `Field`, `ValidationError`
- `model_validate`, `model_dump`
- Optional fields, list fields, nested models

Practice:
1. Define a `ChatRequest` model with:
   - `provider: str`
   - `model: str`
   - `prompt: str`
   - `max_tokens: int = Field(ge=1, le=4096)`
2. Define `Usage` and `ChatResponse` nested model.
3. Validate one good payload and one bad payload.

Checkpoint:
- You can explain why validation should happen before calling provider APIs.

### Block B (40 min): httpx patterns (sync + async)

Focus:
- `httpx.Client(timeout=...)`
- `httpx.AsyncClient(timeout=...)`
- `response.raise_for_status()`
- handling `httpx.TimeoutException` and `httpx.HTTPStatusError`

Practice:
1. Sync GET to a public endpoint and parse JSON.
2. Async version of same call using `asyncio.run(...)`.
3. Add structured logging for status code + latency.

Checkpoint:
- You can describe when to use sync vs async client.

### Block C (35 min): tenacity retry strategy

Focus:
- `@retry(...)`
- `stop_after_attempt(3)`
- `wait_exponential(multiplier=1, min=1, max=8)`
- `retry_if_exception_type(...)`

Practice:
1. Wrap flaky function with retry.
2. Retry only on transient errors (timeout, connection).
3. Keep non-retriable errors (schema/validation mistakes) as immediate failures.

Checkpoint:
- You can justify retry policy in one sentence: safe retries only for transient failures.

### Block D (20-30 min): Mini integration drill

Build one function:

1. Makes HTTP call with `httpx`.
2. Retries with `tenacity` on timeout/5xx.
3. Validates final response using Pydantic v2.
4. Prints clean success summary.

Stretch (if time left):
- Add fallback message when all retries fail.

---

## 2) Quick Reference Snippets

### Pydantic v2 sample

```python
from pydantic import BaseModel, Field, ValidationError


class Usage(BaseModel):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)


class ChatResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: Usage


payload = {
    "provider": "openai",
    "model": "gpt-4.1",
    "content": "hello",
    "usage": {"prompt_tokens": 10, "completion_tokens": 20},
}

try:
    resp = ChatResponse.model_validate(payload)
    print(resp.model_dump())
except ValidationError as exc:
    print(exc)
```

### httpx + tenacity sample

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
)
def fetch_json(url: str) -> dict:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
```

---

## 3) Fast Self-Test (5 min)

- [ ] I can create one nested Pydantic v2 model without looking up docs.
- [ ] I can catch and log `httpx` timeout/status errors correctly.
- [ ] I can write retry with stop + exponential wait + exception filter.
- [ ] I can explain why we should not retry validation errors.

If all are checked, Saturday target is complete.
