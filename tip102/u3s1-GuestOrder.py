'''
Understand:
    I: String of chars I's and D's
    O: Length of the string + 1 of numbers 
    C: Assume the numbers ranging from 1-9
    E: Empty string, inputs not I or D
Plan: 
    If I:
        if not stack:
            Add I to string
        Append I and pop stack
    If D:
        Add to stack 
Implement:
'''
def arrange_guest_arrival_order(arrival_pattern):
    count = 1
    ans = []
    stack = []
    for i in range(len(arrival_pattern)):
        stack.append(count)
        if arrival_pattern[i] == 'I':
            while stack:
                ans.append(stack.pop())
        count += 1
    
    stack.append(count)
    while stack:
        ans.append(stack.pop())
    
    return ''.join(map(str, ans))


print(arrange_guest_arrival_order("IIIDIDDD"))  
print(arrange_guest_arrival_order("DDD"))  

123549876
4321