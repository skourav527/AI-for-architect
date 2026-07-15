"""
Minimal multi-provider CLI.

Examples:
  python multi_provider_cli.py --provider openai --prompt "What is Python?"
  python multi_provider_cli.py --provider openai --prompt "What is Python?" --stream
  python multi_provider_cli.py --provider anthropic --prompt "What is Python?" --stream --simulate
"""

import argparse
import asyncio
import os
from pathlib import Path

from anthropic import AsyncAnthropic, APIConnectionError as AnthropicConnectionError
from anthropic import AuthenticationError as AnthropicAuthenticationError
from anthropic import BadRequestError as AnthropicBadRequestError
from dotenv import load_dotenv
from openai import APIConnectionError as OpenAIConnectionError
from openai import AsyncOpenAI, AuthenticationError as OpenAIAuthenticationError


env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_ANTHROPIC_MODEL = os.getenv("DEFAULT_ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")


def mock_answer(provider: str, prompt: str) -> str:
    text = prompt.strip()
    if provider == "openai":
        return f"[OpenAI mock] {text} -> Python is easy to learn because it reads like simple English."
    return f"[Anthropic mock] {text} -> Python is a high-level language that is readable and widely used."


class OpenAIProvider:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.client = None if simulate else AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def chat(self, prompt: str, model: str = DEFAULT_OPENAI_MODEL) -> str:
        if self.simulate:
            return mock_answer("openai", prompt)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
            )
            return response.choices[0].message.content or ""
        except OpenAIAuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except OpenAIConnectionError as e:
            raise ValueError(f"OpenAI network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))

    async def chat_stream(self, prompt: str, model: str = DEFAULT_OPENAI_MODEL):
        if self.simulate:
            for word in mock_answer("openai", prompt).split():
                yield word + " "
            return
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except OpenAIAuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except OpenAIConnectionError as e:
            raise ValueError(f"OpenAI network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))


class AnthropicProvider:
    def __init__(self, simulate: bool = False):
        self.simulate = simulate
        self.client = None if simulate else AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def chat(self, prompt: str, model: str = DEFAULT_ANTHROPIC_MODEL) -> str:
        if self.simulate:
            return mock_answer("anthropic", prompt)
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        except AnthropicAuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except AnthropicBadRequestError as e:
            raise ValueError(str(e))
        except AnthropicConnectionError as e:
            raise ValueError(f"Anthropic network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))

    async def chat_stream(self, prompt: str, model: str = DEFAULT_ANTHROPIC_MODEL):
        if self.simulate:
            for word in mock_answer("anthropic", prompt).split():
                yield word + " "
            return
        try:
            stream = await self.client.messages.create(
                model=model,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            async for event in stream:
                if event.type == "content_block_delta" and getattr(event.delta, "type", "") == "text_delta":
                    yield event.delta.text
        except AnthropicAuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except AnthropicBadRequestError as e:
            raise ValueError(str(e))
        except AnthropicConnectionError as e:
            raise ValueError(f"Anthropic network error: {str(e)[:50]}")
        except Exception as e:
            raise ValueError(str(e))


def build_provider(name: str, simulate: bool):
    if name == "openai":
        return OpenAIProvider(simulate=simulate)
    return AnthropicProvider(simulate=simulate)


def parse_args():
    parser = argparse.ArgumentParser(description="Multi-provider CLI")
    parser.add_argument("--provider", choices=["openai", "anthropic"], required=True)
    parser.add_argument("--prompt", help="Prompt text")
    parser.add_argument("--stream", action="store_true", help="Stream the response")
    parser.add_argument("--simulate", action="store_true", help="Do not call the real API")
    return parser.parse_args()


async def main():
    args = parse_args()
    prompt = args.prompt or input("Prompt: ").strip()
    if not prompt:
        raise ValueError("Prompt cannot be empty")

    provider = build_provider(args.provider, args.simulate)

    print("\n" + "=" * 60)
    print(f"Provider : {args.provider}")
    print(f"Mode     : {'stream' if args.stream else 'single'}")
    print(f"Prompt   : {prompt}")
    print("=" * 60)
    print("Response")
    print("-" * 60)

    if args.stream:
        async for chunk in provider.chat_stream(prompt):
            print(chunk, end="", flush=True)
            await asyncio.sleep(0.03)
        print("\n")
    else:
        response = await provider.chat(prompt)
        print(response)
        print()


if __name__ == "__main__":
    asyncio.run(main())
