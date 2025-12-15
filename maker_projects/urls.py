from django.urls import path
from .views import maker_projects

app_name = "projects"

urlpatterns = [
    path("", maker_projects, name="list"),
]
