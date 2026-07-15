"""
Project 1 - Stage 2: Async LLM Client with Retry Logic
=======================================================

GOAL: Make API calls concurrent and add automatic retry logic

LEARNING OBJECTIVES:
- async/await fundamentals
- httpx for async HTTP requests
- tenacity for retry logic
- asyncio.gather() for concurrent requests
- Decorator patterns

TIME: 3-4 hours
PREVIOUS: stage1_sync_client.py
NEXT: stage3_production_ready.py (add rate limiting, streaming)
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# PYDANTIC MODELS (Same as Stage 1)
# =============================================================================

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: str = "gpt-3.5-turbo"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None


class ChatResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    timestamp: datetime = Field(default_factory=datetime.now)
    request_duration: Optional[float] = None


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================

class RateLimitError(Exception):
    """Raised when API rate limit is hit"""
    pass


class APIError(Exception):
    """Raised for API errors"""
    pass


# =============================================================================
# ASYNC LLM CLIENT
# =============================================================================

class AsyncLLMClient:
    """
    Async LLM client with retry logic and concurrent request handling.
    
    Key differences from Stage 1:
    - All methods are async (use 'await')
    - Uses httpx for async HTTP
    - Automatic retry with exponential backoff
    - Can handle multiple requests concurrently
    
    Usage:
        async with AsyncLLMClient() as client:
            response = await client.chat([{"role": "user", "content": "Hi"}])
            print(response.content)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-3.5-turbo",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = "https://api.openai.com/v1"
        
        # Async HTTP client (will be created in __aenter__)
        self._http_client: Optional[httpx.AsyncClient] = None
        
        logger.info(f"AsyncLLMClient initialized: model={default_model}, timeout={timeout}s")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._http_client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        logger.info("HTTP client created")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._http_client:
            await self._http_client.aclose()
            logger.info("HTTP client closed")
        return False
    
    # =========================================================================
    # RETRY DECORATOR (Key Learning: Decorators + Retry Logic)
    # =========================================================================
    
    @retry(
        # Retry up to 3 times
        stop=stop_after_attempt(3),
        # Wait 1s, 2s, 4s between retries (exponential backoff)
        wait=wait_exponential(multiplier=1, min=1, max=10),
        # Only retry on specific errors
        retry=retry_if_exception_type((RateLimitError, APIError, httpx.RequestError)),
        # Log before sleeping
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request with automatic retry logic.
        
        This method demonstrates:
        1. @retry decorator for automatic retries
        2. Exponential backoff (wait longer between each retry)
        3. Error classification (which errors to retry)
        
        Args:
            endpoint: API endpoint (e.g., "/chat/completions")
            payload: Request payload
            
        Returns:
            Response JSON
            
        Raises:
            RateLimitError: On rate limit (will be retried)
            APIError: On API error (will be retried)
            Exception: On unexpected error (won't be retried)
        """
        if not self._http_client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            logger.debug(f"Making request to {endpoint}")
            start_time = datetime.now()
            
            response = await self._http_client.post(url, json=payload)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Request completed in {duration:.2f}s")
            
            # Handle rate limits (429)
            if response.status_code == 429:
                logger.warning("Rate limit hit, will retry...")
                raise RateLimitError("Rate limit exceeded")
            
            # Handle other errors
            if response.status_code >= 400:
                error_detail = response.json().get("error", {}).get("message", "Unknown error")
                logger.error(f"API error {response.status_code}: {error_detail}")
                raise APIError(f"API error: {error_detail}")
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
    
    # =========================================================================
    # MAIN CHAT METHOD
    # =========================================================================
    
    async def chat(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """
        Send async chat completion request.
        
        Args:
            messages: List of message dicts
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            ChatResponse
        """
        # Validate with Pydantic
        request = ChatRequest(
            messages=[Message(**msg) for msg in messages],
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Sending async chat: {len(messages)} messages, model={request.model}")
        
        # Prepare payload
        payload = {
            "model": request.model,
            "messages": [msg.model_dump() for msg in request.messages],
            "temperature": request.temperature
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        
        # Make request (with automatic retry)
        start_time = datetime.now()
        response_data = await self._make_request("/chat/completions", payload)
        duration = (datetime.now() - start_time).total_seconds()
        
        # Parse response
        choice = response_data["choices"][0]
        usage = response_data["usage"]
        
        return ChatResponse(
            content=choice["message"]["content"],
            model=response_data["model"],
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            finish_reason=choice["finish_reason"],
            request_duration=duration
        )
    
    async def simple_completion(self, prompt: str, **kwargs) -> str:
        """Convenience method for simple prompts"""
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat(messages, **kwargs)
        return response.content
    
    # =========================================================================
    # CONCURRENT REQUESTS (Key Learning: asyncio.gather)
    # =========================================================================
    
    async def batch_completions(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[ChatResponse]:
        """
        Process multiple prompts concurrently.
        
        This demonstrates the POWER of async:
        - 10 sequential requests: ~10-20 seconds
        - 10 concurrent requests: ~2-3 seconds
        
        Args:
            prompts: List of prompts to process
            **kwargs: Arguments for chat()
            
        Returns:
            List of ChatResponse objects
        """
        logger.info(f"Processing {len(prompts)} prompts concurrently")
        
        # Create tasks for all prompts
        tasks = [
            self.chat(
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            for prompt in prompts
        ]
        
        # Run all tasks concurrently
        start_time = datetime.now()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Batch completed in {duration:.2f}s")
        
        # Filter out errors
        successful = [r for r in responses if isinstance(r, ChatResponse)]
        failed = [r for r in responses if isinstance(r, Exception)]
        
        if failed:
            logger.warning(f"{len(failed)} requests failed")
        
        return successful


# =============================================================================
# EXAMPLES
# =============================================================================

async def example_basic_async():
    """Example: Basic async usage"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Async Usage")
    print("="*60)
    
    async with AsyncLLMClient() as client:
        response = await client.simple_completion(
            "Explain async/await in Python in one sentence."
        )
        print(f"\nResponse: {response}")


async def example_concurrent_requests():
    """Example: Concurrent requests (the magic of async!)"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Concurrent Requests")
    print("="*60)
    
    prompts = [
        "What is a Python list comprehension?",
        "What is a Python decorator?",
        "What is a Python context manager?",
        "What is async/await?",
        "What is a Python generator?"
    ]
    
    async with AsyncLLMClient() as client:
        start = datetime.now()
        responses = await client.batch_completions(
            prompts,
            temperature=0.5,
            max_tokens=50
        )
        duration = (datetime.now() - start).total_seconds()
        
        print(f"\n✓ Processed {len(responses)} requests in {duration:.2f}s")
        print("\nFirst response:")
        print(f"  {responses[0].content[:100]}...")


async def example_retry_mechanism():
    """Example: Retry mechanism in action"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Retry Mechanism")
    print("="*60)
    
    # This will demonstrate retries (if there's a transient error)
    async with AsyncLLMClient(timeout=5.0, max_retries=3) as client:
        try:
            response = await client.simple_completion(
                "Generate a very long response about Python best practices" * 10,
                max_tokens=100
            )
            print(f"\n✓ Request succeeded (possibly with retries)")
            print(f"  Response length: {len(response)} chars")
        except Exception as e:
            print(f"\n✗ Request failed after retries: {e}")


