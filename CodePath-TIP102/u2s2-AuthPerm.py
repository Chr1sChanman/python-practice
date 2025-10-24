'''
Understand:
    Input: List of perm ints
    Output: A boolean
    Constraints: N/A
    Edge Cases: No list
Plan:
    Get max int of list
    If max int of list is equal to or less then length of list:
        return false
    
'''

def is_authentic_collection(art_pieces):
    highest = max(art_pieces)
    if highest >= len(art_pieces):
        return False
    return True

collection1 = [2, 1, 3]
collection2 = [1, 3, 3, 2]
collection3 = [1, 1]

print(is_authentic_collection(collection1))
print(is_authentic_collection(collection2))
print(is_authentic_collection(collection3))