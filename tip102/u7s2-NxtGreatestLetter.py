def next_greatest_letter(letters, target):
    left = 0
    right = len(letters) - 1
    
    if target >= letters[-1]:
        return letters[0]
    
    while left <= right:
        mid = (left + right) //2
        if letters[mid] <= target:
            left = mid + 1
        else:
            right = mid - 1
    return letters[left]

letters = ['a', 'a', 'b', 'c', 'c', 'c', 'e', 'h', 'w']

print(next_greatest_letter(letters, 'a'))
print(next_greatest_letter(letters, 'd'))
print(next_greatest_letter(letters, 'y'))