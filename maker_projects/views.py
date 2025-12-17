from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MakerProject
from .forms import MakerProjectForm


@login_required
def create_project(request):
    if request.method == "POST":
        form = MakerProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("accounts:profile", request.user.username)
    else:
        form = MakerProjectForm()

    return render(
        request,
        "maker_projects/create_project.html",
        {"form": form},
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(MakerProject, pk=pk, owner=request.user)

    if request.method == "POST":
        form = MakerProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect("maker_projects:detail", pk=project.pk)
    else:
        form = MakerProjectForm(instance=project)

    return render(
        request,
        "maker_projects/edit_project.html",
        {"form": form, "project": project},
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


def project_detail(request, pk):
    project = get_object_or_404(MakerProject.objects.select_related("owner"), pk=pk)

    return render(
        request,
        "maker_projects/project_detail.html",
        {"project": project},
    )
