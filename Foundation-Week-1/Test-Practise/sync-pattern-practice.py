#===============================
# basic aync await 
#=====================================

import asyncio
import time
from typing import List
import httpx 


# print("=" * 60)
# print("Basic async await example")
# print("=" * 60)

# async def say_hello():
#     print("Hello from say_hello")
#     await asyncio.sleep(1)
#     print("Shiv")

# async def hello_world():
#     print("hello -- hello world")
#     asyncio.create_task(say_hello())
#     print("good bye from hello world")
# # Run function 
# asyncio.run(hello_world())


# def sync_function(duration, name):
#     """Simulate a synchronous function that takes some time to complete."""
#     print(f"Sync function '{name}' started, will take {duration} seconds")
#     time.sleep(duration)
#     print(f"Sync function '{name}'  completed after {duration} seconds")

# async def async_function(duration, name):
#     """Simulate an asynchronous function that takes some time to complete."""
#     print(f"Async function '{name}' started, will take {duration} seconds")
#     await asyncio.sleep(duration)
#     print(f"Async function '{name}' completed after {duration} seconds")

# print("\n--- Synchronous (one at a time)---")
# start = time.time()
# sync_function(1,"Task 1")
# sync_function(1,"Task 2")
# sync_function(1,"Task 3")
# print(f"total time: {time.time()- start:.2f} seconds")

# print("\n--- Asynchronous (concurrent)---")
# async def run_async_tasks():
#     start = time.time()
#     await asyncio.gather(
#         async_function(1,"Task 1"),
#         async_function(1,"Task 2"),
#         async_function(1,"Task 3")
#     )
#     print(f"total time: {time.time()- start:.2f} seconds")

# asyncio.run(run_async_tasks())

# =============================================================================
# 2. ASYNCIO.GATHER (Run multiple tasks concurrently)
# =============================================================================
# print("\n" + "=" * 60)
# print("ASYNCIO.Gather example")
# print("=" * 60)

# async def fetch_data(id: int, delay: float) -> dict:
#     print(f"Fetching data for ID {id} (will take {delay} seconds)...")
#     await asyncio.sleep(delay)  # Simulate network delay
#     print(f"Data for ID {id} fetched.")
#     return {"id": id, "data": f"Data for ID {id}"}

# async def gather_example():
#     tasks = [
#         fetch_data(1,1.0),
#         fetch_data(2, 0.5),
#         fetch_data(3, 1.5)
#     ]
#     results = await asyncio.gather(*tasks)
#     print(f"All data fetched: {results}")
# asyncio.run(gather_example())

#exception handdling with gather 

# async def may_fail(id: int, should_fail: bool):
#     await asyncio.sleep(0.1)
#     if should_fail:
#         raise ValueError(f"Task {id} failed!")
#     return f"task {id} succeeded"

# async def gather_with_exceptions():
#     try:
#         results = await asyncio.gather(
#             may_fail(1, False),
#             may_fail(2, True),  # This will raise an exception
#             may_fail(3, False),
#             return_exceptions=True  # This allows gather to return exceptions instead of raising them
#         )

#         for i, result in enumerate(results, 1):
#             if isinstance(result, Exception):
#                 print(f"Task {i}: Failed with error: {result}")
#             else:
#                 print(f"Task {i}: Succeeded with result: {result}")
#     except Exception as e:
#         print(f"gather Failed: {e}")

# asyncio.run(gather_with_exceptions())

# =============================================================================
# 3. ASYNC CONTEXT MANAGERS
# =============================================================================

# class AsyncDatabase:

#     async def __aenter__ (self):
#         print("Openning database connection...")
#         await asyncio.sleep(0.1)
#         self.connection = "db_Connection"
#         return self
    
#     async def __aexit__ (self, exc_type, exc_val, exc_tb):
#         print("Closing database connection...")
#         await asyncio.sleep(0.1)
#         self.connection = None
#         return False
    
#     async def query (self, sql:str):
#         print(f"Executing query: {sql}")
#         await asyncio.sleep(0.1)
#         return f"Results for query: {sql}"
    
# async def async_context_manager_example():
#     async with AsyncDatabase() as db:
#         result = await db.query("SELECT * FROM users")
#         print(result)

# asyncio.run(async_context_manager_example())

# =============================================================================
# 4. ASYNC HTTP REQUESTS (httpx)
# =============================================================================
# print("\n" + "=" * 60)
# print(" ASYNC HTTP Requests with httpx")
# print("=" * 60)

# async def fetch_url(client: httpx.AsyncClient, url: str) -> dict:
#     print(f"printing url: {url}")
#     response = await client.get(url)
#     return {
#         "url": url,
#         "status_code": response.status_code,
#         "length": len(response.content)
#     }

