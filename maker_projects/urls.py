from django.urls import path
from .views import (
    create_project,
    project_detail,
    edit_project,
    delete_project,
    create_ProjectFeature,
    edit_ProjectFeature,
    delete_ProjectFeature,
    complete_project,
    toggle_like,
)

app_name = "maker_projects"

urlpatterns = [
    path("", create_project, name="list"),
    path("create/", create_project, name="create"),
    path("<int:pk>/edit/", edit_project, name="edit"),
    path("<int:pk>/delete/", delete_project, name="delete"),
    path("<int:pk>/confirm_complete/", complete_project, name="confirm_complete"),
    path("<int:pk>/", project_detail, name="detail"),
    path(
        "<int:project_pk>/ProjectFeatures/create/",
        create_ProjectFeature,
        name="ProjectFeature_create",
    ),
    path(
        "ProjectFeatures/<int:pk>/ProjectFeatures/edit/",
        edit_ProjectFeature,
        name="ProjectFeature_edit",
    ),
    path(
        "ProjectFeatures/<int:pk>/ProjectFeatures/delete/",
        delete_ProjectFeature,
        name="ProjectFeature_delete",
    ),
    path("projects/<int:pk>/like/", toggle_like, name="project_like"),
]