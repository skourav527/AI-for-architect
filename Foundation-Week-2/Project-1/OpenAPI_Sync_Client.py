"""
Simple OpenAI async client.

Main learning point:
- OpenAI chat response: response.choices[0].message.content
- OpenAI stream chunk: chunk.choices[0].delta.content
"""

import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI, APIConnectionError, AuthenticationError
from pydantic import BaseModel, Field, ValidationError


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")


class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1)
    model: str = Field(default=DEFAULT_OPENAI_MODEL, min_length=1)
    max_tokens: int = Field(default=100, ge=1, le=4096)


class OpenAIAsyncClient:
    def __init__(self, simulate: bool = True):
        self.simulate = simulate
        api_key = os.getenv("OPENAI_API_KEY")

        if not self.simulate and not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        self.client = None if self.simulate else AsyncOpenAI(api_key=api_key)

    def _mock_answer(self, user_message: str) -> str:
        text = user_message.lower()
        if "python" in text:
            return "Python is a high-level programming language that is easy to learn and widely used."
        if "async" in text:
            return "Async programming lets your code keep working while it waits for slow tasks."
        return f"Mock OpenAI answer for: {user_message.strip()}"

    async def chat(self, user_message: str, model: str = DEFAULT_OPENAI_MODEL) -> str:
        try:
            request = ChatRequest(user_message=user_message, model=model, max_tokens=100)
        except ValidationError as e:
            raise ValueError(e.errors()[0]["msg"])

        if self.simulate:
            return self._mock_answer(request.user_message)

        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": request.user_message}],
                max_tokens=request.max_tokens,
            )
            return response.choices[0].message.content or ""
        except AuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))

    async def chat_stream(self, user_message: str, model: str = DEFAULT_OPENAI_MODEL):
        try:
            request = ChatRequest(user_message=user_message, model=model, max_tokens=100)
        except ValidationError as e:
            raise ValueError(e.errors()[0]["msg"])

        if self.simulate:
            for word in self._mock_answer(request.user_message).split():
                yield word + " "
            return

        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": request.user_message}],
                max_tokens=request.max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except AuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except APIConnectionError as e:
            raise ValueError(f"Network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))


async def run_tests():
    client = OpenAIAsyncClient(simulate=True)

    print("\nNon-stream response")
    print("-" * 50)
    response = await client.chat("Explain async programming in one sentence.")
    print(response)

    print("\nStream response")
    print("-" * 50)
    async for chunk in client.chat_stream("What is Python in one sentence?"):
        print(chunk, end="", flush=True)
        await asyncio.sleep(0.03)
    print("\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
