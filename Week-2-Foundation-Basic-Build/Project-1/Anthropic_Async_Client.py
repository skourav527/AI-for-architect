"""
Simple Anthropic async client.

Main learning point:
- OpenAI chat response: response.choices[0].message.content
- Anthropic chat response: response.content[0].text (text blocks)
- OpenAI stream chunk: chunk.choices[0].delta.content
- Anthropic stream chunk: event.delta.text from content_block_delta events
"""

import os
import asyncio
import logging
from pathlib import Path

from anthropic import AsyncAnthropic, APIConnectionError, AuthenticationError, BadRequestError
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DEFAULT_ANTHROPIC_MODEL = os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

logging.basicConfig(level=logging.ERROR, format="%(message)s")
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    model: str = Field(default=DEFAULT_ANTHROPIC_MODEL, min_length=1)
    max_tokens: int = Field(default=100, ge=1, le=4096)


class AnthropicAsyncClient:
    def __init__(self, simulate: bool = True):
        self.simulate = simulate
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.simulate and not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env")

        self.client = None if self.simulate else AsyncAnthropic(api_key=api_key)

    def _mock_answer(self, user_message: str) -> str:
        text = user_message.lower()
        if "python" in text:
            return "Python is a high-level programming language that is easy to read and widely used."
        if "async" in text:
            return "Async programming lets your code wait for slow tasks without stopping everything else."
        return f"Mock Anthropic answer for: {user_message.strip()}"

    async def chat(self, user_message: str, model: str = DEFAULT_ANTHROPIC_MODEL) -> str:
        try:
            request = ChatRequest(user_message=user_message, model=model, max_tokens=100)
        except ValidationError as e:
            raise ValueError(e.errors()[0]["msg"])

        if self.simulate:
            return self._mock_answer(request.user_message)

        try:
            response = await self.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                messages=[{"role": "user", "content": request.user_message}],
            )
            return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        except AuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except BadRequestError as e:
            raise ValueError(str(e))
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)[:50]}")
        except Exception as e:
            logger.error(str(e))
            raise ValueError(str(e))

    async def chat_stream(self, user_message: str, model: str = DEFAULT_ANTHROPIC_MODEL):
        try:
            request = ChatRequest(user_message=user_message, model=model, max_tokens=100)
        except ValidationError as e:
            raise ValueError(e.errors()[0]["msg"])

        if self.simulate:
            for word in self._mock_answer(request.user_message).split():
                yield word + " "
            return

        try:
            stream = await self.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                messages=[{"role": "user", "content": request.user_message}],
                stream=True,
            )
            async for event in stream:
                if event.type == "content_block_delta" and getattr(event.delta, "type", "") == "text_delta":
                    yield event.delta.text
        except AuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except BadRequestError as e:
            raise ValueError(str(e))
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)[:50]}")
        except Exception as e:
            logger.error(str(e))
            raise ValueError(str(e))


async def run_tests():
    client = AnthropicAsyncClient(simulate=True)

    print("\nNon-stream response")
    print("-" * 50)
    response = await client.chat("Explain async programming in one sentence.")
    print(response)

    print("\nStream response")
    print("-" * 50)
    async for chunk in client.chat_stream("What is Python in one sentence?"):
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.5)
    print("\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
