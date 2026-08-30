from database.models import Nutrition


def lookup_nutrition(food_name):
    normalized_name = food_name.lower().strip().replace(' ', '_')
    food = Nutrition.query.filter_by(food_name=normalized_name).first()
    if not food:
        return None
    return {
        'food_name': food.food_name,
        'calories': food.calories,
        'protein': food.protein,
        'carbohydrates': food.carbohydrates,
        'fat': food.fat,
        'fibre': food.fibre,
        'sugar': food.sugar,
    }
