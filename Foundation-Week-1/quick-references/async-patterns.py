"""
Async/Await Patterns Cheat Sheet
=================================

Master async Python for concurrent API calls.
Type and run each example to understand the flow.
"""

import asyncio
import time
from typing import List
import httpx

# =============================================================================
# 1. BASIC ASYNC/AWAIT
# =============================================================================

print("=" * 60)
print("1. BASIC ASYNC/AWAIT")
print("=" * 60)

async def say_hello():
    """Basic async function"""
    print("Hello")
    await asyncio.sleep(1)  # Non-blocking sleep
    print("World")

# Run async function
asyncio.run(say_hello())


# Comparison: Sync vs Async
def sync_sleep(duration, name):
    """Synchronous sleep (blocks)"""
    print(f"{name}: Start")
    time.sleep(duration)
    print(f"{name}: Done")

async def async_sleep(duration, name):
    """Asynchronous sleep (doesn't block)"""
    print(f"{name}: Start")
    await asyncio.sleep(duration)  # Other tasks can run during this
    print(f"{name}: Done")


print("\n--- Synchronous (one at a time) ---")
start = time.time()
sync_sleep(1, "Task 1")
sync_sleep(1, "Task 2")
sync_sleep(1, "Task 3")
print(f"Total time: {time.time() - start:.2f}s")  # ~3 seconds


print("\n--- Asynchronous (concurrent) ---")
async def run_async_tasks():
    start = time.time()
    # Run all tasks concurrently
    await asyncio.gather(
        async_sleep(1, "Task 1"),
        async_sleep(1, "Task 2"),
        async_sleep(1, "Task 3")
    )
    print(f"Total time: {time.time() - start:.2f}s")  # ~1 second!

asyncio.run(run_async_tasks())


# =============================================================================
# 2. ASYNCIO.GATHER (Run multiple tasks concurrently)
# =============================================================================

print("\n" + "=" * 60)
print("2. ASYNCIO.GATHER")
print("=" * 60)

async def fetch_data(id: int, delay: float) -> dict:
    """Simulate fetching data from API"""
    print(f"Fetching data {id}...")
    await asyncio.sleep(delay)
    return {"id": id, "data": f"result_{id}"}


async def gather_example():
    """Gather multiple async operations"""
    # All tasks start at the same time
    results = await asyncio.gather(
        fetch_data(1, 1.0),
        fetch_data(2, 0.5),
        fetch_data(3, 1.5)
    )
    print(f"Results: {results}")

asyncio.run(gather_example())


# Handle exceptions in gather
async def may_fail(id: int, should_fail: bool):
    """Task that might fail"""
    await asyncio.sleep(0.1)
    if should_fail:
        raise ValueError(f"Task {id} failed")
    return f"Task {id} succeeded"


async def gather_with_errors():
    """Handle errors in gather"""
    try:
        # return_exceptions=True: Don't stop on first error
        results = await asyncio.gather(
            may_fail(1, False),
            may_fail(2, True),  # This will fail
            may_fail(3, False),
            return_exceptions=True  # Continue despite errors
        )
        
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"Task {i}: Failed - {result}")
            else:
                print(f"Task {i}: {result}")
    except Exception as e:
        print(f"Gather failed: {e}")

asyncio.run(gather_with_errors())


# =============================================================================
# 3. ASYNC CONTEXT MANAGERS
# =============================================================================

print("\n" + "=" * 60)
print("3. ASYNC CONTEXT MANAGERS")
print("=" * 60)

