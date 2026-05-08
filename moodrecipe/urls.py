from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("", views.index, name="index"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # JSON API (session-auth, no tokens needed)
    path("api/checkin/", views.checkin, name="checkin"),
    path("api/recipes/save/", views.save_recipe, name="save-recipe"),
    path("api/recipes/saved/", views.saved_recipes, name="saved-recipes"),
    path("api/recipes/<int:pk>/rate/", views.rate_recipe, name="rate-recipe"),
]