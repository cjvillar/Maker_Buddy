from django.urls import path,include
from .views import signup, user_profile, edit_profile, delete_profile

app_name = "accounts"

urlpatterns = [
    path("signup/", signup, name="signup"),
    # path("signup/",CustomSignupView.as_view(), name="signup"),
    path('accounts/', include('allauth.urls')),
    path("edit/", edit_profile, name="edit_profile"),
    path("delete/", delete_profile, name="delete_profile"),
    path("<str:username>/", user_profile, name="profile"),
]
