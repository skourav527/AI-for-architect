# Foundation Week 2 - Project 1

## Day 1 Summary

This project was used to build an OpenAI client step by step across four blocks.

### What I Learned

- How to move from a synchronous client shape to an async client using `AsyncOpenAI` and `asyncio.run()`.
- How to validate both request input and parsed response data with Pydantic.
- How streaming works with OpenAI chat completions by reading `chunk.choices[0].delta.content` and yielding chunks one at a time.
- How to print streamed output in real time using `async for`, `print(..., end="", flush=True)`, and optional `asyncio.sleep(...)` for a slower visual effect.
- How to add retry behavior with Tenacity so transient failures are retried automatically with visible logs.
- How to add simple rate limiting so local testing does not send requests too quickly.
- How to simulate a failure path to verify retry behavior instead of waiting for a real network issue.

### Current Files

- `OpenAPI_Sync_Client.py`: async + streaming practice client.
- `OpenAPI_Streaming_Client_Block3.py`: retry + rate limiting version for Block 3.

## How To Run

Install dependencies if needed:

```bash
pip install openai python-dotenv pydantic tenacity
```

Make sure `.env` contains:

```env
OPENAI_API_KEY=your_key_here
```

Run Block 3 example:

```bash
python OpenAPI_Streaming_Client_Block3.py
```

## Day 2 CLI

Minimal multi-provider CLI:

```bash
python multi_provider_cli.py --provider openai --prompt "What is Python?" --simulate
python multi_provider_cli.py --provider anthropic --prompt "What is Python?" --simulate
python multi_provider_cli.py --provider openai --prompt "What is Python?" --stream --simulate
python multi_provider_cli.py --provider anthropic --prompt "What is Python?" --stream --simulate
```

Files used for the simple provider examples:

- `OpenAPI_Sync_Client.py`
- `Anthropic_Async_Client.py`
- `multi_provider_cli.py`

## Known Edge Cases

- Missing `OPENAI_API_KEY` causes startup failure.
- Invalid request values such as empty prompt or bad `max_tokens` fail validation before any API call.
- Authentication failures should not be retried forever; they usually mean the API key is wrong.
- Streaming retry is safest before any chunks are emitted. If a network failure happens mid-stream, restarting can duplicate partial output unless extra resume logic is added.
- The current rate limiter is in-memory only. It does not coordinate across multiple scripts, terminals, or machines.
- The rate limiter controls request frequency, not token usage. A token-based quota would need separate tracking.
- Logging can make streamed terminal output look messy if API logs and chunk printing happen at the same time.
- The simulated failure path is useful for testing retry logic, but it is not a substitute for testing real timeout, DNS, and API rate-limit scenarios.
- Retry settings that are good for local learning may be too small for production workloads.
- Long responses or very slow model output can make the artificial `asyncio.sleep(...)` display delay feel much slower than the real stream.

## Stabilization Notes

- Keep retry rules focused on transient failures such as connection issues and rate limits.
- Avoid retrying validation errors and invalid credentials.
- For cleaner streaming demos, lower noisy logs from HTTP/OpenAI clients while chunks are printing.
- If this project grows, split client logic, decorators, and tests into separate modules.