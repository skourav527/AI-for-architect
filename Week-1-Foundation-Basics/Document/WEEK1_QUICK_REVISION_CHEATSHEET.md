# Week 1 Quick Revision Cheat Sheet

Scope: OpenAI (chat, streaming, function calling) + Anthropic (messages, streaming, tool use)
Use this 5-10 minutes before coding.

---

## 1) Install + Run Commands

```bash
pip install openai anthropic python-dotenv httpx pydantic tenacity rich click
```

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_key"
$env:ANTHROPIC_API_KEY="your_key"
```

```bash
# Run your existing practice files
python Foundation-Week-1/project1-llm-client/stage1_sync_client.py
python Foundation-Week-1/project1-llm-client/stage2_async_client.py
python Foundation-Week-1/project2-multi-provider-cli/chat_cli.py --provider openai "hello"
python Foundation-Week-1/project2-multi-provider-cli/chat_cli.py --provider anthropic "hello"
```

---

## 2) OpenAI: Minimal API Patterns

### A) Basic response
```python
from openai import OpenAI
client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "Explain asyncio in 3 bullets"}],
)
print(resp.output_text)
```

### B) Streaming
```python
stream = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "Say hello slowly"}],
    stream=True,
)
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
```

### C) Function calling (schema)
```python
tools = [{
  "type": "function",
  "name": "get_weather",
  "description": "Get weather by location",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {"location": {"type": "string"}},
    "required": ["location"],
    "additionalProperties": False
  }
}]
```

### D) Function-calling loop
1. Send input + tools
2. Read function_call from output
3. Execute local function
4. Append function_call_output
5. Request final answer

---

## 3) Anthropic: Minimal API Patterns

### A) Basic message
```python
import anthropic
client = anthropic.Anthropic()

msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": "Explain retries in plain words"}],
)
print(msg.content[0].text)
```

### B) Streaming
```python
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": "Give 5 async tips"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### C) Tool schema
```python
tools = [{
  "name": "get_weather",
  "description": "Get weather by location",
  "input_schema": {
    "type": "object",
    "properties": {"location": {"type": "string"}},
    "required": ["location"]
  }
}]
```

### D) Tool-use loop
1. Send messages + tools
2. If stop_reason == "tool_use", read tool_use blocks
3. Execute local tool
4. Send tool_result block(s)
5. Request final answer

---

## 4) Event Names to Remember

OpenAI streaming:
- response.created
- response.output_text.delta
- response.completed
- error

Anthropic streaming:
- message_start
- content_block_start
- content_block_delta
- content_block_stop
- message_delta
- message_stop
- ping
- error

---

## 5) Pre-Coding Checklist (2 min)

- [ ] API keys loaded
- [ ] Basic non-stream request works
- [ ] Streaming request works
- [ ] One tool/function schema validated
- [ ] One full tool/function roundtrip works
- [ ] Logs include model, latency, tokens, stop_reason

---

## 6) Quick Reference Links

OpenAI:
- https://developers.openai.com/api/docs/overview
- https://developers.openai.com/api/docs/guides/streaming-responses
- https://developers.openai.com/api/docs/guides/function-calling
- https://cookbook.openai.com

Anthropic:
- https://platform.claude.com/docs/en/api/messages-examples
- https://platform.claude.com/docs/en/api/messages-streaming
- https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- https://platform.claude.com/docs/en/api/client-sdks
