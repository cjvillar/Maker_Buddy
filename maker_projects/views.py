from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MakerProject, CheckPoint, ProjectLike
from .forms import MakerProjectForm, CheckPointForm


@login_required
def create_project(request):
    has_active = MakerProject.objects.filter(
        owner=request.user,
        status=MakerProject.Status.ACTIVE,
    ).exists()

    if request.method == "POST" and has_active:
        # temlpate informs user of active project
        return redirect("accounts:profile", request.user.username)

    if request.method == "POST":
        form = MakerProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.status = MakerProject.Status.ACTIVE

            project.save()

            return redirect("accounts:profile", request.user.username)
    else:
        form = MakerProjectForm()

    return render(
        request,
        "maker_projects/create_project.html",
        {"form": form, "has_active_project": has_active},
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

    return render(
        request,
        "maker_projects/project_detail.html",
        {"project": project},
    )


@login_required
def create_checkpoint(request, project_pk):
    project = get_object_or_404(MakerProject, pk=project_pk, owner=request.user)

    if request.method == "POST":
        form = CheckPointForm(request.POST)
        if form.is_valid():
            checkpoint = form.save(commit=False)
            checkpoint.project = project
            checkpoint.order = project.checkpoints.count()
            checkpoint.save()
            return redirect(
                "maker_projects:detail", project.pk
            )  # redirect user to feed after checkpoint created
    else:
        form = CheckPointForm()

    return render(
        request,
        "maker_projects/checkpoints/create.html",
        {"form": form, "project": project},
    )


@login_required
def edit_checkpoint(request, pk):
    checkpoint = get_object_or_404(CheckPoint, pk=pk, project__owner=request.user)

    if request.method == "POST":
        project_pk = checkpoint.project.pk
        form = CheckPointForm(request.POST, instance=checkpoint)
        if form.is_valid():
            form.save()
            return redirect("maker_projects:detail", project_pk)
    else:
        form = CheckPointForm(instance=checkpoint)

    return render(
        request,
        "maker_projects/checkpoints/edit.html",
        {
            "form": form,
            "checkpoint": checkpoint,
            "project": checkpoint.project,
        },
    )


@login_required
def delete_checkpoint(request, pk):
    checkpoint = get_object_or_404(CheckPoint, pk=pk, project__owner=request.user)

    if request.method == "POST":
        project_pk = checkpoint.project.pk
        checkpoint.delete()
        return redirect("maker_projects:detail", project_pk)

    return render(
        request,
        "maker_projects/checkpoints/confirm_delete.html",
        {"checkpoint": checkpoint},
    )



@login_required
def toggle_like(request,pk):
    project = get_object_or_404(MakerProject, pk=pk)
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)

    # unlike a project
    if not created:
        like.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))
