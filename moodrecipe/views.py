import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import SignUpForm, LoginForm
from .models import MoodLog, SavedRecipe
from .services import get_recipes_for_mood, SpoonacularError


# ── Pages ────────────────────────────────────────────────────────────────────

def index(request):
    """Main page — renders the single-page app shell."""
    return render(request, "index.html", {
        "user": request.user,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


# ── API endpoints (JSON, session auth) ────────────────────────────────────────

@login_required
@require_POST
def checkin(request):
    """POST /api/checkin/ — save mood log, return recipe suggestions."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    mood = data.get("mood", "")
    energy = data.get("energy", "")
    ingredients = data.get("ingredients", "")

    valid_moods = [c[0] for c in MoodLog.MOOD_CHOICES]
    if mood not in valid_moods:
        return JsonResponse({"error": f"Invalid mood. Choose from: {', '.join(valid_moods)}"}, status=400)

    mood_log = MoodLog.objects.create(
        user=request.user,
        mood=mood,
        energy=energy,
        ingredients=ingredients,
    )

    try:
        recipes = get_recipes_for_mood(mood=mood, ingredients=mood_log.ingredients_list())
    except SpoonacularError as e:
        return JsonResponse({
            "mood_log_id": mood_log.id,
            "mood": mood,
            "energy": energy,
            "recipes": [],
            "warning": str(e),
        })

    return JsonResponse({
        "mood_log_id": mood_log.id,
        "mood": mood,
        "energy": energy,
        "recipes": recipes,
    })


@login_required
@require_POST
def save_recipe(request):
    """POST /api/recipes/save/"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    mood_log_id = data.get("mood_log_id")
    mood_log = None
    if mood_log_id:
        try:
            mood_log = MoodLog.objects.get(pk=mood_log_id, user=request.user)
        except MoodLog.DoesNotExist:
            pass

    _, created = SavedRecipe.objects.get_or_create(
        user=request.user,
        spoonacular_id=data.get("spoonacular_id"),
        defaults={
            "mood_log": mood_log,
            "title": data.get("title", ""),
            "image_url": data.get("image_url", ""),
            "source_url": data.get("source_url", ""),
            "ready_in_minutes": data.get("ready_in_minutes"),
            "servings": data.get("servings"),
        },
    )

    if not created:
        return JsonResponse({"detail": "Already saved."}, status=409)

    return JsonResponse({"detail": "Saved!"}, status=201)


@login_required
def saved_recipes(request):
    """GET /api/recipes/saved/"""
    qs = SavedRecipe.objects.filter(user=request.user)
    mood = request.GET.get("mood")
    if mood:
        qs = qs.filter(mood_log__mood=mood)

    data = [
        {
            "id": r.id,
            "spoonacular_id": r.spoonacular_id,
            "title": r.title,
            "image_url": r.image_url,
            "source_url": r.source_url,
            "ready_in_minutes": r.ready_in_minutes,
            "servings": r.servings,
            "rating": r.rating,
            "saved_at": r.saved_at.isoformat(),
        }
        for r in qs
    ]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def rate_recipe(request, pk):
    """POST /api/recipes/<pk>/rate/"""
    recipe = get_object_or_404(SavedRecipe, pk=pk, user=request.user)
    try:
        data = json.loads(request.body)
        rating = int(data.get("rating", 0))
        assert 1 <= rating <= 5
    except (ValueError, AssertionError, json.JSONDecodeError):
        return JsonResponse({"error": "Rating must be 1–5"}, status=400)

    recipe.rating = rating
    recipe.save(update_fields=["rating"])
    return JsonResponse({"id": recipe.id, "rating": recipe.rating})