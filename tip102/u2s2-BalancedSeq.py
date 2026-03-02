'''
Understand:
    I: List of ints
    O: Int of the length of the longest subsequence
    C: N/A
    E: Empty list, list of 1
Plan: 
    Int max = 0
    for i in list:
        int count
        for j in list:
            if j = i+1 or j = i -1:
                count += 1
        if count > max:
            max = count
    return max

Implement:
'''

from collections import Counter

def find_balanced_subsequence(art_pieces):
    total = 0
    c = Counter(art_pieces)
    for i in c:
        if i+1 in c:
            total = max(total, (c[i] + c[i+1]))
    return total


art_pieces1 = [1,3,2,2,5,2,3,7]
art_pieces2 = [1,2,3,4]
art_pieces3 = [1,1,1,1]

print(find_balanced_subsequence(art_pieces1))
print(find_balanced_subsequence(art_pieces2))
print(find_balanced_subsequence(art_pieces3))