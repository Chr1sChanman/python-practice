'''
Understand:
    Input: List of ints
    Output: A single int
    Constraints: Ints have to be positive and unique/distinct
    Edge Cases: If list is less than 3, int exceed int value
Plan:
    If list is less than 3:
        return -1
    most = max(nums)
    least = min(nums)
    iterate through the list, if not most and least:
        return int

'''


def goldilocks_approved(nums):
    if len(nums) < 3:
        return print(-1)
    most = max(nums)
    least = min(nums)
    for i in nums:
        if i is not most and i is not least:
            return print(i)

nums = [3, 2, 1, 4]
goldilocks_approved(nums)

nums = [1, 2]
goldilocks_approved(nums)

nums = [1, 2, 3]
goldilocks_approved(nums)
