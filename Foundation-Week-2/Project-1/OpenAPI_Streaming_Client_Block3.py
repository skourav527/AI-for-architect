"""
WEEK 2 DAY 1 - BLOCK 3: Add Retry + Rate-Limiting
===================================================

GOAL: Add production-ready resilience:
  ✓ Tenacity retry with exponential backoff
  ✓ Rate limiter: 60 req/min (or tighter for local test)
  ✓ Visible retry logging
  ✓ Simulated failure path with auto-retry

IMPORTS NEEDED:
  pip install tenacity
"""

import os
import logging
import asyncio
import random
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import AsyncOpenAI, APIConnectionError, AuthenticationError, RateLimitError
from pydantic import BaseModel, Field, ValidationError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log,
)


class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1, description="User prompt")
    model: str = Field(default="gpt-3.5-turbo", min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=100, ge=1, le=4096)


class ChatResponse(BaseModel):
    content: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)
    finish_reason: str = Field(..., min_length=1)


# ============================================================================
# STEP 0: RATE LIMITER (Token Bucket Algorithm)
# ============================================================================

class RateLimiter:
    """
    Simple async rate limiter using token bucket algorithm.
    
    Default: 60 requests per minute (1 req/sec)
    For testing: Can set to tighter limits
    """
    
    def __init__(self, requests_per_minute=5):
        self.requests_per_minute = requests_per_minute
        self.min_interval = 60.0 / requests_per_minute  # Seconds between requests
        self.last_request_time = None
        logger.info(f"✓ Rate limiter initialized: {requests_per_minute} req/min (1 req/{self.min_interval:.2f}s)")
    
    async def acquire(self):
        """
        Wait if necessary to enforce rate limit.
        """
        now = datetime.now()
        
        if self.last_request_time is None:
            # First request
            self.last_request_time = now
            return
        
        time_since_last = (now - self.last_request_time).total_seconds()
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            logger.info(f"⏱️  Rate limited: Waiting {wait_time:.2f}s to stay within limit")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now()


# ============================================================================
# STEP 1: LOAD ENVIRONMENT & SETUP LOGGING
# ============================================================================

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


# ============================================================================
# STEP 2: OPENAI CLIENT WITH RETRY + RATE-LIMITING
# ============================================================================

