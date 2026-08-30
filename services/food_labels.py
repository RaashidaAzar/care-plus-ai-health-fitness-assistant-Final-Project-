FOOD_LABELS = [
    'Apple', 'Banana', 'Bean', 'Beet Salad', 'Biriyani', 'Bitter Gourd',
    'Black Berry', 'Breakfast Burrito', 'Broccoli', 'Cabbage', 'Caesar Salad',
    'Caprese Salad', 'Capsicum', 'Carrot', 'Cauliflower', 'Cheesecake',
    'Chicken Curry', 'Chicken Wings', 'Chocolate Cake', 'Churros',
    'Club Sandwich', 'Cup Cakes', 'Deviled Eggs', 'Donuts', 'Dumplings',
    'Fig', 'Fish And Chips', 'French Fries', 'French Toast', 'Fried Rice',
    'Frozen Yogurt', 'Greek Salad', 'Guacamole', 'Guava', 'Hamburger',
    'Hoppers', 'Ice Cream', 'Kottu', 'Lasagna', 'Macaroni And Cheese',
    'Milk Rice', 'Nachos', 'Oats', 'Omelette', 'Onion Rings', 'Pancakes',
    'Papaya', 'Pittu', 'Pizza', 'Potato', 'Pumpkin', 'Rambutan', 'Ramen',
    'Rice And Curry', 'Samosa', 'Seaweed Salad', 'Spaghetti Carbonara',
    'Spring Rolls', 'Steak', 'Strawberry', 'String Hoppers', 'Sushi',
    'Tiramisu', 'Tomato', 'Waffles', 'Watermelon'
]

EXPECTED_CLASS_COUNT = 66

if len(FOOD_LABELS) != EXPECTED_CLASS_COUNT:
    raise ValueError(f'Food label mapping must contain {EXPECTED_CLASS_COUNT} classes.')


def food_key(label):
    return label.lower().replace(' ', '_')