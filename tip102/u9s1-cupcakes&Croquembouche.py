from collections import deque 

# Tree Node class
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.val = value
        self.left = left
        self.right = right

def print_tree(root):
    if not root:
        return "Empty"
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)
    while result and result[-1] is None:
        result.pop()
    print(result)

def build_tree(values):
  if not values:
      return None

  def get_key_value(item):
      if isinstance(item, tuple):
          return item[0], item[1]
      else:
          return None, item

  key, value = get_key_value(values[0])
  root = TreeNode(value, key)
  queue = deque([root])
  index = 1

  while queue:
      node = queue.popleft()
      if index < len(values) and values[index] is not None:
          left_key, left_value = get_key_value(values[index])
          node.left = TreeNode(left_value, left_key)
          queue.append(node.left)
      index += 1
      if index < len(values) and values[index] is not None:
          right_key, right_value = get_key_value(values[index])
          node.right = TreeNode(right_value, right_key)
          queue.append(node.right)
      index += 1

  return root
'''
class Puff():
     def __init__(self, flavor, left=None, right=None):
        self.val = flavor
        self.left = left
        self.right = right

def listify_design(design):
    if not design:
        return []
    
    res = []
    q = [design]
    while q:
        curr_level = [node.val for node in q]
        res.append(curr_level)
        
        temp = []
        for node in q:
            if node.left:
                temp.append(node.left)
            if node.right:
                temp.append(node.right)
        
        q = temp
    return res

croquembouche = Puff("Vanilla", 
                    Puff("Chocolate", Puff("Vanilla"), Puff("Matcha")), 
                    Puff("Strawberry"))
print(listify_design(croquembouche))

lst= []
q=[Vanilla]
lst.append(q)
temp = [Chocolate, Strawberry]
q= temp
[[Vanilla],[chocolate, Strawberry], [ Vanilla, Matcha]]
            Vanilla
           /       \
      Chocolate   Strawberry
      /     \
  Vanilla   Matcha  


class TreeNode():
     def __init__(self, flavor, left=None, right=None):
        self.val = flavor
        self.left = left
        self.right = right

def zigzag_icing_order(cupcakes):
    if not cupcakes:
        return []
    
    res = []
    q = [cupcakes]

    # 0 = Right; 1 = Left
    dir = 0

    while q:
        curr_level = [node.val for node in q]
        if dir == 0:
            res.append(curr_level)
            dir = 1
        else:
            res.append(curr_level[::-1])
            dir = 0
        
        temp = []
        for node in q:
            if node.left:
                temp.append(node.left)
            if node.right:
                temp.append(node.right)
        
        q = temp
    return res

"""
            Chocolate
           /         \
        Vanilla       Lemon
       /              /    \
    Strawberry   Hazelnut   Red Velvet   
"""

# Using build_tree() function included at top of page
flavors = ["Chocolate", "Vanilla", "Lemon", "Strawberry", None, "Hazelnut", "Red Velvet"]
cupcakes = build_tree(flavors)
print(zigzag_icing_order(cupcakes))
'''

def helper_larger(node, sum_right):
    if not node:
        return sum_right
    node.val = node.val + helper_larger(node.right, sum_right)
    return helper_larger(node.left, node.val )


'''
This version works, we don't handle carrying the cumulative sum of node values properly
We are adding the left subtrees values (like 5) to the parent (6) which is why our output before was:
[51, 159, 21, 159, 107, 26, 15, None, None, None, 54, None, None, None, 8]

Shai: Yep yep. Just like I Just pased.

def helper_larger(node, curr_sum):
    if not node:
        return curr_sum
    
    curr_sum = helper_larger(node.right, curr_sum)

    node.val += curr_sum
    curr_sum = node.val

    return helper_larger(node.left, curr_sum)
'''

def larger_order_tree(orders):
    helper_larger(orders, 0)
    return orders
    



"""
         4 
       /   \
      /     \
     1       6 
    / \     / \
   0   2   5   7 
        \       \
         3       8 


sum_right(node):
    if leaf:
        return node.val
    node.val += sum_right
    return node.val + sum(node.left)
Expected output [30,36,21,36,35,26,15,None,None,None,33,None,None,None,8]
"""
# using build_tree() function included at top of page
order_sizes = [4,1,6,0,2,5,7,None,None,None,3,None,None,None,8]
orders = build_tree(order_sizes)

# using print_tree() function included at top of page
print_tree(larger_order_tree(orders))