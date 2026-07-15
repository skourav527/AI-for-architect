"""
Python Essentials Cheat Sheet
==============================

Type this code out (don't copy-paste!) to build muscle memory.
Run each section and understand the output.
"""

# =============================================================================
# 1. LIST COMPREHENSIONS (You'll use these EVERYWHERE)
# =============================================================================

print("=" * 60)
print("1. LIST COMPREHENSIONS")
print("=" * 60)

# Basic list comprehension
numbers = [1, 2, 3, 4, 5]
squares = [n**2 for n in numbers]
print(f"Squares: {squares}")  # [1, 4, 9, 16, 25]

# With condition
evens = [n for n in numbers if n % 2 == 0]
print(f"Evens: {evens}")  # [2, 4]

# Nested (for nested loops)
matrix = [[i*j for j in range(3)] for i in range(3)]
print(f"Matrix: {matrix}")  # [[0,0,0], [0,1,2], [0,2,4]]

# Dictionary comprehension
word_lengths = {word: len(word) for word in ["hello", "world", "python"]}
print(f"Word lengths: {word_lengths}")  # {'hello': 5, 'world': 5, 'python': 6}

# ✅ When to use: Transforming lists, filtering, creating dicts
# ❌ When not to use: Complex logic (use regular loops for readability)


# =============================================================================
# 2. CONTEXT MANAGERS (For resource management)
# =============================================================================

print("\n" + "=" * 60)
print("2. CONTEXT MANAGERS")
print("=" * 60)

# Built-in: file handling
with open("temp.txt", "w") as f:
    f.write("Hello, context manager!")
    # File automatically closed after this block