class ResilientOpenAIClient:
    """
    OpenAI client with:
      ✓ Retry logic (tenacity)
      ✓ Rate limiting (token bucket)
      ✓ Comprehensive logging
    """
    
    def __init__(self, requests_per_minute=5, simulate_failure=False):
        """
        Args:
            requests_per_minute: Rate limit (default 5 = 1 req/12s for visible testing)
            simulate_failure: If True, first call will fail and retry
        """
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            error = "ERROR: OPENAI_API_KEY not found in .env"
            logger.error(error)
            raise ValueError(error)
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        self.simulate_failure = simulate_failure
        self.call_count = 0
        
        logger.info("✓ Resilient client initialized (with retry + rate-limiting)")
    
    @retry(
        stop=stop_after_attempt(2),  # Max 2 attempts (1 retry) for testing failure path
        wait=wait_exponential(multiplier=1, min=2, max=10),  # Exponential backoff: 2s, 4s, 8s
        retry=retry_if_exception_type((APIConnectionError, RateLimitError, Exception)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
    )
    async def chat(self, user_message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Send message with automatic retry on failure.
        
        Retry strategy:
          - Max 2 attempts (1 retry) for testing failure path
          - Exponential backoff: 2s, 4s, 8s between retries
          - Retries on: APIConnectionError, RateLimitError, or any Exception
        """
        
        # Validate input
        try:
            request = ChatRequest(
                user_message=user_message,
                model=model,
                temperature=0.7,
                max_tokens=100,
            )
        except ValidationError as e:
            error = f"❌ Request validation failed: {e.errors()[0]['msg']}"
            logger.error(error)
            raise ValueError(error)
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Simulate failure on first call (for testing retry logic)
        self.call_count += 1
        if self.simulate_failure and self.call_count == 1:
            logger.warning(f"⚠️  SIMULATED FAILURE (attempt {self.call_count}): Testing retry mechanism")
            raise APIConnectionError("Simulated network error for testing")
        
        logger.info(f"→ API Call #{self.call_count}: Sending '{request.user_message[:40]}...'")
        
        try:
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "user", "content": request.user_message}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            
            # Parse response
            message = response.choices[0].message.content or ""
            usage = response.usage
            parsed_response = ChatResponse(
                content=message,
                model=response.model or request.model,
                prompt_tokens=(usage.prompt_tokens if usage else 0),
                completion_tokens=(usage.completion_tokens if usage else 0),
                total_tokens=(usage.total_tokens if usage else 0),
                finish_reason=response.choices[0].finish_reason or "unknown",
            )
            
            logger.info(f"✓ Response received (Tokens: {parsed_response.total_tokens})")
            return parsed_response.content
            
        except AuthenticationError as e:
            error = f"❌ Auth failed: Invalid API key"
            logger.error(error)
            raise ValueError(error)
        except APIConnectionError as e:
            error = f"❌ Network error: {str(e)[:50]}"
            logger.error(error)
            raise  # Let tenacity handle retry
        except Exception as e:
            error = f"❌ Error: {str(e)[:50]}"
            logger.error(error)
            raise
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APIConnectionError, RateLimitError, Exception)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
    )
    async def chat_stream(self, user_message: str, model: str = "gpt-3.5-turbo"):
        """
        Stream message with automatic retry on failure.
        """
        
        # Validate input
        try:
            request = ChatRequest(
                user_message=user_message,
                model=model,
                temperature=0.7,
                max_tokens=100,
            )
        except ValidationError as e:
            error = f"❌ Request validation failed: {e.errors()[0]['msg']}"
            logger.error(error)
            raise ValueError(error)
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        # Simulate failure on first call
        self.call_count += 1
        if self.simulate_failure and self.call_count == 1:
            logger.warning(f"⚠️  SIMULATED FAILURE (attempt {self.call_count}): Testing retry mechanism")
            raise APIConnectionError("Simulated network error for testing")
        
        logger.info(f"→ Streaming Call #{self.call_count}: '{request.user_message[:40]}...'")
        
        try:
            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "user", "content": request.user_message}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    yield delta
            
            logger.info(f"✓ Stream complete ({len(full_content)} chars)")
            
        except AuthenticationError as e:
            error = f"❌ Auth failed: Invalid API key"
            logger.error(error)
            raise ValueError(error)
        except APIConnectionError as e:
            error = f"❌ Network error: {str(e)[:50]}"
            logger.error(error)
            raise  # Let tenacity handle retry
        except Exception as e:
            error = f"❌ Error: {str(e)[:50]}"
            logger.error(error)
            raise


# ============================================================================
# STEP 3: TESTS FOR BLOCK 3
# ============================================================================

async def run_block3_tests():
    """Run retry + rate-limiting tests"""
    
    print("\n" + "="*70)
    print("WEEK 2 DAY 1 BLOCK 3: Retry + Rate-Limiting")
    print("="*70 + "\n")
    
    # TEST 1: Rate limiting (3 requests, should see delays)
    print("TEST 1: Rate Limiting (2 req/min = ~1 req/30s for visible demo   )")
    print("-" * 70)
    try:
        # Tight rate limit for visible demo: 2 requests per minute
        client = ResilientOpenAIClient(requests_per_minute=2)
        
        questions = [
            "What is Python?",
            "What is async?",
            "What is streaming?"
        ]
        
        for q in questions:
            response = await client.chat(q)
            print(f"Q: {q}")
            print(f"A: {response[:50]}...\n")
        
        print("✓ SUCCESS: Rate limiting worked (should see delays between requests)\n")
    except ValueError as e:
        print(f"✗ FAILED: {e}\n")
    
    # TEST 2: Retry with simulated failure
    print("TEST 2: Retry Logic (Simulated Failure -> Auto-Retry)")
    print("-" * 70)
    try:
        # This client will fail on first attempt, then succeed on retry
        client = ResilientOpenAIClient(
            requests_per_minute=3,  # Normal rate limit
            simulate_failure=True    # Enable failure simulation
        )
        
        print("→ Attempting request that will FAIL then RETRY...\n")
        response = await client.chat("Why does retry matter?")
        print(f"✓ SUCCESS: Request succeeded after retry!\n  Answer: {response[:60]}...\n")
        
    except ValueError as e:
        print(f"✗ FAILED: {e}\n")
    
    # TEST 3: Combined rate limiting + streaming
    print("TEST 3: Rate Limiting + Streaming")
    print("-" * 70)
    try:
        client = ResilientOpenAIClient(requests_per_minute=60)
        
        print("→ Streaming with rate limiting:\n  ", end="", flush=True)
        logging.getLogger("openai").setLevel(logging.CRITICAL)
        
        async for chunk in client.chat_stream("What is concurrency?"):
            print(chunk, end="", flush=True)
            await asyncio.sleep(0.02)
        
        logging.getLogger("openai").setLevel(logging.INFO)
        print("\n✓ SUCCESS: Streaming completed\n")
        
    except ValueError as e:
        print(f"✗ FAILED: {e}\n")
    
    print("="*70)
    print("BLOCK 3 TESTS COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_block3_tests())
