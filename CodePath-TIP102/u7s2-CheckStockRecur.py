def check_stock(inventory, left, right, part_id):
    if right >= left:
        mid = (right + left) // 2
        if inventory[mid] == part_id:
            return True
        
        elif inventory[mid] > part_id:
            return check_stock(inventory, left, mid-1, part_id)
        else:
            return check_stock(inventory, mid+1, right, part_id)
    else:
        return False

inventory = [1, 2, 5, 12, 20]
print(check_stock([1, 2, 5, 12, 20], 0, len(inventory) - 1, 20))
print(check_stock([1, 2, 5, 12, 20], 0, len(inventory) - 1, 100))


#ZN
def check_stock2(inventory, part_id, left = 0, right = None):
    if right is None:
        right = len(inventory) - 1
                               
    if left > right: 
        return -1
    
    mid = (left + right) // 2
    if inventory[mid] == part_id:
        return mid
    if part_id < inventory[mid]:
        return check_stock2(inventory, part_id, left, mid - 1)
    else:
        return check_stock2(inventory, part_id, mid+ 1, right)
    
print(check_stock2([1, 2, 5, 12, 20], 20))
print(check_stock2([1, 2, 5, 12, 20], 100))

        
def check_stock3(inventory, part_id):
    if not inventory:
        return False
    
    mid = len(inventory) // 2
    
    if inventory[mid] == part_id:
        return True
    elif part_id < inventory[mid]: # search left
        return check_stock3(inventory[:mid], part_id)
    else:
        return check_stock3(inventory[mid+1:], part_id) #search right
                             
                             
print(check_stock3([1, 2, 5, 12, 20], 20))
print(check_stock3([1, 2, 5, 12, 20], 100))