# async def fetch_multiple_urls():
#     urls = [
#         "https://www.example.com",
#         "https://www.python.org",
#         "https://www.asyncio.org"
#     ]

#     start = time.time()

#     async with httpx.AsyncClient() as client:
#         tasks = [fetch_url(client, url) for url in urls]
#         results = await asyncio.gather(*tasks)
#     elapsed = time.time() - start 

#     print(f"\n Fetched {len(results)} urls in {elapsed:.2f} seconds")
#     print("sequencial would take: ", len(urls) * elapsed)

#     for result in results:
#         print(f" {result['url']} - Status: {result['status_code']} - Length: {result['length']}")

# asyncio.run(fetch_multiple_urls())

# =============================================================================
# 5. ASYNC GENERATORS
# =============================================================================

# async def async_range(start: int, end: int):
#     for i in range(start, end):
#         await asyncio.sleep(0.1)
#         yield i

# async def async_generator_example():
#     print("async generator example")
#     async for num in async_range(1,5):
#         print(f" Received number: {num}")

# asyncio.run(async_generator_example())


# async def stream_llm_response(prompt: str):
#     word = prompt.split() + ["is", "a", "good", "Question"]
#     for w in word:
#         await asyncio.sleep(0.5)
#         yield w

# async def llm_streaming_example():
#     print("streaming response: ", end="")
#     async for word in stream_llm_response("What is AI?"):
#         print(word, end=" ", flush=True)
#     print()

# asyncio.run(llm_streaming_example())

# =============================================================================
# 6. SEMAPHORES (Limit concurrent operations)
# =============================================================================

# async def limited_concurrent_task(semaphore: asyncio.Semaphore, id: int):
#     async with semaphore:
#         print(f"Task {id} running (max 2 concurrent)")
#         await asyncio.sleep(1)
#         print(f"Task {id} completed")

# async def semaphore_example():
#     semaphore = asyncio.Semaphore(3)
#     tasks = [limited_concurrent_task(semaphore, i) for i in range(6)]
#     await asyncio.gather(*tasks)
# asyncio.run(semaphore_example())

# =============================================================================
# 8. TASKS (Background operations)
# =============================================================================

# async def background_task(name: str):
#     for i in range(3):
#         print(f"{name}: working... {i+1}/3")
#         await asyncio.sleep(0.1)
#     return f"{name} completed"

# async def task_example():
#     task1 = asyncio.create_task(background_task("Task 1"))
#     task2 = asyncio.create_task(background_task("Task 2"))

#     print("Main function is doing other work...")
#     await asyncio.sleep(0.5)
#     print("Main function is waiting for tasks to complete...")

#     result1 = await task1
#     result2 = await task2

#     print(f"Results: {result1}, {result2}")

# asyncio.run(task_example())

# =============================================================================
# 9. REAL-WORLD PATTERN: Async API Client
# =============================================================================

class AsyncAPIClient:

    def __init__ (self, base_url: str, max_concurrent: int = 5):
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client: httpx.AsyncClient = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        return self
    
    async def __aexit__ (self,exc_type, exc_val, exc_tb):
        await self.client.aclose()
        return False
    
    async def request(self, endpoint: str) -> dict:
        async with self.semaphore:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.get(url)
            
            # Add status code check before parsing JSON
            if response.status_code != 200:
                raise ValueError(f"HTTP {response.status_code} from {endpoint}")
            
            try:
                return response.json()
            except Exception as e:
                # Return helpful error info instead of raw parse error
                return {
                    "endpoint": endpoint,
                    "error": f"Not valid JSON - got {response.headers.get('content-type', 'unknown')} response",
                    "status": response.status_code,
                    "preview": response.text[:100]  # First 100 chars of response
                }
    
    async def batch_Request(self, endpoints: List[str]) -> List[dict]:
        tasks = [self.request(endpoint) for endpoint in endpoints]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
async def api_client_example():
    # Use httpbin.org instead - it returns proper JSON responses
    async with AsyncAPIClient("https://httpbin.org") as client:
        results = await client.batch_Request([
            "/delay/1",      # Returns JSON after 1 second
            "/uuid",         # Returns random UUID in JSON
            "/user-agent"    # Returns user agent in JSON
        ])
        
        print(f"\nCompleted {len(results)} requests:\n")
        
        # Process results - handle both success and errors
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"  Request {i}: ❌ FAILED - {type(result).__name__}: {result}")
            else:
                print(f"  Request {i}: ✅ SUCCESS - {result}")

asyncio.run(api_client_example())


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
