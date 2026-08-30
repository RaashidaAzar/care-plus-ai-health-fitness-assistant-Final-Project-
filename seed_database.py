from datetime import datetime, timedelta

from database.db import db
from database.models import FoodRecord, Nutrition
from database.models import User, Profile
from services.food_labels import FOOD_LABELS, food_key
from werkzeug.security import generate_password_hash

# Do not create the Flask application at import time.  This module is also used
# by the app startup nutrition sync, so eager creation would cause a circular
# app-initialisation path.
app = None


def _seed_app():
    global app
    if app is None:
        from app import create_app
        app = create_app()
    return app

# Nutrition entries available for manual food logging.
# All values are standardized for a 100g serving.
SEED_NUTRITION_DATA = [
    {'food_name': 'apple', 'serving_size_g': 100.0, 'calories': 52.0, 'protein': 0.3, 'carbohydrates': 13.8, 'fat': 0.2, 'fibre': 2.4, 'sugar': 10.4},
    {'food_name': 'apple_pie', 'serving_size_g': 100.0, 'calories': 237.0, 'protein': 1.9, 'carbohydrates': 34.0, 'fat': 11.0, 'fibre': 1.6, 'sugar': 18.0},
    {'food_name': 'avocado', 'serving_size_g': 100.0, 'calories': 160.0, 'protein': 2.0, 'carbohydrates': 8.5, 'fat': 14.7, 'fibre': 6.7, 'sugar': 0.7},
    {'food_name': 'banana', 'serving_size_g': 100.0, 'calories': 89.0, 'protein': 1.1, 'carbohydrates': 22.8, 'fat': 0.3, 'fibre': 2.6, 'sugar': 12.2},
    {'food_name': 'beef_curry', 'serving_size_g': 100.0, 'calories': 165.0, 'protein': 14.2, 'carbohydrates': 4.5, 'fat': 10.2, 'fibre': 1.1, 'sugar': 1.5},
    {'food_name': 'biryani', 'serving_size_g': 100.0, 'calories': 170.0, 'protein': 7.5, 'carbohydrates': 24.0, 'fat': 5.2, 'fibre': 1.2, 'sugar': 0.8},
    {'food_name': 'bread', 'serving_size_g': 100.0, 'calories': 265.0, 'protein': 9.0, 'carbohydrates': 49.0, 'fat': 3.2, 'fibre': 2.7, 'sugar': 5.0},
    {'food_name': 'broccoli', 'serving_size_g': 100.0, 'calories': 34.0, 'protein': 2.8, 'carbohydrates': 6.6, 'fat': 0.4, 'fibre': 2.6, 'sugar': 1.7},
    {'food_name': 'burger', 'serving_size_g': 100.0, 'calories': 295.0, 'protein': 15.0, 'carbohydrates': 28.0, 'fat': 14.0, 'fibre': 1.8, 'sugar': 4.5},
    {'food_name': 'butter_chicken', 'serving_size_g': 100.0, 'calories': 185.0, 'protein': 12.5, 'carbohydrates': 5.0, 'fat': 13.0, 'fibre': 0.8, 'sugar': 2.5},
    {'food_name': 'cake', 'serving_size_g': 100.0, 'calories': 371.0, 'protein': 5.3, 'carbohydrates': 53.0, 'fat': 15.0, 'fibre': 1.0, 'sugar': 34.0},
    {'food_name': 'carrot', 'serving_size_g': 100.0, 'calories': 41.0, 'protein': 0.9, 'carbohydrates': 9.6, 'fat': 0.2, 'fibre': 2.8, 'sugar': 4.7},
    {'food_name': 'chicken_curry', 'serving_size_g': 100.0, 'calories': 150.0, 'protein': 13.5, 'carbohydrates': 4.0, 'fat': 8.5, 'fibre': 1.0, 'sugar': 1.2},
    {'food_name': 'chicken_wings', 'serving_size_g': 100.0, 'calories': 203.0, 'protein': 18.3, 'carbohydrates': 0.0, 'fat': 14.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'chocolate_cake', 'serving_size_g': 100.0, 'calories': 389.0, 'protein': 4.9, 'carbohydrates': 51.0, 'fat': 19.0, 'fibre': 2.5, 'sugar': 38.0},
    {'food_name': 'coffee', 'serving_size_g': 100.0, 'calories': 2.0, 'protein': 0.1, 'carbohydrates': 0.2, 'fat': 0.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'cookie', 'serving_size_g': 100.0, 'calories': 502.0, 'protein': 5.5, 'carbohydrates': 64.0, 'fat': 24.0, 'fibre': 2.0, 'sugar': 32.0},
    {'food_name': 'cup_cakes', 'serving_size_g': 100.0, 'calories': 305.0, 'protein': 3.5, 'carbohydrates': 50.0, 'fat': 10.0, 'fibre': 0.8, 'sugar': 36.0},
    {'food_name': 'dal_makhani', 'serving_size_g': 100.0, 'calories': 140.0, 'protein': 6.0, 'carbohydrates': 15.0, 'fat': 6.5, 'fibre': 4.0, 'sugar': 1.5},
    {'food_name': 'donut', 'serving_size_g': 100.0, 'calories': 452.0, 'protein': 4.9, 'carbohydrates': 51.0, 'fat': 25.0, 'fibre': 1.7, 'sugar': 27.0},
    {'food_name': 'dosa', 'serving_size_g': 100.0, 'calories': 168.0, 'protein': 3.9, 'carbohydrates': 29.0, 'fat': 3.7, 'fibre': 1.5, 'sugar': 0.5},
    {'food_name': 'dumplings', 'serving_size_g': 100.0, 'calories': 190.0, 'protein': 7.0, 'carbohydrates': 25.0, 'fat': 6.8, 'fibre': 1.2, 'sugar': 1.0},
    {'food_name': 'egg_fried_rice', 'serving_size_g': 100.0, 'calories': 174.0, 'protein': 5.2, 'carbohydrates': 24.5, 'fat': 6.0, 'fibre': 1.0, 'sugar': 0.6},
    {'food_name': 'eggs', 'serving_size_g': 100.0, 'calories': 155.0, 'protein': 12.6, 'carbohydrates': 1.1, 'fat': 10.6, 'fibre': 0.0, 'sugar': 1.1},
    {'food_name': 'fish_and_chips', 'serving_size_g': 100.0, 'calories': 232.0, 'protein': 11.0, 'carbohydrates': 22.0, 'fat': 11.0, 'fibre': 1.8, 'sugar': 0.4},
    {'food_name': 'french_fries', 'serving_size_g': 100.0, 'calories': 312.0, 'protein': 3.4, 'carbohydrates': 41.0, 'fat': 15.0, 'fibre': 3.8, 'sugar': 0.3},
    {'food_name': 'fried_rice', 'serving_size_g': 100.0, 'calories': 163.0, 'protein': 4.1, 'carbohydrates': 25.0, 'fat': 5.0, 'fibre': 1.1, 'sugar': 0.5},
    {'food_name': 'garlic_bread', 'serving_size_g': 100.0, 'calories': 350.0, 'protein': 8.5, 'carbohydrates': 42.0, 'fat': 16.5, 'fibre': 2.1, 'sugar': 2.5},
    {'food_name': 'grilled_chicken', 'serving_size_g': 100.0, 'calories': 165.0, 'protein': 31.0, 'carbohydrates': 0.0, 'fat': 3.6, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'grilled_salmon', 'serving_size_g': 100.0, 'calories': 206.0, 'protein': 22.0, 'carbohydrates': 0.0, 'fat': 12.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'hot_dog', 'serving_size_g': 100.0, 'calories': 290.0, 'protein': 10.0, 'carbohydrates': 18.0, 'fat': 20.0, 'fibre': 0.8, 'sugar': 3.5},
    {'food_name': 'ice_cream', 'serving_size_g': 100.0, 'calories': 207.0, 'protein': 3.5, 'carbohydrates': 24.0, 'fat': 11.0, 'fibre': 0.7, 'sugar': 21.0},
    {'food_name': 'idli', 'serving_size_g': 100.0, 'calories': 132.0, 'protein': 4.5, 'carbohydrates': 27.5, 'fat': 0.4, 'fibre': 1.8, 'sugar': 0.3},
    {'food_name': 'lasagna', 'serving_size_g': 100.0, 'calories': 135.0, 'protein': 7.5, 'carbohydrates': 14.0, 'fat': 5.5, 'fibre': 1.1, 'sugar': 2.2},
    {'food_name': 'mac_and_cheese', 'serving_size_g': 100.0, 'calories': 164.0, 'protein': 6.5, 'carbohydrates': 19.5, 'fat': 6.8, 'fibre': 1.0, 'sugar': 2.0},
    {'food_name': 'momos', 'serving_size_g': 100.0, 'calories': 175.0, 'protein': 6.8, 'carbohydrates': 26.0, 'fat': 4.8, 'fibre': 1.2, 'sugar': 1.0},
    {'food_name': 'naan', 'serving_size_g': 100.0, 'calories': 310.0, 'protein': 9.0, 'carbohydrates': 52.0, 'fat': 7.2, 'fibre': 2.2, 'sugar': 3.0},
    {'food_name': 'noodles', 'serving_size_g': 100.0, 'calories': 138.0, 'protein': 4.5, 'carbohydrates': 25.0, 'fat': 2.1, 'fibre': 1.2, 'sugar': 0.8},
    {'food_name': 'oatmeal', 'serving_size_g': 100.0, 'calories': 68.0, 'protein': 2.4, 'carbohydrates': 12.0, 'fat': 1.4, 'fibre': 1.7, 'sugar': 0.5},
    {'food_name': 'omelette', 'serving_size_g': 100.0, 'calories': 154.0, 'protein': 11.0, 'carbohydrates': 0.6, 'fat': 12.0, 'fibre': 0.0, 'sugar': 0.4},
    {'food_name': 'pancake', 'serving_size_g': 100.0, 'calories': 227.0, 'protein': 6.4, 'carbohydrates': 28.0, 'fat': 10.0, 'fibre': 1.5, 'sugar': 7.0},
    {'food_name': 'paneer_butter_masala', 'serving_size_g': 100.0, 'calories': 210.0, 'protein': 7.8, 'carbohydrates': 8.0, 'fat': 16.5, 'fibre': 1.5, 'sugar': 3.0},
    {'food_name': 'pasta', 'serving_size_g': 100.0, 'calories': 131.0, 'protein': 5.0, 'carbohydrates': 25.0, 'fat': 1.1, 'fibre': 1.8, 'sugar': 0.6},
    {'food_name': 'pastry', 'serving_size_g': 100.0, 'calories': 338.0, 'protein': 4.2, 'carbohydrates': 45.0, 'fat': 16.0, 'fibre': 1.2, 'sugar': 22.0},
    {'food_name': 'pizza', 'serving_size_g': 100.0, 'calories': 266.0, 'protein': 11.0, 'carbohydrates': 33.0, 'fat': 10.0, 'fibre': 2.3, 'sugar': 3.6},
    {'food_name': 'porridge', 'serving_size_g': 100.0, 'calories': 71.0, 'protein': 2.5, 'carbohydrates': 12.0, 'fat': 1.5, 'fibre': 1.7, 'sugar': 0.5},
    {'food_name': 'ramen', 'serving_size_g': 100.0, 'calories': 142.0, 'protein': 5.5, 'carbohydrates': 20.0, 'fat': 4.5, 'fibre': 1.0, 'sugar': 1.2},
    {'food_name': 'roast_chicken', 'serving_size_g': 100.0, 'calories': 195.0, 'protein': 24.0, 'carbohydrates': 0.0, 'fat': 11.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'roti', 'serving_size_g': 100.0, 'calories': 297.0, 'protein': 11.0, 'carbohydrates': 52.0, 'fat': 3.7, 'fibre': 9.0, 'sugar': 0.5},
    {'food_name': 'salad', 'serving_size_g': 100.0, 'calories': 45.0, 'protein': 1.5, 'carbohydrates': 7.0, 'fat': 1.2, 'fibre': 2.5, 'sugar': 2.8},
    {'food_name': 'sandwich', 'serving_size_g': 100.0, 'calories': 250.0, 'protein': 10.0, 'carbohydrates': 30.0, 'fat': 9.5, 'fibre': 2.0, 'sugar': 3.0},
    {'food_name': 'samosa', 'serving_size_g': 100.0, 'calories': 262.0, 'protein': 4.5, 'carbohydrates': 32.0, 'fat': 13.0, 'fibre': 2.5, 'sugar': 1.5},
    {'food_name': 'soup', 'serving_size_g': 100.0, 'calories': 42.0, 'protein': 1.8, 'carbohydrates': 5.5, 'fat': 1.5, 'fibre': 0.8, 'sugar': 1.2},
    {'food_name': 'spaghetti', 'serving_size_g': 100.0, 'calories': 158.0, 'protein': 5.8, 'carbohydrates': 31.0, 'fat': 0.9, 'fibre': 1.8, 'sugar': 0.6},
    {'food_name': 'spring_rolls', 'serving_size_g': 100.0, 'calories': 220.0, 'protein': 4.5, 'carbohydrates': 28.0, 'fat': 10.0, 'fibre': 2.0, 'sugar': 2.0},
    {'food_name': 'steak', 'serving_size_g': 100.0, 'calories': 271.0, 'protein': 26.0, 'carbohydrates': 0.0, 'fat': 18.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'strawberry', 'serving_size_g': 100.0, 'calories': 32.0, 'protein': 0.7, 'carbohydrates': 7.7, 'fat': 0.3, 'fibre': 2.0, 'sugar': 4.9},
    {'food_name': 'sushi', 'serving_size_g': 100.0, 'calories': 143.0, 'protein': 4.5, 'carbohydrates': 28.0, 'fat': 1.5, 'fibre': 0.5, 'sugar': 2.5},
    {'food_name': 'tacos', 'serving_size_g': 100.0, 'calories': 226.0, 'protein': 9.0, 'carbohydrates': 20.0, 'fat': 12.0, 'fibre': 3.0, 'sugar': 1.2},
    {'food_name': 'tea', 'serving_size_g': 100.0, 'calories': 1.0, 'protein': 0.0, 'carbohydrates': 0.2, 'fat': 0.0, 'fibre': 0.0, 'sugar': 0.0},
    {'food_name': 'toast', 'serving_size_g': 100.0, 'calories': 293.0, 'protein': 10.0, 'carbohydrates': 54.0, 'fat': 3.5, 'fibre': 3.0, 'sugar': 5.5},
    {'food_name': 'tomato_soup', 'serving_size_g': 100.0, 'calories': 30.0, 'protein': 0.8, 'carbohydrates': 6.0, 'fat': 0.5, 'fibre': 0.7, 'sugar': 3.5},
    {'food_name': 'tuna_salad', 'serving_size_g': 100.0, 'calories': 187.0, 'protein': 16.0, 'carbohydrates': 3.0, 'fat': 12.0, 'fibre': 0.5, 'sugar': 1.0},
    {'food_name': 'vegetable_curry', 'serving_size_g': 100.0, 'calories': 95.0, 'protein': 2.5, 'carbohydrates': 11.0, 'fat': 4.5, 'fibre': 3.0, 'sugar': 3.5},
    {'food_name': 'waffle', 'serving_size_g': 100.0, 'calories': 291.0, 'protein': 7.9, 'carbohydrates': 41.0, 'fat': 11.0, 'fibre': 2.2, 'sugar': 14.0},
    {'food_name': 'yogurt', 'serving_size_g': 100.0, 'calories': 59.0, 'protein': 3.5, 'carbohydrates': 4.7, 'fat': 3.3, 'fibre': 0.0, 'sugar': 4.7},
]

