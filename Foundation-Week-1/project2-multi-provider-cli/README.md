# Multi-Provider Chat CLI - README

## What You'll Learn

1. **Abstract Base Classes (ABC)** - Define interfaces that all providers must implement
2. **Polymorphism** - Switch between providers seamlessly
3. **Factory Pattern** - Centralized object creation
4. **Click** - Professional CLI creation
5. **Rich** - Beautiful terminal output
6. **Streaming APIs** - Real-time response handling

## Quick Start

### 1. Install Dependencies
```bash
pip install click rich httpx python-dotenv
```

### 2. Set up API Keys
Create `.env` file:
```
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

### 3. Run Examples

```bash
# Single query
python chat_cli.py "What is Python?"

# Use Claude
python chat_cli.py --provider anthropic "Write a haiku about coding"

# Stream response (see it type in real-time)
python chat_cli.py --stream "Explain async/await"

# Interactive mode
python chat_cli.py --interactive

# Use GPT-4
python chat_cli.py --provider gpt4 "Explain decorators"

# Test all providers
python chat_cli.py --test
```

## Architecture

```
LLMProvider (Abstract Base Class)
    ├── chat() - abstract method
    └── chat_stream() - abstract method

OpenAIProvider(LLMProvider)
    ├── chat() - OpenAI implementation
    └── chat_stream() - OpenAI streaming

AnthropicProvider(LLMProvider)
    ├── chat() - Anthropic implementation
    └── chat_stream() - Anthropic streaming

get_provider() - Factory function
    └── Returns appropriate provider instance
```

## Key Concepts Demonstrated

### 1. Abstract Base Class
```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str:
        """All providers MUST implement this"""
        pass
```

### 2. Polymorphism
```python
# Same interface, different implementations
provider = get_provider("openai")  # or "anthropic"
response = await provider.chat("Hello")  # Works with any provider!
```

### 3. Factory Pattern
```python
def get_provider(name: str) -> LLMProvider:
    """Create provider without knowing implementation details"""
    if name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
```

### 4. Streaming Responses
```python
async for chunk in provider.chat_stream("Write a story"):
    print(chunk, end="")  # Print in real-time
```

## Exercises

### Easy
1. Add a `--temperature` option to control randomness
2. Add a `--max-tokens` option to limit response length
3. Count and display token usage

### Medium
4. Add support for conversation history (multi-turn chat)
5. Add a `--save` option to save conversations to file
6. Add support for system prompts

### Hard
7. Add a new provider (e.g., Cohere, local Ollama)
8. Implement response caching to avoid repeat API calls
9. Add multi-language support for the CLI

## Common Issues

### "API key not found"
- Create `.env` file with your API keys
- Or set environment variables:
  ```powershell
  $env:OPENAI_API_KEY="sk-..."
  ```

### "Provider not found"
- Check spelling: `openai`, `anthropic`, `claude`, `gpt`, `gpt4`

### Streaming not working
- Make sure provider implements `chat_stream()`
- Check network/firewall settings

## Next Steps

1. Complete the exercises above
2. Integrate with Project 3 (Token Tracker)
3. Add more providers (Cohere, local models)
4. Deploy as a package (`pip install my-chat-cli`)

## Learning Verification

After completing this project, you should be able to:

- [ ] Explain what an abstract base class is and why it's useful
- [ ] Create a new provider in < 30 minutes
- [ ] Debug streaming API issues
- [ ] Build a CLI with Click
- [ ] Use Rich for beautiful terminal output
- [ ] Understand the factory pattern

---

**Time to complete:** 4-6 hours
**Difficulty:** Intermediate
**Prerequisites:** Project 1 Stage 2
