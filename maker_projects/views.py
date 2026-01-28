from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import MakerProject, CheckPoint, ProjectLike
from .forms import MakerProjectForm, CheckPointForm, ProjectLinkForm, ProjectLink
from django.forms import inlineformset_factory


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
        link_form = ProjectLinkForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.status = MakerProject.Status.ACTIVE

            project.save()

            # optional links
            if link_form.is_valid() and link_form.cleaned_data:
                link = link_form.save(commit=False)
                link.project = project
                link.save()

            return redirect("accounts:profile", request.user.username)
    else:
        form = MakerProjectForm()
        link_form = ProjectLinkForm()

    return render(
        request,
        "maker_projects/create_project.html",
        {"form": form, "link_form": link_form, "has_active_project": has_active},
    )


@login_required
def edit_project(request, pk):
    project = get_object_or_404(MakerProject, pk=pk, owner=request.user)

    # https://docs.djangoproject.com/en/6.0/ref/forms/models/

    ProjectLinkFormSet = inlineformset_factory(
        MakerProject,
        ProjectLink,
        form=ProjectLinkForm,
        extra=1,  # show one empty form for adding a new link
        can_delete=True,  # enables deleting existing links
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

    return render(
        request,
        "maker_projects/project_detail.html",
        {"project": project},
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
def toggle_like(request, pk):
    project = get_object_or_404(MakerProject, pk=pk)
    like, created = ProjectLike.objects.get_or_create(
        user=request.user, project=project
    )

    # unlike a project
    if not created:
        like.delete()
    return redirect(request.META.get("HTTP_REFERER", "home"))