DEMO_USERS = [
    {'username': 'Anne',  'age': 52, 'gender': 'female', 'registered_days_ago': 90},
    {'username': 'James', 'age': 62, 'gender': 'male',   'registered_days_ago': 180},
    {'username': 'Peter', 'age': 43, 'gender': 'male',   'registered_days_ago': 14},
]

# Nutrition is expressed per 100 g.  These entries cover recognition labels that
# do not already have a matching record in SEED_NUTRITION_DATA.
def _nutrition(calories, protein, carbohydrates, fat, fibre, sugar):
    return {'calories': calories, 'protein': protein, 'carbohydrates': carbohydrates,
            'fat': fat, 'fibre': fibre, 'sugar': sugar}


MODEL_ONLY_NUTRITION_DATA = {
    'bean': _nutrition(127, 8.7, 22.8, 0.5, 6.4, 0.3), 'beet_salad': _nutrition(74, 2.1, 10.5, 3.1, 2.8, 6.1),
    'bitter_gourd': _nutrition(17, 1.0, 3.7, 0.2, 2.8, 1.9), 'black_berry': _nutrition(43, 1.4, 9.6, 0.5, 5.3, 4.9),
    'breakfast_burrito': _nutrition(206, 9.2, 22.0, 9.1, 2.1, 1.5), 'cabbage': _nutrition(25, 1.3, 5.8, 0.1, 2.5, 3.2),
    'caesar_salad': _nutrition(190, 7.0, 8.0, 15.0, 2.0, 2.0), 'caprese_salad': _nutrition(143, 8.1, 4.0, 10.5, 1.2, 2.4),
    'capsicum': _nutrition(31, 1.0, 6.0, 0.3, 2.1, 4.2), 'cauliflower': _nutrition(25, 1.9, 5.0, 0.3, 2.0, 1.9),
    'cheesecake': _nutrition(321, 5.5, 25.5, 22.5, 0.4, 20.0), 'churros': _nutrition(447, 5.0, 57.0, 23.0, 2.0, 22.0),
    'club_sandwich': _nutrition(240, 12.0, 21.0, 12.5, 1.8, 3.0), 'deviled_eggs': _nutrition(201, 10.8, 1.5, 16.5, 0.0, 1.0),
    'fig': _nutrition(74, 0.8, 19.2, 0.3, 2.9, 16.3), 'french_toast': _nutrition(229, 8.0, 29.0, 9.0, 1.5, 8.0),
    'frozen_yogurt': _nutrition(159, 4.0, 28.0, 3.0, 0.0, 24.0), 'greek_salad': _nutrition(101, 3.4, 5.1, 7.5, 1.8, 2.8),
    'guacamole': _nutrition(160, 2.0, 8.5, 14.7, 6.7, 0.7), 'guava': _nutrition(68, 2.6, 14.3, 1.0, 5.4, 8.9),
    'hoppers': _nutrition(180, 3.0, 35.0, 3.5, 1.2, 0.8), 'kottu': _nutrition(193, 7.0, 24.0, 8.0, 2.5, 1.5),
    'milk_rice': _nutrition(174, 3.6, 30.0, 4.3, 0.5, 1.8), 'nachos': _nutrition(343, 6.5, 45.0, 16.0, 4.0, 1.5),
    'onion_rings': _nutrition(332, 4.0, 43.0, 17.0, 2.5, 4.0), 'papaya': _nutrition(43, 0.5, 10.8, 0.3, 1.7, 7.8),
    'pittu': _nutrition(190, 3.2, 38.0, 2.5, 3.5, 1.0), 'potato': _nutrition(77, 2.0, 17.0, 0.1, 2.2, 0.8),
    'pumpkin': _nutrition(26, 1.0, 6.5, 0.1, 0.5, 2.8), 'rambutan': _nutrition(82, 0.7, 20.9, 0.2, 0.9, 13.0),
    'rice_and_curry': _nutrition(145, 4.0, 23.0, 4.5, 2.5, 1.5), 'seaweed_salad': _nutrition(90, 2.0, 12.0, 4.0, 2.0, 5.0),
    'spaghetti_carbonara': _nutrition(280, 11.0, 27.0, 14.0, 1.5, 1.5), 'string_hoppers': _nutrition(154, 2.8, 32.0, 0.7, 1.0, 0.3),
    'tiramisu': _nutrition(283, 4.8, 31.0, 15.0, 0.5, 22.0), 'tomato': _nutrition(18, 0.9, 3.9, 0.2, 1.2, 2.6),
    'watermelon': _nutrition(30, 0.6, 7.6, 0.2, 0.4, 6.2),
}

