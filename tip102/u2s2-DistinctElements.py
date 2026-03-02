''''
Understand: 
    Input: List of strings
    Output: 2D array 
    Constraints: N/A
    Edge Cases: Obvious
Plan:
'''

from collections import Counter

def organize_exhibition(collection):
    c = Counter(collection)
    res = []

    while any(c.values()):
        temp = []
        for key in list(c.keys()):
            if c[key] > 0:
                temp.append(key)
                c[key] -= 1
        res.append(temp)
    return res
    


collection1 = ["O'Keefe", "Kahlo", "Picasso", "O'Keefe", "Warhol", 
              "Kahlo", "O'Keefe"]
collection2 = ["Kusama", "Monet", "Ofili", "Banksy"]

print(organize_exhibition(collection1))
print(organize_exhibition(collection2))