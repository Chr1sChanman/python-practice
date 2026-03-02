'''
def fib_seq(n):
    print(f"fib_seq({n}) called")
    
    if n == 0:
        print(f"fib_seq({n}) returns 0")
        return 0
    elif n == 1:
        print(f"fib_seq({n}) returns 1")
        return 1

    result = fib_seq(n-1) + fib_seq(n-2)
    print(f"fib_seq({n}) returns {result}")
    return result
fib_seq(100)
'''
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_seq(n):
    print(f"Calculating fib_seq({n})")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return fib_seq(n-1) + fib_seq(n-2)

print(fib_seq(100))