MODEL_FOOD_ALIASES = {
    'biriyani': 'biryani', 'cup_cakes': 'cup_cakes', 'donuts': 'donut',
    'hamburger': 'burger', 'macaroni_and_cheese': 'mac_and_cheese',
    'oats': 'oatmeal', 'pancakes': 'pancake', 'waffles': 'waffle',
}

# Labels already covered by the main nutrition data must retain those values.
# The old implementation appended a 150 kcal placeholder for every model label,
# which overwrote entries such as french_fries and ice_cream during seeding.
_SEED_NUTRITION_BY_NAME = {item['food_name']: item for item in SEED_NUTRITION_DATA}


def _nutrition_values(item):
    return {field: item[field] for field in ('calories', 'protein', 'carbohydrates', 'fat', 'fibre', 'sugar')}


def _model_nutrition_for(label):
    key = food_key(label)
    if key in MODEL_ONLY_NUTRITION_DATA:
        return MODEL_ONLY_NUTRITION_DATA[key]
    return _nutrition_values(_SEED_NUTRITION_BY_NAME[MODEL_FOOD_ALIASES.get(key, key)])


MODEL_FOOD_NUTRITION_DATA = [
    {
        'food_name': food_key(label),
        'serving_size_g': 100.0,
        **_model_nutrition_for(label),
    }
    for label in FOOD_LABELS
]


