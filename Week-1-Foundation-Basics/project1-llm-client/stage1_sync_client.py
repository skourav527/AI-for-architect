"""
Project 1 - Stage 1: Synchronous LLM Client
============================================

GOAL: Build a basic OpenAI client that works. Simple, but complete.

LEARNING OBJECTIVES:
- Environment variables with dotenv
- Basic error handling
- Logging
- Pydantic for validation
- Context managers for resource management

TIME: 2-3 hours
NEXT: stage2_async_client.py (add async + retry logic)
"""

import os
import logging
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import openai
import httpx

# =============================================================================
# STEP 1: LOGGING SETUP (You'll use this everywhere)
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# STEP 2: PYDANTIC MODELS (Type-safe API requests/responses)
# =============================================================================

class Message(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat completion"""
    messages: List[Message]
    model: str = Field(default="gpt-3.5-turbo", description="Model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, description="Max tokens to generate")


class ChatResponse(BaseModel):
    """Response model with metadata"""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    timestamp: datetime = Field(default_factory=datetime.now)


# =============================================================================
# STEP 3: LLM CLIENT (The main class)
# =============================================================================

class LLMClient:
    """
    Synchronous LLM client with error handling and logging.
    
    Usage:
        client = LLMClient(api_key="your_api_key_here")
        response = client.chat(
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(response.content)
    """
    
    def __init__(self, api_key: Optional[str] = None, default_model: str = "GPT-4.1", verify_ssl: bool = False):
        """
        Initialize the client.
        
        Args:
            api_key: OpenAI API key (if None, loads from environment)
            default_model: Default model to use
            verify_ssl: Whether to verify SSL certificates (set to False for corporate proxies)
        """
        # Load environment variables
        load_dotenv()
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.default_model = default_model
        
        # Create httpx client with SSL settings
        if not verify_ssl:
            logger.warning("SSL verification disabled - not recommended for production")
            http_client = httpx.Client(verify=False)
            self.client = openai.OpenAI(api_key=self.api_key, http_client=http_client)
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
        
        logger.info(f"LLMClient initialized with model: {default_model}")
    
    def chat(
        self,
        messages: List[dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (overrides default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            ChatResponse with content and metadata
            
        Raises:
            openai.APIError: If the API request fails
        """
        # Validate request using Pydantic
        request = ChatRequest(
            messages=[Message(**msg) for msg in messages],
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        logger.info(f"Sending chat request: {len(messages)} messages, model={request.model}")
        
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=request.model,
                messages=[msg.model_dump() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Extract response data
            choice = response.choices[0]
            usage = response.usage
            
            # Create structured response
            chat_response = ChatResponse(
                content=choice.message.content,
                model=response.model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                finish_reason=choice.finish_reason
            )
            
            logger.info(
                f"Response received: {chat_response.total_tokens} tokens, "
                f"finish_reason={chat_response.finish_reason}"
            )
            
            return chat_response
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def simple_completion(self, prompt: str, **kwargs) -> str:
        """
        Convenience method for simple prompts.
        
        Args:
            prompt: User prompt
            **kwargs: Additional arguments for chat()
            
        Returns:
            Response content as string
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, **kwargs)
        return response.content


# =============================================================================
# STEP 4: CONTEXT MANAGER (Proper resource management)
# =============================================================================

class LLMClientContext:
    """
    Context manager for LLM client.
    
    Usage:
        with LLMClientContext() as client:
            response = client.chat([...])
    """
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.client: Optional[LLMClient] = None
    
    def __enter__(self) -> LLMClient:
        """Enter context - create client"""
        logger.info("Creating LLM client context")
        self.client = LLMClient(**self.kwargs)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - cleanup"""
        if exc_type is not None:
            logger.error(f"Exception in context: {exc_val}")
        logger.info("Closing LLM client context")
        # No cleanup needed for OpenAI client, but structure is here for future
        return False  # Don't suppress exceptions


# =============================================================================
# STEP 5: EXAMPLES & TESTING
# =============================================================================

def example_basic_usage():
    """Example: Basic usage"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)
    
    client = LLMClient(verify_ssl=False)
    
    response = client.chat(
        messages=[
            {"role": "system", "content": "you are helpful in in learning GenAI."},
            {"role": "user", "content": "Explain the 5 steps to learn GenAI from basic."}
        ]
    )
    
    print(f"\nResponse: {response.content}")
    print(f"Tokens used: {response.total_tokens}")


def example_simple_completion():
    """Example: Simple completion"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Simple Completion")
    print("="*60)
    
    client = LLMClient(verify_ssl=False)
    
    response = client.simple_completion(
        "What are the 3 main benefits of async programming in Python?",
        temperature=0.5,
        max_tokens=150
    )
    
    print(f"\nResponse: {response}")


def example_context_manager():
    """Example: Using context manager"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Context Manager")
    print("="*60)
    
    with LLMClientContext(verify_ssl=False) as client:
        response = client.simple_completion(
            "What is a decorator in Python? Answer in 20 words."
        )
        print(f"\nResponse: {response}")


def example_error_handling():
    """Example: Error handling"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Error Handling")
    print("="*60)
    
    try:
        # This will fail if API key is invalid
        client = LLMClient(api_key="invalid-key")
        client.simple_completion("Test")
    except Exception as e:
        print(f"\n✓ Error caught and handled: {type(e).__name__}")
        print(f"  Message: {str(e)[:100]}")


# =============================================================================
# MAIN: Run examples
# =============================================================================

if __name__ == "__main__":
    print("\n🚀 Stage 1: Synchronous LLM Client")
    print("=" * 60)
    print("\nLEARNING CHECKLIST:")
    print("[ ] Environment variables with .env")
    print("[ ] Pydantic models for validation")
    print("[ ] Logging setup and usage")
    print("[ ] Error handling with try/except")
    print("[ ] Context managers (__enter__, __exit__)")
    print("\n" + "=" * 60)
    
    # Run examples
    try:
        example_basic_usage()
        #example_simple_completion()
        #example_context_manager()
        #example_error_handling()
        
        print("\n" + "="*60)
        #print("✓ All examples completed!")
        #print("="*60)
        #print("\nNEXT STEPS:")
        #print("1. Modify the examples above to test different prompts")
        #print("2. Add a method to get available models")
        #print("3. Add token counting before sending requests")
        #print("4. Move to stage2_async_client.py when ready")
        
    except ValueError as e:
        print("\n" + "="*60)
        print("⚠️  SETUP REQUIRED")
        print("="*60)
        print(f"\nError: {e}")
        print("\nAction needed:")
        print("1. Create a .env file in this directory")
        print("2. Add: OPENAI_API_KEY=sk-your-key-here")
        print("3. Run this script again")
        print("\nOr set environment variable:")
        print('   $env:OPENAI_API_KEY="sk-your-key-here"  # PowerShell')
