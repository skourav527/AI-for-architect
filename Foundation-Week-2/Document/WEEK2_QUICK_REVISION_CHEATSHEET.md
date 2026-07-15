# Week 2 Quick Revision Cheat Sheet

Scope: OpenAI async + streaming + retry/rate limit + Anthropic mirror + multi-provider CLI
Use this as a fast 5-10 minute review before coding.

---

## 1) What Week 2 Was About

Week 2 was about turning basic LLM calls into reusable client patterns:
- async request flow
- streaming output
- retry and rate limiting
- mirroring one provider into another
- switching providers from one CLI

Main learning goal:
- same shape, different SDK details

---

## 2) Core Workflow You Reused

1. Load `.env`
2. Read API key
3. Validate input with Pydantic
4. Call provider client
5. Parse response safely
6. Handle errors clearly
7. Stream chunks when needed

---

## 3) OpenAI Async Pattern

### Non-stream
```python
response = await client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=100,
)
text = response.choices[0].message.content or ""
```

### Stream
```python
stream = await client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": prompt}],
    max_tokens=100,
    stream=True,
)

async for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### OpenAI response shape
- full text: `response.choices[0].message.content`
- stream text: `chunk.choices[0].delta.content`

---

## 4) Anthropic Async Pattern

### Non-stream
```python
response = await client.messages.create(
    model=model,
    max_tokens=100,
    messages=[{"role": "user", "content": prompt}],
)
text = "".join(
    block.text for block in response.content
    if getattr(block, "type", "") == "text"
)
```

### Stream
```python
stream = await client.messages.create(
    model=model,
    max_tokens=100,
    messages=[{"role": "user", "content": prompt}],
    stream=True,
)

async for event in stream:
    if event.type == "content_block_delta" and getattr(event.delta, "type", "") == "text_delta":
        print(event.delta.text, end="", flush=True)
```

### Anthropic response shape
- full text comes from text blocks in `response.content`
- stream text comes from `event.delta.text`

---

## 5) OpenAI vs Anthropic

### Same idea
- both use a client object
- both take a `messages` style prompt
- both support async
- both support streaming
- both need API key and error handling

### Different details
- OpenAI returns text in `choices[0].message.content`
- Anthropic returns text blocks in `response.content`
- OpenAI stream reads `delta.content`
- Anthropic stream reads `event.delta.text`
- Anthropic uses `max_tokens` as a required request field

---

## 6) Pydantic Reminder

Use Pydantic to catch bad input before the API call.

```python
class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    model: str = Field(default="gpt-4o-mini")
    max_tokens: int = Field(default=100, ge=1, le=4096)
```

Why it helped:
- empty prompt fails early
- bad token values fail early
- cleaner error messages

---

## 7) Retry + Rate Limit Basics

### Retry idea
- retry only transient failures
- use visible logging
- stop after a small number of tries

### Rate limit idea
- wait before sending the next request
- local test value can be tighter than real production value

### Memory hook
- retry = try again later
- rate limit = do not send too fast

---

## 8) Streaming Output Tips

Use this pattern to print chunks nicely:

```python
async for chunk in client.chat_stream(prompt):
    print(chunk, end="", flush=True)
    await asyncio.sleep(0.03)
```

Remember:
- `end=""` keeps output on one line
- `flush=True` shows text immediately
- `asyncio.sleep(...)` is only for demo smoothness

---

## 9) Multi-Provider CLI

Minimum features you built:
- provider switch: OpenAI or Anthropic
- prompt input
- `--stream` flag
- clear terminal formatting
- simulate mode for local testing

Example commands:

```bash
python multi_provider_cli.py --provider openai --prompt "What is Python?" --simulate
python multi_provider_cli.py --provider anthropic --prompt "What is Python?" --simulate
python multi_provider_cli.py --provider openai --prompt "What is Python?" --stream --simulate
python multi_provider_cli.py --provider anthropic --prompt "What is Python?" --stream --simulate
```

---

## 10) Quick File Map

- `OpenAPI_Sync_Client.py` -> minimal OpenAI async example
- `Anthropic_Async_Client.py` -> minimal Anthropic async example
- `multi_provider_cli.py` -> provider switch CLI
- `OpenAPI_Streaming_Client_Block3.py` -> retry + rate limiting example
- `README.md` -> project notes and commands

---

## 11) Common Edge Cases

- missing API key
- empty prompt
- bad model name
- stream output mixed with logs
- retrying a non-transient error
- Anthropic billing / access issues when not using simulate mode
- streaming output looking slow because of artificial sleep

---

## 12) What You Should Be Able To Explain

- why async helps with API calls
- how streaming differs from one-shot output
- how OpenAI and Anthropic response shapes differ
- why retry and rate limiting matter
- how one CLI can switch providers with a shared interface

---

## 13) Two-Minute Memory Check

If you forget the provider differences, remember this:
- OpenAI: `choices -> message -> content`
- Anthropic: `content blocks -> text`
- OpenAI stream: `delta.content`
- Anthropic stream: `event.delta.text`

That is the main comparison from Week 2.
