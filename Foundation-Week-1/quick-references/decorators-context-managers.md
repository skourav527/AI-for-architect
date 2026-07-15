# Decorators & Context Managers Quick Reference

## Decorators

### What are decorators?
Functions that modify other functions without changing their code.

### Basic Pattern
```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        # Do something before
        result = func(*args, **kwargs)
        # Do something after
        return result
    return wrapper

@my_decorator
def my_function():
    pass
```

### Common Use Cases

#### 1. Timing
```python
import time

def timing(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start:.2f}s")
        return result
    return wrapper

@timing
def slow_function():
    time.sleep(1)
```

#### 2. Logging
```python
import logging

def log_calls(func):
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b
```

#### 3. Retry Logic
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def api_call():
    # Will retry up to 3 times with exponential backoff
    pass
```

#### 4. Authentication
```python
def require_auth(func):
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            raise PermissionError("Not authenticated")
        return func(*args, **kwargs)
    return wrapper

@require_auth
def sensitive_operation():
    pass
```

#### 5. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n):
    # Result is cached
    return sum(range(n))
```

### Decorators with Arguments
```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet():
    print("Hello!")
```

### Preserving Function Metadata
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

---

## Context Managers

### What are context managers?
Objects that define runtime context - setup and cleanup logic.

### Basic Pattern
```python
class MyContext:
    def __enter__(self):
        # Setup code
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup code (always runs)
        print("Exiting context")
        return False  # Don't suppress exceptions

with MyContext():
    # Use context
    pass
```

### Common Use Cases

#### 1. File Handling
```python
# Built-in context manager
with open("file.txt", "w") as f:
    f.write("Hello")
# File automatically closed
```

#### 2. Database Connections
```python
class DatabaseConnection:
    def __enter__(self):
        self.conn = connect_to_database()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False

with DatabaseConnection() as conn:
    conn.execute("SELECT * FROM users")
```

#### 3. Timing
```python
import time

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        print(f"Elapsed: {elapsed:.2f}s")
        return False

with Timer():
    # Code to time
    time.sleep(1)
```

#### 4. Temporary State Changes
```python
import os

class ChangeDirectory:
    def __init__(self, path):
        self.path = path
        self.original = None
    
    def __enter__(self):
        self.original = os.getcwd()
        os.chdir(self.path)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original)
        return False

with ChangeDirectory("/tmp"):
    # Working directory is /tmp
    pass
# Back to original directory
```

#### 5. Locks and Semaphores
```python
import threading

lock = threading.Lock()

with lock:
    # Critical section
    # Lock automatically released
    pass
```

### Async Context Managers
```python
class AsyncResource:
    async def __aenter__(self):
        # Async setup
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Async cleanup
        await self.disconnect()
        return False

async with AsyncResource() as resource:
    # Use resource
    pass
```

### Using contextlib
```python
from contextlib import contextmanager

@contextmanager
def my_context():
    # Setup
    print("Entering")
    try:
        yield  # Context body runs here
    finally:
        # Cleanup (always runs)
        print("Exiting")

with my_context():
    print("Inside context")
```

### Suppressing Exceptions
```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove("nonexistent.txt")
# Exception is silently ignored
```

---

## Combining Decorators and Context Managers

### Example: Retry with Context Manager
```python
from contextlib import contextmanager

@contextmanager
def retry_context(max_attempts=3):
    """Context manager with retry logic"""
    attempts = 0
    while attempts < max_attempts:
        try:
            yield
            break  # Success
        except Exception as e:
            attempts += 1
            if attempts >= max_attempts:
                raise
            print(f"Retry {attempts}/{max_attempts}")

with retry_context(max_attempts=3):
    # Code that might fail
    risky_operation()
```

---

## When to Use What?

### Use Decorators When:
- ✅ Adding functionality to multiple functions
- ✅ Logging, timing, authentication
- ✅ Retry logic
- ✅ Caching
- ✅ Validation

### Use Context Managers When:
- ✅ Managing resources (files, connections)
- ✅ Setup and cleanup needed
- ✅ Temporary state changes
- ✅ Exception handling with cleanup
- ✅ Locks and synchronization

### Use Both When:
- ✅ Complex resource management with reusable patterns
- ✅ API clients (decorator for retry, context for connection)

---

## Practice Exercises

### Exercise 1: Create a rate-limiting decorator
```python
import time

def rate_limit(calls_per_second):
    """Decorator that limits function calls per second"""
    # Your code here
    pass
```

### Exercise 2: Create a transaction context manager
```python
class Transaction:
    """Context manager for database transactions"""
    def __enter__(self):
        # Begin transaction
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Commit if no exception
            pass
        else:
            # Rollback on exception
            pass
        return False
```

### Exercise 3: Combine both
```python
@retry(attempts=3)
async def api_call():
    async with AsyncClient() as client:
        return await client.get("...")
```

---

## Key Takeaways

1. **Decorators** = Modify function behavior
2. **Context Managers** = Manage resources
3. Always clean up resources (especially in async code)
4. Use `@wraps` to preserve function metadata
5. Context managers ALWAYS run cleanup code
6. Decorators can be stacked: `@decorator1 @decorator2`
7. Async versions: `async def __aenter__` and `async def __aexit__`

🎯 **Next**: Apply these patterns in your LLM client projects!