async def example_error_handling():
    """Example: Handling errors in async context"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling")
    print("="*60)
    
    try:
        async with AsyncLLMClient(api_key="invalid") as client:
            await client.simple_completion("Test")
    except Exception as e:
        print(f"\n✓ Error caught: {type(e).__name__}")


# =============================================================================
# MAIN
# =============================================================================

async def main():
    print("\n🚀 Stage 2: Async LLM Client with Retry Logic")
    print("=" * 60)
    print("\nLEARNING CHECKLIST:")
    print("[ ] async/await syntax")
    print("[ ] Async context managers (__aenter__, __aexit__)")
    print("[ ] httpx for async HTTP requests")
    print("[ ] @retry decorator for automatic retries")
    print("[ ] asyncio.gather() for concurrent execution")
    print("[ ] Error classification and handling")
    print("\n" + "=" * 60)
    
    try:
        await example_basic_async()
        await example_concurrent_requests()
        await example_retry_mechanism()
        await example_error_handling()
        
        print("\n" + "="*60)
        print("✓ All examples completed!")
        print("="*60)
        print("\nKEY LEARNINGS:")
        print("1. async/await makes concurrent requests easy")
        print("2. @retry decorator handles transient failures automatically")
        print("3. asyncio.gather() runs multiple tasks in parallel")
        print("4. Proper error handling is crucial for production code")
        print("\nNEXT STEPS:")
        print("1. Try changing max_retries and timeout values")
        print("2. Add more prompts to batch_completions")
        print("3. Monitor the logs to see retry behavior")
        print("4. Move to stage3_production_ready.py for advanced features")
        
    except ValueError as e:
        print(f"\n⚠️  Setup required: {e}")
        print("Create .env file with OPENAI_API_KEY=sk-your-key")


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
