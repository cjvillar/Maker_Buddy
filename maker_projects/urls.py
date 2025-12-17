from django.urls import path
from .views import create_project

app_name = "maker_projects"

urlpatterns = [
    path("", create_project, name="list"),
    path("create/", create_project, name="create"),
]
