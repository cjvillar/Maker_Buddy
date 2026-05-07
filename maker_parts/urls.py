"""
maker_parts/urls.py
"""

from django.urls import path
from . import views

app_name = "maker_parts"

urlpatterns = [
    path("", views.ComponentListView.as_view(), name="component_list"),
    path("<int:pk>/add/", views.AddToProjectView.as_view(), name="add_to_project"),
    path(
        "remove/<int:pk>/",
        views.RemoveFromProjectView.as_view(),
        name="remove_from_project",
    ),
]
