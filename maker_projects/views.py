from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
