from typing import List
"""
Problem: 605. Can Place Flowers
Difficulty: Easy
URL: https://leetcode.com/problems/can-place-flowers/

Description:
You have a long flowerbed in which some of the plots are planted, and some are not. 
However, flowers cannot be planted in adjacent plots. Given an integer array flowerbed 
containing 0's and 1's, where 0 means empty and 1 means not empty, and an integer n, 
return true if n new flowers can be planted in the flowerbed without violating the 
no-adjacent-flowers rule.

Examples:
Input: flowerbed = [1,0,0,0,1], n = 1
Output: true

Input: flowerbed = [1,0,0,0,1], n = 2
Output: false

Constraints:
- 1 <= flowerbed.length <= 2 * 104
- flowerbed[i] is 0 or 1.
- There are no two adjacent flowers in flowerbed.
- 0 <= n <= flowerbed.length
"""

class Solution:
    def canPlaceFlowers(self, flowerbed: List[int], n: int) -> bool:
        if n == 0:
            return True
        for i in range(len(flowerbed)):
            if flowerbed[i] == 0 and (i == 0 or flowerbed[i-1] == 0) and (i == len(flowerbed)-1 or flowerbed[i+1] == 0):
                flowerbed[i] = 1
                n -= 1
                if n == 0:
                    return True
        return False
        pass

# Test cases
def test_can_place_flowers():
    solution = Solution()
    
    # Test case 1
    assert solution.canPlaceFlowers([1,0,0,0,1], 1) == True
    
    # Test case 2
    assert solution.canPlaceFlowers([1,0,0,0,1], 2) == False
    
    # Edge cases
    assert solution.canPlaceFlowers([0], 1) == True
    assert solution.canPlaceFlowers([1], 0) == True
    assert solution.canPlaceFlowers([0,0,1,0,0], 1) == True
    
    print("All test cases passed!")

if __name__ == "__main__":
    test_can_place_flowers()