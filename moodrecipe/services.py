import requests

# TheMealDB - completely free, no API key needed
BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Mood to search keywords mapping
MOOD_QUERIES = {
    "happy":    ["pasta", "pizza", "burger", "cake"],
    "stressed": ["biryani", "curry", "lasagna", "mac cheese"],
    "tired":    ["soup", "sandwich", "eggs", "toast"],
    "energetic":["salad", "chicken", "fish", "quinoa"],
    "sad":      ["chocolate", "ice cream", "brownie", "pancakes"],
    "anxious":  ["oatmeal", "smoothie", "rice", "lentil"],
}


def get_recipes_for_mood(mood: str, ingredients: list = None, number: int = 6) -> list:
    """
    Fetch recipes from TheMealDB based on mood.
    Completely free - no API key required.
    """
    keywords = MOOD_QUERIES.get(mood, ["chicken", "pasta", "soup"])

    recipes = []
    seen_ids = set()

    # If user gave ingredients, search those first
    search_terms = []
    if ingredients:
        search_terms = ingredients[:3]
    search_terms += keywords

    for term in search_terms:
        if len(recipes) >= number:
            break
        try:
            response = requests.get(
                f"{BASE_URL}/search.php",
                params={"s": term},
                timeout=8
            )
            response.raise_for_status()
            meals = response.json().get("meals") or []
            for meal in meals:
                if len(recipes) >= number:
                    break
                if meal["idMeal"] not in seen_ids:
                    seen_ids.add(meal["idMeal"])
                    recipes.append(_parse_meal(meal))
        except Exception:
            continue

    # If still not enough, fetch random ones to fill
    while len(recipes) < number:
        try:
            response = requests.get(f"{BASE_URL}/random.php", timeout=8)
            response.raise_for_status()
            meals = response.json().get("meals") or []
            if meals and meals[0]["idMeal"] not in seen_ids:
                seen_ids.add(meals[0]["idMeal"])
                recipes.append(_parse_meal(meals[0]))
        except Exception:
            break

    return recipes[:number]


def _parse_meal(meal: dict) -> dict:
    """Convert TheMealDB meal format to our app's format."""
    # Collect ingredients (MealDB has ingredient1..ingredient20)
    ingredients = []
    for i in range(1, 21):
        ing = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if ing and ing.strip():
            ingredients.append(f"{measure.strip()} {ing.strip()}".strip())

    summary = meal.get("strInstructions", "")
    summary = summary[:300] + "..." if len(summary) > 300 else summary

    return {
        "spoonacular_id": int(meal["idMeal"]),  # reusing same field name for compatibility
        "title": meal.get("strMeal", ""),
        "image_url": meal.get("strMealThumb", ""),
        "source_url": meal.get("strSource") or f"https://www.themealdb.com/meal/{meal['idMeal']}",
        "ready_in_minutes": None,
        "servings": None,
        "summary": summary,
        "diets": [meal["strCategory"]] if meal.get("strCategory") else [],
        "dish_types": [meal["strArea"]] if meal.get("strArea") else [],
    }


class SpoonacularError(Exception):
    pass