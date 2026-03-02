'''
U:
I - plant collection in a binary search tree (BST) where each node has a key and a val. The val contains the plant name, and the key is an integer representing the plant's rarity. 
Plants are organized in the BST by their key.
O - array of plant nodes as tuples in the form (key, val) sorted from least to most rare. 
C - N/A
E - No leaf or subtree
P:
I:
'''
from collections import deque 
class TreeNode():
     def __init__(self, value, left=None, right=None):
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

''''

def sort_plants(collection):
    lst = []
    get_plant(collection, lst)
    return lst

    
def get_plant(node, lst):
    if not node:
        return
    get_plant(node.left, lst)
    lst.append((node.key, node.val))
    get_plant(node.right, lst)

"""
         (3, "Monstera")
        /               \
   (1, "Pothos")     (5, "Witchcraft Orchid")
        \                 /
  (2, "Spider Plant")   (4, "Hoya Motoskei")
"""

# Using build_tree() function at the top of page
values = [(3, "Monstera"), (1, "Pothos"), (5, "Witchcraft Orchid"), None, (2, "Spider Plant"), (4, "Hoya Motoskei")]
collection = build_tree(values)

print(sort_plants(collection))

if root is None: return False
if name is val: return true 
if name is less, go left find_flower(inventory.left, name):
otherwise go right find_flower(inventory.right, name):


'''


'''
def find_flower(inventory, name):
    if inventory is None:
        return False
    
    if name == inventory.val:
        return True

    elif name < inventory.val:
        return find_flower(inventory.left, name)

    else:
        return find_flower(inventory.right, name)
        
        
    

"""
         Rose
        /    \
      Lilac   Tulip
     /  \       \
  Daisy  Lily  Violet
"""

# using build_tree() function at top of page
values = ["Rose", "Lilac", "Tulip", "Daisy", "Lily", None, "Violet"]
garden = build_tree(values)

print(find_flower(garden, "Lilac"))  
print(find_flower(garden, "Sunflower")) 
'''

'''
P: 
if node is leaf, add to left or right.
if name is less, go left
otherwise go right 

'''

'''
def add_plant(collection, name):
    add(collection, name)
    return collection
    
def add(collection, name):
    if collection.left is None and collection.right is None:
        if name < collection.val:
            collection.left = TreeNode(name)
        else:
            collection.right = TreeNode(name)
        return
    if name < collection.val:
        add_plant(collection.left, name)
    else:
        add_plant(collection.right, name)


    

"""
            Money Tree
        /              \
Fiddle Leaf Fig    Snake Plant
"""

# Using build_tree() function at the top of page
values = ["Money Tree", "Fiddle Leaf Fig", "Snake Plant"]
collection = build_tree(values)

# Using print_tree() function at the top of page
print_tree(add_plant(collection, "Aloe"))

'''

def find_plant(collection, name):
    if collection is None:
        return None
    
    if name == collection.val:
        return collection

    elif name < collection.val:
        return find_plant(collection.left, name)

    else:
        return find_plant(collection.right, name)

def get_successor(node, parent, dir): #this has a bug that needs fixing
    if node.left is None and node.right is None:
        #before removing, you need to handle it's children
        if dir == 'left':
            if node.left
                parent.left = node.left
            else:
                parent.left = node.right 
        else:
            if node.left
                parent.right = node.left
            else:
                parent.right = node.right
        return node.val
    get_successor(node.right, node, 'right')

def remove_plant(collection, name):
    plant_to_remove = find_plant(collection,name)
    if plant_to_remove.left and plant_to_remove.right:
        plant_to_remove.val = get_successor(plant_to_remove.left, plant_to_remove,  'left')
    elif plant_to_remove.left:
        plant_to_remove.val = plant_to_remove.left.val
        plant_to_remove.left = None
    else:
        plant_to_remove.val = plant_to_remove.right.val
        plant_to_remove.right = None
    return collection



"""
              Money Tree
             /         \
           Hoya        Pilea
              \        /   \
             Ivy    Orchid  ZZ Plant
"""

# Using build_tree() function at the top of page
values = ["Money Tree", "Hoya", "Pilea", None, "Ivy", "Orchid", "ZZ Plant"]
collection = build_tree(values)

# Using print_tree() function at the top of page
print_tree(remove_plant(collection, "Pilea"))