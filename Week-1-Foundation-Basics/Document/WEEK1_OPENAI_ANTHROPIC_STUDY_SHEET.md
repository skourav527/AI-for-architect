# Week 1 Study Sheet: OpenAI + Anthropic SDK Fundamentals

Purpose: Complete the two Foundation Week 1 theory topics and be fully ready for Week 2 implementation.

Topics covered:
- Wed: OpenAI SDK - chat completions, streaming, function calling
- Thu: Anthropic SDK - messages API, streaming, tool use

---

## 1) Setup (10-15 min once)

1. Create a .env file at repo root with:
   - OPENAI_API_KEY=...
   - ANTHROPIC_API_KEY=...
2. Install required packages:

```bash
pip install openai anthropic python-dotenv httpx pydantic tenacity rich click
```

3. Reuse existing project files as references:
   - Foundation-Week-1/project1-llm-client/stage1_sync_client.py
   - Foundation-Week-1/project1-llm-client/stage2_async_client.py
   - Foundation-Week-1/project2-multi-provider-cli/chat_cli.py

---

## 2) Wednesday Plan (OpenAI, 60 min)

### 2.1 Read (25 min)
- OpenAI overview:
  - https://developers.openai.com/api/docs/overview
- Streaming responses:
  - https://developers.openai.com/api/docs/guides/streaming-responses
- Function calling:
  - https://developers.openai.com/api/docs/guides/function-calling
- Cookbook:
  - https://cookbook.openai.com

### 2.2 Understand (10 min)
OpenAI function-calling loop:
1. Send user input + tool schema(s)
2. Receive function call(s) from model
3. Execute function(s) in your app
4. Send function_call_output back
5. Receive final model response

### 2.3 Run (25 min)

#### A) OpenAI streaming quick test
```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "Explain async/await in 5 bullets."}],
    stream=True,
)

for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.completed":
        print()
```

#### B) OpenAI function calling quick test
```python
import json
from openai import OpenAI

client = OpenAI()

def get_weather(location: str):
    return {"location": location, "temp_c": 30, "condition": "Cloudy"}

tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current weather for a location.",
    "strict": True,
    "parameters": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"],
        "additionalProperties": False
    }
}]

conversation = [{"role": "user", "content": "Do I need umbrella in Bangalore?"}]

first = client.responses.create(model="gpt-4.1", input=conversation, tools=tools)
conversation += first.output

for item in first.output:
    if item.type == "function_call" and item.name == "get_weather":
        args = json.loads(item.arguments)
        result = get_weather(args["location"])
        conversation.append({
            "type": "function_call_output",
            "call_id": item.call_id,
            "output": json.dumps(result)
        })

final = client.responses.create(model="gpt-4.1", input=conversation, tools=tools)
print(final.output_text)
```

---

## 3) Thursday Plan (Anthropic, 60 min)

### 3.1 Read (25 min)
- Messages API examples:
  - https://platform.claude.com/docs/en/api/messages-examples
- Streaming messages:
  - https://platform.claude.com/docs/en/api/messages-streaming
- Tool use overview:
  - https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
- Python SDK docs entry:
  - https://platform.claude.com/docs/en/api/client-sdks

### 3.2 Understand (10 min)
Anthropic tool-use loop:
1. Send messages + tools
2. Model responds with stop_reason="tool_use" and tool_use block(s)
3. Execute tool(s) in your app
4. Send tool_result block(s)
5. Receive final assistant answer

### 3.3 Run (25 min)

#### A) Anthropic streaming quick test
```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=512,
    messages=[{"role": "user", "content": "Explain retries and exponential backoff simply."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()
```

#### B) Anthropic tool-use quick test
```python
import json
import anthropic

client = anthropic.Anthropic()

def get_weather(location: str):
    return {"location": location, "temp_c": 28, "condition": "Sunny"}

tools = [{
    "name": "get_weather",
    "description": "Get weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"]
    }
}]

messages = [{"role": "user", "content": "What is weather in Hyderabad right now?"}]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=512,
    tools=tools,
    messages=messages,
)

if response.stop_reason == "tool_use":
    tool_results = []
    for block in response.content:
        if block.type == "tool_use" and block.name == "get_weather":
            result = get_weather(block.input["location"])
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result)
            })

    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": tool_results})

    final = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        tools=tools,
        messages=messages,
    )
    print(final.content[0].text)
```

---

## 4) Key concepts to lock in

1. Both providers are event-driven for streaming.
2. Tool/function calling is always a loop, not one request.
3. Tool arguments must be validated before executing real code.
4. Keep tool schemas minimal and explicit for better model accuracy.
5. Log model, latency, stop_reason, and token usage each call.
6. Add retry with backoff for transient API failures.

---

## 5) Best practices (implementation week ready)

1. Use provider abstraction (single interface for OpenAI and Anthropic).
2. Add timeout + retries + fallback messages.
3. Parse and handle streaming events safely (ignore unknown events gracefully).
4. Keep prompts/tool descriptions specific and deterministic.
5. Use Pydantic to validate request and response structures.
6. Start with one tool, then scale to multiple tools.

---

## 6) Week 2 readiness checklist

- [ ] OpenAI streaming script works end-to-end
- [ ] OpenAI function calling roundtrip works
- [ ] Anthropic streaming script works end-to-end
- [ ] Anthropic tool-use roundtrip works
- [ ] You can explain each request/response field without notes
- [ ] You can implement both providers behind one CLI command

If all boxes are checked, you are implementation-ready for Week 2.
