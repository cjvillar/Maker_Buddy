from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    # projects = profile_user.projects.all().order_by("-created_at")
    projects = profile_user.maker_projects.select_related("owner").order_by(
        "-created_at"
    )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile_user": profile_user,
            "projects": projects,
        },
    )
