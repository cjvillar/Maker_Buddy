from django.urls import path
from .views import (
    CreateProjectWizard,
    project_detail,
    edit_project,
    delete_project,
    add_build_step,
    edit_build_step,
    complete_project,
    toggle_like,
)

app_name = "maker_projects"

urlpatterns = [
    path(
        "create/",
        CreateProjectWizard.as_view(
            template_name="maker_projects/create_project_wizard.html"
        ),
        name="create_project",
    ),
    path("<int:pk>/edit/", edit_project, name="edit"),
    path("<int:pk>/delete/", delete_project, name="delete"),
    path("<int:pk>/confirm_complete/", complete_project, name="confirm_complete"),
    path("<int:pk>/", project_detail, name="detail"),
    path("<int:project_pk>/build-steps/add/", add_build_step, name="build_step_add"),
    path("build-steps/<int:pk>/edit/", edit_build_step, name="build_step_edit"),
    path("<int:pk>/like/", toggle_like, name="project_like"),
]
