'''
Understand:
    I: List with ints
    O: List with ints
    C: N/A
    E: This is an index 1 list, empty list
Plan: 
    Create dictionary frequency
    result list
    Iterate through list:
        if i in freq and not in result:
            appending i to result
        if not:
            create key and value 1
Implement:
'''

def find_duplicate_chests(chests):
    freq = {}
    res = []
    for i in chests:
        if i in freq and i not in res:
            res.append(i)
        else:
            freq[i] = 1
    return res
chests1 = [4, 3, 2, 7, 8, 2, 3, 1]
chests2 = [1, 1, 2]
chests3 = [1]

print(find_duplicate_chests(chests1))
print(find_duplicate_chests(chests2))
print(find_duplicate_chests(chests3))