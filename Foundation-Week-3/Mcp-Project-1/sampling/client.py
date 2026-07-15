import argparse
import os
import sys
from pathlib import Path

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)

# Load .env from project root (or any parent directory) before creating clients.
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
if not anthropic_api_key:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is missing. Set it in the project .env file."
    )

anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
# Prefer explicit model from .env. Fall back to a broadly available alias.
model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5").strip()

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
    cwd=Path(__file__).resolve().parent,
)


def _load_text_to_summarize() -> str:
    parser = argparse.ArgumentParser(
        description="Call MCP summarize tool with text from CLI, file, or stdin."
    )
    parser.add_argument("--text", help="Text to summarize.")
    parser.add_argument(
        "--file",
        dest="file_path",
        help="Path to a UTF-8 text file to summarize.",
    )
    args = parser.parse_args()

    if args.text:
        text = args.text.strip()
        if text:
            return text

    if args.file_path:
        file_text = Path(args.file_path).read_text(encoding="utf-8").strip()
        if file_text:
            return file_text

    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            return piped

    raise SystemExit(
        "Provide input with --text, --file, or piped stdin. "
        "Example: uv run client.py --text \"your content\""
    )


async def chat(input_messages: list[SamplingMessage], max_tokens=4000):
    messages = [
        {"role": msg.role, "content": msg.content.text}
        for msg in input_messages
        if msg.content.type == "text" and msg.role in {"user", "assistant"}
    ]

    response = await anthropic_client.messages.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    text = "".join([p.text for p in response.content if p.type == "text"])
    return text, model


async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    # Call Claude using the Anthropic SDK
    text, selected_model = await chat(params.messages)

    return CreateMessageResult(
        role="assistant",
        model=selected_model,
        content=TextContent(type="text", text=text),
    )


async def run(text_to_summarize: str):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write, sampling_callback=sampling_callback
        ) as session:
            await session.initialize()

            result = await session.call_tool(
                name="summarize",
                arguments={"text_to_summarize": text_to_summarize},
            )
            print(result.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run(_load_text_to_summarize()))