def seed_nutrition(target_app=None):
    with (target_app or _seed_app()).app_context():
        db.create_all()
        added_count = 0
        updated_count = 0
        for item in SEED_NUTRITION_DATA + MODEL_FOOD_NUTRITION_DATA:
            existing = Nutrition.query.filter_by(food_name=item['food_name']).first()
            if existing:
                existing.serving_size_g = item.get('serving_size_g', 100.0)
                existing.calories = item['calories']
                existing.protein = item['protein']
                existing.carbohydrates = item['carbohydrates']
                existing.fat = item['fat']
                existing.fibre = item['fibre']
                existing.sugar = item['sugar']
                updated_count += 1
            else:
                db.session.add(Nutrition(**item))
                added_count += 1

        # Food history stores a snapshot of nutrition at save time. Refresh
        # snapshots linked to a nutrition row so entries written with the old
        # generic placeholder are corrected as well.
        db.session.flush()
        for record in FoodRecord.query.filter(FoodRecord.nutrition_id.isnot(None)).all():
            nutrition = record.nutrition
            if not nutrition:
                continue
            multiplier = (record.serving_amount_g or 100.0) / 100.0
            record.calories = round(nutrition.calories * multiplier, 1)
            record.protein = round(nutrition.protein * multiplier, 1)
            record.carbohydrates = round(nutrition.carbohydrates * multiplier, 1)
            record.fat = round(nutrition.fat * multiplier, 1)
            record.fibre = round(nutrition.fibre * multiplier, 1)
            record.sugar = round(nutrition.sugar * multiplier, 1)
        db.session.commit()
        print(f"Database nutrition seeding complete: {added_count} added, {updated_count} updated (Total: {len(SEED_NUTRITION_DATA)} entries).")


