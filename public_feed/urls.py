from django.urls import path
from .views import public_feed

app_name = "public_feed"

urlpatterns = [
    path("", public_feed, name="home"),
]
