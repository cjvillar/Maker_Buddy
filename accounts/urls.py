from django.urls import path
from .views import signup, user_profile, edit_profile

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    path('edit/', edit_profile, name='edit_profile'),
    path("<str:username>/", user_profile, name="profile"),
   
]
