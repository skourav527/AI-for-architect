
import os 
from pathlib import Path
from pyexpat.errors import messages
import httpx 
from dotenv import load_dotenv
import json
import anthropic 

# Load .env from Foundation-Week-1
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ANTHROPIC_API_KEY")
model = os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-sonnet-4-5")

if not api_key:
    raise RuntimeError("ANTHROPIC_API_KEY not found in .env")

# Corporate proxy: SSL verification disabled, redirects enabled
http_client = httpx.Client(verify=False, follow_redirects=True, timeout=30.0)
client = anthropic.Anthropic(api_key=api_key, http_client=http_client)


# Anthropic streaming response use case:

message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[{"role": "user", "content": "how to complete anthropic architect certification?"}],
)

#Anthropic tool use case:

def get_current_weather(location: str):
    return {"location": location, "temperature": "22°C", "condition": "Sunny"}


tools = [{
    "name": "get_current_weather",
    "description": "Get the current weather for a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            }
        },
        "required": ["location"]
    }
}]

message = [{"role": "user", "content": "What is the current weather in New York?"}]

response = client.messages.create(
    model=model,
    messages=message,
    tools=tools,
    max_tokens=1000,
)

print("Response:", response)


if response.stop_reason == "tool_use":
    tool_result = []
    for block in response.content:
        if block.type == "tool_use" and block.name == "get_current_weather":
            result = get_current_weather(block.input["location"])
            tool_result.append({"type": "tool_result", "name": block.name, "output": result, "content": json.dumps(result)
                                })

message.append({"role": "assistant", "content": response.content})
message.append({"role": "user", "content": tool_result})

followup_response = client.messages.create(
    model=model,
    max_tokens=512,
    tools=tools,
    messages=message,
)

print("Follow-up Response:", followup_response.content[0].text)