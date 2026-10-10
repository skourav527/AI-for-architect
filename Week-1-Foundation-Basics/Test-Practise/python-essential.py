# print("=" * 200)
# print("Welcome to Python Essentials!")
# print("=" * 200)


# 1. List comprehensions
from time import time


number = [1, 2, 3, 4, 5]
#squares = [n ** 3 for n in number]
#print(f"squares: {squares}")

# with condition
even = [n for n in number if n%2 == 0]
#print(f"even: {even}")

# Nested for nested loop

# matrix = [[i*j for j in range(4)] for i in range(4)]

# i = 0
# j = 0
# matrix2 = []
# for i in range(4):
#     matrix2.append([])
#     for j in range(4):
#         matrix2[i].append(i*j)
# print(f"matrix: {matrix2}")

# disctionary comprehension
# word_lenth  = {word: len(word) for word in ["apple", "hell0", "python", "Shivkumar"]}
# print(f"lenth of worrds: {word_lenth}")

#==================================================
# 2. COntext Managers (for resource management)
#==================================================

# print("\n" + "=" * 50)
# print("Context Mannagers")
# print("=" * 50)

# build-in : file handdling

# with open("temp.txt", "w") as f:
#     f.write("Hello, context managers!")

# class Timer:
#     def __enter__(self):
#         import time
#         self.start = time.time()
#         self.time = time  # Store reference to time module
#         print("Timer started.")
#         return self
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         elapsed = self.time.time() - self.start
#         print(f"Timer stopped: {elapsed:.2f}s elapsed.")
#         return False
    
# # Using Custom context manager 
# with Timer():
#      sum([i**2 for i in range(1000000)])

# # Context manager for cleanup 

# class DatabaseConnection:
#     def __enter__(self):
#         print("Opening database connection.")
#         self.conn = "Fake_Connection"
#         return self.conn
    
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         print("Closing database connecttion")
#         return False
    
# with DatabaseConnection() as conn:
#     print(f"using connection: {conn}")

#==================================================
# 3. Decorator (modify function behavior    )
#==================================================
# print("\n" + "=" * 50)
# print("Decorators")
# print("=" * 50)

# # basic decorator 
# def log_calls(func):
#     def wrapper(*args, **kwargs):
#         print(f"calling {func.__name__} with args: {args}, kwargs: {kwargs}")
#         result = func(*args, **kwargs)
#         print(f"{func.__name__} returned: {result}")
#         return result
#     return wrapper

# @log_calls
# def add(a, b):
#     return a + b
# result = add(5,3) 

# Decorator with arguments 

# def repeat(times):
#     """"Decorator that repeates function execution"""
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for _ in range(times):
#                 result = func(*args, **kwargs)
#             return result
#         return wrapper
#     return decorator

# @repeat(times=3)
# def greet(name):
#     print(f"hello, {name}")
# greet("Shivkumar")

# timing decorator

# import time
# def timing(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time() - start_time
#         print(f"{func.__name__} took {end_time:.4f} second to excute")
#         return result
#     return wrapper

# @timing
# def slow_function():
#     time.sleep(0.1)
#     return "Done"
# slow_function()

# ==================================================
# when to use logging , authentication , timing , caching and retry logic 
# pattenrn: wrapper function that call original function
#==============================================================

#====================================================================
# Type Hint ( make code self documented)
#=============================

# print("\n" + "=" * 60)
# print("Type Hint")
# print("=" * 60)

# from typing import List, Dict, Optional, Union
# def process_itme(items: List[str], limit: Optional[int] = None) -> Dist[str, int]:
#     """
#     process item and return their lengths.
#     args:
#     items : list of the string to process 
#     limit: Optional limit on numbers of items

#     Returns:
#        Dictionary mapping item to lenght
#     """
#     if limit:
#         items = items[:limit]
#     return {item: len(item) for item in items}

# result = process_itme(["hello", "world"], limit=1)
# print(f"Result: {result}")

#=====================================================
#  Pydantic - type validation at runtime
#=======================================================


# from pydantic import BaseModel, Field, field_validator

# class User(BaseModel):
#     """ user Model with validation"""
#     name: str = Field(..., min_length=1, max_length=50)
#     age: int = Field(..., ge=0, le=150)
#     email: str
#     is_active: bool = True

#     @field_validator('email')
#     @classmethod
#     def email_must_be_valid(cls, v):
#         if '@' not in v:
#             raise ValueError('Invalid email')
#         return v
    
# # valid user
# try:
#     user = User(name="shiv", age=200, email="skouravslb.com")
# except Exception as e:
#     print(f"validation error {e}")


#=======================================
# modern string formating
#=========================

# name= "shivkuamr"
# version= 3.11

# print (f"I am leaning {name} and {version}")

# print (f"2 + 2 = {2 + 2}")

# pi= 3.14159 
# print(f"pi: {pi:.2f}")

# #===================================Wakrus operator===================

# data = [1, 2, 3, 4, 5 ]
# n = len(data)
# if n > 3:
#     print(f"Length {n} is > 3")


# # with walrus operator
# if (n := len(data)) > 3:
#     print(f"Length {n} is > 3")


#=========================generator  (memeory efficent)===============


def print_up_to(n):
    """ print number from 1 to n """
    i = 1 
    while i <= n : 
        yield i # pause and retun value
        i+= 1

for num in print_up_to(10):
    print(num, end="")
print()