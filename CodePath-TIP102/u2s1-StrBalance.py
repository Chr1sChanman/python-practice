'''
Understand:
    I: String of ONLY lowercase letter
    O: Boolean
    C: N/A
    E: Empty string
Plan: 
    Convert the string into a Counter type dictionary
    Return all values in the dictionary as a list
    Convert list into Counter
    con
    If only one item in counter:
        return False
    else if 
Implement:
'''
from collections import Counter

def can_make_balanced(code):
    n = len(code)
    if n == 0:
        return False
    if n == 1:
        return True

    c = Counter(code)
    freq = Counter(c.values())

    if len(freq) == 2:
        (f1, n1), (f2, n2) = sorted(freq.items())

        if f1 == 1 and n1 == 1:
            return True

        if f2 == f1 + 1 and n2 == 1:
            return True

    return False
    


code1 = "arghh"
code2 = "haha"
code3 = "arghhbb"
code4 = ""

print(can_make_balanced(code1)) 
print(can_make_balanced(code2)) 
print(can_make_balanced(code3)) 
print(can_make_balanced(code4)) 