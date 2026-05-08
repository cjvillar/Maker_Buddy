from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MakerProject, ProjectFeature, ProjectLike
from .forms import (
    ProjectBasicForm,
    ProjectTimelineForm,
    ProjectMediaGoalForm,
    ProjectLinkForm,
    ProjectLink,
    ProjectFeatureForm,
    MakerProjectForm,
)
from django.forms import inlineformset_factory
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class CreateProjectWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        ("basic", ProjectBasicForm),
        ("timeline", ProjectTimelineForm),
        ("media", ProjectMediaGoalForm),
        ("feature", ProjectFeatureForm),
        ("link", ProjectLinkForm),
    ]

    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    # Check for active pprojects, only allow one
    def dispatch(self, request, *args, **kwargs):
        has_active = MakerProject.objects.filter(
            owner=request.user, status=MakerProject.Status.ACTIVE
        ).exists()
        if has_active:
            return render(request, "maker_projects/active_project_block.html")
        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        # Create new project
        project = MakerProject(
            owner=self.request.user, status=MakerProject.Status.ACTIVE
        )

        # Merge first three forms (basic, timeline, media)
        for form in form_list[:3]:
            for field, value in form.cleaned_data.items():
                setattr(project, field, value)

        project.save()

        # Handle feature and link forms, TODO: Links still not optional must fix
        feature_data = form_list[3].cleaned_data
        if feature_data:
            ProjectFeature.objects.create(project=project, **feature_data)

        link_data = form_list[4].cleaned_data
        if link_data.get("url"):
            ProjectLink.objects.create(project=project, **link_data)

        return redirect("accounts:profile", self.request.user.username)


@login_required
def edit_project(request, pk):
    project = get_object_or_404(MakerProject, pk=pk, owner=request.user)

    # https://docs.djangoproject.com/en/6.0/ref/forms/models/

    ProjectLinkFormSet = inlineformset_factory(
        MakerProject,
        ProjectLink,
        form=ProjectLinkForm,
        extra=1,
        can_delete=True,
        min_num=0,
        validate_min=False,
    )

    if request.method == "POST":
        form = MakerProjectForm(request.POST, request.FILES, instance=project)
        link_formset = ProjectLinkFormSet(request.POST, instance=project)

        if form.is_valid() and link_formset.is_valid():
            form.save()
            link_formset.save()

            return redirect("maker_projects:detail", pk=project.pk)
    else:
        form = MakerProjectForm(instance=project)
        link_formset = ProjectLinkFormSet(instance=project)

    return render(
        request,
        "maker_projects/edit_project.html",
        {"form": form, "link_formset": link_formset, "project": project},
    )


@login_required
def delete_project(request, pk):
    project = get_object_or_404(MakerProject, pk=pk, owner=request.user)

    if request.method == "POST":
        project.delete()
        return redirect("accounts:profile", request.user.username)

    return render(
        request,
        "maker_projects/confirm_delete.html",
        {"project": project},
    )


@login_required
def complete_project(request, pk):
    project = get_object_or_404(MakerProject, pk=pk, owner=request.user)

    if request.method == "POST":
        project.status = MakerProject.Status.COMPLETED
        project.save()
        return redirect("maker_projects:detail", pk=project.pk)

    return render(request, "maker_projects/confirm_complete.html", {"project": project})


def project_detail(request, pk):
    project = get_object_or_404(MakerProject.objects.select_related("owner"), pk=pk)
    parts = project.parts.select_related("component").prefetch_related(
        "component__prices"
    )
    return render(
        request,
        "maker_projects/project_detail.html",
        {"project": project, "parts": parts},
    )


@login_required
def add_project_link(request, project_id):
    project = get_object_or_404(MakerProject, id=project_id, owner=request.user)

    if request.method == "POST":
        form = ProjectLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.project = project
            link.save()
            return redirect("maker_projects:detail", project_id=project.id)
    else:
        form = ProjectLinkForm()

    return render(
        request, "maker_projects/add_link.html", {"form": form, "project": project}
    )


@login_required
def create_ProjectFeature(request, project_pk):
    project = get_object_or_404(MakerProject, pk=project_pk, owner=request.user)

    if request.method == "POST":
        form = ProjectFeatureForm(request.POST)
        if form.is_valid():
            ProjectFeature = form.save(commit=False)
            ProjectFeature.project = project
            ProjectFeature.order = project.features.count()
            ProjectFeature.save()
            return redirect(
                "maker_projects:detail", project.pk
            )  # redirect user to feed after ProjectFeature created
    else:
        form = ProjectFeatureForm()

    return render(
        request,
        "maker_projects/ProjectFeatures/create.html",
        {"form": form, "project": project},
    )


@login_required
def edit_ProjectFeature(request, pk):
    ProjectFeature = get_object_or_404(
        ProjectFeature, pk=pk, project__owner=request.user
    )

    if request.method == "POST":
        project_pk = ProjectFeature.project.pk
        form = ProjectFeatureForm(request.POST, instance=ProjectFeature)
        if form.is_valid():
            form.save()
            return redirect("maker_projects:detail", project_pk)
    else:
        form = ProjectFeatureForm(instance=ProjectFeature)

    return render(
        request,
        "maker_projects/ProjectFeatures/edit.html",
        {
            "form": form,
            "ProjectFeature": ProjectFeature,
            "project": ProjectFeature.project,
        },
    )


@login_required
def delete_ProjectFeature(request, pk):
    ProjectFeature = get_object_or_404(
        ProjectFeature, pk=pk, project__owner=request.user
    )

    if request.method == "POST":
        project_pk = ProjectFeature.project.pk
        ProjectFeature.delete()
        return redirect("maker_projects:detail", project_pk)

    return render(
        request,
        "maker_projects/ProjectFeatures/confirm_delete.html",
        {"ProjectFeature": ProjectFeature},
    )


@login_required
def toggle_like(request, pk):
    project = get_object_or_404(MakerProject, pk=pk)
    like, created = ProjectLike.objects.get_or_create(
        user=request.user, project=project
    )

    # unlike a project
    if not created:
        like.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))
