from django.urls import path
from .views import create_project, project_detail, edit_project, delete_project

app_name = "maker_projects"

urlpatterns = [
    path("", create_project, name="list"),
    path("create/", create_project, name="create"),
    path("<int:pk>/edit/", edit_project, name="edit"),
    path("<int:pk>/delete/", delete_project, name="delete"),
    path("<int:pk>/", project_detail, name="detail"),
]
