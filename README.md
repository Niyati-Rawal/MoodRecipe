# MoodRecipe

A Django REST API that recommends recipes based on your current mood.

## Setup

```bash
git clone <your-repo>
cd moodrecipe
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=moodrecipe
DB_USER=postgres
DB_PASSWORD=yourpassword
SPOONACULAR_API_KEY=your-key-from-spoonacular.com
```

Run migrations:
```bash
python manage.py makemigrations core
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/registration/` | Register a new user |
| POST | `/api/auth/login/` | Login, returns auth token |
| POST | `/api/checkin/` | Submit mood → get recipe suggestions |
| POST | `/api/recipes/save/` | Save a recipe to your collection |
| GET | `/api/recipes/saved/` | List saved recipes (`?mood=stressed`) |
| PATCH | `/api/recipes/saved/<id>/rate/` | Rate a saved recipe 1–5 |

## Example: Mood Check-in

**Request**
```json
POST /api/checkin/
Authorization: Token <your-token>

{
  "mood": "stressed",
  "energy": "low",
  "ingredients": "pasta, tomato, garlic",
  "notes": "long day at work"
}
```

**Response**
```json
{
  "mood_log_id": 12,
  "mood": "stressed",
  "energy": "low",
  "recipes": [
    {
      "spoonacular_id": 716429,
      "title": "Pasta with Garlic, Scallions, Cauliflower & Breadcrumbs",
      "image_url": "https://spoonacular.com/recipeImages/716429-312x231.jpg",
      "ready_in_minutes": 45,
      "servings": 2,
      "summary": "A comforting pasta dish...",
      "diets": ["dairy free", "vegan"],
      "dish_types": ["lunch", "main course"]
    }
  ]
}
```

## Mood → Recipe Mapping

| Mood | Recipe Style |
|------|-------------|
| happy | Party food, fun dishes |
| stressed | Comfort food |
| tired | Quick meals under 20 min |
| energetic | Healthy, vegetarian |
| sad | Comfort food & desserts |
| anxious | Light, healthy meals |

## Next Features to Build
- `GET /api/mood-history/` — mood logs with charts data
- `GET /api/analytics/` — mood pattern insights
- Celery task for weekly email digest
