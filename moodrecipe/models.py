from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"


class MoodLog(models.Model):
    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("stressed", "Stressed"),
        ("tired", "Tired"),
        ("energetic", "Energetic"),
        ("sad", "Sad"),
        ("anxious", "Anxious"),
    ]

    ENERGY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mood_logs")
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    energy = models.CharField(max_length=10, choices=ENERGY_CHOICES)
    ingredients = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mood_logs"
        ordering = ["-logged_at"]

    def ingredients_list(self):
        return [i.strip() for i in self.ingredients.split(",") if i.strip()]


class SavedRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_recipes")
    mood_log = models.ForeignKey(MoodLog, on_delete=models.SET_NULL, null=True, blank=True)
    spoonacular_id = models.IntegerField()
    title = models.CharField(max_length=255)
    image_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    ready_in_minutes = models.IntegerField(null=True, blank=True)
    servings = models.IntegerField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_recipes"
        unique_together = ("user", "spoonacular_id")
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.title} saved by {self.user.username}"