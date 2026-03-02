memo = {}
def fib(n):
	if n in memo:
		return memo[n]
	if n <= 1:
		return n
	memo[n] = fib(n-1) + fib(n-2)
	return memo[n]

print(fib(7))
assert fib(0) == 0
# print(fib.cache_info())