from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import MakerProject, BuildStep, ProjectLike
from .forms import (
    ProjectBasicForm,
    ProjectTimelineForm,
    ProjectMediaGoalForm,
    ProjectLinkForm,
    ProjectLink,
    BuildStepForm,
    BuildStepEditForm,
    MakerProjectForm,
)
from django.forms import inlineformset_factory
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin


class CreateProjectWizard(LoginRequiredMixin, SessionWizardView):

    form_list = [
        ("basic", ProjectBasicForm),
        ("timeline", ProjectTimelineForm),
        ("media", ProjectMediaGoalForm),
        ("build_step", BuildStepForm),
        ("link", ProjectLinkForm),
    ]

    file_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

    def dispatch(self, request, *args, **kwargs):
        has_active = MakerProject.objects.filter(
            owner=request.user, status=MakerProject.Status.ACTIVE
        ).exists()
        if has_active:
            return render(request, "maker_projects/active_project_block.html")
        return super().dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        project = MakerProject(
            owner=self.request.user, status=MakerProject.Status.ACTIVE
        )

        for form in form_list[:3]:
            for field, value in form.cleaned_data.items():
                setattr(project, field, value)

        project.save()

        step_data = form_list[3].cleaned_data
        if step_data.get("title"):
            BuildStep.objects.create(project=project, order=0, **step_data)

        link_data = form_list[4].cleaned_data
        if link_data.get("url"):
            ProjectLink.objects.create(project=project, **link_data)

        return redirect("accounts:profile", self.request.user.username)


@login_required
def edit_project(request, slug):
    project = get_object_or_404(MakerProject, slug=slug, owner=request.user)

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
            return redirect("maker_projects:detail", slug=project.slug)
    else:
        form = MakerProjectForm(instance=project)
        link_formset = ProjectLinkFormSet(instance=project)

    return render(
        request,
        "maker_projects/edit_project.html",
        {
            "form": form,
            "link_formset": link_formset,
            "step_form": BuildStepForm(),
            "project": project,
        },
    )


@login_required
def delete_project(request, slug):
    project = get_object_or_404(MakerProject, slug=slug, owner=request.user)

    if request.method == "POST":
        project.delete()
        return redirect("accounts:profile", request.user.username)

    return render(request, "maker_projects/confirm_delete.html", {"project": project})


@login_required
def complete_project(request, slug):
    project = get_object_or_404(MakerProject, slug=slug, owner=request.user)

    if request.method == "POST":
        project.status = MakerProject.Status.COMPLETED
        project.save()
        return redirect("maker_projects:detail", slug=project.slug)

    return render(request, "maker_projects/confirm_complete.html", {"project": project})


def project_detail(request, slug):
    project = get_object_or_404(MakerProject.objects.select_related("owner"), slug=slug)
    parts = project.parts.select_related("component").prefetch_related(
        "component__prices"
    )
    return render(
        request,
        "maker_projects/project_detail.html",
        {"project": project, "parts": parts},
    )


@login_required
def add_project_link(request, slug):
    project = get_object_or_404(MakerProject, slug=slug, owner=request.user)

    if request.method == "POST":
        form = ProjectLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.project = project
            link.save()
            return redirect("maker_projects:detail", slug=project.slug)
    else:
        form = ProjectLinkForm()

    return render(
        request, "maker_projects/add_link.html", {"form": form, "project": project}
    )


@login_required
@require_POST
def add_build_step(request, slug):
    project = get_object_or_404(MakerProject, slug=slug, owner=request.user)
    form = BuildStepForm(request.POST)
    if form.is_valid():
        step = form.save(commit=False)
        step.project = project
        step.order = project.build_steps.count()
        step.save()
    return redirect("maker_projects:edit", slug=slug)


@login_required
def edit_build_step(request, pk):
    step = get_object_or_404(BuildStep, pk=pk, project__owner=request.user)
    project_slug = step.project.slug

    if request.method == "POST":
        if request.POST.get("action") == "delete":
            step.delete()
            return redirect("maker_projects:detail", slug=project_slug)

        form = BuildStepEditForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            return redirect("maker_projects:detail", slug=project_slug)
    else:
        form = BuildStepEditForm(instance=step)

    return render(
        request,
        "maker_projects/build_steps/edit.html",
        {
            "form": form,
            "step": step,
            "project": step.project,
        },
    )


@login_required
def toggle_like(request, slug):
    project = get_object_or_404(MakerProject, slug=slug)
    like, created = ProjectLike.objects.get_or_create(
        user=request.user, project=project
    )

    if not created:
        like.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))
