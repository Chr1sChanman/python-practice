def isPalindrome(x):
    x = str(x)
    l = 0
    r = len(x)-1
    while l < r:
        if x[l] != x[r]:
            return False
        l += 1
        r -= 1
    return True

x = 121
print(isPalindrome(x))