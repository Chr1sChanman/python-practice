from collections import deque 

class TreeNode:
  def __init__(self, value, key=None, left=None, right=None):
      self.key = key
      self.val = value
      self.left = left
      self.right = right

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

# PLAN:
# for each description, check if parent exists
#   - if it exist, great
#   - else create one
# if children in exists,
#   - if exists, great
#   - else create one
# if is_left,
#   - add to parent left
#   - else, add to partent right

def build_cookie_tree(descriptions):

    if not descriptions:
        return None

    exists = {}
    children = set()

    for parent, child, is_left in descriptions:
        
        if parent not in exists:
            exists[parent] = TreeNode(parent)
        
        if child not in exists:
            exists[child] = TreeNode(child)
        
        if is_left == 1:
            exists[parent].left = exists[child]
        else:
            exists[parent].right = exists[child]
        
        children.add(child)
    
    for flavor in exists:
        if flavor not in children:
            return exists[flavor]
        '''
        if x[0] in exists:
            if x[2] == 1:
                exists[x[0]].left = exists[x[1]]
            else:
                exists[x[0]].right = exists[x[1]]
        else:
            if x[2] == 1:
                exists[x[0]] = TreeNode(x[0], x[1], None)
            else:
                exists[x[0]] = TreeNode(x[0], None, x[1])
        '''
    
    return exists[0]

descriptions1 = [
    ["Chocolate Chip", "Peanut Butter", 1],
    ["Chocolate Chip", "Oatmeal Raisin", 0],
    ["Peanut Butter", "Sugar", 1]
]

descriptions2 = [
    ["Ginger Snap", "Snickerdoodle", 0],
    ["Ginger Snap", "Shortbread", 1]
]

# Using print_tree() function included at top of page
print_tree(build_cookie_tree(descriptions1))
print_tree(build_cookie_tree(descriptions2))
