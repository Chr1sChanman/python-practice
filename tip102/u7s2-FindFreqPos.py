def find_frequency_positions(transmissions, target_code):
    def search(x): 
        left = 0
        right = len(transmissions) - 1
        while left < right:
            mid = (left + right) // 2
            if transmissions[mid] < x:
                left = mid + 1
            else:
                right = mid
        return left
    
    left = search(target_code)
    right = search(target_code+1) - 1
    
    if left <= right:
        return tuple([left, right])
    return tuple([-1, -1])
                 
print(find_frequency_positions([5,7,7,8,8,10], 8))
print(find_frequency_positions([5,7,7,8,8,10], 6))
print(find_frequency_positions([], 0))
