from django.urls import path
from .views import signup, user_profile

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("<str:username>/", user_profile, name="profile"),
]
