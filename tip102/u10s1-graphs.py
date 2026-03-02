"""
# def bidirectional_flights(flights):
#     n = len(flights)
#     can_reach = [[False for i in range(n)] for i in range(n)]
#     for i, destinations in enumerate(flights):
#         can_reach[i][i] = True
#         for j in destinations:
#             can_reach[i][j] = True
#     def is_reachable(i, j)
#         if can_reach[i][j] == True:
#             return True
#         if j == j:
#             can_reach[i][j] = True
#             return can_reach[i][j]
#         for n in flights[i]:
#             can_reach = is_reachable(n,j)
        
#     return can_reach

def bidirectional_flights(flights):

    for i, destinations in enumerate(flights): # 0, [1, 2] -> 1, [0]
        for j in destinations: #[1,2]
            if i not in flights[j]: #0 in flights
                return False
    return True
flights1 = [[1, 2], [0], [0, 3], [2]]
flights2 = [[1, 2], [], [0], [2]]

print(bidirectional_flights(flights1))
print(bidirectional_flights(flights2))

set({1-2},{2-1})
visited()
plan: 
function called is_reachable(i,j) checks if we can reach i from j
is_reachable(i,j):
    if i == j:
        return true
    for n in flights1[i]:
        return is_reachable(n, j)

1,2 2,1
for i in range((flights)):
    for j in range(len(flights))



simplified plan:
we create 2d matrix of destinations. can_reach[i,j] there's a flight from i to j

we have the is_reachable function to check if we can reach i from j.
0, 1, 3
can_reach[0,3] = true
can_reach[0,1] = true
can_reach[1,3] = true
"""
"""
terminals1 = [[1,2],[2,3],[4,2]]
terminals2 = [[1,2],[5,1],[1,3],[1,4]]


"""

def find_center(terminals):
    a, b = terminals[0], terminals[1]
    for node in a:
        if node in b:
            return node
        
terminals1 = [[1,2],[2,3],[4,2]]
terminals2 = [[1,2],[5,1],[1,3],[1,4]]

print(find_center(terminals1))
print(find_center(terminals2))