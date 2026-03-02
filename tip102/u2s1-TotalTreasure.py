'''
Understand:
    I: {String keys, int values}
    O: int
    C: N/A
    E: Empty dictionary, non numerical values
Plan: 
    Total count/sum
    For i in dictionary:
        result = dictionary.value
    return total
Implement:
'''

def total_treasures(treasure_map):
    res = 0
    for i in treasure_map.values():
        res += i
    return res

treasure_map1 = {
    "Cove": 3,
    "Beach": 7,
    "Forest": 5
}

treasure_map2 = {
    "Shipwreck": 10,
    "Cave": 20,
    "Lagoon": 15,
    "Island Peak": 5
}

print(total_treasures(treasure_map1)) 
print(total_treasures(treasure_map2)) 