class AsyncDatabase:
    """Example async context manager"""
    
    async def __aenter__(self):
        """Called when entering 'async with' block"""
        print("Opening database connection...")
        await asyncio.sleep(0.1)  # Simulate connection time
        self.connection = "db_connection"
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting 'async with' block"""
        print("Closing database connection...")
        await asyncio.sleep(0.1)  # Simulate cleanup time
        return False  # Don't suppress exceptions
    
    async def query(self, sql: str):
        """Simulate database query"""
        await asyncio.sleep(0.1)
        return f"Result for: {sql}"


async def use_async_context_manager():
    """Using async context manager"""
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(f"Query result: {result}")

asyncio.run(use_async_context_manager())


# =============================================================================
# 4. ASYNC HTTP REQUESTS (httpx)
# =============================================================================

print("\n" + "=" * 60)
print("4. ASYNC HTTP REQUESTS")
print("=" * 60)

async def fetch_url(client: httpx.AsyncClient, url: str) -> dict:
    """Fetch a URL asynchronously"""
    response = await client.get(url)
    return {
        "url": url,
        "status": response.status_code,
        "length": len(response.text)
    }


async def fetch_multiple_urls():
    """Fetch multiple URLs concurrently"""
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1"
    ]
    
    start = time.time()
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        # Fetch all URLs concurrently
        tasks = [fetch_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    
    print(f"\nFetched {len(results)} URLs in {elapsed:.2f}s")
    print("(Sequential would take ~3 seconds)")
    
    for result in results:
        print(f"  {result['url']}: {result['status']} ({result['length']} bytes)")

# Uncomment to run (requires internet)
# asyncio.run(fetch_multiple_urls())


# =============================================================================
# 5. ASYNC GENERATORS
# =============================================================================

print("\n" + "=" * 60)
print("5. ASYNC GENERATORS")
print("=" * 60)

async def async_range(start: int, end: int):
    """Async generator - yields values asynchronously"""
    for i in range(start, end):
        await asyncio.sleep(0.1)  # Simulate async work
        yield i


async def use_async_generator():
    """Consume async generator"""
    print("Numbers from async generator:")
    async for num in async_range(1, 6):
        print(f"  {num}")

asyncio.run(use_async_generator())


# Real-world example: Streaming API responses
async def stream_llm_response(prompt: str):
    """Simulate streaming LLM response"""
    words = prompt.split() + ["is", "a", "good", "question"]
    
    for word in words:
        await asyncio.sleep(0.2)  # Simulate network delay
        yield word


async def consume_stream():
    """Consume streaming response"""
    print("Streaming response: ", end="")
    async for word in stream_llm_response("What is Python"):
        print(word, end=" ")
    print()

asyncio.run(consume_stream())


# =============================================================================
# 6. SEMAPHORES (Limit concurrent operations)
# =============================================================================

print("\n" + "=" * 60)
print("6. SEMAPHORES - Rate Limiting")
print("=" * 60)

async def limited_task(semaphore: asyncio.Semaphore, id: int):
    """Task that respects concurrency limit"""
    async with semaphore:
        print(f"Task {id} running (max 2 concurrent)")
        await asyncio.sleep(1)
        print(f"Task {id} done")


async def semaphore_example():
    """Limit concurrent tasks with semaphore"""
    # Only 2 tasks can run at the same time
    semaphore = asyncio.Semaphore(2)
    
    tasks = [limited_task(semaphore, i) for i in range(5)]
    await asyncio.gather(*tasks)

asyncio.run(semaphore_example())


# =============================================================================
# 7. TIMEOUT
# =============================================================================

print("\n" + "=" * 60)
print("7. TIMEOUT")
print("=" * 60)

async def slow_operation():
    """Operation that takes too long"""
    print("Starting slow operation...")
    await asyncio.sleep(5)
    return "Done"


async def timeout_example():
    """Set timeout for async operations"""
    try:
        # Timeout after 2 seconds
        result = await asyncio.wait_for(slow_operation(), timeout=2.0)
        print(f"Result: {result}")
    except asyncio.TimeoutError:
        print("Operation timed out!")

asyncio.run(timeout_example())


# =============================================================================
# 8. TASKS (Background operations)
# =============================================================================

print("\n" + "=" * 60)
print("8. TASKS")
print("=" * 60)

async def background_task(name: str):
    """Task that runs in background"""
    for i in range(3):
        print(f"{name}: Working... ({i+1}/3)")
        await asyncio.sleep(0.5)
    return f"{name} completed"


async def task_example():
    """Create and manage tasks"""
    # Create task (starts immediately)
    task1 = asyncio.create_task(background_task("Task1"))
    task2 = asyncio.create_task(background_task("Task2"))
    
    # Do other work while tasks run
    print("Main: Doing other work...")
    await asyncio.sleep(1)
    print("Main: Still working...")
    
    # Wait for tasks to complete
    result1 = await task1
    result2 = await task2
    
    print(f"Results: {result1}, {result2}")

asyncio.run(task_example())


# =============================================================================
# 9. REAL-WORLD PATTERN: Async API Client
# =============================================================================

print("\n" + "=" * 60)
print("9. REAL-WORLD PATTERN: Async API Client")
print("=" * 60)

class AsyncAPIClient:
    """Example async API client pattern"""
    
    def __init__(self, base_url: str, max_concurrent: int = 5):
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._client: httpx.AsyncClient = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
        return False
    
    async def request(self, endpoint: str) -> dict:
        """Make rate-limited request"""
        async with self.semaphore:  # Rate limiting
            url = f"{self.base_url}{endpoint}"
            response = await self._client.get(url)
            return response.json()
    
    async def batch_request(self, endpoints: List[str]) -> List[dict]:
        """Make multiple requests concurrently"""
        tasks = [self.request(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks, return_exceptions=True)


async def api_client_example():
    """Using async API client"""
    async with AsyncAPIClient("https://httpbin.org") as client:
        # Batch requests
        results = await client.batch_request([
            "/delay/1",
            "/uuid",
            "/user-agent"
        ])
        
        print(f"Completed {len(results)} requests")

# Uncomment to run (requires internet)
# asyncio.run(api_client_example())


# =============================================================================
# 10. COMMON MISTAKES & SOLUTIONS
# =============================================================================

print("\n" + "=" * 60)
print("10. COMMON MISTAKES")
print("=" * 60)

# ❌ MISTAKE 1: Forgetting await
async def mistake_1():
    # This doesn't work - returns coroutine object, doesn't execute
    result = asyncio.sleep(1)  # ❌ Missing await
    print(f"Result: {result}")  # <coroutine object>

# ✅ SOLUTION: Always await
async def solution_1():
    result = await asyncio.sleep(1)  # ✅ Correct
    print("Done sleeping")


# ❌ MISTAKE 2: Mixing sync and async
def sync_function():
    # Can't use await in regular function
    # await asyncio.sleep(1)  # ❌ SyntaxError
    pass

# ✅ SOLUTION: Make function async
async def async_function():
    await asyncio.sleep(1)  # ✅ Correct


# ❌ MISTAKE 3: Blocking operations in async code
async def mistake_3():
    time.sleep(1)  # ❌ Blocks entire event loop!
    return "Done"

# ✅ SOLUTION: Use async equivalents
async def solution_3():
    await asyncio.sleep(1)  # ✅ Non-blocking


# ❌ MISTAKE 4: Not using context managers for cleanup
async def mistake_4():
    client = httpx.AsyncClient()
    # Make requests...
    # ❌ Forgot to close client

# ✅ SOLUTION: Use context manager
async def solution_4():
    async with httpx.AsyncClient() as client:  # ✅ Auto cleanup
        pass  # Make requests


# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 60)
print("SUMMARY: Async Patterns")
print("=" * 60)

print("""
KEY CONCEPTS:
1. async def - Define async function
2. await - Wait for async operation
3. asyncio.gather() - Run tasks concurrently
4. async with - Async context managers
5. async for - Iterate async generators
6. Semaphore - Limit concurrency
7. wait_for() - Set timeouts
8. create_task() - Background tasks

WHEN TO USE ASYNC:
✅ Multiple I/O operations (API calls, database queries)
✅ Network requests (HTTP, WebSocket)
✅ File I/O (with aiofiles)

WHEN NOT TO USE:
❌ CPU-bound tasks (use multiprocessing instead)
❌ Simple scripts with single operations
❌ When code doesn't do I/O

REMEMBER:
- Async makes I/O operations concurrent, not faster individually
- 10 API calls: sync = 10s, async = ~1s (if each takes 1s)
- Always await async functions
- Use async context managers for cleanup

🎯 PRACTICE: Convert Project 1 from sync to async!
""")
