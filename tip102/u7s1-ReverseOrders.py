def reverse_orders(orders):
    if isinstance(orders, str):
        orders = orders.split()
    if len(orders) <= 1:
        return orders
    return reverse_orders(orders[1:]) + [orders[0]]

print(' '.join(reverse_orders("Bagel Sandwich Coffee")))