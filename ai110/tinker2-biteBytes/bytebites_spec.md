Client Feature Request
We need to build the backend logic for the ByteBites app. The system needs to manage our customers, tracking their names and their past purchase history so the system can verify they are real users.

These customers need to browse specific food items (like a "Spicy Burger" or "Large Soda"), so we must track the name, price, category, and popularity rating for every item we sell.

We also need a way to manage the full collection of items — a digital list that holds all items and lets us filter by category such as "Drinks" or "Desserts".

Finally, when a user picks items, we need to group them into a single transaction. This transaction object should store the selected items and compute the total cost.

# Candidate Classes
1. Customer
Attributes (explicit): name, purchase history
Behavior (explicit): verify they are real users
Relationships: linked to Transaction (through "past purchase history" / "when a user picks items")
2. Item
Attributes (explicit): name, price, category, popularity rating
Relationships: belongs to a Category; is contained in a Transaction
3. Transaction
Attributes (explicit): selected items (a collection of Item), total cost
Behavior (explicit): compute the total cost
Relationships: aggregates multiple Item objects; associated with a Customer
4. Category
Attributes (implied): name (e.g., "Drinks", "Desserts")
Behavior (implied from context): used to filter items — the spec says "a digital list that holds all items and lets us filter by category"
Relationships: groups multiple Item objects