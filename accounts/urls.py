from django.urls import path
from .views import user_profile

app_name = "accounts"

urlpatterns = [
    path("<str:username>/", user_profile, name="profile"),
]
