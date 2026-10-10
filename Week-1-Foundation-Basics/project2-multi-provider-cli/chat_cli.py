"""
Project 2: Multi-Provider Chat CLI
===================================

GOAL: Build a beautiful CLI that works with multiple LLM providers

LEARNING OBJECTIVES:
- Abstract base classes for provider interface
- Click for CLI creation
- Rich for beautiful terminal output
- Streaming API responses
- Provider abstraction patterns

TIME: 4-6 hours
REQUIRES: Completion of Project 1 Stage 2

Usage:
    python chat_cli.py --provider openai "Tell me about Python"
    python chat_cli.py --provider anthropic --stream "Write a haiku"
"""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator
from datetime import datetime
from dotenv import load_dotenv
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
import httpx

# Load environment
load_dotenv()

# Rich console for beautiful output
console = Console()


# =============================================================================
# ABSTRACT BASE CLASS (Provider Interface)
# =============================================================================

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This demonstrates POLYMORPHISM - all providers implement the same interface,
    so we can switch between them seamlessly.
    """
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Setup async context"""
        self._client = httpx.AsyncClient(timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async context"""
        if self._client:
            await self._client.aclose()
        return False
    
    @abstractmethod
    async def chat(self, message: str, stream: bool = False) -> str:
        """Send a chat message and get response"""
        pass
    
    @abstractmethod
    async def chat_stream(self, message: str) -> AsyncIterator[str]:
        """Stream chat response"""
        pass


# =============================================================================
# OPENAI PROVIDER
# =============================================================================

class OpenAIProvider(LLMProvider):
    """OpenAI (GPT) provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        super().__init__(api_key, model)
        self.base_url = "https://api.openai.com/v1"
    
    async def chat(self, message: str, stream: bool = False) -> str:
        """Send chat message"""
        if stream:
            # Collect all chunks
            chunks = []
            async for chunk in self.chat_stream(message):
                chunks.append(chunk)
            return "".join(chunks)
        
        # Non-streaming request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.7
        }
        
        response = await self._client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def chat_stream(self, message: str) -> AsyncIterator[str]:
        """Stream chat response"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "temperature": 0.7,
            "stream": True
        }
        
        async with self._client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code}")
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
                    except json.JSONDecodeError:
                        continue


# =============================================================================
# ANTHROPIC PROVIDER
# =============================================================================

class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) provider implementation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        super().__init__(api_key, model)
        self.base_url = "https://api.anthropic.com/v1"
    
    async def chat(self, message: str, stream: bool = False) -> str:
        """Send chat message"""
        if stream:
            chunks = []
            async for chunk in self.chat_stream(message):
                chunks.append(chunk)
            return "".join(chunks)
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": message}]
        }
        
        response = await self._client.post(
            f"{self.base_url}/messages",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["content"][0]["text"]
    
    async def chat_stream(self, message: str) -> AsyncIterator[str]:
        """Stream chat response"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": message}],
            "stream": True
        }
        
        async with self._client.stream(
            "POST",
            f"{self.base_url}/messages",
            headers=headers,
            json=payload
        ) as response:
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code}")
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        
                        if data["type"] == "content_block_delta":
                            if "delta" in data and "text" in data["delta"]:
                                yield data["delta"]["text"]
                    except json.JSONDecodeError:
                        continue


# =============================================================================
# PROVIDER FACTORY
# =============================================================================