# Custom context manager
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        print("Timer started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        print(f"Timer stopped: {elapsed:.2f}s elapsed")
        return False  # Don't suppress exceptions

# Using custom context manager
with Timer():
    sum([i**2 for i in range(1000000)])

# Context manager for cleanup
class DatabaseConnection:
    def __enter__(self):
        print("Opening database connection")
        self.conn = "fake_connection"
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing database connection")
        # Cleanup happens even if exception occurs
        return False

with DatabaseConnection() as conn:
    print(f"Using connection: {conn}")

# ✅ When to use: Managing resources (files, connections, locks)
# Pattern: Setup in __enter__, cleanup in __exit__


# =============================================================================
# 3. DECORATORS (Modify function behavior)
# =============================================================================

print("\n" + "=" * 60)
print("3. DECORATORS")
print("=" * 60)

# Basic decorator
def log_calls(func):
    """Decorator that logs function calls"""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

result = add(3, 5)  # Will print logs


# Decorator with arguments
def repeat(times):
    """Decorator that repeats function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Python")  # Prints 3 times


# Practical: Timing decorator
import time
def timing(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timing
def slow_function():
    time.sleep(0.1)
    return "Done"

slow_function()

# ✅ When to use: Logging, timing, authentication, caching, retry logic
# Pattern: wrapper function that calls original function


# =============================================================================
# 4. TYPE HINTS (Make code self-documenting)
# =============================================================================

print("\n" + "=" * 60)
print("4. TYPE HINTS")
print("=" * 60)

from typing import List, Dict, Optional, Union

def process_items(items: List[str], limit: Optional[int] = None) -> Dict[str, int]:
    """
    Process items and return their lengths.
    
    Args:
        items: List of strings to process
        limit: Optional limit on number of items
        
    Returns:
        Dictionary mapping item to length
    """
    if limit:
        items = items[:limit]
    return {item: len(item) for item in items}

result = process_items(["hello", "world"], limit=1)
print(f"Result: {result}")

# Complex types
from typing import Callable

def apply_operation(
    numbers: List[int],
    operation: Callable[[int], int]
) -> List[int]:
    """Apply operation to each number"""
    return [operation(n) for n in numbers]

result = apply_operation([1, 2, 3], lambda x: x**2)
print(f"Squared: {result}")

# ✅ When to use: Always! Type hints improve IDE support and catch bugs
# Tool: Use mypy for static type checking


# =============================================================================
# 5. PYDANTIC (Type validation at runtime)
# =============================================================================

print("\n" + "=" * 60)
print("5. PYDANTIC")
print("=" * 60)

from pydantic import BaseModel, Field, validator

class User(BaseModel):
    """User model with validation"""
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=150)
    email: str
    is_active: bool = True
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v

# Valid user
user = User(name="Alice", age=30, email="alice@example.com")
print(f"User: {user}")
print(f"As dict: {user.model_dump()}")
print(f"As JSON: {user.model_dump_json()}")

# Invalid user (will raise validation error)
try:
    invalid_user = User(name="", age=200, email="not-an-email")
except Exception as e:
    print(f"Validation error: {e}")

# ✅ When to use: API request/response validation, configuration, data classes
# Benefit: Runtime validation + type hints


# =============================================================================
# 6. F-STRINGS (Modern string formatting)
# =============================================================================

print("\n" + "=" * 60)
print("6. F-STRINGS")
print("=" * 60)

name = "Python"
version = 3.11

# Basic
print(f"I'm learning {name} {version}")

# Expressions
print(f"2 + 2 = {2 + 2}")

# Formatting
pi = 3.14159
print(f"Pi: {pi:.2f}")  # 2 decimal places

# Debug (Python 3.8+)
x = 42
print(f"{x=}")  # Prints: x=42

# Multi-line
message = (
    f"Name: {name}\n"
    f"Version: {version}\n"
    f"Pi: {pi:.2f}"
)
print(message)

# ✅ When to use: Always! Cleaner than .format() or %


# =============================================================================
# 7. WALRUS OPERATOR := (Python 3.8+)
# =============================================================================

print("\n" + "=" * 60)
print("7. WALRUS OPERATOR :=")
print("=" * 60)

# Without walrus
data = [1, 2, 3, 4, 5]
n = len(data)
if n > 3:
    print(f"Length {n} is > 3")

# With walrus (assign and use in one expression)
if (n := len(data)) > 3:
    print(f"Length {n} is > 3")

# In list comprehensions
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Get squares only if square is > 25
big_squares = [square for n in numbers if (square := n**2) > 25]
print(f"Big squares: {big_squares}")

# ✅ When to use: Avoid duplicate calculations, cleaner code
# ❌ Don't overuse: Can hurt readability


# =============================================================================
# 8. GENERATORS (Memory-efficient iteration)
# =============================================================================

print("\n" + "=" * 60)
print("8. GENERATORS")
print("=" * 60)

# Generator function
def count_up_to(n):
    """Generate numbers from 1 to n"""
    i = 1
    while i <= n:
        yield i  # Pause and return value
        i += 1

# Use generator
for num in count_up_to(5):
    print(num, end=" ")
print()

# Generator expression (like list comprehension but lazy)
squares_gen = (x**2 for x in range(1000000))  # Doesn't compute until needed
print(f"First 5 squares: {[next(squares_gen) for _ in range(5)]}")

# ✅ When to use: Large datasets, streaming, infinite sequences
# Benefit: Memory efficient (generates values on demand)


# =============================================================================
# 9. UNPACKING
# =============================================================================

print("\n" + "=" * 60)
print("9. UNPACKING")
print("=" * 60)

# Basic unpacking
x, y, z = [1, 2, 3]
print(f"x={x}, y={y}, z={z}")

# Star unpacking
first, *middle, last = [1, 2, 3, 4, 5]
print(f"first={first}, middle={middle}, last={last}")

# Dictionary unpacking
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
combined = {**dict1, **dict2}
print(f"Combined: {combined}")

# Function arguments
def greet(name, age):
    print(f"Hello {name}, age {age}")

user_data = {"name": "Alice", "age": 30}
greet(**user_data)  # Unpack dict as kwargs


# =============================================================================
# 10. PATHLIB (Modern file paths)
# =============================================================================

print("\n" + "=" * 60)
print("10. PATHLIB")
print("=" * 60)

from pathlib import Path

# Create path
current = Path.cwd()
print(f"Current directory: {current}")

# Join paths (works on Windows and Linux!)
config_path = current / "config" / "settings.json"
print(f"Config path: {config_path}")

# Check existence
print(f"Exists: {current.exists()}")

# Get parts
print(f"Name: {config_path.name}")
print(f"Suffix: {config_path.suffix}")
print(f"Parent: {config_path.parent}")

# ✅ When to use: Always! Better than os.path


# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 60)
print("SUMMARY: Python Essentials for LLM Development")
print("=" * 60)

print("""
1. List Comprehensions - Transform/filter data elegantly
2. Context Managers - Manage resources (with statement)
3. Decorators - Add functionality to functions
4. Type Hints - Self-documenting code
5. Pydantic - Runtime validation
6. F-strings - Modern string formatting
7. Walrus Operator - Assign in expressions
8. Generators - Memory-efficient iteration
9. Unpacking - Destructure data
10. Pathlib - Modern file paths

🎯 PRACTICE: Use these in your projects today!
""")

# Cleanup
Path("temp.txt").unlink(missing_ok=True)
