# import os
# from pathlib import Path

# import httpx
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load .env from Foundation-Week-1
# env_path = Path(__file__).resolve().parents[1] / ".env"
# load_dotenv(dotenv_path=env_path)

# api_key = os.getenv("OPENAI_API_KEY")
# model = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")

# if not api_key:
#     raise RuntimeError("OPENAI_API_KEY not found in .env")

# # Corporate proxy: SSL verification disabled, redirects enabled
# http_client = httpx.Client(verify=False, follow_redirects=True, timeout=30.0)
# client = OpenAI(api_key=api_key, http_client=http_client)

# # Streaming chat completion
# stream = client.chat.completions.create(
#     model="gpt-4.1",
#     messages=[{"role": "user", "content": "Explain streaming responses in one paragraph."}],
#     stream=True,
# )

# print("Response:\n")
# for chunk in stream:
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
# print("\n")

#================================Function calling with streaming response================================

import os 
from pathlib import Path
import httpx 
from dotenv import load_dotenv
import json
from openai import OpenAI


# Load .env from Foundation-Week-1
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

# Corporate proxy: SSL verification disabled, redirects enabled
http_client = httpx.Client(verify=False, follow_redirects=True, timeout=30.0)
client = OpenAI(api_key=api_key, http_client=http_client)

def get_weather(location: str):
    return {"location": location, "temperature": "30", "condition": "Cloudy"}

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }
}]

conversation = [{"role": "user", "content": "Do I need umbrella in Bangalore?"}]

first_response = client.chat.completions.create(
    model="gpt-4.1",
    messages=conversation,
    tools=tools
)

assistant_message = first_response.choices[0].message
tool_calls = assistant_message.tool_calls or []
conversation.append({
    "role": "assistant",
    "content": assistant_message.content or "",
    "tool_calls": [tc.model_dump() for tc in tool_calls]
})

for tool_call in tool_calls:
    if tool_call.function.name == "get_weather":
        args = json.loads(tool_call.function.arguments)
        result = get_weather(args["location"])
        conversation.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })


final = client.chat.completions.create(
    model="gpt-4.1",
    messages=conversation,
    tools=tools,
    stream=True
)

print("Assistant: ", end="", flush=True)
for chunk in final:
    delta = chunk.choices[0].delta
    if delta and delta.content:
        print(delta.content, end="", flush=True)
print()