def get_provider(provider_name: str, model: Optional[str] = None) -> LLMProvider:
    """
    Factory function to get provider by name.
    
    This is the FACTORY PATTERN - centralized object creation.
    """
    providers = {
        "openai": (OpenAIProvider, "gpt-3.5-turbo"),
        "gpt": (OpenAIProvider, "gpt-3.5-turbo"),
        "gpt4": (OpenAIProvider, "gpt-4"),
        "anthropic": (AnthropicProvider, "claude-3-5-sonnet-20241022"),
        "claude": (AnthropicProvider, "claude-3-5-sonnet-20241022"),
    }
    
    if provider_name.lower() not in providers:
        available = ", ".join(providers.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
    
    provider_class, default_model = providers[provider_name.lower()]
    return provider_class(model=model or default_model)


# =============================================================================
# CLI INTERFACE (Click + Rich)
# =============================================================================

@click.command()
@click.argument('prompt', required=False)
@click.option(
    '--provider', '-p',
    default='openai',
    help='LLM provider: openai, gpt4, anthropic, claude'
)
@click.option(
    '--model', '-m',
    default=None,
    help='Specific model to use (overrides provider default)'
)
@click.option(
    '--stream/--no-stream', '-s',
    default=False,
    help='Stream the response'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Start interactive chat mode'
)
def main(prompt: Optional[str], provider: str, model: Optional[str], stream: bool, interactive: bool):
    """
    Multi-Provider LLM Chat CLI
    
    Examples:
        chat_cli.py "What is Python?"
        chat_cli.py --provider anthropic --stream "Write a poem"
        chat_cli.py --interactive
    """
    
    # Show banner
    console.print(Panel.fit(
        "🤖 [bold cyan]Multi-Provider LLM Chat[/bold cyan]\n"
        f"Provider: [yellow]{provider}[/yellow] | "
        f"Streaming: [yellow]{stream}[/yellow]",
        border_style="cyan"
    ))
    
    if interactive:
        asyncio.run(interactive_mode(provider, model, stream))
    elif prompt:
        asyncio.run(single_query(prompt, provider, model, stream))
    else:
        console.print("[red]Error:[/red] Provide a prompt or use --interactive mode")
        console.print("\nExamples:")
        console.print('  chat_cli.py "What is async Python?"')
        console.print('  chat_cli.py --interactive')


async def single_query(prompt: str, provider_name: str, model: Optional[str], stream: bool):
    """Handle a single query"""
    try:
        # Get provider
        provider = get_provider(provider_name, model)
        
        # Show user message
        console.print(f"\n[bold blue]You:[/bold blue] {prompt}\n")
        
        # Get response
        async with provider:
            if stream:
                # Stream response with live updates
                console.print("[bold green]Assistant:[/bold green] ", end="")
                response_text = ""
                async for chunk in provider.chat_stream(prompt):
                    response_text += chunk
                    console.print(chunk, end="")
                console.print("\n")
            else:
                # Non-streaming with spinner
                with console.status("[bold green]Thinking...", spinner="dots"):
                    response = await provider.chat(prompt, stream=False)
                
                console.print(f"[bold green]Assistant:[/bold green]\n")
                console.print(Markdown(response))
        
        console.print(f"\n[dim]✓ Response from {provider_name}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


async def interactive_mode(provider_name: str, model: Optional[str], stream: bool):
    """Interactive chat mode"""
    console.print("\n[bold green]Interactive Mode[/bold green] - Type 'quit' to exit\n")
    
    try:
        provider = get_provider(provider_name, model)
        
        async with provider:
            while True:
                # Get user input
                user_input = console.input("[bold blue]You:[/bold blue] ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("\n[dim]Goodbye! 👋[/dim]")
                    break
                
                if not user_input:
                    continue
                
                console.print()
                
                # Get response
                try:
                    if stream:
                        console.print("[bold green]Assistant:[/bold green] ", end="")
                        async for chunk in provider.chat_stream(user_input):
                            console.print(chunk, end="")
                        console.print("\n")
                    else:
                        with console.status("[bold green]Thinking...", spinner="dots"):
                            response = await provider.chat(user_input, stream=False)
                        console.print(f"[bold green]Assistant:[/bold green]\n")
                        console.print(Markdown(response))
                        console.print()
                
                except Exception as e:
                    console.print(f"[red]Error:[/red] {e}\n")
    
    except Exception as e:
        console.print(f"[red]Setup Error:[/red] {e}")


# =============================================================================
# TESTING
# =============================================================================

async def test_providers():
    """Test all providers"""
    console.print("\n[bold]Testing Providers[/bold]\n")
    
    providers_to_test = [
        ("openai", "What is 2+2? Answer in 5 words."),
        ("anthropic", "What is Python? Answer in 5 words."),
    ]
    
    for provider_name, prompt in providers_to_test:
        try:
            console.print(f"\n[cyan]Testing {provider_name}...[/cyan]")
            provider = get_provider(provider_name)
            
            async with provider:
                response = await provider.chat(prompt, stream=False)
                console.print(f"✓ {provider_name}: {response[:50]}...")
        
        except Exception as e:
            console.print(f"✗ {provider_name}: {e}")


if __name__ == "__main__":
    # If run with --test flag, run tests
    import sys
    if "--test" in sys.argv:
        asyncio.run(test_providers())
    else:
        main()
