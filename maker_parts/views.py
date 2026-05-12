"""
maker_parts/views.py
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View
from django.urls import reverse
from maker_projects.models import MakerProject
from .models import Component, ProjectPart


class ComponentListView(LoginRequiredMixin, ListView):
    """
    Paginated catalog of all active components with search and category filter.
    Each row has an 'Add to my project' button.
    """

    model = Component
    template_name = "maker_parts/component_list.html"
    context_object_name = "components"
    paginate_by = 20

    def get_queryset(self):
        qs = Component.objects.filter(is_active=True).prefetch_related("prices")
        q = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()

        if q:
            qs = qs.filter(
                Q(manufacturer_pn__icontains=q)
                | Q(description__icontains=q)
                | Q(digikey_part_number__icontains=q)
            )
        if category:
            qs = qs.filter(category=category)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["category"] = self.request.GET.get("category", "")
        ctx["categories"] = (
            Component.objects.filter(is_active=True)
            .values_list("category", flat=True)
            .distinct()
            .order_by("category")
        )
        # Does the user have any active or complete projects project to add parts to?
        # one query creates a list all_proojects (active_project, completed_projects, and selected_project):
        all_projects = list(MakerProject.objects.filter(owner=self.request.user))
        active_project = next((p for p in all_projects if p.status == "active"), None)
        completed_projects = [p for p in all_projects if p.status == "completed"]

        #  coming from a completed project
        selected_id = self.request.GET.get("project_id")
        selected_project = next(
            (p for p in all_projects if str(p.pk) == selected_id), None
        )

        default_project = (
            selected_project
            or active_project
            or (completed_projects[0] if completed_projects else None)
        )

        ctx["active_project"] = active_project
        ctx["default_project"] = default_project
        ctx["completed_projects"] = completed_projects
        return ctx


class AddToProjectView(LoginRequiredMixin, View):
    """
    POST only. Adds a component to the user's active project.
    Redirects back to the catalog (or next param).
    """

    http_method_names = ["post"]

    def post(self, request, pk):
        component = get_object_or_404(Component, pk=pk)
        project_id = request.POST.get("project_id")
        project = get_object_or_404(MakerProject, pk=project_id, owner=request.user)

        # if not project:
        #     messages.warning(request, "You need an active project before adding parts.")
        #     return redirect("maker_parts:component_list")

        quantity = int(request.POST.get("quantity", 1))
        notes = request.POST.get("notes", "").strip()

        try:
            ProjectPart.objects.create(
                project=project,
                component=component,
                quantity=quantity,
                notes=notes,
            )
            messages.success(
                request,
                f'{component.manufacturer} {component.manufacturer_pn} added to "{project.title}".',
            )
        except IntegrityError:
            messages.info(
                request, f'{component.manufacturer_pn} is already in "{project.title}".'
            )

        return redirect(request.POST.get("next") or "maker_parts:component_list")


class RemoveFromProjectView(LoginRequiredMixin, View):
    """
    POST only. Removes a ProjectPart row — only the project owner can do this.
    Redirects back to the project detail page.
    """

    http_method_names = ["post"]

    def post(self, request, pk):
        project_part = get_object_or_404(
            ProjectPart,
            pk=pk,
            project__owner=request.user,
        )
        project = project_part.project
        part_name = project_part.component.manufacturer_pn
        project_part.delete()
        messages.success(request, f'{part_name} removed from "{project.title}".')
        # return redirect("maker_projects:detail", pk=project.pk)
        return redirect(
            reverse("maker_projects:detail", kwargs={"pk": project.pk}) + "#bom"
        )