def seed_demo_users(target_app=None):
    with (target_app or _seed_app()).app_context():
        db.create_all()
        now = datetime.utcnow()
        for item in DEMO_USERS:
            user = User.query.filter_by(username=item['username']).first()
            if user is None:
                user = User(
                    username=item['username'],
                    email=f"{item['username'].lower()}@gmail.com",
                    password_hash=generate_password_hash('12345'),
                    created_at=now - timedelta(days=item['registered_days_ago']),
                )
                db.session.add(user)
                db.session.flush()
            else:
                user.email = f"{item['username'].lower()}@gmail.com"
                user.password_hash = generate_password_hash('12345')
                user.created_at = now - timedelta(days=item['registered_days_ago'])

            if user.profile is None:
                db.session.add(Profile(
                    user_id=user.id,
                    full_name=item['username'],
                    age=item['age'],
                    birth_year=datetime.utcnow().year - item['age'],
                    gender=item['gender'],
                    height_cm=170.0,
                    weight_kg=70.0,
                    activity_level='moderate',
                    theme_preference='light',
                    bmi_onboarding_completed=True,
                ))
            else:
                user.profile.full_name = item['username']
                user.profile.age = item['age']
                user.profile.birth_year = datetime.utcnow().year - item['age']
                user.profile.gender = item['gender']
                user.profile.theme_preference = 'light'
                user.profile.bmi_onboarding_completed = True
        db.session.commit()
        print('Demo users seeded: Peter, James, Anne.')


if __name__ == '__main__':
    seed_nutrition()
    seed_demo_users()
